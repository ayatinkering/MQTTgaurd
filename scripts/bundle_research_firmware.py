"""Generate an extended ESP32 demo without replacing the verified original demo."""
from pathlib import Path
import hashlib
import json
import shutil
from train_pipeline import ROOT


def main():
    selection=json.loads((ROOT/'docs/research/validation_frontiers.json').read_text())[0]['selected']
    policy=next(r['policy'] for r in selection if r['policy']['family']=='bounded_evidence')
    h=policy['h'];decay=policy['decay']
    source=ROOT/'firmware/mqttguard';fw=ROOT/'firmware/research';out=ROOT/'firmware/wokwi_research'
    fw.mkdir(exist_ok=True);out.mkdir(exist_ok=True)
    sketch=(source/'sketch.ino').read_text()
    def replace(old,new):
        nonlocal sketch
        if sketch.count(old)!=1:raise ValueError(f'Expected one source anchor: {old[:70]}')
        sketch=sketch.replace(old,new)
    replace('#include "confirmation.h"','#include "confirmation.h"\n#include "evidence_policy.h"')
    replace('Confirmation state;',f'Confirmation state;\nBoundedEvidence evidence({h!r}, {decay!r});\nstatic const int EVIDENCE_LED=21;')
    replace('bool test; uint8_t clip; };','bool test; uint8_t clip; double evidenceValue; bool evidenceActive; uint32_t evidenceEvents; };')
    replace('state=Confirmation();cursor=0;',f'state=Confirmation();evidence=BoundedEvidence({h!r},{decay!r});digitalWrite(EVIDENCE_LED,LOW);cursor=0;')
    replace('uint32_t oldEvents=state.events[1];bool accepted=state.accept(id,prediction);',
            'uint32_t oldEvents=state.events[1];bool accepted=state.accept(id,prediction);\n  double score=prediction<0?NAN:(scripted?(double)prediction:probability);\n  bool evidenceAccepted=evidence.accept(id,score);\n  digitalWrite(EVIDENCE_LED,evidence.active?HIGH:LOW);')
    replace('Status s={};s.id=id;',
            'Serial.printf("EVIDENCE window=%lu value=%.9f confirmed=%d events=%lu accepted=%d\\n",(unsigned long)id,evidence.value,evidence.active,(unsigned long)evidence.events,evidenceAccepted);\n  Status s={};s.evidenceValue=evidence.value;s.evidenceActive=evidence.active;s.evidenceEvents=evidence.events;s.id=id;')
    replace('pinMode(BUZZER,OUTPUT);pinMode(MARKER,OUTPUT);',
            'pinMode(BUZZER,OUTPUT);pinMode(MARKER,OUTPUT);pinMode(EVIDENCE_LED,OUTPUT);')
    replace('Serial.printf("BUILD=%s\\n",BUILD_ID);',
            f'Serial.printf("BUILD=%s\\n",BUILD_ID);\n  Serial.printf("EVIDENCE_POLICY h={h} decay={decay} bytes=%u\\n",(unsigned)sizeof(BoundedEvidence));')
    replace('\\"inference_us_simulated\\":%lu}',
            '\\"evidence\\":%.6f,\\"evidence_confirmed\\":%d,\\"evidence_events\\":%lu,\\"inference_us_simulated\\":%lu}')
    replace('(unsigned long)latest.inferenceUs);',
            'latest.evidenceValue,latest.evidenceActive,(unsigned long)latest.evidenceEvents,(unsigned long)latest.inferenceUs);')
    (fw/'sketch.ino').write_text(sketch)
    for name in ['mqttguard_model.h','replay_data.h','confirmation.h','libraries.txt']:
        shutil.copyfile(source/name,fw/name)
    bundled=sketch
    for name in ['mqttguard_model.h','replay_data.h','confirmation.h','evidence_policy.h']:
        bundled=bundled.replace('#include "'+name+'"','// '+name+'\n'+(fw/name).read_text().replace('#pragma once',''))
    build=hashlib.sha256(bundled.encode()).hexdigest()[:16]
    bundled=bundled.replace('SOURCE_BUILD_ID',build)
    (out/'sketch.ino').write_text(bundled)
    (out/'build.json').write_text(json.dumps({'build_id':build,'sketch_sha256':hashlib.sha256(bundled.encode()).hexdigest(),'policy':policy},indent=2)+'\n')
    shutil.copyfile(source/'libraries.txt',out/'libraries.txt')
    circuit=json.loads((ROOT/'firmware/wokwi/diagram.json').read_text())
    circuit['parts'] += [
        {'type':'wokwi-led','id':'evidenceLED','top':-70,'left':465,'attrs':{'color':'green','label':'BOUNDED EVIDENCE'}},
        {'type':'wokwi-resistor','id':'evidenceR','top':-15,'left':460,'attrs':{'value':'220'}}]
    circuit['connections'] += [['esp:D21','evidenceR:1','green',[]],['evidenceR:2','evidenceLED:A','green',[]],['evidenceLED:C','esp:GND.1','black',[]]]
    (out/'diagram.json').write_text(json.dumps(circuit,indent=2)+'\n')
    print('Extended source build:',build,'policy:',policy)


if __name__=='__main__':main()
