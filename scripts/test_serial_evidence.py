"""Ensure target-evidence validation rejects fabricated/wrong build, model and state output."""
import json
import numpy as np
import pytest
import verify_wokwi_serial as verifier

@pytest.fixture
def sample(monkeypatch,tmp_path):
    (tmp_path/'firmware/wokwi').mkdir(parents=True)
    (tmp_path/'docs/results').mkdir(parents=True)
    (tmp_path/'firmware/wokwi/build.json').write_text(json.dumps({'build_id':'fixture'}))
    (tmp_path/'docs/results/manifest.json').write_text(json.dumps({'clips':[{'name':'CLIP','start_window':0,'count':1}]}))
    class Imputer:
        def transform(self,x):return x
    class Model:
        def predict_proba(self,x):return np.array([[.1,.9]])
    monkeypatch.setattr(verifier,'ROOT',tmp_path)
    monkeypatch.setattr(verifier.joblib,'load',lambda _: {'imputer':Imputer(),'model':Model()})
    monkeypatch.setattr(verifier,'make_capture',lambda *_:{'windows':[{'valid':True,'x':[1,2,3,4]}]})
    monkeypatch.setattr(verifier,'predict_capture',lambda *_:([1],0))
    return 'BUILD=fixture\nSCENARIO mode=ACTUAL_MODEL clip=CLIP capture=3;\nMODEL window=0 pred=1 probability=0.900000 accepted=1 streak=1/1/1 confirmed=1/0/0 events=1/0/0 inference_us_simulated=50\n'

def test_observed_row_and_complete_clip(sample):
    r=verifier.verify(sample)
    assert r['complete_clip_passes']==['CLIP']
    assert r['observed_model_rows']==1

@pytest.mark.parametrize('before,after',[('BUILD=fixture','BUILD=wrong'),('pred=1','pred=0'),('probability=0.900000','probability=0.800000'),('confirmed=1/0/0','confirmed=1/1/0')])
def test_rejects_wrong_target_output(sample,before,after):
    with pytest.raises(AssertionError):verifier.verify(sample.replace(before,after))
