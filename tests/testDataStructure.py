# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$

import unittest
from Testing.ZopeTestCase import ZopeLite

import cPickle
from cStringIO import StringIO
from Products.CPSSchemas.DataStructure import DataStructure


class FakeRequest(dict):
    def __init__(self, d={}):
        self.update(d)
        self.SESSION = {}
        self.other = {'SESSION': self.SESSION}

class TestDataStructure(unittest.TestCase):
    """Tests the DataStructure

    Also depends on some fields for testing"""

    def testWithoutDatamodel(self):
        d1 = {'f1': 'Value1', 'f2': 'Value2', 'f3': 'Value3'}
        d2 = {'f2': 'Error2'}
        ds = DataStructure(d1, d2)

        # XXX: do we really want to access the attributes ?
        self.assertEquals(ds.data, d1)
        self.assertEquals(ds.errors, d2)

        ds_copy = ds.copy()
        self.assertEquals(ds_copy.data, d1)
        self.assertEquals(ds_copy.errors, d2)

        self.assertEquals(ds.getError('f2'), 'Error2')
        self.assert_(ds.hasError('f2'))

        ds.setError('f2', 'New error text')
        self.assertEquals(ds.getError('f2'), 'New error text')
        self.assert_(ds.hasError('f2'))

        ds.clearErrors()
        self.assert_(not ds.hasError('f2'))

        ds.set('f1', 'New value')
        self.assertEquals(ds['f1'], 'New value')

        # Test has_key and __contains__
        self.assert_(ds.has_key('f1'))
        self.assert_('f1' in ds)
        self.failIf(ds.has_key('lol'))
        self.failIf('lol' in ds)

        # Test clear()
        ds.clear()
        self.assertEquals(ds.data, {})
        self.assertEquals(ds.errors, {})

        # Test __delitem__()
        ds['f1'] = 'Value1'
        del ds['f1']
        self.assertEquals(ds.data, {})
        self.assertEquals(ds.errors, {})

        ds['f1'] = 'Value1'
        ds.setError('f1', 'Error')
        del ds['f1']
        self.assertEquals(ds.data, {})
        self.assertEquals(ds.errors, {})

        # Test popitem()
        ds['f1'] = 'Value1'
        self.assertEquals(ds.popitem(), ('f1', 'Value1'))
        self.assertRaises(KeyError, ds.popitem)
        self.assertEquals(ds.data, {})
        self.assertEquals(ds.errors, {})

        ds['f1'] = 'Value1'
        ds.setError('f1', 'Error')
        self.assertEquals(ds.popitem(), ('f1', 'Value1'))
        self.assertRaises(KeyError, ds.popitem)
        self.assertEquals(ds.data, {})
        self.assertEquals(ds.errors, {})

        # Test update()
        ds.clear()
        ds.update(d1)
        self.assertEquals(ds.data, d1)
        self.assertEquals(ds.errors, {})

        # Test updateFromMapping()
        d3 = {'widget__f1': 'Value1bis', 'widget__f4': 'Value4'}
        ds.updateFromMapping(d3)
        self.assertEquals(ds.data['f1'], 'Value1bis')
        self.assert_(not ds.has_key('f4'))

    def testSessionLoadSave(self):
        ds = DataStructure()
        somelist = [4, 5]
        somedict = {1: 2, 3: somelist}
        ds['foo'] = 'bar'
        ds['baz'] = somedict
        request = FakeRequest()

        # Testing
        ds._saveToSession(request, '123')
        # Make sure session is picklable
        p = cPickle.Pickler(StringIO(), 1).dump(request.SESSION)
        ds.clear()
        ds['goo'] = 'yuck'
        ds._updateFromSession(request, '123')
        self.assertEquals(ds['goo'], 'yuck')
        self.assertEquals(ds['foo'], 'bar')
        self.assertEquals(ds['baz'], somedict)
        self.failIf(ds['baz'] is somedict) # was copied
        self.failIf(ds['baz'][3] is somelist) # was copied


def test_suite():
    return unittest.makeSuite(TestDataStructure)

if __name__ == "__main__":
    unittest.main(defaultTest='test_suite')
