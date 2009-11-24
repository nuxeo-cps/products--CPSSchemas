# (C) Copyright 2004-2007 Nuxeo SAS <http://nuxeo.com>
# Authors:
# Florent Guillaume <fg@nuxeo.com>
# Georges Racinet <gracinet@nuxeo.com>
# M.-A. Darche <madarche@nuxeo.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
# $Id$

import unittest

from OFS.Folder import Folder
from Products.CPSSchemas import Vocabulary

i18n_dict = {'label_foo': 'Foo',
             'label_bar': 'Bar',
             'label_cow': 'Cow',
             'label_empty': 'No choice',
             }

class FakeTranslationService:
    def __call__(self, msgid, default=None):
        if default is None:
            default = msgid
        return i18n_dict.get(msgid, default)

class FakePortal:
    translation_service = FakeTranslationService()

class FakePortalUrl:
    def getPortalObject(self):
        return FakePortal()

class BasicVocabularyTests(unittest.TestCase):

    def makeOne(self):
        return Vocabulary.CPSVocabulary(
            'the_id', (('foo', 'F'), ('bar', 'B'), ('meuh', 'M')))

    def makeWithMsgids(self):
        voc = Vocabulary.CPSVocabulary(
            'the_id', (('foo', 'F', 'label_foo'), ('bar', 'B', 'label_bar'),
                       ('meuh', 'M', 'label_cow')))
        voc.portal_url = FakePortalUrl()
        return voc

    def testInterface(self):
        from zope.interface.verify import verifyClass
        from Products.CPSSchemas.interfaces import IVocabulary
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

    def testEmpty(self):
        v = Vocabulary.CPSVocabulary('someid')
        self.assertEquals(v.keys(), [])
        self.assertEquals(v.values(), [])

    def testSimpleGets(self):
        v = self.makeOne()

        self.assertEquals(v['bar'], 'B')
        self.assertRaises(KeyError, v.__getitem__, 'blah')

        self.assertEquals(v.get('foo'), 'F')
        self.assertEquals(v.get('blah'), None)

        self.assertEquals(v.has_key('foo'), True)
        self.assertEquals(v.has_key('blah'), False)

    def test_getMsgid(self):
        v = self.makeWithMsgids()

        self.assertEquals(v.getMsgid('foo'), 'label_foo')
        self.assertEquals(v.getMsgid('meuh'), 'label_cow')
        self.assertEquals(v.getMsgid('blah'), None)

    def testSimpleLists(self):
        v = self.makeOne()
        self.assertEquals(v.keys(), ['foo', 'bar', 'meuh'])
        self.assertEquals(v.items(), [('foo', 'F'),
                                      ('bar', 'B'),
                                      ('meuh', 'M')])
        self.assertEquals(v.values(), ['F', 'B', 'M'])

    def testEmptyKeyForEmptyVoc(self):
        class UnMutableEmptyVoc(Vocabulary.CPSVocabulary):
            def __init__(self, vid, **kw):
                self._setId(vid)

            def keys(self):
                return ()
            def items(self):
                return ()
            def values(self):
                return ()

        v = Vocabulary.EmptyKeyVocabularyWrapper(UnMutableEmptyVoc('uev'),
                                                 'Empty Key')
        self.assertEquals(v.keys(), [''])
        self.assertEquals(v.values(), ['Empty Key'])
        self.assertEquals(v.items(), [('', 'Empty Key')])

    def test_keysSortedBy(self):
        v = self.makeWithMsgids()
        # B, F, M
        self.assertEquals(v.keysSortedBy('label'), ['bar', 'foo', 'meuh'])
        # Bar, Cow, Meuh
        self.assertEquals(v.keysSortedBy('i18n'), ['bar', 'meuh', 'foo'])

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
        v = self.makeOne()
        v.set('bar', 'hm')
        self.assertEquals(v['bar'], 'hm')
        self.assertEquals(v.get('bar'), 'hm')
        self.assertEquals(v.keys(), ['foo', 'bar', 'meuh'])
        self.assertEquals(v.items(), [('foo', 'F'),
                                      ('bar', 'hm'),
                                      ('meuh', 'M')])
        self.assertEquals(v.values(), ['F', 'hm', 'M'])

    def test_reset(self):
        v = self.makeOne()
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

    def test_modify(self):
        v = self.makeOne()
        v.set('bar', 'hm')
        for modified in (False, True):
            v.setUserModified(modified)
            res = v.isUserModified()
            self.assertEquals(res, modified)

    # XXX Could test msgids but I'm not sure we really use them.

