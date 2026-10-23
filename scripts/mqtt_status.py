"""Subscribe to the exact TOPIC printed by Wokwi; log ordinary demo status only."""
import argparse,json,time
from pathlib import Path
import paho.mqtt.client as mqtt
p=argparse.ArgumentParser();p.add_argument('--topic',required=True);p.add_argument('--host',default='test.mosquitto.org');p.add_argument('--port',type=int,default=1883);p.add_argument('--output',default='reports/mqtt_received.jsonl');p.add_argument('--seconds',type=int,default=120);a=p.parse_args()
path=Path(a.output);path.parent.mkdir(parents=True,exist_ok=True)
def connect(client,userdata,flags,reason,properties):
    print('CONNECTED',reason,flush=True);client.subscribe(a.topic)
def message(client,userdata,msg):
    try:
        payload=json.loads(msg.payload)
        with path.open('a') as f:f.write(json.dumps({'received_at':time.time(),'topic':msg.topic,'payload':payload})+'\n')
        print(json.dumps(payload),flush=True)
    except (ValueError,UnicodeDecodeError) as e: print('INVALID',str(e),flush=True)
c=mqtt.Client(mqtt.CallbackAPIVersion.VERSION2);c.on_connect=connect;c.on_message=message;c.connect(a.host,a.port,60);c.loop_start()
try:time.sleep(a.seconds)
finally:c.disconnect();c.loop_stop()
