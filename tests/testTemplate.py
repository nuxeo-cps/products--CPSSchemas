# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$

import unittest
from Testing.ZopeTestCase import ZopeLite

from Products.CPSDocument.Template import Template
from Products.CPSDocument.Schema import CPSSchema
from Products.CPSDocument.Layout import HtmlLayout
from Products.CPSDocument.Fields.TextField import TextField
from Products.CPSDocument.Fields.SelectionField import SelectionField

class AttributeHolder:
    pass

class TemplateTests(unittest.TestCase):

    def testCreation(self):
        """Check that the template sets up reasonable defaults"""
        template = Template('template', 'Template')
        self.failUnless(template.id == 'template', 
            'Template Id not set correctly')
        self.failUnless(template.title == 'Template', 
            'Template Title not set correctly')
        views = template.getLayoutIds()
        self.failUnless('view' in views and 'edit' in views,
                        'Default layout creation failed')
        self.failUnless(template.isFixedValidation(), 
            'Fixed validation is not default')
        schemas = template.getSchemaIds()
        self.failUnless(schemas == ['default'], 'Default schema not created')

    def testAddLayout(self):
        """Add a layout"""
        template = Template('template', 'Template')
        template.addLayout(HtmlLayout('new', 'New'))
        self.failUnless('new' in template.getLayoutIds(), 
            'Could not add new layout')

    def testRemoveLayout(self):
        """Remove a layout"""
        template = Template('template', 'Template')
        template.removeLayout('view')
        self.failIf('view' in template.getLayoutIds(), 
            'Could not remove layout')

    def testGetLayout(self):
        """Retreive the layout object"""
        template = Template('template', 'Template')
        layout = template.getLayout('view')
        self.failUnless(isinstance(layout, HtmlLayout), 'getLayout() Failed')
        self.failUnless(layout.id == 'view', 
            'getLayout retreived the wrong layout')

    def testGetNoLayout(self):
        """Retreiving non-existing layouts should fail"""
        template = Template('template', 'Template')
        self.failUnlessRaises(KeyError, template.getLayout, 'notalayout' )

    def testAddSchema(self):
        """Add a schema"""
        template = Template('template', 'Template')
        template.addSchema(CPSSchema('new', 'New'))
        self.failUnless('new' in template.getSchemaIds(), 
            'Could not add new layout')

    def testRemoveSchema(self):
        """Remove a schema"""
        template = Template('template', 'Template')
        template.removeSchema('default')
        self.failIf('default' in template.getSchemaIds(), 
            'Could not remove schema')

    def testGetSchema(self):
        template = Template('template', 'Template')
        self.failUnlessRaises(KeyError, template.getSchema, 'notaschema')
        self.failUnless(isinstance(template.getSchema('default'), Schema))
        self.failUnless(template.getSchema('default').id == 'default')

    def testGetSchemaForFieldId(self):
        template = Template('template', 'Template')
        # Create an extra schema to test merging of schemas:
        template.addSchema(CPSSchema('new', 'New'))
        # Add a bunch of fields
        template.getSchema('default')['f1'] = TextField('f1', 'Field1')
        template.getSchema('default')['f2'] = TextField('f2', 'Field2')
        template.getSchema('default')['f3'] = SelectionField('f3', 'Field3')
        template.getSchema('new')['f4'] = TextField('f4', 'Field4')
        template.getSchema('new')['f5'] = SelectionField('f5', 'Field5')
        template.getSchema('new')['f6'] = TextField('f6', 'Field6')
        schema = template.getSchemaForFieldId('f5')
        self.failUnless(schema.id == 'new')

    def testGetModel(self):
        """Retreive the DataModel"""
        template = Template('template', 'Template')
        # Create an extra schema to test merging of schemas:
        template.addSchema(CPSSchema('new', 'New'))
        # Add a bunch of fields
        template.getSchema('default')['f1'] = TextField('f1', 'Field1')
        template.getSchema('default')['f2'] = TextField('f2', 'Field2')
        template.getSchema('default')['f3'] = SelectionField('f3', 'Field3')
        template.getSchema('new')['f4'] = TextField('f4', 'Field4')
        template.getSchema('new')['f5'] = SelectionField('f5', 'Field5')
        template.getSchema('new')['f6'] = TextField('f6', 'Field6')
        dm = template.getDataModel()
        fields = dm.getFieldIds()
        fields.sort()
        self.failUnless(fields == ['f1', 'f2', 'f3', 'f4', 'f5', 'f6'])


    # Tests TODO:
    # Structure verification

def test_suite():
    return unittest.makeSuite(TemplateTests)

if __name__=="__main__":
    unittest.main(defaultTest)