class EmptyKeyVocabularyWrapperTests(BasicVocabularyTests):

    def makeOne(self):
        return Vocabulary.EmptyKeyVocabularyWrapper(
            BasicVocabularyTests.makeOne(self), 'Empty Value')

    def makeOneEmpty(self, position='first'):
        v = Vocabulary.CPSVocabulary('the_id', ())
        return Vocabulary.EmptyKeyVocabularyWrapper(v, 'Empty Value', position=position)

    def makeOneAlreadyWithEmptyKeyAtBeginning(self, position='first'):
        v = Vocabulary.CPSVocabulary(
            'the_id', (('', ''), ('foo', 'F'), ('bar', 'B'), ('meuh', 'M')))
        return Vocabulary.EmptyKeyVocabularyWrapper(v, '', position=position)

    def makeOneAlreadyWithEmptyKeyAtEnd(self, position='first'):
        v = Vocabulary.CPSVocabulary(
            'the_id', (('foo', 'F'), ('bar', 'B'), ('meuh', 'M'), ('', '')))
        return Vocabulary.EmptyKeyVocabularyWrapper(v, '', position=position)

    def makeWithMsgids(self):
        return Vocabulary.EmptyKeyVocabularyWrapper(
            BasicVocabularyTests.makeWithMsgids(self),
            'Empty Value', 'label_empty')

    def testInterface(self):
        from zope.interface.verify import verifyClass
        from Products.CPSSchemas.interfaces import IVocabulary
        verifyClass(IVocabulary, Vocabulary.EmptyKeyVocabularyWrapper)

    def testSimpleLists(self):
        v = self.makeOneEmpty()
        self.assertEquals(v.keys(), [''])
        self.assertEquals(v.items(), [('', 'Empty Value'),
                                      ])
        self.assertEquals(v.values(), ['Empty Value'])

        v = self.makeOne()
        self.assertEquals(v.keys(), ['', 'foo', 'bar', 'meuh'])
        self.assertEquals(v.items(), [('', 'Empty Value'),
                                      ('foo', 'F'),
                                      ('bar', 'B'),
                                      ('meuh', 'M')])
        self.assertEquals(v.values(), ['Empty Value', 'F', 'B', 'M'])

    def testListsWithEmptyKeyAtBeginning(self):
        # The aim is to test that there won't be more than one empty key
        v = self.makeOneAlreadyWithEmptyKeyAtBeginning()
        self.assertEquals(v.keys(), ['', 'foo', 'bar', 'meuh'])
        self.assertEquals(v.items(), [('', ''),
                                      ('foo', 'F'),
                                      ('bar', 'B'),
                                      ('meuh', 'M'),
                                      ])
        self.assertEquals(v.values(), ['', 'F', 'B', 'M'])

        v = self.makeOneAlreadyWithEmptyKeyAtBeginning(position='end')
        self.assertEquals(v.keys(), ['foo', 'bar', 'meuh', ''])
        self.assertEquals(v.items(), [('foo', 'F'),
                                      ('bar', 'B'),
                                      ('meuh', 'M'),
                                      ('', ''),
                                      ])
        self.assertEquals(v.values(), ['F', 'B', 'M', ''])

    def testListsWithEmptyKeyAtEnd(self):
        # The aim is to test that there won't be more than one empty key
        v = self.makeOneAlreadyWithEmptyKeyAtEnd()
        self.assertEquals(v.keys(), ['', 'foo', 'bar', 'meuh'])
        self.assertEquals(v.items(), [('', ''),
                                      ('foo', 'F'),
                                      ('bar', 'B'),
                                      ('meuh', 'M'),
                                      ])
        self.assertEquals(v.values(), ['', 'F', 'B', 'M'])

        v = self.makeOneAlreadyWithEmptyKeyAtBeginning(position='end')
        self.assertEquals(v.keys(), ['foo', 'bar', 'meuh', ''])
        self.assertEquals(v.items(), [('foo', 'F'),
                                      ('bar', 'B'),
                                      ('meuh', 'M'),
                                      ('', ''),
                                      ])
        self.assertEquals(v.values(), ['F', 'B', 'M', ''])

    def test_keysSortedBy(self):
        v = self.makeWithMsgids()
        # for reference
        cpsmcat = FakeTranslationService()
        self.assertEquals(cpsmcat('label_empty'), 'No choice')
        # B, F, M
        self.assertEquals(v.keysSortedBy('label'), ['', 'bar', 'foo', 'meuh'])
        # No choice, Bar, Cow, Foo: empty key always first
        self.assertEquals(v.keysSortedBy('i18n'), ['', 'bar', 'meuh', 'foo'])

    # disable tests for not forwarded part of API
    def test_modify(self):
        pass

    def test_reset(self):
        pass

def test_suite():
    suites = [unittest.makeSuite(BasicVocabularyTests),
              unittest.makeSuite(EmptyKeyVocabularyWrapperTests)]
    return unittest.TestSuite(suites)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
