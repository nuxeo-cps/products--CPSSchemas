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
from OFS.ObjectManager import IFAwareObjectManager
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.permissions import ManagePortal, View

from zope.interface import implements
from Products.CPSSchemas.interfaces import IVocabularyTool
from Products.CPSSchemas.interfaces import IVocabulary


LOCAL_VOCABULARY_CONTAINER_ID = '.cps_vocabularies'

class VocabulariesTool(UniqueObject, IFAwareObjectManager, Folder):
    """Vocabularies Tool

    The Vocabularies Tool stores the definition of vocabularies.
    A vocabulary describes the correspondance between a list of internal
    values and their human-readable couterpart (maybe internationalized).
    """

    implements(IVocabularyTool)

    id = 'portal_vocabularies'
    meta_type = 'CPS Vocabularies Tool'
    _product_interfaces = (IVocabulary,)

    security = ClassSecurityInfo()

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

    # BBB for old installers/importers, will be removed in CPS 3.5
    security.declarePrivate('manage_addCPSVocabulary')
    def manage_addCPSVocabulary(self, id, meta_type='CPS Vocabulary', **kw):
        import Products
        for mt in Products.meta_types:
            if mt['name'] == meta_type:
                klass = mt['instance']
                self._setObject(id, klass(id, **kw))
                return self._getOb(id)
        raise ValueError("Unknown meta_type %r" % meta_type)

InitializeClass(VocabulariesTool)


class VocabularyTypeRegistry:
    """Registry of the available vocabulary types.

    Internally strips spaces, to be able to use arguments extracted from
    URL components.
    """

    def __init__(self):
        self._types = {}
        self._exporters = {}

    def register(self, cls, exporter=None):
        """Register a vocabulary type."""
        mt = cls.meta_type.replace(' ', '')
        self._types[mt] = cls
        if exporter is not None:
            self._exporters[mt] = exporter

    def listTypes(self):
        """List vocabulary types."""
        types = [cls.meta_type for cls in self._types.values()]
        types.sort()
        return types

    def getType(self, meta_type):
        """Get a vocabulary type."""
        mt = meta_type.replace(' ', '')
        return self._types[mt]

    def getExporter(self, meta_type):
        """Get a vocabulary exporter."""
        mt = meta_type.replace(' ', '')
        return self._exporters.get(mt)

# Singleton
VocabularyTypeRegistry = VocabularyTypeRegistry()
