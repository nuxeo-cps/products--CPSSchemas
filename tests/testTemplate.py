# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$

import unittest
from Products.NuxCPS3Document.Template import Template
from Products.NuxCPS3Document.Schema import Schema
from Products.NuxCPS3Document.Layout import HtmlLayout
from Products.NuxCPS3Document.Fields.BasicField import BasicField
from Products.NuxCPS3Document.OrderedDictionary import OrderedDictionary

class TemplateTests(unittest.TestCase):

    def testCreation(self):
        """Check that the template sets up reasonable defaults"""
        template = Template('template', 'Template')
        self.failUnless(template.id == 'template', 'Template Id not set correctly')
        self.failUnless(template.title == 'Template', 'Template Title not set correctly')
        views = template.getLayoutIds()
        self.failUnless('view' in views and 'edit' in views, \
                        'Default layout creation failed')
        self.failUnless(template.isFixedValidation(), 'Fixed validation is not default')
        schemas = template.getSchemaIds()
        self.failUnless(schemas == ['default'], 'Default schema not created')

    def testAddLayout(self):
        """Add a layout"""
        template = Template('template', 'Template')
        template.addLayout(HtmlLayout('new', 'New'))
        self.failUnless('new' in template.getLayoutIds(), 'Could not add new layout')

    def testRemoveLayout(self):
        """Remove a layout"""
        template = Template('template', 'Template')
        template.removeLayout('view')
        self.failIf('view' in template.getLayoutIds(), 'Could not remove layout')

    def testGetLayout(self):
        """Retreive the layout object"""
        template = Template('template', 'Template')
        layout = template.getLayout('view')
        self.failUnless(isinstance(layout, HtmlLayout), 'getLayout() Failed')
        self.failUnless(layout.id == 'view', 'getLayout retreived the wrong layout')

    def testGetNoLayout(self):
        """Retreiving non-existing layouts should fail"""
        template = Template('template', 'Template')
        self.failUnlessRaises(KeyError, template.getLayout, 'notalayout' )

    def testAddSchema(self):
        """Add a schema"""
        template = Template('template', 'Template')
        template.addSchema(Schema('new', 'New'))
        self.failUnless('new' in template.getSchemaIds(), 'Could not add new layout')

    def testRemoveSchema(self):
        """Remove a schema"""
        template = Template('template', 'Template')
        template.removeSchema('default')
        self.failIf('default' in template.getSchemaIds(), 'Could not remove schema')

    def testGetSchema(self):
        template = Template('template', 'Template')
        self.failUnlessRaises(KeyError, template.getSchema, 'notaschema')
        self.failUnless(isinstance(template.getSchema('default'), Schema))
        self.failUnless(template.getSchema('default').id == 'default')

    #def testGetModel(self):
    #def testGetData(self):

    # Tests TODO:
    # Structure verification

def test_suite():
    return unittest.makeSuite(TemplateTests)

if __name__=="__main__":
    unittest.main(defaultTest)
