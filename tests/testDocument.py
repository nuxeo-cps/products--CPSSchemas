# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$

import unittest
from Products.NuxCPS3Document.NuxCPS3Document import NuxCPS3Document
from Products.NuxCPS3Document.Template import Template
from Products.NuxCPS3Document.Layout import HtmlLayout

class DocumentTests(unittest.TestCase):
    pass

    # TODO: 
    # test setting of non-template structure and non-template layouts


def test_suite():
    return unittest.makeSuite(DocumentTests)

if __name__=="__main__":
    unittest.main(defaultTest)
