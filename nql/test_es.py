import nql
import unittest
import json

def transform(q):
  nql_tree = nql.NqlParser().parse(q)
  es_transformer = nql.EsTransformer()
  return es_transformer.to_dict(nql_tree)

class TestEsTransformer(unittest.TestCase):
  def test_eq(self):
    expected = {'query': {'term': { 'a': 'b'}}}
    actual = transform('"a"="b"')
    self.assertEqual(expected, actual)

  def test_and(self):
    expected = {
      'query': { 
        'bool': {
          "filter": [
            {'term': { 'a': 'b'}},
            {'term': { 'c': 'd'}}
          ]
        }
      }
    }

    actual = transform('AND("a"="b", "c"="d")')
    self.assertEqual(expected, actual)
  
  def test_not(self):
    expected = {
      'query': { 
        'bool': {
          "must_not": [
            {'term': { 'a': 'b'}}
          ]
        }
      }
    }
    actual = transform('NOT("a"="b")')
    self.assertEqual(expected, actual)
    