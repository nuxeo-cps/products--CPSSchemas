# (C) Copyright 2003-2007 Nuxeo SAS <http://nuxeo.com>
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
"""Vocabulary

Vocabularies store a correspondance between keys and a human-readable
label. They can be ordered, and may get their data from an external or
computed source.
"""

from zLOG import LOG, DEBUG
from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo
from AccessControl import getSecurityManager
from AccessControl import Unauthorized
from Persistence import Persistent
from Acquisition import Implicit

from Products.CMFCore.permissions import View, ManagePortal
from Products.CMFCore.utils import SimpleItemWithProperties, getToolByName
from Products.CPSUtil.PropertiesPostProcessor import PropertiesPostProcessor
from Products.CPSSchemas.VocabulariesTool import VocabularyTypeRegistry

from zope.interface import implements
from Products.CPSSchemas.interfaces import ICPSVocabulary

builtins_list = list


class Vocabulary(Persistent, Implicit):
    """Vocabulary

    Base class for explicit vocabularies.
    """

    security = ClassSecurityInfo()

    def __init__(self, tuples=None, list=None, dict=None):
        """Initialize a vocabulary.

        Allowed parameter syntaxes are:

          - Vocabulary((('foo', "Foo"), ('bar', "Bar")))

            Preferred

          - Vocabulary(tuples=(('foo', "Foo"), ('bar', "Bar")))

            Same as first.

          - Vocabulary((('foo', "Foo", 'label_foo'), ('bar', "Bar", 'label_bar')))

            Same as first with message ids (msgids) that can be used for i18n

          - Vocabulary(('foo', 'bar'))

            Values are same as keys.

          - Vocabulary(list=('foo', 'bar'))

            Values are same as keys, alternate syntax.

          - Vocabulary(tuples=('foo', 'bar'))

            Values are same as keys, other syntax.

          - Vocabulary(list=('foo', 'bar'), dict={'foo':"Foo", 'bar':"Bar"})

            Old syntax.

          - Vocabulary(dict={'foo':"Foo", 'bar':"Bar"})

            Old syntax, key order is random.
        """
        self.clear()
        l = []
        d = {}
        m = {}
        # We suppose that initial vocabulary is sorted
        if tuples:
            if isinstance(tuples[0], str):
                # Vocabulary(('foo', 'bar'))
                l = builtins_list(tuples)
                for k in l:
                    d[k] = k
            elif len(tuples[0]) == 2:
                # Vocabulary((('foo', "Foo"), ('bar', "Bar")))
                for k, v in tuples:
                    l.append(k)
                    d[k] = v
            else:
                # Vocabulary((('foo', "Foo", 'label_foo'), ('bar', "Bar", 'label_bar')))
                for k, v, msgid in tuples:
                    l.append(k)
                    d[k] = v
                    m[k] = msgid
        elif dict is not None:
            d = dict.copy()
            if list is not None:
                # Vocabulary(list=('foo',), dict={'foo':"Foo"})
                l = builtins_list(list)
            else:
                # Vocabulary(dict={'foo':"Foo", 'bar':"Bar"})
                l = dict.keys()
        elif list is not None:
            # Vocabulary(list=('foo', 'bar'))
            l = builtins_list(list)
            for k in l:
                d[k] = k
        else:
            # Vocabulary()
            pass
        self._list = l
        self._dict = d
        self._msgids = m

    def clear(self):
        """Clear the vocabulary."""
        self._list = []
        self._dict = {}
        self._msgids = {}

    def __delitem__(self, key):
        self._p_changed = 1
        del self._dict[key]
        try:
            del self._msgids[key]
        except KeyError:
            # __init__ doesn't initialize _msgids so this can't be
            # *del*eted directly
            pass
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

    def values(self):
        """Get the ordered list of values."""
        return [self._dict.get(key) for key in self._list]

    def keysSortedBy(self, crit='id'):
        """Return a keys list sorted on a criterium

        Crit is one of 'id', 'label' or 'i18n'.
        """

        if crit == 'label':
            l = [(x[1], x[0]) for x in self.items()]
            l.sort()
            return [x[1] for x in l]
        elif crit == 'i18n':
            portal = getToolByName(self, 'portal_url').getPortalObject()
            cpsmcat = portal.translation_service
            l = [(cpsmcat(self.getMsgid(key)).encode('ISO-8859-15', 'ignore'),
                  key) for key in self.keys()]
            l.sort()
            return [x[1] for x in l]
        else:
            return self.keys()

