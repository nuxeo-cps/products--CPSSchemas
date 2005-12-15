# (C) Copyright 2005 Nuxeo SARL <http://nuxeo.com>
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
from Products.CPSSchemas.LocalVocabulary import addLocalVocabularyContainer
from Products.CPSSchemas.LocalVocabulary import LocalVocabulary
from Products.CPSSchemas.LocalVocabulary import union
from Products.CPSSchemas.LocalVocabulary import LOCAL_VOCABULARY_CONTAINER_ID
from Products.CPSSchemas.Vocabulary import CPSVocabulary
from Testing import ZopeTestCase
from Products.CPSSchemas.tests.testVocabulary import BasicVocabularyTests

from OFS.Folder import Folder


class LocalVocabularyTests(BasicVocabularyTests):

    def makeOne(self):
        return LocalVocabulary(
            'the_id', (('foo', 'F'), ('bar', 'B'), ('meuh', 'M')))

    def testAttributes(self):
        voc = self.makeOne()

        self.assertEqual(voc.inheritance_type, 'inherit')
        self.assertEqual(voc.merge_behaviour, 'None')


class LocalVocabularyContainerTests(ZopeTestCase.PortalTestCase):

    def getPortal(self):
        return Folder('portal')

    def _setupHomeFolder(self):
        pass

    def afterSetUp(self):
        from Products.CPSSchemas.VocabulariesTool import VocabulariesTool
        self.portal.ws = Folder('workspaces')
        self.portal.ws.pfolder = Folder('pfolder')
        self.ws = self.portal.ws
        self.pfolder = self.portal.ws.pfolder
        self.portal.portal_vocabularies = VocabulariesTool()

        addLocalVocabularyContainer(self.pfolder)
        self.vocabcontainer = getattr(self.pfolder,
                                      LOCAL_VOCABULARY_CONTAINER_ID)
        self.globalvoctuples = (('en', 'E'), ('fr', 'F'), ('ru', 'R'))
        vocobj = CPSVocabulary('dummylanguage_voc', self.globalvoctuples)
        for key in list(vocobj.keys()):
            vocobj.set(key, vocobj[key], key + '_dummymsgid')
        self.portal.portal_vocabularies._setObject('dummylanguage_voc', vocobj)

    def _makeUpperVocabulary(self):
        addLocalVocabularyContainer(self.ws)
        vocabcontainer = getattr(self.ws, LOCAL_VOCABULARY_CONTAINER_ID)
        tuples = (('ro', 'R'), )
        vocobj = LocalVocabulary('dummylanguage_voc', tuples)

        for key in list(vocobj.keys()):
            vocobj.set(key, vocobj[key], key + '_dummymsgid')
        vocabcontainer._setObject('dummylanguage_voc', vocobj)
        return vocobj, tuples


    def testGetVocabulary1(self):
        # Test case when there is no local vocabulary with given id
        # in container.
        # And container inheritance_type parameter is 'global'
        voc_id = 'dummylanguage_voc'
        container = self.vocabcontainer
        self.assertEqual(len(container.objectIds()), 0)

        container.inheritance_type = 'global'
        container.merge_behaviour = 'None'

        voc = container.getVocabulary(voc_id)
        self.assert_(voc is not None)
        self.assertEqual(len(voc.keys()), 3)
        for key in voc.keys():
            self.assertEqual(voc.getMsgid(key), key + '_dummymsgid')
        for key, val in self.globalvoctuples:
            self.assertEqual(voc[key], val)

        self.assertRaises(KeyError, container.getVocabulary, voc_id + '1')

    def testGetVocabulary2(self):
        # Test case when there is no local vocabulary with given id
        # in container.
        # And container inheritance_type parameter is 'inherit'
        voc_id = 'dummylanguage_voc'
        container = self.vocabcontainer
        self.assertEqual(len(container.objectIds()), 0)

        container.inheritance_type = 'inherit'
        container.merge_behaviour = 'None'

        voc = container.getVocabulary(voc_id)
        self.assert_(voc is not None)
        self.assertEqual(len(voc.keys()), 3)
        for key in voc.keys():
            self.assertEqual(voc.getMsgid(key), key + '_dummymsgid')
        for key, val in self.globalvoctuples:
            self.assertEqual(voc[key], val)

        self.assertRaises(KeyError, container.getVocabulary, voc_id + '1')

    def testGetVocabulary3(self):
        # Test case when there is no local vocabulary with given id
        # in container.
        # Testing acquiring local vocabulary from the upper tree with its own
        # configuration policy.

        voc_id = 'dummylanguage_voc'
        container = self.vocabcontainer

        uppervoc, uppertuples = self._makeUpperVocabulary()

        uppervoc.inheritance_type = 'global'
        uppervoc.merge_behaviour = 'None'
        voc = container.getVocabulary(voc_id)
        self.assert_(voc is not None)
        self.assertEqual(len(voc.keys()), 3)
        for key, val in self.globalvoctuples:
            self.assertEqual(voc[key], val)
        for key, val in uppertuples:
            self.assertEqual(voc.get(key), None)

        uppervoc.inheritance_type = 'global'
        uppervoc.merge_behaviour = 'union'
        voc = container.getVocabulary(voc_id)
        self.assertEqual(len(voc.keys()), 4)
        for key, val in self.globalvoctuples + uppertuples:
            self.assertEqual(voc[key], val)

        uppervoc.inheritance_type = 'inherit'
        uppervoc.merge_behaviour = 'None'
        voc = container.getVocabulary(voc_id)
        self.assertEqual(len(voc.keys()), 1)
        for key, val in uppertuples:
            self.assertEqual(voc[key], val)

        uppervoc.inheritance_type = 'inherit'
        uppervoc.merge_behaviour = 'union'
        voc = container.getVocabulary(voc_id)
        self.assertEqual(len(voc.keys()), 4)
        for key, val in self.globalvoctuples + uppertuples:
            self.assertEqual(voc[key], val)


    def testGetVocabulary4(self):
        # Local vocabulary is in container
        # local vocabulary attributes:
        # inheritance_type = 'inherit'
        # merge_behaviour = 'None'
        # Result: only content of this local vocabulary is used
        voc_id = 'dummylanguage_voc'
        container = self.vocabcontainer
        tuples = (('nl', 'N'), ('ua', 'U'))
        localvoc = LocalVocabulary(voc_id, tuples,
                                   inheritance_type='inherit',
                                   merge_behaviour='None')
        container._setObject(voc_id, localvoc)
        self.assertEqual(len(container.objectIds()), 1)

        voc = container.getVocabulary(voc_id)
        self.assert_(voc is not None)
        self.assertEqual(len(voc.keys()), 2)
        for key in voc.keys():
            self.assertEqual(voc.getMsgid(key), None)
        for key, val in tuples:
            self.assertEqual(voc[key], val)

        # check that container parameters are not taken into account when
        # local vocabulary with given id exists in container
        container.inheritance_type = 'inherit'
        container.merge_behaviour = 'None'
        voc = container.getVocabulary(voc_id)
        self.assertEqual(len(voc.keys()), 2)

        container.inheritance_type = 'global'
        container.merge_behaviour = 'None'
        voc = container.getVocabulary(voc_id)
        self.assertEqual(len(voc.keys()), 2)

    def testGetVocabulary5(self):
        # Local vocabulary is in container
        # local vocabulary attributes:
        # inheritance_type = 'inherit'
        # merge_behaviour = 'union'
        # Result: union with upper local vocabulary which itself may be
        # defined as it sees fit
        voc_id = 'dummylanguage_voc'
        container = self.vocabcontainer
        tuples = (('nl', 'N'), ('ua', 'U'))
        localvoc = LocalVocabulary(voc_id, tuples,
                                   inheritance_type='inherit',
                                   merge_behaviour='union')
        container._setObject(voc_id, localvoc)
        self.assertEqual(len(container.objectIds()), 1)

        voc = container.getVocabulary(voc_id)
        self.assert_(voc is not None)
        self.assertEqual(len(voc.keys()), 5)
        for key, val in self.globalvoctuples + tuples:
            self.assertEqual(voc[key], val)

        # check that container parameters are not taken into account when
        # local vocabulary with given id exists in container
        container.inheritance_type = 'inherit'
        container.merge_behaviour = 'None'
        voc = container.getVocabulary(voc_id)
        self.assertEqual(len(voc.keys()), 5)

        container.inheritance_type = 'global'
        container.merge_behaviour = 'None'
        voc = container.getVocabulary(voc_id)
        self.assertEqual(len(voc.keys()), 5)

        # check: if in local vocabulary there is key equal to the key in
        # an acquired vocabulary, then key from local vocabulary will be in
        # result thus overriding similar key from acquired vocabulary.
        localvoc = getattr(container, voc_id)
        localvoc.set('en', 'English')
        self.assertEqual(voc['en'], 'E')
        voc = container.getVocabulary(voc_id)
        self.assertEqual(len(voc.keys()), 5)
        self.assertEqual(voc['en'], 'English')


    def testGetVocabulary6(self):
        # Local vocabulary is in container
        # local vocabulary attributes:
        # inheritance_type = 'inherit'
        # merge_behaviour = 'union'
        # Testing acquiring local vocabulary from the upper tree with its own
        # configuration policy.

        voc_id = 'dummylanguage_voc'
        container = self.vocabcontainer
        tuples = (('nl', 'N'), ('ua', 'U'))
        localvoc = LocalVocabulary(voc_id, tuples,
                                   inheritance_type='inherit',
                                   merge_behaviour='union')

        uppervoc, uppertuples = self._makeUpperVocabulary()

        container._setObject(voc_id, localvoc)
        self.assertEqual(len(container.objectIds()), 1)

        uppervoc.inheritance_type = 'global'
        uppervoc.merge_behaviour = 'None'
        voc = container.getVocabulary(voc_id)
        self.assert_(voc is not None)
        self.assertEqual(len(voc.keys()), 5)
        for key, val in self.globalvoctuples + tuples:
            self.assertEqual(voc[key], val)
        for key, val in uppertuples:
            self.assertEqual(voc.get(key), None)

        uppervoc.inheritance_type = 'global'
        uppervoc.merge_behaviour = 'union'
        voc = container.getVocabulary(voc_id)
        self.assertEqual(len(voc.keys()), 6)
        for key, val in self.globalvoctuples + uppertuples + tuples:
            self.assertEqual(voc[key], val)

        uppervoc.inheritance_type = 'inherit'
        uppervoc.merge_behaviour = 'None'
        voc = container.getVocabulary(voc_id)
        self.assertEqual(len(voc.keys()), 3)
        for key, val in uppertuples + tuples:
            self.assertEqual(voc[key], val)

        uppervoc.inheritance_type = 'inherit'
        uppervoc.merge_behaviour = 'union'
        voc = container.getVocabulary(voc_id)
        self.assertEqual(len(voc.keys()), 6)
        for key, val in self.globalvoctuples + uppertuples + tuples:
            self.assertEqual(voc[key], val)


    def testGetVocabulary7(self):
        # Local vocabulary is in container
        # local vocabulary attributes:
        # inheritance_type = 'global'
        # merge_behaviour = 'None'
        # Result: local vocabulary is ignored and the global one is used
        voc_id = 'dummylanguage_voc'
        container = self.vocabcontainer
        tuples = (('nl', 'N'), ('ua', 'U'))
        localvoc = LocalVocabulary(voc_id, tuples,
                                   inheritance_type='global',
                                   merge_behaviour='None')
        container._setObject(voc_id, localvoc)
        self.assertEqual(len(container.objectIds()), 1)

        voc = container.getVocabulary(voc_id)
        self.assertEqual(len(voc.keys()), 3)
        for key in voc.keys():
            self.assertEqual(voc.getMsgid(key), key + '_dummymsgid')
        for key, val in self.globalvoctuples:
            self.assertEqual(voc[key], val)

        self.assertRaises(KeyError, container.getVocabulary, voc_id + '1')

        # check that container parameters are not taken into account when
        # local vocabulary with given id exists in container
        container.inheritance_type = 'inherit'
        container.merge_behaviour = 'None'
        voc = container.getVocabulary(voc_id)
        self.assertEqual(len(voc.keys()), 3)

        container.inheritance_type = 'global'
        container.merge_behaviour = 'None'
        voc = container.getVocabulary(voc_id)
        self.assertEqual(len(voc.keys()), 3)


    def testGetVocabulary8(self):
        # Local vocabulary is in container
        # local vocabulary attributes:
        # inheritance_type = 'global'
        # merge_behaviour = 'union'
        # Result: union with the global vocabulary
        voc_id = 'dummylanguage_voc'
        container = self.vocabcontainer
        tuples = (('nl', 'N'), ('ua', 'U'))
        localvoc = LocalVocabulary(voc_id, tuples,
                                   inheritance_type='global',
                                   merge_behaviour='union')
        container._setObject(voc_id, localvoc)
        self.assertEqual(len(container.objectIds()), 1)

        voc = container.getVocabulary(voc_id)
        self.assertEqual(len(voc.keys()), 5)
        for key, val in self.globalvoctuples + tuples:
            self.assertEqual(voc[key], val)

        self.assertRaises(KeyError, container.getVocabulary, voc_id + '1')

        # check that container parameters are not taken into account when
        # local vocabulary with given id exists in container
        container.inheritance_type = 'inherit'
        container.merge_behaviour = 'None'
        voc = container.getVocabulary(voc_id)
        self.assertEqual(len(voc.keys()), 5)

        container.inheritance_type = 'global'
        container.merge_behaviour = 'None'
        voc = container.getVocabulary(voc_id)
        self.assertEqual(len(voc.keys()), 5)


