"""Compare the actual C++ evidence module with Python over saved score streams."""
import ctypes
import json
from pathlib import Path
import subprocess
import numpy as np
from research_core import apply_policy, audit
from train_pipeline import ROOT


def main():
    cache=ROOT/'reports/research';cpp=cache/'evidence_parity.cpp';lib=cache/'evidence_parity.so'
    cpp.write_text('#include "'+str(ROOT/'firmware/research/evidence_policy.h')+'"\n'
        'extern "C" void run(const double*p,const uint32_t*id,int n,double h,double d,uint8_t*out,uint32_t*events){'
        'BoundedEvidence s(h,d);for(int i=0;i<n;i++){s.accept(id[i],p[i]);out[i]=s.active;events[i]=s.events;}}\n'
        'extern "C" unsigned state_size(){return sizeof(BoundedEvidence);}\n')
    subprocess.run(['g++','-std=c++17','-O2','-Wall','-Wextra','-Werror','-shared','-fPIC',str(cpp),'-o',str(lib)],check=True)
    dll=ctypes.CDLL(str(lib));fn=dll.run
    fn.argtypes=[ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_uint32),ctypes.c_int,
                 ctypes.c_double,ctypes.c_double,ctypes.POINTER(ctypes.c_uint8),ctypes.POINTER(ctypes.c_uint32)]
    policies=[]
    for fold in json.loads((ROOT/'docs/research/validation_frontiers.json').read_text()):
        policies += [r['policy'] for r in fold['selected'] if r['policy']['family']=='bounded_evidence']
    ext=json.loads((ROOT/'docs/research/external_results.json').read_text())
    policies += [r['policy'] for r in ext['adaptation_validation_selection'] if r['policy']['family']=='bounded_evidence']
    checks=[];transitions=0
    for file in sorted(cache.glob('*.npz')):
        data=np.load(file,allow_pickle=False);scores=np.ascontiguousarray(data['scores'],dtype=np.float64)
        ids=np.ascontiguousarray(data['ids'],dtype=np.uint32)
        for policy in policies:
            actual=np.zeros(len(ids),dtype=np.uint8);events=np.zeros(len(ids),dtype=np.uint32)
            fn(scores.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),ids.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
               len(ids),policy['h'],policy['decay'],actual.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8)),events.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)))
            expected=apply_policy(scores,ids,policy)
            starts=expected & (~np.r_[False,expected[:-1]] | np.r_[True,ids[1:]!=ids[:-1]+1])
            assert np.array_equal(actual,expected),(file.name,policy,'active')
            assert np.array_equal(events,np.cumsum(starts)),(file.name,policy,'events')
            transitions+=len(ids);checks.append({'stream':file.name,'policy':policy,'transitions':len(ids),'disagreements':0})
    # Actual acceptance semantics: duplicates/older IDs must not mutate the evidence state.
    test=cache/'evidence_edges.cpp';exe=cache/'evidence_edges'
    test.write_text('#include <cassert>\n#include "'+str(ROOT/'firmware/research/evidence_policy.h')+'"\n'
        'int main(){BoundedEvidence s(.5,1.);assert(s.accept(0,.9));assert(!s.active);'
        'assert(!s.accept(0,.9));assert(s.value<.5);assert(s.accept(1,.9));assert(s.active);'
        'assert(!s.accept(0,.9));assert(s.events==1);s.accept(4,.9);assert(!s.active);'
        's.accept(5,NAN);assert(s.value==0);s.accept(6,.9);assert(!s.active);}\n')
    subprocess.run(['g++','-std=c++17','-Wall','-Wextra','-Werror',str(test),'-o',str(exe)],check=True)
    subprocess.run([str(exe)],check=True)
    result={'score_policy_transitions':transitions,'label_or_event_disagreements':0,
            'host_state_bytes':dll.state_size(),'checks':checks,'edge_cases_passed':True,
            'scope':'Host-compiled actual evidence module; not an ESP32 timing or full target execution claim'}
    (ROOT/'docs/research/evidence_cpp_parity.json').write_text(json.dumps(result,indent=2)+'\n')
    print('C++ evidence parity:',transitions,'transitions; zero discrepancies; state bytes:',dll.state_size())


if __name__=='__main__':main()