InitializeClass(Vocabulary)


class CPSVocabulary(PropertiesPostProcessor, SimpleItemWithProperties):
    """CPS Vocabulary.
    """

    implements(ICPSVocabulary)

    meta_type = "CPS Vocabulary"

    security = ClassSecurityInfo()
    security.declareObjectProtected(View)

    _propertiesBaseClass = SimpleItemWithProperties
    _properties = (
        {'id': 'title', 'type': 'string', 'mode': 'w',
         'label': 'Title'},
        {'id': 'title_msgid', 'type': 'string', 'mode': 'w',
         'label': 'Title msgid'},
        {'id': 'description', 'type': 'text', 'mode': 'w',
         'label':'Description'},
        {'id': 'acl_write_roles', 'type': 'string', 'mode': 'w',
         'label':'ACL: write roles'},
        )

    title = ''
    title_msgid = ''
    description = ''
    acl_write_roles = 'Manager'

    acl_write_roles_c = ['Manager']

    _properties_post_process_split = (
        ('acl_write_roles', 'acl_write_roles_c', ',; '),
        )

    user_modified = 0

    def __init__(self, id, tuples=None, list=None, dict=None, title='',
                 **kw):
        self.id = id
        self.title = title
        vocab = Vocabulary(tuples=tuples, list=list, dict=dict)
        self.setVocabulary(vocab)

    security.declareProtected(ManagePortal, 'setVocabulary')
    def setVocabulary(self, vocab):
        # XXX check base class ?
        self._vocab = vocab

    security.declareProtected(ManagePortal, 'clear')
    def clear(self):
        # _p_changed shouldn't be necessary
        return self._vocab.clear()

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

    security.declareProtected(View, 'values')
    def values(self):
        return self._vocab.values()

    security.declareProtected(View, 'has_key')
    def has_key(self, key):
        return self._vocab.has_key(key)

    security.declareProtected(View, 'keysSortedBy')
    def keysSortedBy(self, crit):
        return self._vocab.keysSortedBy(crit)

    #
    # Management
    #

    security.declarePublic('isWriteAllowed')
    def isWriteAllowed(self):
        """Test if the user can write to this vocabulary."""
        return getSecurityManager().getUser().has_role(
            self.acl_write_roles_c, object=self)

    security.declareProtected(ManagePortal, 'isUserModified')
    def isUserModified(self):
        """Tell if the vocabulary has been modified by a user.
        """
        return self.user_modified

    security.declareProtected(ManagePortal, 'setUserModified')
    def setUserModified(self, modified):
        """Set the vocabulary as modified.

        This is useful for scripts triggered by user actions.
        """
        self.user_modified = modified

    #
    # ZMI
    #

    manage_options = (
        {'label': 'Vocabulary',
         'action': 'manage_editVocabulary',
         },
        ) + SimpleItemWithProperties.manage_options + (
        {'label': 'Export',
         'action': 'manage_genericSetupExport.html',
         },
        )

    security.declareProtected(ManagePortal, 'manage_editVocabulary')
    manage_editVocabulary = DTMLFile('zmi/vocabulary_editform', globals())

    security.declareProtected(ManagePortal, 'manage_export')
    manage_export = DTMLFile('zmi/vocabulary_export', globals())

    security.declareProtected(ManagePortal, 'manage_main')
    manage_editVocabulary._setName('manage_main')
    manage_main = manage_editVocabulary

    security.declarePrivate('_checkWriteAllowed')
    def _checkWriteAllowed(self):
        """Check that user can write to this vocabulary."""
        if not self.isWriteAllowed():
            raise Unauthorized("No write access to vocabulary")

    security.declarePublic('manage_addVocabularyItem')
    def manage_addVocabularyItem(self, new_key, new_label, new_msgid,
                                 REQUEST=None):
        """Add a vocabulary item."""
        self._checkWriteAllowed()
        self.set(new_key, new_label, new_msgid)
        self.user_modified = 1
        if REQUEST is not None:
            return self.manage_main(REQUEST, manage_tabs_message='Added.')

    security.declarePublic('manage_changeVocabulary')
    def manage_changeVocabulary(self, form={}, REQUEST=None):
        """Change a vocabulary.

        The form parameter must contains the full new vocabulary as a
        dict with keys key_0, label_0, msgid_0, etc.
        """
        self._checkWriteAllowed()
        form = form.copy()
        if REQUEST is not None:
            form.update(REQUEST.form)
        vocab = Vocabulary()
        i = -1
        while 1:
            i += 1
            k = 'key_%d' % i
            if not form.has_key(k):
                break
            vocab.set(form[k], form['label_%d' % i], form['msgid_%d' % i])
        self.setVocabulary(vocab)
        self.user_modified = 1
        if REQUEST is not None:
            return self.manage_main(REQUEST, manage_tabs_message='Changed.')

    security.declarePublic('manage_delVocabularyItems')
    def manage_delVocabularyItems(self, keys, REQUEST=None):
        """Delete vocabulary items."""
        self._checkWriteAllowed()
        for key in keys:
            del self[key]
        self.user_modified = 1
        if REQUEST is not None:
            return self.manage_main(REQUEST, manage_tabs_message='Deleted.')

