# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$

import unittest

from Acquisition import Implicit
from OFS.Image import File
from Products.CPSSchemas import FileUtils


class FakePortal(Implicit):
    default_charset = 'unicode'
    pass
fakePortal = FakePortal()

class FakePortalTransforms(Implicit):
    def convertTo(self, mt, raw, **kw):
        if raw is None:
            return None
        class Result:
            def __init__(self, s):
                self.s = s
            def getData(self):
                return self.s
        return Result('converted_'+raw)


fakePortalTransforms = FakePortalTransforms()

fakePortal.portal_transforms = fakePortalTransforms



class TestFileUtils(unittest.TestCase):
    def testConvertFileToText(self):
        file = None
        self.assertEquals(
            FileUtils.convertFileToText(file, context=fakePortal), None)

        file = File('test', 'test', 'test')
        file.content_type = 'text/html'
        result = FileUtils.convertFileToText(file, context=fakePortal)
        self.assertEquals(result.strip(), 'converted_test')

    def testConvertFileToHtml(self):
        file = None
        self.assertEquals(
            FileUtils.convertFileToHtml(file, context=fakePortal), None)

        file = File('test', 'test', 'test')
        file.content_type = 'text/html'
        result = FileUtils.convertFileToHtml(file, context=fakePortal)
        self.assertEquals(result.getData().strip(), 'converted_test')


def test_suite():
    suites = [unittest.makeSuite(TestFileUtils)]
    return unittest.TestSuite(suites)

if __name__=="__main__":
    unittest.main(defaultTest='test_suite')
