# (C) Copyright 2003 Nuxeo SARL <http://nuxeo.com>
# Author: Florent Guillaume <fg@nuxeo.com>
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
"""Vocabularies Tool
"""

from Globals import InitializeClass, DTMLFile
from Acquisition import aq_parent, aq_inner, aq_base
from AccessControl import ClassSecurityInfo

from OFS.Folder import Folder

from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.CMFCorePermissions import ManagePortal

from Products.CPSDocument.Vocabulary import CPSVocabulary

class VocabulariesTool(UniqueObject, Folder):
    """Vocabularies Tool

    The Vocabularies Tool stores the definition of vocabularies.
    A vocabulary describes the correspondance between a list of internal
    values and their human-readable couterpart (maybe internationalized).
    """

    id = 'portal_vocabularies'
    meta_type = 'CPS Vocabularies Tool'

    security = ClassSecurityInfo()

    security.declarePrivate('addVocabulary')
    def addVocabulary(self, id):
        """Add a vocabulary."""
        ob = CPSVocabulary(id)
        self._setObject(id, ob)
        ob = self._getOb(id)
        return ob

    #
    # ZMI
    #

    def all_meta_types(self):
        return ({'name': 'CPS Vocabulary',
                 'action': 'manage_addCPSVocabularyForm',
                 'permission': ManagePortal},
                # XXX also :
                #  CPS Computed Vocabulary
                #  CPS Members Vocabulary
                #  CPS Roles Vocabulary
                #  CPS Groups Vocabulary
                #  CPS Directory Vocabulary
                )

    security.declareProtected(ManagePortal, 'manage_addCPSVocabularyForm')
    manage_addCPSVocabularyForm = DTMLFile('zmi/vocabulary_addform', globals())

    security.declareProtected(ManagePortal, 'manage_addCPSVocabulary')
    def manage_addCPSVocabulary(self, id, REQUEST):
        """Add a vocabulary, called from the ZMI."""
        vocab = self.addVocabulary(id)
        REQUEST.RESPONSE.redirect(vocab.absolute_url()+'/manage_main'
                                  '?psm=Added.')

InitializeClass(VocabulariesTool)
