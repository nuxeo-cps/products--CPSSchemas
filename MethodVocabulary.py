# (C) Copyright 2004 Nuxeo SARL <http://nuxeo.com>
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
"""MethodVocabulary.

Vocabulary referencing a method.
"""

from zLOG import LOG, DEBUG
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Acquisition import Implicit

from Products.CMFCore.CMFCorePermissions import View, ManagePortal
from Products.CMFCore.utils import SimpleItemWithProperties

class MethodVocabulary(SimpleItemWithProperties):
    """Method Vocabulary

    Define a dynamic vocabulary using a method
    the method have to return a list of tuples like this
    (('foo', "Foo"), ('bar', "Bar"))

    the method should handle a 'key' argument
    if the key is not None then the method must return the value.
    The method should also handle the 'is_i18n' boolean argument
    if it's not False and return msgid corresponsding to the passed
    'key' argument
    """

    meta_type = "CPS Method Vocabulary"

    security = ClassSecurityInfo()

    _properties = (
        {'id': 'title', 'type': 'string', 'mode': 'w',
         'label': 'Title'},
        {'id': 'title_msgid', 'type': 'string', 'mode': 'w',
         'label': 'Title msgid'},
        {'id': 'description', 'type': 'text', 'mode': 'w',
         'label':'Description'},
        {'id': 'get_vocabulary_method', 'type': 'string', 'mode': 'w',
         'label':'Method'},
        {'id': 'add_empty_key', 'type': 'boolean', 'mode': 'w',
         'label':'Add an empty key'},
        {'id': 'empty_key_pos', 'type': 'selection', 'mode': 'w',
         'select_variable': 'empty_key_pos_select',
         'label':'Empty key position'},
        {'id': 'empty_key_value', 'type': 'string', 'mode': 'w',
         'label':'Empty key value'},
        {'id': 'empty_key_value_i18n', 'type': 'string', 'mode': 'w',
         'label':'Empty key i18n value'},
        )

    title = ''
    title_msgid = ''
    description = ''
    get_vocabulary_method = ''
    add_empty_key = 0
    empty_key_pos_select = ('first', 'last')
    empty_key_pos = empty_key_pos_select[0]
    empty_key_value = ''
    empty_key_value_i18n = ''

    def __init__(self, id, **kw):
        self.id = id
        self.manage_changeProperties(**kw)

    def _getMethod(self):
        """return the method that define the vocabulary."""
        meth = getattr(self, self.get_vocabulary_method, None)
        if meth is None:
            msg = "Unknown Vocabulary Method %s. " \
            + "Please set or change the 'get_vocabulary_method' attribute " \
            + "on your Method Vocabulary declaration for %s."
            raise RuntimeError(msg % (self.get_vocabulary_method,
                                      self.getId()))
        return meth

    security.declareProtected(View, '__getitem__')
    def __getitem__(self, key):
        if self.add_empty_key and key == '':
            return self.empty_key_value
        meth = self._getMethod()
        return meth(key=key)

    security.declareProtected(View, 'get')
    def get(self, key, default=None):
        try:
            return self[key]
        except (KeyError, AttributeError):
            return default

    security.declareProtected(View, 'getMsgid')
    def getMsgid(self, key, default=None):
        # XXX dummy
        return key+'msgid'

    security.declareProtected(View, 'keys')
    def keys(self):
        meth = self._getMethod()
        res = meth()
        res = [item[0] for item in res]
        if self.add_empty_key:
            v = ''
            res = list(res)
            if self.empty_key_pos == 'first':
                res.insert(0, v)
            else:
                res.append(v)
        return res

    security.declareProtected(View, 'items')
    def items(self):
        meth = self._getMethod()
        res = meth()
        if self.add_empty_key:
            v = ('', self.empty_key_value)
            res = list(res)
            if self.empty_key_pos == 'first':
                res.insert(0, v)
            else:
                res.append(v)
        return res

    security.declareProtected(View, 'values')
    def values(self):
        return [t[1] for t in self.items()]

    security.declareProtected(View, 'has_key')
    def has_key(self, key):
        _marker = []
        value = self.get(key, _marker)
        if value is _marker:
            return 0
        return 1

    security.declareProtected(ManagePortal, 'isUserModified')
    def isUserModified(self):
        """Tell if the vocabulary has been modified by a user.
        """
        return 0

InitializeClass(MethodVocabulary)


class MethodVocabularyWithContext(Implicit):
    """MethodVocabulary with context support."""

    security = ClassSecurityInfo()

    def __init__(self, vocabulary, context):
        self.vocabulary = vocabulary
        self.context = context

    def _getMethod(self):
        meth = getattr(self.context,
                       self.vocabulary.get_vocabulary_method,
                       None)
        if meth is None:
            msg = "Unknown Vocabulary Method %s. " \
            + "Please set or change the 'get_vocabulary_method' attribute " \
            + "on your Method Vocabulary declaration for %s."
            raise RuntimeError(msg % (self.vocabulary.get_vocabulary_method,
                                      self.vocabulary.getId()))
        return meth

    security.declareProtected(View, '__getitem__')
    def __getitem__(self, key):
        if self.vocabulary.add_empty_key and key == '':
            return self.vocabulary.empty_key_value
        meth = self._getMethod()
        return meth(key=key)

    security.declareProtected(View, 'get')
    def get(self, key, default=None):
        try:
            return self[key]
        except (KeyError, AttributeError):
            return default

    security.declareProtected(View, 'getMsgid')
    def getMsgid(self, key, default=None):
        if self.vocabulary.add_empty_key and key == '':
            return self.vocabulary.empty_key_value_i18n
        meth = self._getMethod()
        return meth(key=key, is_i18n=True)

    security.declareProtected(View, 'keys')
    def keys(self):
        meth = self._getMethod()
        res = meth()
        res = [item[0] for item in res]
        if self.vocabulary.add_empty_key:
            v = ''
            res = list(res)
            if self.vocabulary.empty_key_pos == 'first':
                res.insert(0, v)
            else:
                res.append(v)
        return res

    security.declareProtected(View, 'items')
    def items(self):
        meth = self._getMethod()
        res = meth()
        if self.vocabulary.add_empty_key:
            v = ('', self.vocabulary.empty_key_value)
            res = list(res)
            if self.vocabulary.empty_key_pos == 'first':
                res.insert(0, v)
            else:
                res.append(v)
        return res

    security.declareProtected(View, 'values')
    def values(self):
        return [t[1] for t in self.items()]

    security.declareProtected(View, 'has_key')
    def has_key(self, key):
        _marker = []
        value = self.get(key, _marker)
        if value is _marker:
            return 0
        return 1

    security.declareProtected(ManagePortal, 'isUserModified')
    def isUserModified(self):
        """Tell if the vocabulary has been modified by a user."""
        return 0

InitializeClass(MethodVocabularyWithContext)
