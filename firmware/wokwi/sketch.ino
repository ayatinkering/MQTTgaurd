#include <WiFi.h>
#include <PubSubClient.h>
// mqttguard_model.h

#include <stdint.h>
#include <math.h>
// Generated from the frozen sklearn model; soft voting, no quantization.
static const float MQTTGUARD_MEDIANS[4] = {0x1.0000000000000p+0f, 0x1.3400000000000p+9f, 0x1.fef416bdb1a6dp-2f, 0x0.0p+0f};
static inline double mqttguard_probability(const float *x) {
double sum = 0.0;
if ((double)x[1] <= 0x1.38f0000000000p+9) {
 if ((double)x[3] <= 0x1.5a7cc60000000p+5) {
  if ((double)x[2] <= 0x1.024c1e8000000p-1) {
   sum += 0x1.2efb34bbecd2fp-3;
  } else {
   sum += 0x1.a2e8ba2e8ba2fp-2;
  }
 } else {
  if ((double)x[0] <= 0x1.4000000000000p+1) {
   sum += 0x1.0000000000000p-1;
  } else {
   sum += 0x1.f5637b5b85f81p-1;
  }
 }
} else {
 if ((double)x[2] <= 0x1.9fe4738000000p-6) {
  sum += 0x0.0p+0;
 } else {
  if ((double)x[2] <= 0x1.04fde30000000p-1) {
   sum += 0x1.ed751ed751ed7p-1;
  } else {
   sum += 0x1.86bca1af286bdp-1;
  }
 }
}
if ((double)x[2] <= 0x1.ff52a20000000p-2) {
 if ((double)x[2] <= 0x1.f6d96a0000000p-2) {
  if ((double)x[2] <= 0x1.1e1f1a0000000p-5) {
   sum += 0x1.662e255b31713p-1;
  } else {
   sum += 0x1.efeda1dd8f7f7p-1;
  }
 } else {
  if ((double)x[3] <= 0x1.e000000000000p+4) {
   sum += 0x1.c50ef4904660cp-3;
  } else {
   sum += 0x1.3333333333333p-1;
  }
 }
} else {
 if ((double)x[2] <= 0x1.0538150000000p-1) {
  sum += 0x1.0000000000000p+0;
 } else {
  if ((double)x[2] <= 0x1.1296570000000p+0) {
   sum += 0x1.3737373737373p-1;
  } else {
   sum += 0x1.e38e38e38e38ep-1;
  }
 }
}
if ((double)x[0] <= 0x1.8000000000000p+0) {
 if ((double)x[1] <= 0x1.41c0000000000p+9) {
  if ((double)x[1] <= 0x1.2e40000000000p+9) {
   sum += 0x1.6c797dd49c341p-1;
  } else {
   sum += 0x1.02c5c6b34adbfp-3;
  }
 } else {
  if ((double)x[1] <= 0x1.85a0000000000p+10) {
   sum += 0x1.c8dc8dc8dc8ddp-1;
  } else {
   sum += 0x1.91b91b91b91b9p-1;
  }
 }
} else {
 if ((double)x[2] <= 0x1.1e1f1a0000000p-5) {
  if ((double)x[3] <= 0x1.7b03f00000000p+5) {
   sum += 0x1.e50d79435e50dp-3;
  } else {
   sum += 0x1.fc3518a6dfc35p-1;
  }
 } else {
  if ((double)x[1] <= 0x1.32e0000000000p+9) {
   sum += 0x1.5a95a95a95a96p-1;
  } else {
   sum += 0x1.f800000000000p-1;
  }
 }
}
if ((double)x[1] <= 0x1.3900000000000p+9) {
 if ((double)x[1] <= 0x1.2c20000000000p+9) {
  if ((double)x[1] <= 0x1.decc060000000p+7) {
   sum += 0x1.a0a0a0a0a0a0ap-1;
  } else {
   sum += 0x1.ecc07b301ecc0p-2;
  }
 } else {
  if ((double)x[2] <= 0x1.3c5ed48000000p-1) {
   sum += 0x1.eb2da5c5ce593p-4;
  } else {
   sum += 0x1.0000000000000p+0;
  }
 }
} else {
 if ((double)x[0] <= 0x1.4000000000000p+1) {
  if ((double)x[2] <= 0x1.41cbcc0000000p-4) {
   sum += 0x1.1745d1745d174p-1;
  } else {
   sum += 0x1.ca4d6ca4d6ca5p-1;
  }
 } else {
  if ((double)x[3] <= 0x1.1512bb8000000p+4) {
   sum += 0x1.ff85288c1dc03p-1;
  } else {
   sum += 0x1.999999999999ap-1;
  }
 }
}
if ((double)x[1] <= 0x1.3900000000000p+9) {
 if ((double)x[1] <= 0x1.2e00000000000p+9) {
  if ((double)x[1] <= 0x1.cc7b180000000p+7) {
   sum += 0x1.b2b78c13521d0p-1;
  } else {
   sum += 0x1.0cb58f6ec0743p-1;
  }
 } else {
  if ((double)x[1] <= 0x1.2f40000000000p+9) {
   sum += 0x1.1745d1745d174p-2;
  } else {
   sum += 0x1.02532e3d7b389p-3;
  }
 }
} else {
 if ((double)x[0] <= 0x1.4000000000000p+1) {
  if ((double)x[1] <= 0x1.3560000000000p+10) {
   sum += 0x1.adcc548ceadccp-1;
  } else {
   sum += 0x1.d824ca58e9019p-1;
  }
 } else {
  if ((double)x[1] <= 0x1.b9aaab0000000p+9) {
   sum += 0x1.e8ba2e8ba2e8cp-1;
  } else {
   sum += 0x1.0000000000000p+0;
  }
 }
}
if ((double)x[2] <= 0x1.ff52a20000000p-2) {
 if ((double)x[0] <= 0x1.8000000000000p+0) {
  if ((double)x[1] <= 0x1.3d00000000000p+9) {
   sum += 0x1.0e273b5825bdfp-3;
  } else {
   sum += 0x1.cc74d50c06df6p-1;
  }
 } else {
  if ((double)x[1] <= 0x1.3300000000000p+9) {
   sum += 0x1.60d6c5835b161p-1;
  } else {
   sum += 0x1.f131f75d25a10p-1;
  }
 }
} else {
 if ((double)x[1] <= 0x1.f280000000000p+8) {
  sum += 0x0.0p+0;
 } else {
  if ((double)x[0] <= 0x1.4000000000000p+1) {
   sum += 0x1.b555555555555p-1;
  } else {
   sum += 0x1.ff3795876ff38p-1;
  }
 }
}
if ((double)x[1] <= 0x1.41c0000000000p+9) {
 if ((double)x[0] <= 0x1.8000000000000p+0) {
  if ((double)x[1] <= 0x1.2e40000000000p+9) {
   sum += 0x1.745d1745d1746p-1;
  } else {
   sum += 0x1.0dd3cddc13203p-3;
  }
 } else {
  if ((double)x[3] <= 0x1.5db8080000000p+5) {
   sum += 0x1.0572620ae4c41p-2;
  } else {
   sum += 0x1.f149902f14990p-1;
  }
 }
} else {
 if ((double)x[1] <= 0x1.86f0000000000p+10) {
  if ((double)x[1] <= 0x1.bba6660000000p+9) {
   sum += 0x1.cdb017ad2208ep-1;
  } else {
   sum += 0x1.f4d50c06df5b1p-1;
  }
 } else {
  if ((double)x[0] <= 0x1.8000000000000p+0) {
   sum += 0x1.8e38e38e38e39p-1;
  } else {
   sum += 0x1.0000000000000p+0;
  }
 }
}
if ((double)x[1] <= 0x1.3900000000000p+9) {
 if ((double)x[3] <= 0x1.72f7e40000000p+5) {
  if ((double)x[1] <= 0x1.2c20000000000p+9) {
   sum += 0x1.674c59d31674cp-2;
  } else {
   sum += 0x1.f9fd20042e859p-4;
  }
 } else {
  if ((double)x[2] <= 0x1.2507adc000000p-2) {
   sum += 0x1.f98f4bac46d7cp-1;
  } else {
   sum += 0x1.5555555555555p-2;
  }
 }
} else {
 if ((double)x[0] <= 0x1.4000000000000p+1) {
  if ((double)x[2] <= 0x1.e64fba0000000p-2) {
   sum += 0x1.999999999999ap-1;
  } else {
   sum += 0x1.d25cb3b2fc6f4p-1;
  }
 } else {
  if ((double)x[3] <= 0x1.07c8a60000000p+4) {
   sum += 0x1.ff8580b7beec6p-1;
  } else {
   sum += 0x1.3333333333333p-1;
  }
 }
}
if ((double)x[1] <= 0x1.38f0000000000p+9) {
 if ((double)x[1] <= 0x1.2ec0000000000p+9) {
  if ((double)x[3] <= 0x1.68ec4f0000000p+5) {
   sum += 0x1.c71c71c71c71cp-2;
  } else {
   sum += 0x1.df51b3bea3678p-1;
  }
 } else {
  if ((double)x[2] <= 0x1.3c5ed48000000p-1) {
   sum += 0x1.06b85c4e9cf90p-3;
  } else {
   sum += 0x1.0000000000000p+0;
  }
 }
} else {
 if ((double)x[1] <= 0x1.85c0000000000p+10) {
  if ((double)x[2] <= 0x1.12e72d8000000p-6) {
   sum += 0x0.0p+0;
  } else {
   sum += 0x1.f392247c4a932p-1;
  }
 } else {
  if ((double)x[0] <= 0x1.8000000000000p+0) {
   sum += 0x1.9add3c0ca4588p-1;
  } else {
   sum += 0x1.0000000000000p+0;
  }
 }
}
if ((double)x[1] <= 0x1.38f0000000000p+9) {
 if ((double)x[3] <= 0x1.570f0f0000000p+5) {
  if ((double)x[0] <= 0x1.8000000000000p+0) {
   sum += 0x1.0a4ce0181e25bp-3;
  } else {
   sum += 0x1.f58d0fac687d6p-3;
  }
 } else {
  if ((double)x[0] <= 0x1.a000000000000p+2) {
   sum += 0x1.0000000000000p-1;
  } else {
   sum += 0x1.f1c71c71c71c7p-1;
  }
 }
} else {
 if ((double)x[1] <= 0x1.da80000000000p+10) {
  if ((double)x[2] <= 0x1.ff52a20000000p-2) {
   sum += 0x1.df783893180b5p-1;
  } else {
   sum += 0x1.ff4437bf7329dp-1;
  }
 } else {
  if ((double)x[1] <= 0x1.e140000000000p+10) {
   sum += 0x0.0p+0;
  } else {
   sum += 0x1.0000000000000p+0;
  }
 }
}
if ((double)x[0] <= 0x1.8000000000000p+0) {
 if ((double)x[1] <= 0x1.3940000000000p+9) {
  if ((double)x[1] <= 0x1.2b00000000000p+9) {
   sum += 0x1.6f4de9bd37a6fp-1;
  } else {
   sum += 0x1.233d26592233dp-3;
  }
 } else {
  if ((double)x[1] <= 0x1.85c0000000000p+10) {
   sum += 0x1.dd5a77569dd5ap-1;
  } else {
   sum += 0x1.9ee58469ee584p-1;
  }
 }
} else {
 if ((double)x[3] <= 0x1.1d37a70000000p+4) {
  if ((double)x[1] <= 0x1.2ca0000000000p+9) {
   sum += 0x1.0000000000000p-2;
  } else {
   sum += 0x1.fae0165cb5b14p-1;
  }
 } else {
  if ((double)x[3] <= 0x1.5b0f0f0000000p+5) {
   sum += 0x1.2bb512bb512bbp-2;
  } else {
   sum += 0x1.e762762762762p-1;
  }
 }
}
if ((double)x[1] <= 0x1.3900000000000p+9) {
 if ((double)x[3] <= 0x1.68ec4f0000000p+5) {
  if ((double)x[0] <= 0x1.8000000000000p+0) {
   sum += 0x1.24dcec3aacb52p-3;
  } else {
   sum += 0x1.c924924924925p-3;
  }
 } else {
  if ((double)x[0] <= 0x1.a000000000000p+2) {
   sum += 0x1.0000000000000p-2;
  } else {
   sum += 0x1.f322bbd1b03dcp-1;
  }
 }
} else {
 if ((double)x[0] <= 0x1.4000000000000p+1) {
  if ((double)x[2] <= 0x1.c3541a0000000p-2) {
   sum += 0x1.684bda12f684cp-1;
  } else {
   sum += 0x1.cecb785a6e611p-1;
  }
 } else {
  if ((double)x[2] <= 0x1.a068060000000p-4) {
   sum += 0x1.f5dc83cd4e930p-1;
  } else {
   sum += 0x1.0000000000000p+0;
  }
 }
}
if ((double)x[0] <= 0x1.8000000000000p+0) {
 if ((double)x[1] <= 0x1.3940000000000p+9) {
  if ((double)x[3] <= 0x1.e000000000000p+4) {
   sum += 0x1.2d92446bece4cp-3;
  } else {
   sum += 0x1.b6db6db6db6dbp-2;
  }
 } else {
  if ((double)x[1] <= 0x1.5dc0000000000p+9) {
   sum += 0x1.5555555555555p-1;
  } else {
   sum += 0x1.d260511be1959p-1;
  }
 }
} else {
 if ((double)x[1] <= 0x1.32e0000000000p+9) {
  if ((double)x[3] <= 0x1.6d8b480000000p+5) {
   sum += 0x1.e1e1e1e1e1e1ep-3;
  } else {
   sum += 0x1.f666666666666p-1;
  }
 } else {
  if ((double)x[1] <= 0x1.cde0000000000p+9) {
   sum += 0x1.ec8590b21642dp-1;
  } else {
   sum += 0x1.fbdde6af24f0cp-1;
  }
 }
}
if ((double)x[0] <= 0x1.8000000000000p+0) {
 if ((double)x[3] <= 0x1.e000000000000p+4) {
  if ((double)x[1] <= 0x1.3940000000000p+9) {
   sum += 0x1.2691896c77534p-3;
  } else {
   sum += 0x1.cf3cf3cf3cf3dp-1;
  }
 } else {
  sum += 0x1.0000000000000p-1;
 }
} else {
 if ((double)x[3] <= 0x1.b7b8650000000p+4) {
  if ((double)x[0] <= 0x1.4000000000000p+1) {
   sum += 0x1.8dab7ec1dd343p-1;
  } else {
   sum += 0x1.fcfc3b4a1ca3dp-1;
  }
 } else {
  if ((double)x[1] <= 0x1.3a1d010000000p+8) {
   sum += 0x1.b5d4ef40991f2p-1;
  } else {
   sum += 0x1.0572620ae4c41p-2;
  }
 }
}
if ((double)x[2] <= 0x1.ff52a20000000p-2) {
 if ((double)x[1] <= 0x1.3900000000000p+9) {
  if ((double)x[3] <= 0x1.5c64640000000p+5) {
   sum += 0x1.20fb49d0e228dp-3;
  } else {
   sum += 0x1.fa1d6cdfa1d6dp-1;
  }
 } else {
  if ((double)x[0] <= 0x1.c000000000000p+1) {
   sum += 0x1.b11dc47711dc4p-1;
  } else {
   sum += 0x1.feb77faddfeb7p-1;
  }
 }
} else {
 if ((double)x[2] <= 0x1.0321cc0000000p+0) {
  if ((double)x[1] <= 0x1.f6d5550000000p+8) {
   sum += 0x0.0p+0;
  } else {
   sum += 0x1.fe814edb005fbp-1;
  }
 } else {
  if ((double)x[1] <= 0x1.3120000000000p+9) {
   sum += 0x0.0p+0;
  } else {
   sum += 0x1.b333333333333p-1;
  }
 }
}
if ((double)x[1] <= 0x1.38f0000000000p+9) {
 if ((double)x[3] <= 0x1.5c64640000000p+5) {
  if ((double)x[1] <= 0x1.2e40000000000p+9) {
   sum += 0x1.d0cb58f6ec074p-2;
  } else {
   sum += 0x1.da895da895da9p-4;
  }
 } else {
  if ((double)x[2] <= 0x1.785b240000000p-4) {
   sum += 0x1.e25b9efd4e25cp-1;
  } else {
   sum += 0x1.aaaaaaaaaaaabp-2;
  }
 }
} else {
 if ((double)x[2] <= 0x1.0419a08000000p-6) {
  sum += 0x0.0p+0;
 } else {
  if ((double)x[0] <= 0x1.4000000000000p+1) {
   sum += 0x1.c96720c21f8b8p-1;
  } else {
   sum += 0x1.ff7efdfbf7efep-1;
  }
 }
}
return sum / 16.0;
}
static inline int mqttguard_predict(const float *x) { return mqttguard_probability(x) > 0.5 ? 1 : 0; }

