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
"""Vocabulary

Vocabularies store a correspondance between keys and a human-readable
label. They can be ordered, and may get their data from an external or
computed source.
"""

from zLOG import LOG, DEBUG
from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo
from Persistence import Persistent
from Interface import Interface

from Products.CMFCore.CMFCorePermissions import View, ManagePortal
from Products.CMFCore.utils import SimpleItemWithProperties

builtins_list = list


class IVocabulary(Interface):
    """Interface for Vocabulary."""
    # XXX TODO
    pass


class Vocabulary(Persistent):
    """Vocabulary

    Base class for explicit vocabularies.
    """

    __implements__ = IVocabulary

    security = ClassSecurityInfo()
    security.setDefaultAccess('allow')

    def __init__(self, dict=None, list=None):
        # XXX improve
        self.clear()
        if dict is not None:
            self._dict = dict.copy()
            if list is not None:
                self._list = builtins_list(list)
            else:
                self._list = dict.keys()

    def __repr__(self):
        return '<Vocabulary %s>' % repr(self._dict)

    def clear(self):
        """Clear the vocabulary."""
        self._list = []
        self._dict = {}
        self._msgids = {}

    def __delitem__(self, key):
        self._p_changed = 1
        del self._dict[key]
        del self._msgids[key]
        self._list.remove(key)

    def set(self, key, label, msgid=None):
        """Set a label for a key."""
        self._p_changed = 1
        if not self._dict.has_key(key):
            self._list.append(key)
        self._dict[key] = label
        self._msgids[key] = msgid

    def __getitem__(self, key):
        """Get a label for a key."""
        return self._dict[key]

    def get(self, key, default=None):
        """Get a label for a key, default to None."""
        try:
            v = self._dict.get(key, default)
        except TypeError:
            # XXX temporary fix, don't know why sometime rendering try to do
            # get([]) that returning a typeError
            return ''
        return v

    def getMsgid(self, key, default=None):
        """Get a msgid for a key, default to None."""
        return self._msgids.get(key, default)

    def has_key(self, key):
        """Test if a key is present."""
        return self._dict.has_key(key)

    def keys(self):
        """Get the ordered list of keys."""
        return self._list[:]

    def items(self):
        """Get the ordered list of (key, value)."""
        return [(key, self._dict.get(key)) for key in self._list]

    def orderKeys(self, keys):
        """Set the order of keys."""
        raise NotImplementedError

InitializeClass(Vocabulary)


class CPSVocabulary(SimpleItemWithProperties):
    """Persistent Vocabulary."""

    meta_type = "CPS Vocabulary"

    security = ClassSecurityInfo()

    title = ''
    title_msgid = ''
    description = ''

    def __init__(self, id, title='', vocab=None, **kw):
        self.id = id
        self.title = title
        if vocab is None:
            vocab = Vocabulary()
        self.setVocabulary(vocab)

    security.declareProtected(ManagePortal, 'setVocabulary')
    def setVocabulary(self, vocab):
        # XXX check base class ?
        self._vocab = vocab

    security.declareProtected(ManagePortal, '__delitem__')
    def __delitem__(self, key):
        del self._vocab[key]

    security.declareProtected(ManagePortal, 'set')
    def set(self, key, label, msgid=None):
        return self._vocab.set(key, label, msgid)

    security.declareProtected(View, '__getitem__')
    def __getitem__(self, key):
        return self._vocab[key]

    security.declareProtected(View, 'get')
    def get(self, key, default=None):
        return self._vocab.get(key, default)

    security.declareProtected(View, 'getMsgid')
    def getMsgid(self, key, default=None):
        return self._vocab.getMsgid(key, default)

    security.declareProtected(View, 'keys')
    def keys(self):
        return self._vocab.keys()

    security.declareProtected(View, 'items')
    def items(self):
        return self._vocab.items()

    security.declareProtected(View, 'has_key')
    def has_key(self, key):
        return self._vocab.has_key(key)

    #
    # ZMI
    #

    _properties = (
        {'id': 'title', 'type': 'string', 'mode': 'w',
         'label': 'Title'},
        {'id': 'title_msgid', 'type': 'string', 'mode': 'w',
         'label': 'Title Msgid'},
        {'id': 'description', 'type': 'text', 'mode': 'w',
         'label':'Description'},
        )

    manage_options = (
        {'label': 'Vocabulary',
         'action': 'manage_editVocabulary',
         },
        ) + SimpleItemWithProperties.manage_options + (
        {'label': 'Export',
         'action': 'manage_export',
         },
        )

    security.declareProtected(ManagePortal, 'manage_editVocabulary')
    manage_editVocabulary = DTMLFile('zmi/vocabulary_editform', globals())

    security.declareProtected(ManagePortal, 'manage_export')
    manage_export = DTMLFile('zmi/vocabulary_export', globals())

    security.declareProtected(ManagePortal, 'manage_main')
    manage_main = manage_editVocabulary

    security.declareProtected(ManagePortal, 'manage_addVocabularyItem')
    def manage_addVocabularyItem(self, new_key, new_label, new_msgid, REQUEST):
        """Add a vocabulary item TTW."""
        self.set(new_key, new_label, new_msgid)
        return self.manage_main(REQUEST, manage_tabs_message='Added.')

    security.declareProtected(ManagePortal, 'manage_changeVocabulary')
    def manage_changeVocabulary(self, REQUEST):
        """Change a vocabulary TTW."""
        kw = REQUEST.form
        vocab = Vocabulary()
        i = -1
        while 1:
            i += 1
            k = 'key_%d' % i
            if not kw.has_key(k):
                break
            vocab.set(kw[k], kw['label_%d' % i], kw['msgid_%d' % i])
        self.setVocabulary(vocab)
        return self.manage_main(REQUEST, manage_tabs_message='Changed.')

    security.declareProtected(ManagePortal, 'manage_delVocabularyItems')
    def manage_delVocabularyItems(self, keys, REQUEST):
        """Delete vocabulary items TTW."""
        for key in keys:
            del self[key]
        return self.manage_main(REQUEST, manage_tabs_message='Deleted.')

InitializeClass(CPSVocabulary)


addCPSVocabularyForm = DTMLFile('zmi/vocabulary_addform', globals())

def addCPSVocabulary(container, id, REQUEST=None):
    """Add a CPS Vocabulary."""
    ob = CPSVocabulary(id)
    container._setObject(id, ob)
    ob = container._getOb(id)
    if REQUEST is not None:
        REQUEST.RESPONSE.redirect(ob.absolute_url() + "/manage_main")

