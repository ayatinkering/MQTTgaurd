#include <WiFi.h>
#include <PubSubClient.h>
#include "mqttguard_model.h"
#include "replay_data.h"
#include "confirmation.h"

// Default traffic source is recorded validation windows, not a live packet sniffer.
static const int LEDS[3]={16,17,18};
static const int BUTTONS[3]={25,26,27};
static const int BUZZER=19, MARKER=23;
static const char *BROKER="test.mosquitto.org";
Confirmation state;
bool playing=true, scripted=false;
uint8_t clipIndex=1;
uint16_t cursor=0;
uint32_t due=0, toneUntil=0;
char runId[40], topic[100];
struct Status { uint32_t id; int prediction; uint8_t streak[3]; bool active[3]; uint32_t events[3]; uint32_t inferenceUs; bool test; uint8_t clip; };
QueueHandle_t statusQueue;

void networkTask(void *) {
  WiFiClient transport;
  PubSubClient mqtt(transport);
  mqtt.setServer(BROKER,1883);mqtt.setBufferSize(512);mqtt.setSocketTimeout(2);
  WiFi.mode(WIFI_STA);WiFi.begin("Wokwi-GUEST","",6);
  uint32_t retry=0;
  Status latest={};bool pending=false;
  for(;;) {
    if(WiFi.status()==WL_CONNECTED) {
      if(!mqtt.connected() && (int32_t)(millis()-retry)>=0) {
        retry=millis()+5000;
        if(mqtt.connect(runId)) Serial.printf("MQTT_CONNECTED topic=%s\n",topic);
      }
      if(mqtt.connected()) {
        mqtt.loop();
        if(xQueueReceive(statusQueue,&latest,0)==pdTRUE) pending=true;
        if(pending) {
          char payload[450];
          snprintf(payload,sizeof(payload),"{\"run\":\"%s\",\"mode\":\"%s\",\"clip\":%u,\"capture\":3,\"window\":%lu,\"prediction\":%d,\"streak\":[%u,%u,%u],\"confirmed\":[%d,%d,%d],\"events\":[%lu,%lu,%lu],\"inference_us_simulated\":%lu}",runId,latest.test?"SCRIPTED_TEST":"ACTUAL_MODEL",latest.clip,(unsigned long)latest.id,latest.prediction,latest.streak[0],latest.streak[1],latest.streak[2],latest.active[0],latest.active[1],latest.active[2],(unsigned long)latest.events[0],(unsigned long)latest.events[1],(unsigned long)latest.events[2],(unsigned long)latest.inferenceUs);
          if(mqtt.publish(topic,payload,false)) { Serial.printf("MQTT_SENT window=%lu\n",(unsigned long)latest.id);pending=false; }
        }
      }
    }
    vTaskDelay(pdMS_TO_TICKS(20));
  }
}

void restartScenario() {
  state=Confirmation();cursor=0;due=millis()+500;playing=true;
  for(int pin:LEDS) digitalWrite(pin,LOW);
  Serial.printf("SCENARIO mode=%s clip=%s capture=3; original window IDs preserved\n",scripted?"SCRIPTED_TEST (bypasses AI)":"ACTUAL_MODEL",CLIPS[clipIndex].name);
}

