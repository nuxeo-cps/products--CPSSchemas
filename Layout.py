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

    _properties = (
        {'id': 'style_prefix', 'type': 'string', 'mode': 'w',
         'label': 'Prefix for zpt'},
        )

    style_prefix = ''
    prefix = 'w__'

    security = ClassSecurityInfo()
    security.setDefaultAccess('allow')

    id = None

    def __init__(self, **kw):
        layoutdef = {'ncols': 1, 'rows': []}
        self.setLayoutDefinition(layoutdef)
        self.manage_changeProperties(**kw)

    security.declarePrivate('normalizeLayoutDefinition')
    def normalizeLayoutDefinition(self, layoutdef):
        """Normalize a layout definition.

        Removes empty rows, normalize last cells so all widths are
        equal, recomputes ncols.
        """
        rows = layoutdef['rows']
        # Find max width.
        maxw = 1
        for row in rows:
            w = 0
            for cell in row:
                w += cell.get('ncols', 1)
            if w > maxw:
                maxw = w
        layoutdef['ncols'] = maxw
        # Normalize short widths.
        for row in rows:
            w = 0
            for cell in row:
                if cell is row[-1]:
                    cell['ncols'] = maxw - w
                else:
                    w += cell.get('ncols', 1)
        # Remove empty rows.
        layoutdef['rows'] = filter(None, rows)
        return layoutdef

    security.declarePrivate('setLayoutDefinition')
    def setLayoutDefinition(self, layoutdef):
        """Set the layout definition."""
        layoutdef = self.normalizeLayoutDefinition(layoutdef)
        self._layoutdef = deepcopy(layoutdef)

    security.declareProtected(View, 'getLayoutDefinition')
    def getLayoutDefinition(self):
        """Get the layout definition."""
        return deepcopy(self._layoutdef)

    security.declarePrivate('getStandardWidgetModeChooser')
    def getStandardWidgetModeChooser(self, layout_mode, datastructure):
        """Get a function to choose the mode to render a widget.
        """
        def widgetModeChooser(widget,
                              layout=self, layout_mode=layout_mode,
                              datastructure=datastructure):
            """Choose the mode to render a widget."""
            if layout_mode == 'view':
                if widget.hidden_view:
                    mode = None
                else:
                    mode = 'view'
            elif layout_mode in ('edit', 'create'):
                if widget.hidden_edit:
                    mode = None
                elif 0: # XXX widget read-only
                    mode = 'view'
                else:
                    mode = 'edit'
            elif layout_mode == 'editlayout':
                mode = 'view'
            else:
                raise ValueError("Unknown layout mode '%s'" % layout_mode)
            return mode

        return widgetModeChooser

    security.declarePrivate('prepareLayoutWidgets')
    def prepareLayoutWidgets(self, datastructure):
        """Prepare the layout widgets.

        Prepare all the widgets and thus updates the datastructure.
        """
        for widget_id, widget in self.items():
            widget.prepare(datastructure)

    security.declarePrivate('computeLayout')
    def computeLayout(self, datastructure, widget_mode_chooser):
        """Compute the layout.

        Renders the widgets and computes the final layout structure.

        The datastructure may have been updated with user data since the
        prepare phase.

        Renders all the widgets in an appropriate mode, and computes the
        final row/cell structure.

        Return a layout data.
        """
        layoutdata = self.getLayoutDefinition() # get a copy
        layoutdata['id'] = self.getId()
        # Render all the widgets.
        widgets = {}
        for widget_id, widget in self.items():
            mode = widget_mode_chooser(widget)
            if mode is not None:
                rendered = widget.render(mode, datastructure).strip()
                if widget.hidden_empty and not rendered:
                    hidden = 1
                else:
                    hidden = 0
            else:
                rendered = ''
                hidden = 1
            widgets[widget_id] = {
                'widget': widget,
                'widget_rendered': rendered,
                'hidden': hidden,
                }
        layoutdata['widgets'] = widgets
        # Store computed widget info in row/cell structure.
        for row in layoutdata['rows']:
            new_row = []
            for cell in row:
                cell.update(widgets[cell['widget_id']])
                if not cell['hidden']:
                    new_row.append(cell)
            row[:] = new_row
        # XXX hiding a cell should be made more configurable,
        # decide if it gets set to '', or if it is removed and
        # its space contributed to the left or right cell.
        # Re-normalize after removed cells.
        self.normalizeLayoutDefinition(layoutdata)
        layoutdata['style_prefix'] = self.style_prefix
        return layoutdata

    security.declarePrivate('validateLayout')
    def validateLayout(self, layoutdata, datastructure):
        """Validate the layout."""
        ok = 1
        for row in layoutdata['rows']:
            for cell in row:
                widget = cell['widget']
                ok = widget.validate(datastructure) and ok
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
        ) + SimpleItemWithProperties.manage_options + (
        {'label': 'Export',
         'action': 'manage_export',
         },
        )

    security.declareProtected(ManagePortal, 'manage_editLayout')
    manage_editLayout = DTMLFile('zmi/layout_editform', globals())

    security.declareProtected(ManagePortal, 'manage_export')
    manage_export = DTMLFile('zmi/layout_export', globals())

    security.declareProtected(ManagePortal, 'manage_addCPSWidgetForm')
    manage_addCPSWidgetForm = DTMLFile('zmi/widget_addform', globals())

    security.declareProtected(ManagePortal, 'getUnstrippedWidgetTypeId')
    def getUnstrippedWidgetTypeId(self, swtid):
        """Get an unstripped version of a widget type id."""
        wtool = getToolByName(self, 'portal_widget_types')
        twtid = swtid.replace(' ', '')
        for wtid in wtool.objectIds():
            if wtid.replace(' ', '') == twtid:
                return wtid
        raise ValueError(swtid)

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

