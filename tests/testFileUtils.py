# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$

import unittest
import CPSSchemasTestCase

from OFS.Image import File
from Products.CPSSchemas import FileUtils


class TestFileUtils(CPSSchemasTestCase.CPSSchemasTestCase):
    def testConvertFileToText(self):
        file = None
        self.assertEquals(
            FileUtils.convertFileToText(file, context=self.portal), None)

        file = File('test', 'test', 'test')
        file.content_type = 'text/html'
        result = FileUtils.convertFileToText(file, context=self.portal)
        self.assertEquals(result.strip(), 'test')

    def testConvertFileToHtml(self):
        file = None
        self.assertEquals(
            FileUtils.convertFileToHtml(file, context=self.portal), None)

        file = File('test', 'test', 'test')
        file.content_type = 'text/html'
        result = FileUtils.convertFileToHtml(file, context=self.portal)
        self.assertEquals(result.getData().strip(), 'test')


def test_suite():
    suites = [unittest.makeSuite(TestFileUtils)]
    return unittest.TestSuite(suites)

if __name__=="__main__":
    unittest.main(defaultTest='test_suite')
