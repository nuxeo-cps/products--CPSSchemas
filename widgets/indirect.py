# (C) Copyright 2010 CPS-CMS Community <http://cps-cms.org/>
# Authors:
#     G. Racinet <georges@racinet.fr>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from copy import deepcopy

from zope.interface import implements
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base, aq_inner, aq_parent, aq_get

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import SimpleItemWithProperties

from Products.CPSSchemas.interfaces import IWidget

class IndirectWidget(SimpleItemWithProperties, object):
    """See documentation in CPSSchemas/doc/indirect_widget

    current implementation actually makes a copy of the base widget and store
    it as a volatile attribute. This is good enough for now, we'll see what
    profiling tells us.

    This is not an adapter because:
    - making an adapter persistent is probably funky
    - flexibility does not seem to be needed there

    The current implementation uses dirty acquisition hacks. Namely, it stores
    the wrapped parent in a volatile attribute, to perform lookup on it.
    The reason is that both in @property or in __getattr__, aq_chain is None,
    but we need to avoid constructing the worker widget each time a simple
    attribute is being looked up, and the Layout class does lots of them.

    An alternative would have been to use zope.proxy, but it's not clear
    without further study whether this goes well with acquisition, although
    rewriting in ZTK style would certainly have to be tried this way first.
    """

    implements(IWidget)

    meta_type = 'Indirect Widget'

    security = ClassSecurityInfo()

    _properties = (dict(id='base_widget_rpath', type='string', mode='w',
                        label='Relative path of base widget'),
                   dict(id='is_parent_indirect', type='boolean', mode='w',
                        label="Is the worker widget aq parent the indirect's"),
                   )

    _v_worker = (None, None) # actualy, worker + base widget
    _v_parent = (None,)
    is_parent_indirect = True

    def __init__(self, wid, **kw):
        self._setId(wid)

    @classmethod
    def localProps(cls):
        """Properties that are always local to the indirected widget."""
        return (p['id'] for p in cls._properties)

    def getWorkerWidget(self):
        worker, base = self._v_worker
        if worker is None:
            self.makeWorkerWidget()
            worker, base = self._v_worker

        # place in right aq context
        # _v_parent is more volatile that _v_worker because it gets
        # written over with each traversal, and in particular each request.
        # This is important: if we store the worker with its aq chain,
        # an expired request with no URL or RESPONSE can be acquired
        # from the widget in subsequent requests.
        if self.is_parent_indirect: # avoid and/or pattern to avoid bool(self)
            parent = self._v_parent[0]
        else:
            parent = aq_parent(aq_inner(base))
        return worker.__of__(parent)

    @property
    def title(self):
        return self.getProperty('title', None) or self.getWorkerWidget().title

#    def title_or_id(self):
#        return self.getWorkerWidget().title or self.getId()

    def clear(self):
        delattr(self, '_v_worker')

    def getTemplateWidget(self):
        utool = getToolByName(self._v_parent[0], 'portal_url')
        portal = utool.getPortalObject()
        return portal.unrestrictedTraverse(self.base_widget_rpath)

    def makeWorkerWidget(self):
        # using _v_parent to avoid loops in __getattr__
        base = self.getTemplateWidget()
        worker = deepcopy(aq_base(base))

        # update worker properties, by creating them if needed
        props_upd = {}
        worker_base_props = set(p['id'] for p in worker._properties)
        for p in self._properties:
            pid = p['id']
            if pid in self.localProps():
                continue
            if pid in worker_base_props:
                props_upd[pid] = self.getProperty(pid)
            else:
                worker.manage_addProperty(pid, self.getProperty(pid),
                                          p['type'])
        worker.manage_changeProperties(**props_upd)

        # fix worker widget id
        worker._setId(self.getId())

        # store in volatile var, without any aq wrapping (tuple hack)
        self._v_worker = (worker, base)

    security.declarePublic('getWidgetId')
    def getWidgetId(self):
        """Get this widget's id."""
        zid = self.getId()
        try:
            # Inside a FolderWithPrefixedIds.
            # method on parent used in makeWorkerWidget: avoid aq loops
            return getattr(self._v_parent[0], 'getIdUnprefixed')(zid)
        except AttributeError:
            # Standalone
            return zid

    def isHidden(self):
        # some buggy old template widgets may have been there and got through
        # if upgraded before fix for #2394
        return self.fields == ('?',)

    #
    # All other attributes from Widget API are indirected to worker widget
    #

    def __of__(self, parent):
        """Zope2 trick so that we can carry on aq chain from __getattr__
        """
        # tuple hack to store original aq (includes request container)
        self._v_parent = (parent,)
        return SimpleItemWithProperties.__of__(self, parent)

    def __getattr__(self, k):
        """This is called if normal python attr lookup fails, but before aq.

        In this method, the instance is never wrapped by acquisition.
        """
        if k in self.forwarded_attributes:
            try:
                return getattr(self.getWorkerWidget(), k)
            except AttributeError:
                pass
        if k.startswith('_'):
            raise AttributeError(k) # XXX maybe some have to get through
        assert self._v_parent[0] is not None
        return getattr(self._v_parent[0], k)

    forwarded_attributes = frozenset([
            'has_input_area', 'label_edit', 'hidden_empty', 'required',
            'label', 'help', 'is_i18n', 'fieldset', 'prepare', 'validate',
            'render', 'getHtmlWidgetId', 'getModeFromLayoutMode',
            'getProperty',
            'isReadOnly', 'getCssClass', 'getJavaScriptCode'])

InitializeClass(IndirectWidget)
