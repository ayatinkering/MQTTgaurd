import csv, subprocess
from pathlib import Path
from train_pipeline import make_capture, confirm, ROOT

def test_boundaries_empty_and_singletons(tmp_path):
    p=tmp_path/'capture.csv'
    with p.open('w') as f:
        w=csv.writer(f);w.writerow(['timestamp','label','tcp_len','mqtt_kalive'])
        w.writerows([['0','legitimate',10,0],['2','slowite',20,60],['6','slowite',30,60]])
    cap=make_capture(p,1)
    assert [w['id'] for w in cap['windows']]==[0,1,2]
    assert [w['valid'] for w in cap['windows']]==[True,True,False]
    assert cap['windows'][1]['y']==1
    assert cap['windows'][1]['end']==4000000
    assert len(cap['runs'])==1

def test_consecutive_events_and_gaps():
    assert confirm([1,1,1,1],2)==([False,True,True,True],[1])
    assert confirm([1,-1,1],2)==([False,False,False],[])
    assert confirm([1,0,1],1)[1]==[0,2]

def test_cpp_actual_firmware_confirmation(tmp_path):
    p=tmp_path/'test.cpp'
    p.write_text('#include <cassert>\n#include "'+str(ROOT/'firmware/mqttguard/confirmation.h')+'"\nint main(){Confirmation s;assert(s.accept(1,1));assert(!s.active[1]);assert(!s.accept(1,1));assert(s.accept(2,1));assert(s.active[1]);assert(s.events[1]==1);s.accept(3,1);assert(s.events[1]==1);s.accept(5,1);assert(!s.active[1]);s.accept(6,-1);assert(!s.active[0]);s.accept(7,1);assert(!s.active[1]);s.reset();s.accept(0,1);assert(!s.active[1]);}\n')
    exe=tmp_path/'test';subprocess.run(['g++','-std=c++17','-Wall','-Wextra','-Werror',str(p),'-o',str(exe)],check=True);subprocess.run([str(exe)],check=True)