// replay_data.h

struct ReplayWindow { uint32_t id; bool valid; uint8_t missing; float x[4]; };
struct ReplayClip { const char *name; const ReplayWindow *rows; uint16_t count; };
static const ReplayWindow CLIP_0[] = {
{0,true,4,{0x1.0000000000000p+0f,0x1.3080000000000p+9f,0.0f,0x0.0p+0f}},
{1,false,15,{0.0f,0.0f,0.0f,0.0f}},
{2,false,15,{0.0f,0.0f,0.0f,0.0f}},
{3,false,15,{0.0f,0.0f,0.0f,0.0f}},
{4,false,15,{0.0f,0.0f,0.0f,0.0f}},
{5,true,4,{0x1.0000000000000p+0f,0x1.3300000000000p+9f,0.0f,0x0.0p+0f}},
{6,false,15,{0.0f,0.0f,0.0f,0.0f}},
{7,false,15,{0.0f,0.0f,0.0f,0.0f}},
{8,false,15,{0.0f,0.0f,0.0f,0.0f}},
{9,false,15,{0.0f,0.0f,0.0f,0.0f}},
{10,true,4,{0x1.0000000000000p+0f,0x1.3380000000000p+9f,0.0f,0x0.0p+0f}},
{11,false,15,{0.0f,0.0f,0.0f,0.0f}},
{12,false,15,{0.0f,0.0f,0.0f,0.0f}},
{13,false,15,{0.0f,0.0f,0.0f,0.0f}},
{14,false,15,{0.0f,0.0f,0.0f,0.0f}},
{15,true,4,{0x1.0000000000000p+0f,0x1.3280000000000p+9f,0.0f,0x0.0p+0f}},
{16,false,15,{0.0f,0.0f,0.0f,0.0f}},
{17,false,15,{0.0f,0.0f,0.0f,0.0f}},
};
static const ReplayWindow CLIP_1[] = {
{712,true,4,{0x1.0000000000000p+0f,0x1.2700000000000p+9f,0.0f,0x0.0p+0f}},
{713,false,15,{0.0f,0.0f,0.0f,0.0f}},
{714,true,0,{0x1.e000000000000p+3f,0x1.3aaaaaaaaaaabp+5f,0x1.c5bf73a3ff2f8p-8f,0x1.e000000000000p+5f}},
{715,true,0,{0x1.a400000000000p+6f,0x1.b1fb1fb1fb1fbp+7f,0x1.3181b1c9aeea1p-6f,0x1.8492492492492p+5f}},
{716,true,0,{0x1.1800000000000p+5f,0x1.13d999999999ap+10f,0x1.d8ed926517d7bp-5f,0x0.0p+0f}},
{717,true,0,{0x1.2000000000000p+5f,0x1.2caaaaaaaaaabp+10f,0x1.c84af26c99865p-5f,0x0.0p+0f}},
{718,false,15,{0.0f,0.0f,0.0f,0.0f}},
{719,false,15,{0.0f,0.0f,0.0f,0.0f}},
{720,true,4,{0x1.0000000000000p+0f,0x1.3b00000000000p+9f,0.0f,0x0.0p+0f}},
{721,false,15,{0.0f,0.0f,0.0f,0.0f}},
{722,false,15,{0.0f,0.0f,0.0f,0.0f}},
{723,true,4,{0x1.0000000000000p+0f,0x1.2900000000000p+9f,0.0f,0x0.0p+0f}},
{724,false,15,{0.0f,0.0f,0.0f,0.0f}},
{725,true,0,{0x1.9800000000000p+5f,0x1.d1e1e1e1e1e1ep+5f,0x1.808edba582b0fp-7f,0x1.d696969696969p+5f}},
{726,true,0,{0x1.8000000000000p+1f,0x1.db00000000000p+9f,0x1.01991361dc93fp-1f,0x0.0p+0f}},
{727,true,0,{0x1.0000000000000p+2f,0x1.a020000000000p+9f,0x1.0129d6dab45dbp-1f,0x0.0p+0f}},
{728,true,0,{0x1.4000000000000p+2f,0x1.20d999999999ap+10f,0x1.822e1ac57e23fp-2f,0x0.0p+0f}},
{729,true,0,{0x1.0000000000000p+2f,0x1.2af0000000000p+10f,0x1.016e20b6a0823p-1f,0x0.0p+0f}},
};
static const ReplayWindow CLIP_2[] = {
{0,true,4,{0x1.0000000000000p+0f,0x1.3080000000000p+9f,0.0f,0x0.0p+0f}},
{1,false,15,{0.0f,0.0f,0.0f,0.0f}},
{2,false,15,{0.0f,0.0f,0.0f,0.0f}},
{3,false,15,{0.0f,0.0f,0.0f,0.0f}},
{4,false,15,{0.0f,0.0f,0.0f,0.0f}},
{5,true,4,{0x1.0000000000000p+0f,0x1.3300000000000p+9f,0.0f,0x0.0p+0f}},
{6,false,15,{0.0f,0.0f,0.0f,0.0f}},
{7,false,15,{0.0f,0.0f,0.0f,0.0f}},
{8,false,15,{0.0f,0.0f,0.0f,0.0f}},
{9,false,15,{0.0f,0.0f,0.0f,0.0f}},
{10,true,4,{0x1.0000000000000p+0f,0x1.3380000000000p+9f,0.0f,0x0.0p+0f}},
{11,false,15,{0.0f,0.0f,0.0f,0.0f}},
{12,false,15,{0.0f,0.0f,0.0f,0.0f}},
{13,false,15,{0.0f,0.0f,0.0f,0.0f}},
{14,false,15,{0.0f,0.0f,0.0f,0.0f}},
{15,true,4,{0x1.0000000000000p+0f,0x1.3280000000000p+9f,0.0f,0x0.0p+0f}},
{16,false,15,{0.0f,0.0f,0.0f,0.0f}},
{17,false,15,{0.0f,0.0f,0.0f,0.0f}},
};
static const ReplayClip CLIPS[] = {{"BENIGN TRACE",CLIP_0,18},{"SLOWITE TRACE",CLIP_1,18},{"GAP TRACE",CLIP_2,18}};
static const uint8_t CLIP_COUNT = 3;

// confirmation.h

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
