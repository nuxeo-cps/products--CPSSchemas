
import unittest

import ZODB # To load Persistence properly.
from DateTime import DateTime

from Products.NuxCPS3Document.BasicStorage import BasicStorage

class BasicStorageTests(unittest.TestCase):

    def testData(self):
        storage = BasicStorage()
        storage.setData('string', 'abcdefg')
        storage.setData('date', DateTime('2003-02-19 13:45'))
        storage.setData('list', ['umpa', 'bumpa', 'humpapa'])
        self.failUnlessEqual(storage.getData('string'), 'abcdefg')
        self.failUnlessEqual(storage.getData('date'), DateTime('2003-02-19 13:45'))
        self.failUnlessEqual(storage.getData('list'), ['umpa', 'bumpa', 'humpapa'])
        storage.delData('string')
        self.failUnlessRaises(AttributeError, storage.getData, 'string')


def test_suite():
    return unittest.makeSuite(BasicStorageTests)

if __name__=="__main__":
    unittest.main(defaultTest)