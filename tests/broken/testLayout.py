# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$

import unittest
from Testing.ZopeTestCase import ZopeLite

from Products.CPSSchemas.Layout import Layout
from Products.CPSSchemas.CPSSchemas import CPSSchemas
from Products.CPSSchemas.Fields.TextField import TextField, TextFieldWidget
from Products.CPSSchemas.Fields.SelectionField import SelectionField, \
    SelectionFieldWidget

class LayoutTests(unittest.TestCase):
    pass

# Test TODO:
# Making sure only widgets connected to fields can be added.


def test_suite():
    return unittest.makeSuite(LayoutTests)

if __name__=="__main__":
    unittest.main(defaultTest)
