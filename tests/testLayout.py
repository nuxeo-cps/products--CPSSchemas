# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$

import unittest
from Products.NuxCPS3Document.Layout import BasicLayout
from Products.NuxCPS3Document.NuxCPS3Document import NuxCPS3Document
from Products.NuxCPS3Document.Template import Template
from Products.NuxCPS3Document.Fields.TextField import TextField, TextFieldWidget
from Products.NuxCPS3Document.Fields.SelectionField import SelectionField, SelectionFieldWidget

class LayoutTests(unittest.TestCase):
    pass

# Test TODO:
# Making sure only widgets connected to fields can be added.


def test_suite():
    return unittest.makeSuite(LayoutTests)

if __name__=="__main__":
    unittest.main(defaultTest)
