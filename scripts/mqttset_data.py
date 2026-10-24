"""Download original MQTTset v5 captures and extract timestamped TCP metadata.

No payload is used as a model feature. CONNECT parsing only reads protocol metadata.
PCAP file-level scenarios are not asserted to be packet-level attack ground truth.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import socket
import struct
import urllib.parse
import urllib.request
from zipfile import ZipFile, is_zipfile
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
BASE='https://www.kaggle.com/api/v1/datasets/download/cnrieiit/mqttset/'


def download():
    dest=ROOT/'data/external/mqttset';dest.mkdir(parents=True,exist_ok=True)
    entries=[]
    for name in ['capture_1w.pcap','slowite.pcap','capture_malariaDoS.pcap']:
        remote='Data/PCAP/'+name
        url=BASE+urllib.parse.quote(remote,safe='')+'?datasetVersionNumber=5'
        p=dest/name
        if not p.exists():
            with urllib.request.urlopen(url,timeout=120) as response,p.with_suffix('.part').open('wb') as f:
                shutil.copyfileobj(response,f,4*1024*1024)
            p.with_suffix('.part').replace(p)
        if is_zipfile(p):
            compressed=p.with_suffix('.zip');p.replace(compressed)
            with ZipFile(compressed) as archive:
                members=[i for i in archive.infolist() if Path(i.filename).name==name]
                if len(members)!=1:raise ValueError('Unexpected download archive members')
                with archive.open(members[0]) as source,p.open('wb') as f:shutil.copyfileobj(source,f,4*1024*1024)
        h=hashlib.sha256()
        with p.open('rb') as f:
            for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
        entries.append({'name':name,'bytes':p.stat().st_size,'sha256':h.hexdigest(),'url':url})
    manifest={'dataset':'MQTTset','version':5,'source':'https://www.kaggle.com/datasets/cnrieiit/mqttset',
              'paper':'https://doi.org/10.3390/s20226578','license':'CC BY-NC-SA 4.0 per Kaggle metadata; publisher README contains a conflicting Apache software license statement',
              'files':entries,'label_scope':'Known benign file and SlowITe scenario file; no invented packet-level attack labels'}
    target=ROOT/'docs/research';target.mkdir(parents=True,exist_ok=True)
    (target/'external_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return dest


def mqtt_keepalive(payload):
    if not payload or payload[0]>>4!=1:return 0
    position=1
    for _ in range(4):
        if position>=len(payload):return 0
        b=payload[position];position+=1
        if b<128:break
    else:return 0
    if position+2>len(payload):return 0
    n=int.from_bytes(payload[position:position+2],'big');position+=2
    if position+n+4>len(payload):return 0
    protocol=payload[position:position+n]
    if protocol not in [b'MQTT',b'MQIsdp']:return 0
    return int.from_bytes(payload[position+n+2:position+n+4],'big')


class ConnectReassembly:
    """Attribute CONNECT metadata to its completing TCP segment, like the CSV dissector.

    Only incomplete CONNECT lengths/keepalive/sequence are retained, never payload.
    Other MQTT message contents are not retained or used by the classifier.
    """
    def __init__(self):
        self.pending={};self.completed={}

    def feed(self,flow,sequence,flags,payload):
        if flags&7:
            self.pending.pop(flow,None);self.completed.pop(flow,None)
        if not payload:return 0
        if flow in self.pending:
            expected,remaining,keepalive,start=self.pending[flow]
            if sequence>expected:return 0
            new=max(0,len(payload)-(expected-sequence))
            if not new:return 0
            remaining-=new
            if remaining<=0:
                self.pending.pop(flow);self.completed[flow]=start;return keepalive
            self.pending[flow]=(expected+new,remaining,keepalive,start);return 0
        if payload[0]>>4!=1 or self.completed.get(flow)==sequence:return 0
        length=0;multiple=1;position=1
        for _ in range(4):
            if position>=len(payload):return 0
            b=payload[position];position+=1;length+=(b&127)*multiple;multiple*=128
            if b<128:break
        else:return 0
        # Incomplete fixed/variable headers are unsupported and explicitly return no metadata.
        if position+2>len(payload):return 0
        protocol_length=int.from_bytes(payload[position:position+2],'big')
        if position+2+protocol_length+4>len(payload):return 0
        keepalive=mqtt_keepalive(payload)
        remaining=position+length-len(payload)
        if remaining>0:
            self.pending[flow]=(sequence+len(payload),remaining,keepalive,sequence);return 0
        self.completed[flow]=sequence;return keepalive


def packets(path, port=1883):
    """Yield (integer epoch us, TCP payload length, recorded keepalive, srcport, dstport)."""
    with Path(path).open('rb') as f:
        header=f.read(24)
        formats={b'\xd4\xc3\xb2\xa1':('<',1),b'\xa1\xb2\xc3\xd4':('>',1),
                 b'\x4d\x3c\xb2\xa1':('<',1000),b'\xa1\xb2\x3c\x4d':('>',1000)}
        if header[:4] not in formats:raise ValueError('Expected classic PCAP (use dumpcap -P)')
        endian,divisor=formats[header[:4]]
        link=struct.unpack(endian+'I',header[20:24])[0]
        if link not in [1,113,276]:raise ValueError(f'Unsupported link type {link}')
        unpack=struct.Struct(endian+'IIII').unpack
        decoder=ConnectReassembly()
        while True:
            h=f.read(16)
            if not h:break
            if len(h)!=16:raise ValueError('Truncated record header')
            sec,fraction,n,_=unpack(h);packet=f.read(n)
            if len(packet)!=n:raise ValueError('Truncated captured packet')
            if n<34:continue
            if link==1:eth=int.from_bytes(packet[12:14],'big');offset=14
            elif link==113:eth=int.from_bytes(packet[14:16],'big');offset=16
            else:eth=int.from_bytes(packet[:2],'big');offset=20
            while eth in [0x8100,0x88a8]:
                if len(packet)<offset+4:break
                eth=int.from_bytes(packet[offset+2:offset+4],'big');offset+=4
            if eth!=0x0800 or len(packet)<offset+20:continue
            ip=packet[offset:];ihl=(ip[0]&15)*4
            if ip[0]>>4!=4 or ihl<20 or ip[9]!=6 or len(ip)<ihl+20:continue
            if int.from_bytes(ip[6:8],'big')&0x3fff:continue
            tcp=ip[ihl:];src,dst=struct.unpack('!HH',tcp[:4])
            if src!=port and dst!=port:continue
            thl=(tcp[12]>>4)*4
            length=max(0,int.from_bytes(ip[2:4],'big')-ihl-thl)
            if thl<20:continue
            payload=tcp[thl:thl+length]
            flow=(ip[12:20],src,dst)
            sequence=int.from_bytes(tcp[4:8],'big')
            keepalive=decoder.feed(flow,sequence,tcp[13],payload)
            yield sec*1000000+fraction//divisor,length,keepalive,src,dst


def capture_from_packets(path, name, label, seconds=2, port=1883, accepted_ports=None):
    """Streaming window aggregation preserves empty intervals with O(windows) memory."""
    bins={};origin=None;last=None;count=0;ties=0;inversions=0;previous=None
    for stamp,length,ka,src,dst in packets(path,port):
        if accepted_ports is not None and src not in accepted_ports and dst not in accepted_ports:continue
        if previous is not None:
            ties+=stamp==previous;inversions+=stamp<previous
        previous=stamp
        if origin is None:origin=stamp
        # Preserve real timestamps. Small capture ordering inversions are aggregated by timestamp.
        last=max(last or stamp,stamp);count+=1
        j=(stamp-origin)//(seconds*1000000)
        if j<0:raise ValueError('Packet precedes first timestamp')
        b=bins.get(j)
        if b is None:bins[j]=[1,length,ka,stamp,stamp]
        else:
            b[0]+=1;b[1]+=length;b[2]+=ka;b[3]=min(b[3],stamp);b[4]=max(b[4],stamp)
    if origin is None:raise ValueError(f'No matching TCP records in {name}')
    complete=(last-origin)//(seconds*1000000)
    ids=np.arange(complete,dtype=np.int64);X=np.full((complete,4),np.nan)
    valid=np.zeros(complete,dtype=bool);y=np.full(complete,-1,dtype=np.int8)
    for j,b in bins.items():
        if j>=complete:continue
        n,length,ka,first,end=b
        X[j]=[n,length/n,(end-first)/1e6/(n-1) if n>1 else np.nan,ka/n]
        valid[j]=True;y[j]=label
    runs=[{'id':0,'start':origin,'end':last}] if label==1 else []
    return {'name':name,'seconds':seconds,'ids':ids,'end_us':origin+(ids+1)*seconds*1000000,
            'X':X,'valid':valid,'y':y,'runs':runs,
            'extraction':{'parser_version':2,'packets':count,'first_epoch_us':origin,'last_epoch_us':last,
                          'timestamp_ties':ties,'ordering_inversions':inversions,
                          'schema':'All IPv4 TCP packets to/from broker port; tcp_len=declared TCP payload bytes; CONNECT keepalive attributed to completing TCP segment, otherwise 0',
                          'label_scope':'benign capture' if label==0 else 'attack scenario, not verified per-packet labels'}}


def slice_capture(cap, start_fraction, end_fraction, name, guard_s=5):
    first=cap['end_us'][0]-cap['seconds']*1000000;last=cap['end_us'][-1]
    start=first+(last-first)*start_fraction+(guard_s*1e6 if start_fraction else 0)
    end=first+(last-first)*end_fraction-(guard_s*1e6 if end_fraction<1 else 0)
    mask=(cap['end_us']-cap['seconds']*1000000>=start)&(cap['end_us']<=end)
    result={**cap,'name':name}
    for key in ['ids','end_us','X','valid','y']:result[key]=cap[key][mask].copy()
    result['runs']=[{'id':0,'start':int(start),'end':int(end)}] if cap['runs'] else []
    return result


if __name__=='__main__':
    print(download())
