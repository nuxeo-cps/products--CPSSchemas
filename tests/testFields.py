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


    def testTextFieldRender(self):
        """Do the simplest of all rendering"""
        field = TextField('id','title')
        fieldw = TextFieldWidget(field)
        renderer = BasicRenderer
        self.failUnless(fieldw.render(renderer, {'id': 'This should be displayed'}) == \
                        'This should be displayed\n', 'TextField render failed')
        self.failUnless(fieldw.render(renderer, {'id': 'This should be displayed'}, edit=1) == \
                        '[This should be displayed]\n', 'TextField render as editbox failed')

    # TODO: Test validation when that is to be implemented.

    # Skins and other rendering should be implemented too, I don't know what kind of tests
    # can be done on that.

def test_suite():
    return unittest.makeSuite(FieldTests)

if __name__=="__main__":
    unittest.main(defaultTest='test_suite')
