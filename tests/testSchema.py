# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$

import unittest
from Products.NuxCPS3Document.Schema import Schema
from Products.NuxCPS3Document.Adapter import AttributeAdapter
from Products.NuxCPS3Document.Fields.TextField import TextField

class AttributeHolder:
    pass


class SchemaTests(unittest.TestCase):

    def testCreation(self):
        """Check that the schems sets up reasonable defaults"""
        schema = Schema('schema', 'Schema')
        self.failUnless(isinstance(schema.getAdapter(), AttributeAdapter), \
                        'Default adapter is not AttributeAdapter')

    def testSetGetAdapter(self):
        schema = Schema('schema', 'Schema')
        adapter = AttributeAdapter()
        schema.setAdapter(adapter)
        self.failUnless(schema.getAdapter() == adapter, 'Set or get adapter failed')

    def testSetGetData(self):
        schema = Schema('schema', 'Schema')
        schema['f1'] = TextField('f1', 'Field1')
        doc = AttributeHolder()
        schema.setData(doc, 'f1', 'Spam')
        data = schema.getData(doc, 'f1')
        self.failUnless(data == 'Spam', 'GetData or setData failed')
        self.failUnless(schema.hasData(doc, 'f1'), 'HasData failed')
        schema.delData(doc, 'f1')
        self.failIf(schema.hasData(doc, 'f1'), 'DelData failed')


def test_suite():
    return unittest.makeSuite(SchemaTests)

if __name__=="__main__":
    unittest.main(defaultTest)
