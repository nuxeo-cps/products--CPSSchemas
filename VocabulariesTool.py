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
"""Vocabularies Tool"""

from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo
from OFS.Folder import Folder
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.permissions import ManagePortal, View
from Products.CPSSchemas.LocalVocabulary import LOCAL_VOCABULARY_CONTAINER_ID

class VocabulariesTool(UniqueObject, Folder):
    """Vocabularies Tool

    The Vocabularies Tool stores the definition of vocabularies.
    A vocabulary describes the correspondance between a list of internal
    values and their human-readable couterpart (maybe internationalized).
    """

    id = 'portal_vocabularies'
    meta_type = 'CPS Vocabularies Tool'

    security = ClassSecurityInfo()

    #
    # ZMI
    #

    def all_meta_types(self):
        # Stripping is done to be able to pass a type in the URL.
        return [
            {'name': dt,
             'action': 'manage_addCPSVocabularyForm/' + dt.replace(' ', ''),
             'permission': ManagePortal}
            for dt in VocabularyTypeRegistry.listTypes()]

    security.declareProtected(ManagePortal, 'manage_addCPSVocabularyForm')
    manage_addCPSVocabularyForm = DTMLFile('zmi/vocabulary_addform', globals())

    security.declareProtected(ManagePortal, 'manage_addCPSVocabulary')
    def manage_addCPSVocabulary(self, id, meta_type='CPS Vocabulary',
                                REQUEST=None, **kw):
        """Add a vocabulary, called from the ZMI."""
        container = self
        cls = VocabularyTypeRegistry.getType(meta_type)
        ob = cls(id, **kw)
        container._setObject(id, ob)
        ob = container._getOb(id)
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(ob.absolute_url()+'/manage_workspace'
                                      '?manage_tabs_message=Added.')
        else:
            return ob

    security.declareProtected(ManagePortal, 'getVocabularyMetaType')
    def getVocabularyMetaType(self, meta_type):
        """Get an unstripped version of a vocabulary meta type."""
        return VocabularyTypeRegistry.getType(meta_type).meta_type

    security.declareProtected(View, 'getVocabularyFor')
    def getVocabularyFor(self, context, voc_id):
        """Returns vocabulary for given context."""

        def hasLocalVocContainer(context):
            try:
                return LOCAL_VOCABULARY_CONTAINER_ID in context.objectIds()
            except:
                return 0

        def getLocalVocContainer(context):
            return context._getOb(LOCAL_VOCABULARY_CONTAINER_ID, None)

        getParentNode = lambda node: getattr(getattr(node, 'aq_inner', None),
                                             'aq_parent', None)

        if not hasLocalVocContainer(context):
            parent = getParentNode(context)
            while parent:
                if hasLocalVocContainer(parent):
                    return getLocalVocContainer(parent).getVocabulary(voc_id)
                parent = getParentNode(parent)
            # no local vocabulary container found for given context
            globvoc = self._getOb(voc_id, None)
            if globvoc is None:
                raise KeyError, 'No vocabulary by id %s' % voc_id
            return globvoc
        else:
            return getLocalVocContainer(context).getVocabulary(voc_id)

InitializeClass(VocabulariesTool)


class VocabularyTypeRegistry:
    """Registry of the available vocabulary types.

    Internally strips spaces, to be able to use arguments extracted from
    URL components.
    """

    def __init__(self):
        self._types = {}

    def register(self, cls):
        """Register a vocabulary type."""
        mt = cls.meta_type.replace(' ', '')
        self._types[mt] = cls

    def listTypes(self):
        """List vocabulary types."""
        types = [cls.meta_type for cls in self._types.values()]
        types.sort()
        return types

    def getType(self, meta_type):
        """Get a vocabulary type."""
        mt = meta_type.replace(' ', '')
        return self._types[mt]

# Singleton
VocabularyTypeRegistry = VocabularyTypeRegistry()
