# (C) Copyright 2003 Nuxeo SARL <http://nuxeo.com>
# Authors: Lennart Regebro <lr@nuxeo.com>
#          Florent Guillaume <fg@nuxeo.com>
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
"""Layout

A layout describes how to render the basic fields of a schema.
"""

from zLOG import LOG, DEBUG
from copy import deepcopy
from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo

from OFS.Folder import Folder

from Products.CMFCore.CMFCorePermissions import View
from Products.CMFCore.CMFCorePermissions import ManagePortal
from Products.CMFCore.CMFCorePermissions import ViewManagementScreens
from Products.CMFCore.utils import SimpleItemWithProperties
from Products.CMFCore.utils import getToolByName

from Products.CPSSchemas.FolderWithPrefixedIds import FolderWithPrefixedIds
from Products.CPSSchemas.OrderedDictionary import OrderedDictionary
from Products.CPSSchemas.WidgetTypesTool import WidgetTypeRegistry


class LayoutContainer(Folder):
    """Layout Tool

    Stores persistent layout objects.
    """

    meta_type = 'CPS Layout Container'

    security = ClassSecurityInfo()

    def __init__(self, id):
        self._setId(id)

    security.declarePrivate('addLayout')
    def addLayout(self, id, layout):
        """Add a layout."""
        self._setObject(id, layout)
        return self._getOb(id)

    #
    # ZMI
    #

    def all_meta_types(self):
        return ({'name': 'CPS Layout',
                 'action': 'manage_addCPSLayoutForm',
                 'permission': ManagePortal},
                )

    security.declareProtected(ViewManagementScreens, 'manage_addCPSLayoutForm')
    manage_addCPSLayoutForm = DTMLFile('zmi/layout_addform', globals())

    security.declareProtected(ManagePortal, 'manage_addCPSLayout')
    def manage_addCPSLayout(self, id, REQUEST=None):
        """Add a layout, called from the ZMI."""
        layout = CPSLayout(id)
        layout = self.addLayout(id, layout)
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(layout.absolute_url()+'/manage_main'
                                      '?manage_tabs_message=Added.')
        else:
            return layout

InitializeClass(LayoutContainer)


######################################################################


class Layout(FolderWithPrefixedIds, SimpleItemWithProperties):
    """Basic Layout.

    A layout describes how to render the basic fields of a schema.
    """

    prefix = 'w__'

    security = ClassSecurityInfo()
    security.setDefaultAccess('allow')

    id = None

    def __init__(self, **kw):
        layoutdef = {'ncols': 1, 'rows': []}
        self.setLayoutDefinition(layoutdef)

    security.declarePrivate('_normalizeLayoutDefinition')
    def _normalizeLayoutDefinition(self, layoutdef):
        """Normalize a layout definition."""
        rows = layoutdef['rows']
        # Find max width.
        maxw = 1
        for row in rows:
            w = 0
            for cell in row:
                w += cell.get('ncols', 1)
            if w > maxw:
                maxw = w
        # Normalize short widths.
        for row in rows:
            w = 0
            for cell in row:
                if cell is row[-1]:
                    cell['ncols'] = maxw - w
                else:
                    w += cell.get('ncols', 1)
        layoutdef['ncols'] = maxw
        layoutdef['rows'] = filter(None, rows)
        return layoutdef

    security.declarePrivate('setLayoutDefinition')
    def setLayoutDefinition(self, layoutdef):
        """Set the layout definition."""
        layoutdef = self._normalizeLayoutDefinition(layoutdef)
        self._layoutdef = deepcopy(layoutdef)

    security.declareProtected(View, 'getLayoutDefinition')
    def getLayoutDefinition(self):
        """Get the layout definition."""
        return deepcopy(self._layoutdef)

    security.declarePrivate('getLayoutData')
    def getLayoutData(self, datastructure, datamodel):
        """Get the layout data.

        This has actuel widget instances.
        """
        layoutdata = self.getLayoutDefinition() # get a copy
        widgets = {}
        for row in layoutdata['rows']:
            for cell in row:
                widget_id = cell['widget_id']
                widget = self[widget_id]
                cell['widget'] = widget
                widgets[widget_id] = widget
                # XXX here filtering according to permissions ?
                widget.prepare(datastructure, datamodel)
        layoutdata['id'] = self.getId()
        layoutdata['widgets'] = widgets
        return layoutdata

    security.declarePrivate('validateLayout')
    def validateLayout(self, layoutdata, datastructure, datamodel):
        """Validate the layout."""
        ok = 1
        for row in layoutdata['rows']:
            for cell in row:
                widget = cell['widget']
                ok = widget.validate(datastructure, datamodel) and ok
        return ok

    def __repr__(self):
        return '<Layout %s>' % `self.getLayoutDefinition()`


InitializeClass(Layout)


