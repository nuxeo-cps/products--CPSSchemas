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

from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo
from Products.CPSCore.CPSBase import CPSBaseFolder
from Products.CPSSchemas.Vocabulary import CPSVocabulary, Vocabulary
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import ManagePortal

LOCAL_VOCABULARY_CONTAINER_ID = '.cps_vocabularies'
INHERITANCE_TYPES = ('inherit', 'global')
MERGE_BEHAVIOURS = ('None', 'union')

# Helper functions
def union(voc1=None, voc2=None):
    """Returns union of voc1 and voc2."""
    cvoc = CPSVocabulary('union')
    for voc in voc1, voc2:
        if voc is not None:
            for key, val in voc.items():
                cvoc.set(key, val, voc.getMsgid(key))
    return cvoc

class LocalVocabularyContainer(CPSBaseFolder):
    portal_type = meta_type = 'CPS Local Vocabulary Container'

    inheritance_type = 'inherit'
    merge_behaviour = 'None'

    security = ClassSecurityInfo()

    _properties = CPSBaseFolder._properties + \
                  ({'id': 'inheritance_type',
                    'type': 'selection',
                    'mode': 'w',
                    'select_variable': 'getInheritanceTypes',
                    'label': 'Inheritance type'},
                   {'id': 'merge_behaviour',
                    'type': 'selection',
                    'mode': 'w',
                    'select_variable': 'getMergeBehaviours',
                    'label': 'Merge behaviour'},
                   )

    def __init__(self, id, title=''):
        CPSBaseFolder.__init__(self, id, title=title)
        self.inheritance_type = 'inherit'
        self.merge_behaviour = 'None'

    def getInheritanceTypes(self):
        return INHERITANCE_TYPES

    def getMergeBehaviours(self):
        return MERGE_BEHAVIOURS

    security.declarePrivate('getGlobalVocabulary')
    def getGlobalVocabulary(self, voc_id):
        voctool = getToolByName(self, 'portal_vocabularies')
        globvoc = voctool._getOb(voc_id, None)
        if globvoc is None:
            raise KeyError, 'No vocabulary by id %s' % voc_id
        return globvoc

    security.declarePrivate('getUpperLocalVocabulary')
    def getUpperLocalVocabulary(self, context, voc_id):
        #uplevel = 0
        #if getattr(context, LOCAL_VOCABULARY_CONTAINER_ID, None) is not None:
        #    uplevel = 1
        #elif getattr(context.aq_inner.aq_parent,
        #             LOCAL_VOCABULARY_CONTAINER_ID, None) is not None:
        #    uplevel = 3
        #elif context.getId() == LOCAL_VOCABULARY_CONTAINER_ID:
        #    uplevel = 2
        voctool = getToolByName(self, 'portal_vocabularies')
        parent = context.aq_inner.aq_parent.aq_parent
        return voctool.getVocabularyFor(parent, voc_id)

    def getVocabulary(self, voc_id):
        voc = self._getOb(voc_id, None)

        if voc is None:
            # examine container parameters
            if self.inheritance_type == 'global':
                return self.getGlobalVocabulary(voc_id)
            elif self.inheritance_type == 'inherit':
                return self.getUpperLocalVocabulary(self, voc_id)
        else:
            if voc.inheritance_type == 'inherit':
                if voc.merge_behaviour == 'None':
                    return voc
                elif voc.merge_behaviour == 'union':
                    unionvoc = union(self.getUpperLocalVocabulary(self, voc_id),
                                     voc)
                    return unionvoc.__of__(self)
            elif voc.inheritance_type == 'global':
                if voc.merge_behaviour == 'None':
                    return self.getGlobalVocabulary(voc_id)
                elif voc.merge_behaviour == 'union':
                    unionvoc = union(self.getGlobalVocabulary(voc_id), voc)
                    return unionvoc.__of__(self)


    #########################################
    # ZMI
    #########################################
    manage_options = ({'label' : 'Global Vocabularies',
                       'action' : 'manage_editGlobalVocabularies',
                       },
                      ) + CPSBaseFolder.manage_options

    manage_editGlobalVocabularies = DTMLFile(
        'zmi/global_vocabularies_edit_form',
        globals())

    security.declareProtected(ManagePortal, 'manage_addLocalVocabularyForm')
    manage_addLocalVocabularyForm = DTMLFile('zmi/localvocabulary_addform', globals())

    security.declareProtected(ManagePortal, 'manage_addLocalVocabulary')
    def manage_addLocalVocabulary(self, id, inheritance_type='inherit',
                                  merge_behaviour='None', REQUEST=None):
        """Adds local vocabulary."""
        container = self
        voc = LocalVocabulary(id, inheritance_type=inheritance_type,
                              merge_behaviour=merge_behaviour)
        container._setObject(id, voc)
        ob = container._getOb(id)
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(ob.absolute_url()+'/manage_workspace'
                                      '?manage_tabs_message=Added')
        else:
            return ob

InitializeClass(LocalVocabularyContainer)

def addLocalVocabularyContainer(container, id=None, REQUEST=None):
    """Add Local Vocabulary Container"""

    id = LOCAL_VOCABULARY_CONTAINER_ID

    ob = LocalVocabularyContainer(id, title='Local Vocabularies Container')
    container._setObject(id, ob)

    if REQUEST is not None:
        REQUEST.RESPONSE.redirect(container.absolute_url()+'/manage_main')


class LocalVocabulary(CPSVocabulary):

    security = ClassSecurityInfo()

    portal_type = meta_type = 'CPS Local Vocabulary'

    inheritance_type = 'inherit'
    merge_behaviour = 'None'

    _properties = CPSBaseFolder._properties + \
                  ({'id': 'inheritance_type',
                    'type': 'selection',
                    'mode': 'w',
                    'select_variable': 'getInheritanceTypes',
                    'label': 'Inheritance type'},
                   {'id': 'merge_behaviour',
                    'type': 'selection',
                    'mode': 'w',
                    'select_variable': 'getMergeBehaviours',
                    'label': 'Merge behaviour'},
                   )

    def __init__(self, id, tuples=None, list=None, dict=None, title='',
                 sort_function=None,
                 inheritance_type='inherit',
                 merge_behaviour='None'):
        CPSVocabulary.__init__(self, id, tuples, list, dict, title, sort_function)
        self.inheritance_type = inheritance_type
        self.merge_behaviour = merge_behaviour

    def getInheritanceTypes(self):
        return INHERITANCE_TYPES

    def getMergeBehaviours(self):
        return MERGE_BEHAVIOURS

InitializeClass(LocalVocabulary)
