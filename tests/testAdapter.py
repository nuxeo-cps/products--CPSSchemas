# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$

import unittest
from Products.NuxCPS3Document.Adapter import AttributeAdapter

class AttributeHolder:
    pass

class AttributeAdapterTests(unittest.TestCase):

    def testSet(self):
        """Set Data"""
        a = AttributeAdapter()
        h = AttributeHolder()
        a.setData(h, 'data', 'value')
        self.failUnless(h.data == 'value', 'Set failed')

    def testGet(self):
        """Get Data"""
        a = AttributeAdapter()
        h = AttributeHolder()
        a.setData(h, 'data', 'value')
        self.failUnless(a.getData(h, 'data') == 'value', 'Get failed')
        self.failUnless(a.getData(h, 'nodata') is None, 'Get default failed')

    def testDel(self):
        """Delete Data"""
        a = AttributeAdapter()
        h = AttributeHolder()
        a.setData(h, 'data', 'value')
        a.delData(h, 'data')
        self.failUnlessRaises(AttributeError, getattr, a, 'data')

    def testHas(self):
        """Has Data"""
        a = AttributeAdapter()
        h = AttributeHolder()
        a.setData(h, 'data', 'value')
        self.failUnless(a.hasData(h, 'data'), 'HasData failed')
        self.failIf(a.hasData(h, 'nodata'), 'HasData did not fail when it should')



def test_suite():
    return unittest.makeSuite(AttributeAdapterTests)

if __name__=="__main__":
    unittest.main(defaultTest)