class CPSLayout(Layout):
    """Persistent Layout."""

    meta_type = "CPS Layout"

    security = ClassSecurityInfo()

    def __init__(self, id, **kw):
        self.id = id
        Layout.__init__(self, **kw)

    security.declarePrivate('addWidget')
    def addWidget(self, id, wtid, **kw):
        """Add a new widget instance."""
        wtool = getToolByName(self, 'portal_widget_types')
        widget_type = wtool[wtid]
        widget = widget_type.makeInstance(id, **kw)
        return self.addSubObject(widget)

    #
    # ZMI
    #

    def all_meta_types(self):
        # List of meta types contained in Folder, for copy/paste support.
        return [
            {'name': WidgetTypeRegistry.getClass(wt).meta_type,
             'action': '',
             'permission': ManagePortal}
            for wt in WidgetTypeRegistry.listWidgetTypes()]

    def filtered_meta_types(self):
        # List of types available in Folder menu.
        wtool = getToolByName(self, 'portal_widget_types')
        return [
            {'name': wtid,
             'action': 'manage_addCPSWidgetForm/'+wtid.replace(' ', ''),
             'permission': ManagePortal}
            for wtid in wtool.objectIds()]

    manage_options = (
        {'label': 'Widgets',
         'action': 'manage_main',
         },
        {'label': 'Layout',
         'action': 'manage_editLayout',
         },
        ) + SimpleItemWithProperties.manage_options

    security.declareProtected(ManagePortal, 'manage_editLayout')
    manage_editLayout = DTMLFile('zmi/layout_editform', globals())

    security.declareProtected(ManagePortal, 'manage_addCPSWidgetForm')
    manage_addCPSWidgetForm = DTMLFile('zmi/widget_addform', globals())

    security.declareProtected(ManagePortal, 'getUnstrippedWidgetTypeId')
    def getUnstrippedWidgetTypeId(self, wtid):
        """Get an unstripped version of a widget type id."""
        wtool = getToolByName(self, 'portal_widget_types')
        swtid = wtid.replace(' ', '')
        for wtid in wtool.objectIds():
            if wtid.replace(' ', '') == swtid:
                return wtid
        raise ValueError(wtid)

    security.declareProtected(ManagePortal, 'manage_addCPSWidget')
    def manage_addCPSWidget(self, id, swtid, REQUEST=None, **kw):
        """Add a widget, called from the ZMI."""
        if REQUEST is not None:
            kw.update(REQUEST.form)
            for key in ('id', 'swtid'):
                if kw.has_key(key):
                    del kw[key]
        wtid = self.getUnstrippedWidgetTypeId(swtid)
        widget = self.addWidget(id, wtid, **kw)
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(widget.absolute_url()+
                                      '/manage_workspace')
        else:
            return widget

    security.declareProtected(ManagePortal, 'manage_changeLayout')
    def manage_changeLayout(self, addrow=0,
                            delcell=0, widencell=0, shrinkcell=0, splitcell=0,
                            REQUEST=None, **kw):
        """Change a layout."""
        if REQUEST is not None:
            kw.update(REQUEST.form)
        layoutdef = self.getLayoutDefinition()
        nrow = 0
        rows = layoutdef['rows']
        for row in rows:
            nrow += 1
            ncell = 0
            somedel, somesplit = 0, 0
            for cell in row:
                ncell += 1
                cell['widget_id'] = kw.get('cell_%d_%d' % (nrow, ncell), '')
                if kw.get('check_%d_%d' % (nrow, ncell)):
                    if delcell:
                        cell['del'] = 1
                        somedel = 1
                    if splitcell:
                        cell['split'] = 1
                        somesplit = 1
                    if widencell:
                        cell['ncols'] = cell['ncols']+1
                    if shrinkcell:
                        cell['ncols'] = max(1, cell['ncols']-1)
            if somedel:
                newrow = [cell for cell in row if not cell.get('del')]
                rows[nrow-1] = newrow
            if somesplit:
                newrow = []
                for cell in row:
                    newrow.append(cell)
                    if cell.get('split'):
                        cell['ncols'] = max(1, cell['ncols']-1)
                        del cell['split']
                        newrow.append({'ncols': 1, 'widget_id': ''})
                rows[nrow-1] = newrow
        if addrow:
            rows.append([{'ncols': 1, 'widget_id': ''}])
        layoutdef['rows'] = rows
        self.setLayoutDefinition(layoutdef)
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_editLayout'
                                      '?manage_tabs_message=Changed.')

    security.declareProtected(ManagePortal, 'manage_addLayoutRow')
    def manage_addLayoutRow(self, REQUEST=None, **kw):
        """Add a row to a layout."""
        return self.manage_changeLayout(addrow=1, REQUEST=REQUEST, **kw)

    security.declareProtected(ManagePortal, 'manage_deleteCell')
    def manage_deleteCell(self, REQUEST=None, **kw):
        """Delete a cell from a layout."""
        return self.manage_changeLayout(delcell=1, REQUEST=REQUEST, **kw)

    security.declareProtected(ManagePortal, 'manage_widenCell')
    def manage_widenCell(self, REQUEST=None, **kw):
        """Widen a cell from a layout."""
        return self.manage_changeLayout(widencell=1, REQUEST=REQUEST, **kw)

    security.declareProtected(ManagePortal, 'manage_shrinkCell')
    def manage_shrinkCell(self, REQUEST=None, **kw):
        """Shrink a cell from a layout."""
        return self.manage_changeLayout(shrinkcell=1, REQUEST=REQUEST, **kw)

    security.declareProtected(ManagePortal, 'manage_splitCell')
    def manage_splitCell(self, REQUEST=None, **kw):
        """Split a cell in two."""
        return self.manage_changeLayout(splitcell=1, REQUEST=REQUEST, **kw)

InitializeClass(CPSLayout)