class HelperFunctionsTests(unittest.TestCase):
    def testUnion(self):
        voc1 = CPSVocabulary('id1',
                             (('foo', 'F'), ('bar', 'B'), ('meuh', 'M')))
        self.assertEqual(len(voc1.keys()), 3)
        voc2 = CPSVocabulary('id2', (('gandalf', 'G'), ('neo', 'N')))
        self.assertEqual(len(voc2.keys()), 2)

        cvoc = union(voc1, voc2)
        self.assertEqual(len(cvoc.keys()), 5)

        voc2 = CPSVocabulary('id2',
                             (('foo', 'FRODO'), ('gandalf', 'G'), ('neo', 'N')))
        self.assertEqual(len(voc2.keys()), 3)
        cvoc = union(voc1, voc2)
        self.assertEqual(len(cvoc.keys()), 5)
        self.assertEqual(cvoc['foo'], 'FRODO')

        voc1.set('bar', 'B', 'bar_msgid')
        voc2.set('foo', 'FRODO', 'foo_msgid')
        cvoc = union(voc1, voc2)
        self.assertEqual(cvoc.getMsgid('bar'), 'bar_msgid')
        self.assertEqual(cvoc.getMsgid('foo'), 'foo_msgid')
        self.assertEqual(cvoc.getMsgid('dummy'), None)

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(LocalVocabularyTests),
        unittest.makeSuite(LocalVocabularyContainerTests),
        unittest.makeSuite(HelperFunctionsTests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
