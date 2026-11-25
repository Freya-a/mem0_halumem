import importlib.util
import json
from pathlib import Path
import unittest
from annotations import DATA
import diagnose

HERE=Path(__file__).resolve().parents[1]
ROOT=HERE.parents[2]

def loadplanner():
    path=ROOT/'variants/evidence_scope_planner/candidate_coverage_20261124/scope_planner.py'
    spec=importlib.util.spec_from_file_location('coverage_for_audit',path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

class DiagnosisTests(unittest.TestCase):
    def test_all_original_records_are_reviewed_and_hash_bound(self):
        result=json.loads((HERE/'DIAGNOSIS.json').read_text())
        self.assertEqual(result['metrics']['total'],36)
        self.assertEqual(result['metrics']['facts'],21)
        self.assertEqual(result['metrics']['relations'],15)
        for case in diagnose.NAMES:
            raw=json.loads((diagnose.RUN/(case+'.json')).read_text())['result']['parsed']
            for section in ('facts','relations'):
                audited=result['cases'][case][section]
                self.assertEqual(len(audited),len(raw[section]))
                for record,row in zip(raw[section],audited):
                    self.assertEqual(row['raw_model_output'],record)
                    self.assertEqual(row['record_sha256'],diagnose.digest(record))
                    self.assertEqual(row['record_sha256'],row['prior_review']['sha256'])
                    self.assertIn(row['scope_class'],('embedded','lost','unspecified'))

    def test_overlap_metrics_are_calculated_from_record_flags(self):
        d=json.loads((HERE/'DIAGNOSIS.json').read_text())
        rows=[row for case in d['cases'].values() for s in ('facts','relations') for row in case[s]]
        for combined,count in d['pairwise_overlap'].items():
            left,right=combined.split(' & ')
            self.assertEqual(count,sum(x['flags'][left] and x['flags'][right] for x in rows))
        self.assertEqual(sum(x['scope_class']=='lost' for x in rows),d['metrics']['flag.explicit_qualifier_missing_or_broadened'])
        self.assertGreater(sum(x['scope_class']=='embedded' for x in rows),0)

    def test_unknown_is_not_unconditional_in_scope_calculation(self):
        planner=loadplanner()
        self.assertEqual(planner._conditions({'kind':'unconditional'}),(None,[()]))
        with self.assertRaises(ValueError):planner._conditions({'kind':'unknown'})
        names,cells=planner._conditions({'kind':'finite','dimensions':{'city':['A','B'],'service':['in','out']}})
        self.assertEqual(names,['city','service']);self.assertEqual(len(cells),4)

    def test_model_candidates_have_no_semantic_authorization(self):
        for case in diagnose.NAMES:
            result=json.loads((diagnose.RUN/(case+'.json')).read_text())['result']
            self.assertTrue(result['alignments'])
            self.assertTrue(all(a['semantic_support']=='unknown' for a in result['alignments']))
            self.assertFalse(result['plan']['modify']);self.assertFalse(result['plan']['add'])

if __name__=='__main__':unittest.main()
