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


    # TODO: Test validation when that is to be implemented.

    # test default value handling

def test_suite():
    return unittest.makeSuite(FieldTests)

if __name__=="__main__":
    unittest.main(defaultTest='test_suite')
