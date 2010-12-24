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
from Acquisition import aq_base, aq_inner, aq_parent
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import SimpleItemWithProperties

from Products.CPSSchemas.Widget import CPSWidget

class IndirectWidget(SimpleItemWithProperties): # why not SimpleItemWithProperties ?
    """See documentation in CPSSchemas/doc/indirect_widget

    current implementation actually makes a copy of the base widget and store
    it as a volatile attribute. This is good enough for now, we'll see what
    profiling tells us."""

    _properties = (dict(id='base_widget_rpath', type='string', mode='w',
                        label='Relative path of base widget'),
                   dict(id='is_parent_indirect', type='boolean', mode='w',
                        label="Is the worker widget aq parent the indirect's"),
                   )

    _v_worker = None
    is_parent_indirect = True

    def __init__(self, wid, **kw):
        self._setId(wid)

    def getWorkerWidget(self):
        worker_widget = self._v_worker
        if worker_widget is None:
            worker_widget = self.makeWorkerWidget()
        return worker_widget

    def clear(self):
        self._v_worker = None

    def makeWorkerWidget(self):
        portal = getToolByName(self, 'portal_url').getPortalObject()
        base = portal.unrestrictedTraverse(self.base_widget_rpath)
        worker = deepcopy(aq_base(base))

        # update worker properties, by creating them if needed
        props_upd = {}
        worker_class_props = set(p['id'] for p in worker.__class__._properties)
        for p in self._properties:
            pid = p['id']
            if pid in ('base_widget_rpath', 'is_parent_indirect'):
                continue
            if pid in worker_class_props:
                props_upd[pid] = self.getProperty(pid)
            else:
                worker.manage_addProperty(pid, self.getProperty(pid),
                                          p['type'])
        worker.manage_changeProperties(**props_upd)

        # fix worker widget id
        worker.getWidgetId = lambda : self.getWidgetId()

        # place in right aq context
        if self.is_parent_indirect: # avoid and/or to avoid bool(self)
            aq_ref = self
        else:
            aq_ref = base
        worker = worker.__of__(aq_parent(aq_inner(aq_ref)))

        self._v_worker = worker
        return worker

    # we cannot inherit from CPSWidget
    def getWidgetId(self):
        """Get this widget's id."""
        id = self.getId()
        if hasattr(self, 'getIdUnprefixed'):
            # Inside a FolderWithPrefixedIds.
            return self.getIdUnprefixed(id)
        else:
            # Standalone
            return id

    #
    # Widget API is completely indirected to worker widget
    #


    def prepare(self, ds, **kw):
        self.getWorkerWidget().prepare(ds, **kw)

    def validate(self, ds, **kw):
        return self.getWorkerWidget().validate(ds, **kw)

    def render(self, mode, ds, **kw):
        return self.getWorkerWidget().render(mode, ds, **kw)
