# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$

import unittest
from Products.NuxCPS3Document.Template import Template
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

    def testAddRemoveFields(self):
        """Make sure fields are modifiable"""
        template = Template('template', 'Template')
        structure = template.getFieldDefinition()
        self.failUnless(isinstance(structure, OrderedDictionary), \
                        'The returned field definition is not an OrderedDictionary')

        structure['f1'] = BasicField('f1', 'Field1')
        structure['f2'] = BasicField('f2', 'Field2')
        structure['f3'] = BasicField('f3', 'Field3')
        structure['f4'] = BasicField('f4', 'Field4')
        del structure['f3']

        struct2 = template.getFieldDefinition()
        self.failUnless(structure.keys() == struct2.keys(), \
                        'Update of field definition failed')

    # Tests TODO:
    # Structure verification

def test_suite():
    return unittest.makeSuite(TemplateTests)

if __name__=="__main__":
    unittest.main(defaultTest)
