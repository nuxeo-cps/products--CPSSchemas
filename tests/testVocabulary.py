# Copyright (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$

import unittest
from CPSSchemasTestCase import CPSSchemasTestCase

from OFS.Folder import Folder
from Interface.Verify import verifyClass
from Products.CPSSchemas import Vocabulary
from Products.CPSSchemas.IVocabulary import IVocabulary


class BasicVocabularyTests(CPSSchemasTestCase):

    def afterSetUp(self):
        vocabs = Folder('vocabs')
        self.portal._setObject('vocabs', vocabs)
        self.vocabs = self.portal.vocabs

    def makeOne(self):
        vocab = Vocabulary.CPSVocabulary(
            'the_id', (('foo', 'F'), ('bar', 'B'), ('meuh', 'M')))
        self.vocabs._setObject('the_id', vocab)
        vocab = getattr(self.vocabs, 'the_id')

    def test_interface(self):
        verifyClass(IVocabulary, Vocabulary.Vocabulary)
        verifyClass(IVocabulary, Vocabulary.CPSVocabulary)


    def testConstructor(self):
        v = Vocabulary.CPSVocabulary(
            'someid',
            (('fyy', 'F'), ('bro', 'B')))
        self.assertEquals(v.keys(), ['fyy', 'bro'])
        self.assertEquals(v.values(), ['F', 'B'])
        v = Vocabulary.CPSVocabulary(
            'tuples',
            tuples=(('fyy', 'F'), ('bro', 'B')))
        self.assertEquals(v.keys(), ['fyy', 'bro'])
        self.assertEquals(v.values(), ['F', 'B'])
        v = Vocabulary.CPSVocabulary(
            'tuples2',
            tuples=(('fyy', 'F', 'label_F'), ('bro', 'B', 'label_B')))
        self.assertEquals(v.keys(), ['fyy', 'bro'])
        self.assertEquals(v.values(), ['F', 'B'])
        self.assertEquals(v.getMsgid('fyy'), 'label_F')
        self.assertEquals(v.getMsgid('bro'), 'label_B')
        v = Vocabulary.CPSVocabulary(
            'someid',
            list=('fyy', 'bro'), dict={'fyy': 'F', 'bro': 'B'})
        self.assertEquals(v.keys(), ['fyy', 'bro'])
        self.assertEquals(v.values(), ['F', 'B'])

    def test_empty(self):
        v = Vocabulary.CPSVocabulary('someid')
        self.assertEquals(v.keys(), [])
        self.assertEquals(v.values(), [])

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

    def test_value_is_key(self):
        v = Vocabulary.CPSVocabulary(
            'someid', tuples=('gol', 'do', 'rak'))
        self.assertEquals(v.keys(), ['gol', 'do', 'rak'])
        self.assertEquals(v.values(), ['gol', 'do', 'rak'])
        v = Vocabulary.CPSVocabulary(
            'someid', list=('gren', 'dizer'))
        self.assertEquals(v.keys(), ['gren', 'dizer'])
        self.assertEquals(v.values(), ['gren', 'dizer'])
        v = Vocabulary.CPSVocabulary(
            'someid', ('bidi', 'bulle'))
        self.assertEquals(v.keys(), ['bidi', 'bulle'])
        self.assertEquals(v.values(), ['bidi', 'bulle'])

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
        nv.set('one', '1', 'label_one')
        nv.set('two', '2', 'label_two')
        v.setVocabulary(nv)
        self.assertEquals(v.get('foo'), None)
        self.assertEquals(v['one'], '1')
        self.assertEquals(v.get('two'), '2')
        self.assertEquals(v.getMsgid('two'), 'label_two')
        self.assertEquals(v.keys(), ['one', 'two'])
        self.assertEquals(v.items(), [('one', '1'), ('two', '2')])
        self.assertEquals(v.values(), ['1', '2'])

    # XXX Could test msgids but I'm not sure we really use them.


def test_suite():
    suites = [unittest.makeSuite(BasicVocabularyTests)]
    return unittest.TestSuite(suites)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
