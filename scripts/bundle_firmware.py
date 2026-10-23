"""Generate one browser-friendly sketch; source files remain independently testable."""
from pathlib import Path
import json
root=Path(__file__).resolve().parents[1];fw=root/'firmware/mqttguard';out=root/'firmware/wokwi';out.mkdir(parents=True,exist_ok=True)
headers=['mqttguard_model.h','replay_data.h','confirmation.h']
sketch=(fw/'sketch.ino').read_text()
for h in headers:sketch=sketch.replace('#include "'+h+'"','// '+h+'\n'+(fw/h).read_text().replace('#pragma once',''))
(out/'sketch.ino').write_text(sketch);(out/'libraries.txt').write_text((fw/'libraries.txt').read_text())
parts=[{'type':'wokwi-esp32-devkit-v1','id':'esp','top':0,'left':0,'attrs':{}}];connections=[]
for i,color in enumerate(['orange','red','purple']):
    parts += [{'type':'wokwi-led','id':f'led{i}','top':-70,'left':260+i*65,'attrs':{'color':color,'label':f'k={i+1}'}},{'type':'wokwi-resistor','id':f'r{i}','top':-15,'left':255+i*65,'attrs':{'value':'220'}}]
    connections += [[('esp:RX2' if i==0 else 'esp:TX2' if i==1 else 'esp:D18'),f'r{i}:1','green',[]],[f'r{i}:2',f'led{i}:A','green',[]],[f'led{i}:C','esp:GND.1','black',[]]]
for i,label in enumerate(['NEXT TRACE','PAUSE / PLAY','AI / TEST']):
    parts.append({'type':'wokwi-pushbutton','id':f'btn{i}','top':100+i*65,'left':270,'attrs':{'color':'blue','label':label,'bounce':'0'}})
    connections += [[f'btn{i}:1.l',f'esp:D{25+i}','blue',[]],[f'btn{i}:2.l','esp:GND.1','black',[]]]
parts.append({'type':'wokwi-buzzer','id':'buzzer','top':25,'left':450,'attrs':{'volume':'0.1'}})
connections += [['buzzer:2','esp:D19','red',[]],['buzzer:1','esp:GND.1','black',[]],['esp:TX0','$serialMonitor:RX','',[]],['esp:RX0','$serialMonitor:TX','',[]]]
diagram={'version':1,'author':'MQTTGuard team','editor':'wokwi','parts':parts,'connections':connections,'dependencies':{}}
(out/'diagram.json').write_text(json.dumps(diagram,indent=2)+'\n')
print('Browser bundle:',out)
