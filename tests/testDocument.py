# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$

import unittest
from Testing.ZopeTestCase import ZopeLite

from Products.CPSDocument.CPSDocument import CPSDocument
from Products.CPSDocument.Template import Template
from Products.CPSDocument.Layout import HtmlLayout

class DocumentTests(unittest.TestCase):
    pass

    # TODO: 
    # test setting of non-template structure and non-template layouts


def test_suite():
    return unittest.makeSuite(DocumentTests)

if __name__=="__main__":
    unittest.main(defaultTest)
