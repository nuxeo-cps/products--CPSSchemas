# Copyright (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id $

import unittest
from CPSSchemasTestCase import CPSSchemasTestCase

from DateTime.DateTime import DateTime
from OFS.Folder import Folder
from OFS.Image import Image, File
from Interface.Verify import verifyClass
from Products.CPSSchemas import Vocabulary
from Products.CPSSchemas.IVocabulary import IVocabulary


class BasicVocabularyTests(CPSSchemasTestCase):

    def afterSetUp(self):
        vocabs = Folder('vocabs')
        self.portal._setObject('vocabs', vocabs)
        self.vocabs = self.portal.vocabs

    def makeOne(self):
        l = ('foo', 'bar', 'meuh')
        d = {'foo': 'F', 'bar': 'B', 'meuh': 'M'}
        vocab = Vocabulary.CPSVocabulary('the_id', list=l, dict=d)
        self.vocabs._setObject('the_id', vocab)
        vocab = getattr(self.vocabs, 'the_id')

    def test_interface(self):
        verifyClass(IVocabulary, Vocabulary.Vocabulary)
        verifyClass(IVocabulary, Vocabulary.CPSVocabulary)

    def test_simple(self):
        self.makeOne()
        v = self.vocabs.the_id
        self.assertEquals(v['bar'], 'B')
        self.assertRaises(KeyError, v.__getitem__, 'blah')
        self.assertEquals(v.get('foo'), 'F')
        self.assertEquals(v.get('blah'), None)
        self.assertEquals(v.keys(), ['foo', 'bar', 'meuh'])
        self.assertEquals(v.items(), [('foo', 'F'),
                                      ('bar', 'B'),
                                      ('meuh', 'M')])
        self.assertEquals(v.values(), ['F', 'B', 'M'])

    def test_modify(self):
        self.makeOne()
        v = self.vocabs.the_id
        v.set('bar', 'hm')
        self.assertEquals(v['bar'], 'hm')
        self.assertEquals(v.get('bar'), 'hm')
        self.assertEquals(v.keys(), ['foo', 'bar', 'meuh'])
        self.assertEquals(v.items(), [('foo', 'F'),
                                      ('bar', 'hm'),
                                      ('meuh', 'M')])
        self.assertEquals(v.values(), ['F', 'hm', 'M'])

    def test_reset(self):
        self.makeOne()
        v = self.vocabs.the_id
        nv = Vocabulary.Vocabulary()
        nv.set('one', '1')
        nv.set('two', '2')
        v.setVocabulary(nv)
        self.assertEquals(v.get('foo'), None)
        self.assertEquals(v['one'], '1')
        self.assertEquals(v.get('two'), '2')
        self.assertEquals(v.keys(), ['one', 'two'])
        self.assertEquals(v.items(), [('one', '1'), ('two', '2')])
        self.assertEquals(v.values(), ['1', '2'])

    # XXX Could test msgids but I'm not sure we really use them.


def test_suite():
    suites = [unittest.makeSuite(BasicVocabularyTests)]
    return unittest.TestSuite(suites)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
