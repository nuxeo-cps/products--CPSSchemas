# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$

import unittest
from Testing.ZopeTestCase import ZopeLite

from Products.CPSDocument.Fields.BasicField import BasicField, BasicFieldWidget
from Products.CPSDocument.Fields.TextField import TextField, TextFieldWidget
from Products.CPSDocument.Renderer import BasicRenderer


class BasicFieldTests(unittest.TestCase):

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

#     def testDefaultValues(self):
#         field = BasicField('the_id', 'the_title')
#         self.failUnlessRaises(ValueError, field.validate, None)
#         field.setNotRequired()
#         self.failUnless(field.validate(None) is None)
#         field.setDefaultValue('The Default Value')
#         self.failUnless(field.getDefaultValue() == 'The Default Value')
#         field.setRequired()
#         self.failUnless(field.validate(None) == 'The Default Value')

    def testSetSettings(self):
        field = BasicField('the_id', 'the_title')
        field.setSetting('default', 'newdefault')
        self.failUnless(field.getSetting('default') == 'newdefault')
        self.failUnlessRaises(KeyError, field.setSetting, 'notasetting', 'somevalue')



    def testRequired(self):
        field = BasicField('the_id', 'the_title')
        self.failIf(not field.isRequired())
        field.setNotRequired()
        self.failIf(field.isRequired())
        field.setRequired()
        self.failIf(not field.isRequired())



class NotAString:
    """A class can't be converted to a string"""
    def __str__(self):
        raise TypeError('This can not be converted to a string')

class TextFieldTests(unittest.TestCase):

    def testConversion(self):
        field = TextField('the_id', 'the_title')
        self.failUnless(field.validate('four') == 'four')
        self.failUnless(field.validate(4) == '4')
        four = NotAString()
        self.failUnlessRaises(TypeError, field.validate, four)


    # OK, field settings are not attributes, instead each field instance
    # has a 'settings' naahhhh. Testfirst!!!
    # field.setSetting(setting, value)
    # field.getSetting(setting)
    # filed.get AllSettings(): return list

def test_suite():
    suites = [unittest.makeSuite(BasicFieldTests), \
              unittest.makeSuite(TextFieldTests)]
    return unittest.TestSuite(suites)

if __name__=="__main__":
    unittest.main(defaultTest='test_suite')