InitializeClass(CPSVocabulary)

VocabularyTypeRegistry.register(CPSVocabulary)
# Exporter is registered in setup/vocabulary.py

class EmptyKeyVocabularyWrapper:
    """ A simple class that wraps any vocabulary to add an empty key.
    """

    implements(ICPSVocabulary)

    def __init__(self, vocabulary, value, msgid=None, position='first'):
        """Constructor.

        value: the value to associate to ''
        msgid: the msgid to associate to ''
        position: all other than 'first' mean 'last'
        """
        self._voc = vocabulary
        self._val = value
        self._msgid = msgid
        self._pos = position

    def _wrap_list(self, l, value):
        """Return list l in which value has been inserted.
        """
        # Ensuring that there aren't any empty key duplicate
        l = [x for x in l if x != value]
        if self._pos == 'first' and l[0] != value:
            l.insert(0, value)
        elif l[-1] != value:
            l.append(value)
        return l

    def clear(self):
        """Clear the vocabulary."""
        self._voc.clear()

    def __delitem__(self, key):
        if key != '':
            self._voc.__delitem__(self, key)

    def set(self, key, label, msgid=None):
        """Set a label for a key."""
        if key != '':
            self._voc.set(key, label, msgid=msgid)

    def __getitem__(self, key):
        """Get a label for a key."""
        if key == '':
            return self._val
        return self._voc.__getitem__(key)

    def get(self, key, default=None):
        """Get a label for a key, default to None."""
        if key == '':
            return self._val
        return self._voc.get(key, default)

    def getMsgid(self, key, default=None):
        """Get a msgid for a key, default to None."""
        if key == '':
            return self._msgid
        return self._voc.getMsgid(key, default)

    def has_key(self, key):
        """Test if a key is present."""
        return key == '' or self._voc.has_key(key)

    def keys(self):
        """Get the ordered list of keys."""
        return self._wrap_list(self._voc.keys(), '')

    def items(self):
        """Get the ordered list of (key, value)."""
        return self._wrap_list(self._voc.items(), ('', self._val))

    def values(self):
        """Get the ordered list of values."""
        return self._wrap_list(self._voc.values(), self._val)

    def keysSortedBy(self, crit='id'):
        """Return a keys list sorted on a criterium

        Empty key position is not affected by sorting
        """
        return self._wrap_list(self._voc.keysSortedBy(crit=crit), '')
