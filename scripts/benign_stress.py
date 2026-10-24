"""Record real-time benign MQTT workloads against a local publisher-only broker.

Uses standard Paho clients, a minimal MQTT 3.1.1 broker, and dumpcap on loopback.
No attack traffic or public broker is involved. Independent capture sessions are
concurrent clients, not independent physical devices or days.
"""
import argparse
import asyncio
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import random
import subprocess
import threading
import time
import paho.mqtt.client as mqtt

ROOT=Path(__file__).resolve().parents[1]
PORT=18883


async def broker_client(reader,writer):
    try:
        while True:
            first=(await reader.readexactly(1))[0];length=0;multiple=1
            for _ in range(4):
                byte=(await reader.readexactly(1))[0];length+=(byte&127)*multiple;multiple*=128
                if byte<128:break
            if length>100000:raise ValueError('Unexpected local demo message size')
            payload=await reader.readexactly(length)
            kind=first>>4
            if kind==1:writer.write(b'\x20\x02\x00\x00')
            elif kind==12:writer.write(b'\xd0\x00')
            elif kind==14:break
            elif kind==3 and (first>>1)&3:
                topic_len=int.from_bytes(payload[:2],'big')
                writer.write(b'\x40\x02'+payload[2+topic_len:4+topic_len])
            await writer.drain()
    except (asyncio.IncompleteReadError,ConnectionError):pass
    finally:
        writer.close()


def run(seconds=120,repeats=4):
    dest=ROOT/'data/benign_stress';dest.mkdir(parents=True,exist_ok=True)
    loop=asyncio.new_event_loop();ready=threading.Event()
    def serve():
        asyncio.set_event_loop(loop)
        async def start():
            server=await asyncio.start_server(broker_client,'127.0.0.1',PORT)
            ready.set();return server
        loop.run_until_complete(start());loop.run_forever()
    threading.Thread(target=serve,daemon=True).start()
    if not ready.wait(5):raise RuntimeError('Local broker did not start')
    capture=dest/'legitimate_workloads.pcap'
    diagnostic=(dest/'dumpcap.log').open('w')
    dump=subprocess.Popen(['/usr/bin/dumpcap','-i','lo','-f',f'tcp port {PORT}',
                           '-P','-a',f'duration:{seconds+5}','-w',str(capture)],
                          stdout=diagnostic,stderr=subprocess.STDOUT)
    time.sleep(1)
    if dump.poll() is not None:raise RuntimeError('Capture failed; inspect data/benign_stress/dumpcap.log')
    profiles=['steady','bursts','reconnects','rate_changes','idle','combined']
    lock=threading.Lock();sessions=[]
    def worker(profile,repetition):
        seed=4400+profiles.index(profile)*100+repetition;rng=random.Random(seed)
        name=f'{profile}-{repetition}';ports=set();connected=threading.Event()
        client=mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,client_id='mqg-benign-'+name)
        def on_connect(c,userdata,flags,reason,properties):
            if int(reason.value)!=0:raise RuntimeError(str(reason))
            ports.add(c.socket().getsockname()[1]);connected.set()
        client.on_connect=on_connect
        def connect():
            connected.clear();client.connect('127.0.0.1',PORT,keepalive=15);client.loop_start()
            if not connected.wait(3):raise RuntimeError('Paho failed to connect')
        connect();start=time.monotonic();start_epoch=time.time();next_send=0.;last_reconnect=0.;sent=0
        while True:
            elapsed=time.monotonic()-start
            if elapsed>=seconds:break
            if profile in ['reconnects','combined'] and elapsed-last_reconnect>=9:
                client.disconnect();client.loop_stop();time.sleep(.1);connect();last_reconnect=elapsed
            if elapsed>=next_send:
                if profile=='steady':interval=2.
                elif profile=='bursts':interval=.08 if int(elapsed)%12<2 else 3.
                elif profile=='reconnects':interval=1.5
                elif profile=='rate_changes':interval=[4.,1.,.2,2.][min(3,int(elapsed/(seconds/4)))]
                elif profile=='idle':
                    if seconds*.2<elapsed<seconds*.65:next_send=elapsed+.2;time.sleep(.02);continue
                    interval=1.
                else:interval=rng.choice([.1,.3,1.,3.])
                payload=json.dumps({'client':name,'sequence':sent,'sensor':rng.random(),'padding':'x'*rng.choice([20,100,400,600])})
                info=client.publish('mqttguard/benign/'+name,payload,qos=0)
                if info.rc!=mqtt.MQTT_ERR_SUCCESS:raise RuntimeError(f'Publish failed {info.rc}')
                sent+=1;next_send=elapsed+interval
            time.sleep(.01)
        client.disconnect();client.loop_stop()
        row={'name':name,'profile':profile,'seed':seed,'source_ports':sorted(ports),
             'start_epoch_s':start_epoch,'duration_observed_s':time.monotonic()-start,'published_messages':sent}
        with lock:sessions.append(row)
    print(f'Recording {len(profiles)*repeats} concurrent benign client sessions for {seconds}s',flush=True)
    with ThreadPoolExecutor(max_workers=len(profiles)*repeats) as executor:
        futures=[executor.submit(worker,p,r) for p in profiles for r in range(repeats)]
        for future in futures:future.result()
    dump.wait(timeout=10);diagnostic.close()
    if dump.returncode:raise RuntimeError('dumpcap did not exit successfully')
    loop.call_soon_threadsafe(loop.stop)
    manifest={'scope':'Observed real-time local-only MQTT publisher workloads; concurrent clients, not independent devices/days',
              'duration_s':seconds,'port':PORT,'broker':'Minimal local MQTT 3.1.1 publisher/keepalive broker',
              'sessions':sorted(sessions,key=lambda r:r['name'])}
    (dest/'sessions.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Completed real-time benign capture:',capture,flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--seconds',type=int,default=120)
    parser.add_argument('--repeats',type=int,default=4);args=parser.parse_args();run(args.seconds,args.repeats)
