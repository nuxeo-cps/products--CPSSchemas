# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$

import unittest
from Products.NuxCPS3Document.Fields.BasicField import BasicField, BasicFieldWidget
from Products.NuxCPS3Document.Fields.TextField import TextField, TextFieldWidget
from Products.NuxCPS3Document.Renderer import BasicRenderer


class FieldTests(unittest.TestCase):

    def testCreation(self):
        """Test field creation"""
        field = BasicField('the_id', 'the_title')
        self.failUnless(field.id == 'the_id', 'Id was not set correctly')
        self.failUnless(field.title == 'the_title', 'Title was not set correctly')

    def testBasicValidation(self):
        field = BasicField('the_id', 'the_title')
        self.failUnless(field.validate('bimbo') == 'bimbo')
        self.failUnlessRaises(ValueError, field.validate, None)
        field.setDefaultValue('spam')
        self.failUnless(field.validate(None) == 'spam')
        field.setNotRequired()
        self.failUnless(field.validate(None) == None)

    def testDefaultValues(self):
        field = BasicField('the_id', 'the_title')
        self.failUnlessRaises(ValueError, field.validate, None)
        field.setNotRequired()
        self.failUnless(field.validate(None) is None)
        field.setDefaultValue('The Default Value')
        self.failUnless(field.getDefaultValue() == 'The Default Value')
        field.setRequired()
        self.failUnless(field.validate(None) == 'The Default Value')

    # test required set/is

def test_suite():
    return unittest.makeSuite(FieldTests)

if __name__=="__main__":
    unittest.main(defaultTest='test_suite')
