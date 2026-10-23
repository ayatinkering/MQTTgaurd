#pragma once
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
