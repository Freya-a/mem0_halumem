import copy
import importlib.util
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
from splitter import ValidationError


def load_version():
    assert (HERE / 'v10_splitter.py').exists(), 'v10 component boundary has not been implemented'
    spec = importlib.util.spec_from_file_location('v10_splitter', HERE / 'v10_splitter.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def example():
    request = {'memory_id': 'm', 'memory_text': 'Previously worked as a senior developer in Blockchain Tech'}
    fact = {'fact_index': 1, 'source_memory_id': 'm', 'raw_subfact': request['memory_text'],
            'contextualized_subfact': 'The user previously worked as a senior developer in Blockchain Tech.',
            'evidence': [{'source_type': 'memory', 'source_id': 'm', 'quote': request['memory_text'],
                          'supports': 'The memory states a past position and organization.'}],
            'pending_confirmations': []}
    def located(quote):
        return {'status': 'located', 'source_type': 'memory', 'source_id': 'm', 'quote': quote}
    components = [{'fact_index': 1, 'employer': located('Blockchain Tech'),
                   'position': located('senior developer'), 'relationship': located(request['memory_text'])}]
    return request, {'facts': [fact], 'employment_components': components}


class ComponentBoundaryTests(unittest.TestCase):
    def run_candidate(self, response):
        request, _ = example()
        return load_version().split_memory_v10(request, lambda prompt: lambda _: copy.deepcopy(response))

    def test_returns_original_fact_and_cited_employment_components(self):
        request, response = example()
        result = self.run_candidate(response)
        self.assertEqual(result['memory_text'], request['memory_text'])
        self.assertEqual(result['facts'], response['facts'])
        self.assertEqual(result['employment_components'], response['employment_components'])

    def test_rejects_quote_from_wrong_source(self):
        _, response = example()
        response['employment_components'][0]['employer']['quote'] = 'Imaginary Employer'
        with self.assertRaises(ValidationError) as caught:
            self.run_candidate(response)
        self.assertEqual(caught.exception.code, 'quote_not_found')

    def test_preserves_pending_without_invented_values(self):
        _, response = example()
        pending = {'status': 'pending', 'source_type': None, 'source_id': None, 'quote': None}
        response['employment_components'][0]['employer'] = pending
        response['employment_components'][0]['relationship'] = copy.deepcopy(pending)
        result = self.run_candidate(response)
        self.assertEqual(result['employment_components'][0]['employer'], pending)

    def test_rejects_located_relationship_if_either_component_pending(self):
        _, response = example()
        response['employment_components'][0]['employer'] = {'status': 'pending', 'source_type': None, 'source_id': None, 'quote': None}
        with self.assertRaises(ValidationError) as caught:
            self.run_candidate(response)
        self.assertEqual(caught.exception.code, 'invalid_relationship')

    def test_rejects_component_for_nonexistent_fact(self):
        _, response = example()
        response['employment_components'][0]['fact_index'] = 2
        with self.assertRaises(ValidationError) as caught:
            self.run_candidate(response)
        self.assertEqual(caught.exception.code, 'invalid_fact_index')

    def test_original_fact_quote_validation_still_applies(self):
        _, response = example()
        response['facts'][0]['evidence'][0]['quote'] = 'fabricated'
        with self.assertRaises(ValidationError) as caught:
            self.run_candidate(response)
        self.assertEqual(caught.exception.code, 'quote_not_found')


if __name__ == '__main__':
    unittest.main()