void stepWindow() {
  static const int TEST_PRED[]={0,1,0,1,1,0,1,1,1,-1,1,-1,1,1,1,0};
  static const uint32_t TEST_ID[]={0,1,2,3,4,5,6,7,8,9,10,11,13,13,14,15};
  if(cursor >= (scripted?16:CLIPS[clipIndex].count)) {playing=false;Serial.println("END_OF_SCENARIO: Next or mode button restarts; start/pause replays.");return;}
  uint32_t id;int prediction;uint32_t elapsed=0;double probability=-1;
  if(scripted) {id=TEST_ID[cursor];prediction=TEST_PRED[cursor];}
  else {
    const ReplayWindow &w=CLIPS[clipIndex].rows[cursor];id=w.id;prediction=-1;
    if(w.valid) {
      float x[4];for(int j=0;j<4;j++) x[j]=(w.missing&(1<<j))?MQTTGUARD_MEDIANS[j]:w.x[j];
      digitalWrite(MARKER,HIGH);uint32_t t=micros();
      probability=mqttguard_probability(x);prediction=probability>0.5?1:0;
      elapsed=micros()-t;digitalWrite(MARKER,LOW);
    }
  }
  uint32_t oldEvents=state.events[1];bool accepted=state.accept(id,prediction);
  for(int i=0;i<3;i++) digitalWrite(LEDS[i],state.active[i]?HIGH:LOW);
  if(state.events[1]>oldEvents) {tone(BUZZER,1600);toneUntil=millis()+150;}
  Serial.printf("%s window=%lu pred=%d probability=%.6f accepted=%d streak=%u/%u/%u confirmed=%d/%d/%d events=%lu/%lu/%lu inference_us_simulated=%lu\n",scripted?"TEST":"MODEL",(unsigned long)id,prediction,probability,accepted,state.streak[0],state.streak[1],state.streak[2],state.active[0],state.active[1],state.active[2],(unsigned long)state.events[0],(unsigned long)state.events[1],(unsigned long)state.events[2],(unsigned long)elapsed);
  Status s={};s.id=id;s.prediction=prediction;s.inferenceUs=elapsed;s.test=scripted;s.clip=clipIndex;
  for(int j=0;j<3;j++){s.streak[j]=state.streak[j];s.active[j]=state.active[j];s.events[j]=state.events[j];}
  // Latest-status mailbox: nonblocking, prevents network failure from blocking inference.
  xQueueOverwrite(statusQueue,&s);
  cursor++;
}

void setup() {
  Serial.begin(115200);
  for(int pin:LEDS) {pinMode(pin,OUTPUT);digitalWrite(pin,LOW);}
  for(int pin:BUTTONS) pinMode(pin,INPUT_PULLUP);
  pinMode(BUZZER,OUTPUT);pinMode(MARKER,OUTPUT);
  snprintf(runId,sizeof(runId),"mqg-%08lx-%08lx",(unsigned long)(ESP.getEfuseMac()&0xffffffff),(unsigned long)esp_random());
  snprintf(topic,sizeof(topic),"mqttguard/%s/status",runId);
  Serial.printf("MQTTGuard RF 16 trees / depth 3 | dataset replay, not live packet capture\nTOPIC=%s\nheap=%u bytes\nGPIO25 next, GPIO26 pause/replay, GPIO27 scripted/AI\n",topic,ESP.getFreeHeap());
  statusQueue=xQueueCreate(1,sizeof(Status));
  if(!statusQueue) {Serial.println("FATAL status queue allocation");playing=false;return;}
  xTaskCreatePinnedToCore(networkTask,"mqtt-status",6144,nullptr,1,nullptr,0);
  restartScenario();
}

void loop() {
  if(!statusQueue) {delay(10);return;}
  static bool last[3]={HIGH,HIGH,HIGH};static uint32_t changed[3]={0,0,0};
  for(int i=0;i<3;i++) {
    bool value=digitalRead(BUTTONS[i]);
    if(value!=last[i] && millis()-changed[i]>50) {
      last[i]=value;changed[i]=millis();
      if(value==LOW) {
        if(i==0){clipIndex=(clipIndex+1)%CLIP_COUNT;restartScenario();}
        if(i==1){if(!playing && cursor>=(scripted?16:CLIPS[clipIndex].count)) restartScenario();else {playing=!playing;due=millis()+2000;}}
        if(i==2){scripted=!scripted;restartScenario();}
      }
    }
  }
  if(toneUntil && (int32_t)(millis()-toneUntil)>=0){noTone(BUZZER);toneUntil=0;}
  if(playing && (int32_t)(millis()-due)>=0){stepWindow();due+=2000;}
  delay(1);
}
