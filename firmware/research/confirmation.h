#pragma once
#include <stdint.h>
struct Confirmation {
  uint8_t streak[3] = {0,0,0};
  bool active[3] = {false,false,false};
  uint32_t events[3] = {0,0,0};
  bool seen = false;
  uint32_t last = 0;
  void reset() { for(int i=0;i<3;i++) { streak[i]=0;active[i]=false; } seen=false; }
  bool accept(uint32_t id, int prediction) {
    if (seen && id<=last) return false;
    if (seen && id!=last+1) { for(int i=0;i<3;i++) { streak[i]=0;active[i]=false; } }
    seen=true;last=id;
    for (int i=0;i<3;i++) {
      if (prediction==1) { if (streak[i]<i+1) streak[i]++; } else streak[i]=0;
      bool next=streak[i]>=i+1;
      if(next && !active[i]) events[i]++;
      active[i]=next;
    }
    return true;
  }
};
