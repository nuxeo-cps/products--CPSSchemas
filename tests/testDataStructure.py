# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$

import unittest
from Testing.ZopeTestCase import ZopeLite

from Products.CPSDocument.DataStructure import DataStructure
from Products.CPSDocument.DataModel import DataModel
from Products.CPSDocument.Schema import CPSSchema
from Products.CPSDocument.Fields.BasicField import BasicField
from Products.CPSDocument.Fields.TextField import TextField
from Products.CPSDocument.Fields.SelectionField import SelectionField

class DataStructureTests(unittest.TestCase):
    """Tests the DataStructure

    Also depends on some fields for testing"""

    def makeDatamodel(self):
        dm = DataModel()
        schema = CPSSchema('schema', 'Schema')
        f1 = TextField('f1', 'Field1')
        f2 = TextField('f2', 'Field2')
        f3 = SelectionField('f3', 'Field3')
        f3.setOptions(['Value1', 'Value2', 'Value3'])
        f3.setDefaultValue('Value3')
        schema['f1'] = f1
        schema['f2'] = f2
        schema['f3'] = f3
        dm.addSchema(schema)
        return dm


    def test_05_Init(self):
        """Testing DataStructure __init__()"""
        # NB! This test does care about internal storage...
        ds = DataStructure({'f1': 'Value1', 'f2': 'Value2', 'f3': 'Value3'},
                           {'f2': 'Error2'})
        self.failUnless(ds.data == {'f1': 'Value1', 'f2': 'Value2',
                         'f3': 'Value3'}, 'Init failed to set data')
        self.failUnless(ds.errors == {'f2': 'Error2'},
                         'Init failed to set errors')

    def test_06_Errors(self):
        """Testing the error access interface"""
        ds = DataStructure({'f1': 'Value1', 'f2': 'Value2', 'f3': 'Value3'},
                           {'f2': 'Error2'})
        self.failUnless(ds.hasError('f2'), 'HasError failed')
        ds.setError('f2', 'New error text')
        self.failUnless(ds.getError('f2') == 'New error text', 
            'setError or geError failed')
        ds.delError('f2')
        self.failIf(ds.hasError('f2'), 'dasError failed')

    def test_10_Clear(self):
        """Testing clear()"""
        ds = DataStructure({'f1': 'Value1', 'f2': 'Value2', 'f3': 'Value3'},
                           {'f2': 'Error2'})
        ds.clear()
        self.failUnless(len(ds) == 0, 'Clear() failed')
        self.failUnless(len(ds.errors) == 0, 'Clear() failed')

    def test_15_Del(self):
        """Testing key deletion"""
        ds = DataStructure({'f1': 'Value1', 'f2': 'Value2', 'f3': 'Value3'},
                           {'f2': 'Error2'})
        del ds['f1']
        self.failIf(ds.has_key('f1'), 'Del failed')
        self.failUnless(ds.hasError('f2'), 
            'Del removed an error that should stay')
        del ds['f2']
        self.failIf(ds.has_key('f1'), 'Del failed')
        self.failIf(ds.hasError('f2'), 'Del failed to remove error')


    def test_20_PopItem(self):
        """Testing popitem"""
        ds = DataStructure({'f1': 'Value1', 'f2': 'Value2', 'f3': 'Value3'},
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
        ds = DataStructure({'f1': 'Value1', 'f2': 'Value2', 'f3': 'Value3'},
                           {'f2': 'Error2'})
        while len(ds):
            key, value = ds.popitem()
            if key == 'f2':
                self.failIf(ds.hasError('f2'), 'Popitem failed to remove error')

    def test_25_Update(self):
        ds = DataStructure({'f1': 'Nice fish', 'f2': 'Value2'})
        ds.update({'f1': 'Value1', 'f3': 'Value3'})
        self.assertEquals(ds.data,
            {'f1': 'Value1', 'f2': 'Value2', 'f3': 'Value3'})


    def test_30_Copy(self):
        """Test copy"""
        ds = DataStructure({'f1': 'Value1', 'f2': 'Value2', 'f3': 'Value3'},
                           {'f2': 'Error2'})
        copy = ds.copy()
        self.failUnless(copy.data == {'f1': 'Value1', 'f2': 'Value2',
                         'f3': 'Value3'}, 'Init failed to set data')
        self.failUnless(copy.errors == {'f2': 'Error2'},
                         'Init failed to set errors')

    def test_40_ModifiedFlags(self):
        ds = DataStructure({'f1': 'Value1', 'f2': 'Value2', 'f3': 'Value3'},
                           {'f2': 'Error2'})
        self.failUnless(ds.getModifiedFlags() == [])
        ds.setModifiedFlag('f1')
        self.failUnless(ds.getModifiedFlags() == ['f1'])
        ds.setModifiedFlags( ('f2', 'f3') )
        m = ds.getModifiedFlags()
        m.sort()
        self.failUnless(m == ['f1', 'f2', 'f3'])
        ds.clearModifiedFlag('f2')
        m = ds.getModifiedFlags()
        m.sort()
        self.failUnless(m == ['f1', 'f3'])
        ds.clearModifiedFlags( ['f1', 'f3'])
        self.failIf(ds.getModifiedFlags())

    def test_41_ModificationSetsFlags(self):
        ds = DataStructure( {'f1': 'Value1', 'f2': 'Value2', 'f3': 'Value3'}, \
                            {'f2': 'Error2'})
        ds['f1'] = 'Your hoovercraft is full of eels'
        self.failUnless(ds.getModifiedFlags() == ['f1'])
        del ds['f2']
        m = ds.getModifiedFlags()
        m.sort()
        self.failUnless( m == ['f1', 'f2'])
        ds['f3'] = 'Value3'
        self.failUnless( m == ['f1', 'f2'], 'Modified flag set even though new data \
                                            is equal to old data')


    def test_42_NoMultipleFlags(self):
        ds = DataStructure({'f1': 'Value1', 'f2': 'Value2', 'f3': 'Value3'},
                           {'f2': 'Error2'})
        self.failUnless(ds.getModifiedFlags() == [])
        ds.setModifiedFlag('f1')
        ds['f1'] = 'Your hoovercraft is full of eels'
        del ds['f1']
        self.failUnless(len(ds.getModifiedFlags()) == 1)

    def test_43_ClearModifiedFlags(self):
        ds = DataStructure({'f1': 'Value1', 'f2': 'Value2', 'f3': 'Value3'},
                           {'f2': 'Error2'})
        ds.clear()
        m = ds.getModifiedFlags()
        m.sort()
        self.failUnless(ds.getModifiedFlags() == ['f1', 'f2', 'f3'])
        ds.clear(clear_modified_flags=1)
        self.failIf(ds.getModifiedFlags())

    def test_50_UpdateFromRequest(self):
        """Update from request, with missing values"""
        # Make a 'fake' REQUEST from a dict:
        ds = DataStructure({ 'f1': 'it was', 'f2': 'a', 'f3': 'Value3'})
        rq = { 'field_f1': 'Value1', 'f2': 'Value2', }
        ds.updateFromRequest(rq)
        isequal = (ds.data['f1'] == 'Value1' and 
                   ds.data['f2'] == 'Value2' and 
                   ds.data['f3'] == 'Value3')
        self.failUnless(isequal, 'Update from REQUEST failed')


def test_suite():
    return unittest.makeSuite(DataStructureTests)

if __name__ == "__main__":
    unittest.main(defaultTest='test_suite')
