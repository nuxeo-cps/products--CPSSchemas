# Copyright (c) 2004 Nuxeo SARL <http://nuxeo.com>
# Author: Florent Guillaume <fg@nuxeo.com>
# $Id$

import unittest
#from Testing.ZopeTestCase import ZopeLite

from Acquisition import Implicit
from Products.CPSSchemas.DataModel import DataModel, ValidationError
from Products.CPSSchemas.StorageAdapter import AttributeStorageAdapter
from Products.CPSSchemas.Schema import CPSSchema
from Products.CPSSchemas.BasicFields import CPSStringField
#from Products.CPSSchemas.Schema import Schema
#from Products.CPSSchemas.Fields.TextField import TextField
#from Products.CPSSchemas.Fields.SelectionField import SelectionField

try:
    True
except NameError:
    True = 1
    False = 0

def sort(l):
    l = list(l)
    l.sort()
    return l

class FakePortal(Implicit):
    pass
fakePortal = FakePortal()

class FakeUrlTool(Implicit):
    def getPortalObject(self):
        return fakePortal
fakeUrlTool = FakeUrlTool()

fakePortal.portal_url = fakeUrlTool


class FakeDocument:
    f1 = 'f1class'


# XXX: All these tests must be repared.
class TestDataModel(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        doc = FakeDocument()
        doc.f2 = 'f2inst'
        # Acquisition is needed for expression context computation during fetch
        schema = CPSSchema('s1', 'Schema1').__of__(fakePortal)
        schema.addField('f1', 'CPS String Field')
        schema.addField('f2', 'CPS String Field')
        schema.addField('f3', 'CPS String Field', default_expr='string:f3def')
        schema.addField('f4', 'CPS String Field')
        schema.addField('f5', 'CPS String Field',
                        read_ignore_storage=True,
                        read_process_expr='python: f2+"_yo"',
                        read_process_dependent_fields='f2',
                        )
        adapter = AttributeStorageAdapter(schema, doc, field_ids=schema.keys())
        dm = DataModel(doc, (adapter,))
        self.doc = doc
        self.dm = dm

    def testAPI(self):
        dm = self.dm
        dm._fetch()
        dm['f4'] = 'f4changed'
        ok = {'f1': 'f1class',
              'f2': 'f2inst',
              'f3': 'f3def',
              'f4': 'f4changed',
              'f5': 'f2inst_yo',
              }
        self.assertEquals(sort(dm.keys()), sort(ok.keys()))
        self.assertEquals(dm['f1'], ok['f1'])
        self.assertEquals(dm['f2'], ok['f2'])
        self.assertEquals(dm['f3'], ok['f3'])
        self.assertEquals(dm['f4'], ok['f4'])
        self.assertEquals(dm['f5'], ok['f5'])
        self.assertEquals(dm.getContext(), self.doc)
        self.assertEquals(dm.getProxy(), None)

    def testCreation(self):
        dm = self.dm
        dm._setObject(None) # What we have for creation
        dm._fetch()
        ok = {'f1': '',
              'f2': '',
              'f3': 'f3def',
              'f4': '',
              'f5': '_yo',
              }
        self.assertEquals(sort(dm.keys()), sort(ok.keys()))
        self.assertEquals(dm['f1'], ok['f1'])
        self.assertEquals(dm['f2'], ok['f2'])
        self.assertEquals(dm['f3'], ok['f3'])
        self.assertEquals(dm['f4'], ok['f4'])
        self.assertEquals(dm['f5'], ok['f5'])
        self.assertEquals(dm.getContext(), self.doc)
        self.assertEquals(dm.getProxy(), None)

    def testCommitDirty(self):
        dm = self.dm
        doc = self.doc
        dm._fetch()
        dm['f2'] = 'f2changed'
        dm['f4'] = 'f4changed'

        # Unchanged field with class value is not dirty
        self.assertEquals(dm.isDirty('f1'), False)
        # Changed field with old value is dirty
        self.assertEquals(dm.isDirty('f2'), True)
        # Unchanged field with default is dirty
        self.assertEquals(dm.isDirty('f3'), True)
        # Changed field is dirty
        self.assertEquals(dm.isDirty('f4'), True)
        # Computed field is not dirty
        self.assertEquals(dm.isDirty('f5'), False)

        # Now commit
        dm._commit(check_perms=0)
        self.assertEquals(doc.f1, 'f1class')
        self.assertEquals(doc.f2, 'f2changed')
        self.assertEquals(doc.f3, 'f3def')
        self.assertEquals(doc.f4, 'f4changed')
        self.assertEquals(doc.f5, 'f2inst_yo') # f2 changed after fetch

        # Nothing is dirty anymore
        self.assertEquals(dm.isDirty('f1'), False)
        self.assertEquals(dm.isDirty('f2'), False)
        self.assertEquals(dm.isDirty('f3'), False)
        self.assertEquals(dm.isDirty('f4'), False)
        self.assertEquals(dm.isDirty('f5'), False)

    def testFieldProcessing(self):
        pass


def test_suite():
    return unittest.makeSuite(TestDataModel)

if __name__=="__main__":
    unittest.main(defaultTest)
