# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$

import unittest
from Products.NuxCPS3Document.NuxCPS3Document import NuxCPS3Document
from Products.NuxCPS3Document.Template import Template
from Products.NuxCPS3Document.Layout import HtmlLayout

class DocumentTests(unittest.TestCase):

    def setUp(self):
        # OK, We need to have a complete document.
        # That means not only the document, but a template, and the template
        # needs to have two layouts, one for edit and one for view.
        # So this test tests not only Document, but templates and layouts too.
        # Not much "unit" about it, but there ya go.
        self.template = Template('template', 'Template')


    # TODO: More tests:
    # test setting of non-template structure and non-template layouts
    # Rendering (complex stuff, maybe a separate test suite?)


def test_suite():
    return unittest.makeSuite(DocumentTests)

if __name__=="__main__":
    unittest.main(defaultTest)
