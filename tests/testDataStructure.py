# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$

import unittest
from Products.NuxCPS3Document.DataStructure import DataStructure
from Products.NuxCPS3Document.DataModel import DataModel
from Products.NuxCPS3Document.Fields.BasicField import BasicField
from Products.NuxCPS3Document.Fields.TextField import TextField
from Products.NuxCPS3Document.Fields.SelectionField import SelectionField

class DataStructureTests(unittest.TestCase):
    """Tests the DataStructure

    Also depends on some fields for testing"""
    def makeDatamodel(self):
        dm = DataModel()
        f1 = TextField('f1', 'Field1')
        f2 = TextField('f2', 'Field2')
        f3 = SelectionField('f3', 'Field3')
        f3.setOptions( ['Value1', 'Value2', 'Value3'])
        f3.setDefaultValue('Value3')
        dm['f1'] = f1
        dm['f2'] = f2
        dm['f3'] = f3
        return dm


    def test_05_Init(self):
        """Testing DataStructure __init__()"""
        # NB! This test does care about internal storage...
        ds = DataStructure( {'f1': 'Value1', 'f2': 'Value2', 'f3': 'Value3'}, \
                            {'f2': 'Error2'})
        self.failUnless( ds.data == {'f1': 'Value1', 'f2': 'Value2', \
                         'f3': 'Value3'}, 'Init failed to set data')
        self.failUnless( ds.errors == {'f2': 'Error2'}, \
                         'Init failed to set errors')

    def test_06_Errors(self):
        """Testing the error access interface"""
        ds = DataStructure( {'f1': 'Value1', 'f2': 'Value2', 'f3': 'Value3'}, \
                            {'f2': 'Error2'})
        self.failUnless(ds.hasError('f2'), 'HasError failed')
        ds.setError('f2', 'New error text')
        self.failUnless(ds.getError('f2') == 'New error text', 'setError or geError failed')
        ds.delError('f2')
        self.failIf(ds.hasError('f2'), 'dasError failed')


    def test_10_Clear(self):
        """Testing clear()"""
        ds = DataStructure( {'f1': 'Value1', 'f2': 'Value2', 'f3': 'Value3'}, \
                            {'f2': 'Error2'})
        ds.clear()
        self.failUnless(len(ds) == 0, 'Clear() failed')
        self.failUnless(len(ds.errors) == 0, 'Clear() failed')

    def test_15_Del(self):
        """Testing key deletion"""
        ds = DataStructure( {'f1': 'Value1', 'f2': 'Value2', 'f3': 'Value3'}, \
                            {'f2': 'Error2'})
        del ds['f1']
        self.failIf(ds.has_key('f1'), 'Del failed')
        self.failUnless(ds.hasError('f2'), 'Del removed an error that should stay')
        del ds['f2']
        self.failIf(ds.has_key('f1'), 'Del failed')
        self.failIf(ds.hasError('f2'), 'Del failed to remove error')


    def test_20_PopItem(self):
        """Testing popitem"""
        ds = DataStructure( {'f1': 'Value1', 'f2': 'Value2', 'f3': 'Value3'}, \
                            {'f2': 'Error2'})
        dict = {}
        count = 0
        while len(ds):
            key, value = ds.popitem()
            self.failIf(dict.has_key(key), 'Popitem popped already popped item')
            dict[key] = value
            count = count +1
        self.failUnless(dict == {'f1': 'Value1', 'f2': 'Value2', 'f3': 'Value3'}, \
                        'Popitem did not pop all items')

    def test_21_PopItem(self):
        """Make sure popitem also removes errors"""
        ds = DataStructure( {'f1': 'Value1', 'f2': 'Value2', 'f3': 'Value3'}, \
                            {'f2': 'Error2'})
        while len(ds):
            key, value = ds.popitem()
            if key == 'f2':
                self.failIf(ds.hasError('f2'), 'Popitem failed to remove error')

    def test_30_Copy(self):
        """Test copy"""
        ds = DataStructure( {'f1': 'Value1', 'f2': 'Value2', 'f3': 'Value3'}, \
                            {'f2': 'Error2'})
        copy = ds.copy()
        self.failUnless( copy.data == {'f1': 'Value1', 'f2': 'Value2', \
                         'f3': 'Value3'}, 'Init failed to set data')
        self.failUnless( copy.errors == {'f2': 'Error2'}, \
                         'Init failed to set errors')

    def test_50_UpdateFromRequest(self):
        """Update from request, with missing values"""
        # Make a 'fake' REQUEST from a dict:
        ds = DataStructure()
        dm = self.makeDatamodel()
        rq = { 'field_f1': 'Value1', 'f2': 'Value2', }
        ds.updateFromRequest(dm, rq)
        isequal = ds.data['f1'] == 'Value1' and \
                  ds.data['f2'] == 'Value2' and \
                  ds.data['f3'] == 'Value3'
        self.failUnless(isequal, 'Update from REQUEST failed')

    def test_51_UpdateFromRequestWithError(self):
        """Update from request with invalid values"""
        # Make a 'fake' REQUEST from a dict:
        ds = DataStructure()
        dm = self.makeDatamodel()
        rq = { 'field_f1': 'Value1', 'f2': 'Value2', 'f3': 'Invalid' }
        ds.updateFromRequest(dm, rq)
        isequal = ds.data['f1'] == 'Value1' and \
                  ds.data['f2'] == 'Value2' and \
                  ds.data['f3'] == 'Invalid'
        self.failUnless(isequal, 'Update from REQUEST failed')
        self.failUnless(ds.getError('f3') != None, 'Failed to set error')


def test_suite():
    return unittest.makeSuite(DataStructureTests)

if __name__=="__main__":
    unittest.main(defaultTest='test_suite')
