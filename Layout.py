# (C) Copyright 2003-2005 Nuxeo SARL <http://nuxeo.com>
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

A layout describes how to render a set of widgets.
"""

from zLOG import LOG, DEBUG, WARNING
from copy import deepcopy
from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo

from OFS.Folder import Folder

from Products.CMFCore.permissions import View
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.permissions import ViewManagementScreens
from Products.CMFCore.utils import SimpleItemWithProperties
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import getEngine
from Products.CMFCore.Expression import SecureModuleImporter

from Products.CPSUtil.PropertiesPostProcessor import PropertiesPostProcessor
from Products.CPSSchemas.FolderWithPrefixedIds import FolderWithPrefixedIds
from Products.CPSSchemas.DataModel import ReadAccessError
from Products.CPSSchemas.Widget import widgetRegistry

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
class Layout(PropertiesPostProcessor,
             FolderWithPrefixedIds,
             SimpleItemWithProperties):
    """Basic Layout.

    A layout describes how to render a set of widgets.

    A layout can be rendered in several layout_modes (view, edit,
    create, editlayout, etc.). The rendered widgets themselves can only
    have two mode: 'view' and 'edit'. So the layout has to choose the
    widget modes depending on the layout_mode and various information
    about the widgets and their fields, notably read-only mode and ACLs.

    Layout rendering occurs with the following step:

      - prepareLayoutWidgets(): updates datastructure from field values,

      - (optional) manual updating of datastructure from request,

      - computeLayoutStructure(): computes layout_structure,

      - (optional) validateLayoutStructure(): validates and updates
        datamodel, or sets errors in datastructure,

      - renderLayoutStructure(): renders each widget into
        layout_structure,

      - renderLayoutStyle(): returns the final rendering using the style
        method.
    """

    _properties = (
        {'id': 'layout_create_method', 'type': 'string', 'mode': 'w',
         'label': 'Layout method for create mode'},
        {'id': 'layout_edit_method', 'type': 'string', 'mode': 'w',
         'label': 'Layout method for edit mode'},
        {'id': 'layout_view_method', 'type': 'string', 'mode': 'w',
         'label': 'Layout method for view mode'},
        {'id': 'style_prefix', 'type': 'string', 'mode': 'w',
         'label': 'Layout method prefix for default'},
        {'id': 'flexible_widgets', 'type': 'tokens', 'mode': 'w',
         'label': 'Allowed widgets in flexible'},
        {'id': 'validate_values_expr', 'type': 'text', 'mode': 'w',
         'label': 'Layout validation expression'},
        )

    style_prefix = 'layout_default_'
    layout_create_method = ''
    layout_edit_method = ''
    layout_view_method = ''
    flexible_widgets = ()
    validate_values_expr = ''
    validate_values_expr_c = None

    prefix = 'w__'
    id = None

    security = ClassSecurityInfo()
    security.setDefaultAccess('allow')

    _propertiesBaseClass = SimpleItemWithProperties
    _properties_post_process_tales = (
        ('validate_values_expr', 'validate_values_expr_c'),
        )

    def __init__(self, **kw):
        layoutdef = {'ncols': 1, 'rows': []}
        self.setLayoutDefinition(layoutdef)
        self.manage_changeProperties(**kw)

    security.declarePrivate('_getFlexibleWidgetsInfo')
    def _getFlexibleWidgetsInfo(self, n=0):
        """Return allowed widgets information."""
        items = []
        for item in self.flexible_widgets:
            v = item.split(':')
            if len(v) > n and v[n]:
                items.append(v[n])
            else:
                items.append(None)
        return items

    security.declarePrivate('getFlexibleWidgetIds')
    def getFlexibleWidgetIds(self):
        """Return allowed flexible widget ids."""
        return self._getFlexibleWidgetsInfo()

    security.declarePrivate('getFlexibleWidgetOccurences')
    def getFlexibleWidgetOccurences(self):
        """Return a list of maximum number of flexible widgets.

        0 is no limit."""
        return self._getFlexibleWidgetsInfo(n=1)

    security.declarePrivate('normalizeLayoutDefinition')
    def normalizeLayoutDefinition(self, layoutdef):
        """Normalize a layout definition.

        Removes empty rows, normalize last cells so all widths are
        equal, recomputes ncols, removing duplicate widgets.
        """
        rows = layoutdef['rows']
        # Find max width.
        maxw = 1
        for row in rows:
            w = 0
            for cell in row:
                ncols = cell.get('ncols', 1)
                cell['ncols'] = ncols
                w += ncols
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
                    w += cell['ncols']
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

    security.declarePrivate('removeHiddenWidgets')
    def removeHiddenWidgets(self, layout_structure):
        """Remove cells of hidden widgets.
        """
        # XXX hiding a cell should be made more configurable,
        # decide if it gets set to '', or if it is removed and
        # its space contributed to the left or right cell.
        for row in layout_structure['rows']:
            new_row = []
            for cell in row:
                if not self.has_key(cell['widget_id']):
                    LOG('CPSSchemas', WARNING,
                        'Layout %s refers to deleted widget %s' % (
                            self.getId(), cell['widget_id']))
                elif cell['widget_mode'] != 'hidden':
                    new_row.append(cell)
            row[:] = new_row
        # Re-normalize after removed cells.
        self.normalizeLayoutDefinition(layout_structure)

    security.declarePrivate('prepareLayoutWidgets')
    def prepareLayoutWidgets(self, datastructure, **kw):
        """Prepare the layout widgets.

        Prepare all the widgets and thus updates the datastructure.
        """
        dm = datastructure.getDataModel()
        dm._forbidden_widgets = []
        for widget_id, widget in self.items():
            if not widget.isHidden():
                try:
                    widget.prepare(datastructure)
                except ReadAccessError:
                    dm._forbidden_widgets.append(widget_id)

    security.declarePrivate('computeLayoutStructure')
    def computeLayoutStructure(self, layout_mode, datamodel):
        """Compute the layout structure.

        Chooses the mode for all the widgets. Removes hidden ones.

        Returns a layout structure, which is a dictionary with keys:
         - layout
         - layout_id
         - widgets
         - rows

        Cells in a row have additionnal keys:
         - widget
         - widget_mode
         - widget_css_class
         - widget_rendered
         - widget_javascript
         - widget_input_area_id
        (In addition to widget_id and ncols of the standard data.)
        """
        layout_structure = self.getLayoutDefinition() # get a copy
        layout_structure['layout'] = self
        layout_structure['layout_id'] = self.getId() # XXX FIXME remove
        # Set the mode, CSS class and JavaScript code for all the widgets.
        widgets = {}
        for widget_id, widget in self.items():
            if (not widget_id in datamodel._forbidden_widgets
                and not widget.isHidden()):
                mode = widget.getModeFromLayoutMode(layout_mode, datamodel)
                css_class = widget.getCssClass(layout_mode, datamodel)
                js_code = widget.getJavaScriptCode(layout_mode, datamodel)
                # Information about a potential input area is important for
                # accessibility: it is used to associate the widget label with a
                # potential input area.
                if widget.has_input_area and mode != 'view':
                    input_area_id = widget.getHtmlWidgetId()
                else:
                    input_area_id = None
                widgets[widget_id] = {
                    'widget': widget,
                    'widget_mode': mode,
                    'widget_css_class': css_class,
                    'widget_javascript': js_code,
                    'widget_input_area_id': input_area_id,
                    }
            else:
                widgets[widget_id] = {
                    'widget': widget,
                    'widget_mode': 'hidden',
                    }

        layout_structure['widgets'] = widgets
        # Store computed widget info in row/cell structure.
        for row in layout_structure['rows']:
            for cell in row:
                if widgets.has_key(cell['widget_id']):
                    cell.update(widgets[cell['widget_id']])
                else:
                    LOG('CPSSchemas', WARNING,
                        'Layout %s refers to deleted widget %s' % (
                            self.getId(), cell['widget_id']))
        # Eliminate hidden widgets.
        self.removeHiddenWidgets(layout_structure)
        return layout_structure

    security.declarePrivate('validateLayoutStructure')
    def validateLayoutStructure(self, layout_structure, datastructure, **kw):
        """Validate the layout.

        Only validates the widgets that are in 'edit' mode.
        """
        ok = 1
        for row in layout_structure['rows']:
            for cell in row:
                if cell['widget_mode'] == 'edit':
                    widget = cell['widget']
                    ok = widget.validate(datastructure, **kw) and ok
        if not ok:
            return False
        # Now validate the whole layout
        return self._validateLayout(datastructure, **kw)

    security.declarePrivate('_validateLayout')
    def _validateLayout(self, datastructure, **kw):
        """ Calls a script or an expression
            to validate the layout
        """
        if self.validate_values_expr_c is None:
            return True
        expr_context = self._createExpressionContext(datastructure, **kw)
        return self.validate_values_expr_c(expr_context)

    security.declarePrivate('_createExpressionContext')
    def _createExpressionContext(self, datastructure, **kw):
        """ creates an expression context for script execution
        """
        portal = getToolByName(self, 'portal_url').getPortalObject()
        data = {
            'layout': self,
            'datastructure': datastructure,
            'datamodel' : datastructure.getDataModel(),
            'kw': kw,
            'nothing': None,
            'portal': portal,
            'modules': SecureModuleImporter,
            }
        return getEngine().getContext(data)

    security.declarePrivate('renderLayoutStructure')
    def renderLayoutStructure(self, layout_structure, datastructure, **kw):
        """Render the layout structure.

        Renders the widgets in their chosen mode.

        After rendering, the structure may be updated because some empty
        widgets may have been removed.
        """
        widget_infos = layout_structure['widgets']
        for row in layout_structure['rows']:
            for cell in row:
                widget = cell['widget']
                mode = cell['widget_mode']
                rendered = widget.render(mode, datastructure,
                                         widget_infos=widget_infos, **kw)
                rendered = rendered.strip()
                cell['widget_rendered'] = rendered
                if widget.hidden_empty and not rendered:
                    cell['widget_mode'] = 'hidden'
        # Eliminate hidden widgets.
        self.removeHiddenWidgets(layout_structure)

    security.declarePrivate('renderLayoutStyle')
    def renderLayoutStyle(self, layout_structure, datastructure, context,
                          **kw):
        """Applies the layout style method to the rendered widgets.

        ``context`` is used to find the layout method.

        Returns the rendered string. The rendered string is computed according
        to the following properties and in decreasing order of precedence:
        "layout_create_method", "layout_edit_method", "layout_view_method"
        and "style_prefix" found in the document layout definitions.
        """
        layout_mode = kw['layout_mode']
        layout_method_property = self.getProperty('layout_%s_method' %
                                                  layout_mode, '')
        if layout_method_property != '':
            layout_method = layout_method_property
        else:
            style_prefix = kw.get('style_prefix')
            if not style_prefix:
                style_prefix = self.style_prefix
            layout_method =  style_prefix + layout_mode
        layout_style = getattr(context, layout_method, None)
        if layout_style is None:
            raise ValueError("No layout method '%s' for layout '%s'" %
                             (layout_method, self.getId()))
        # compute the flexible_widgets list
        flexible_widgets = []
        if layout_mode == 'edit':
            ltool = getToolByName(self, 'portal_layouts')
            layout_global = ltool[self.getId()]
            widget_ids = []
            for widget_id, widget in self.items():
                if not widget.isHidden():
                    widget_ids.append(widget_id)
            flexible_widget_ids = layout_global.getFlexibleWidgetIds()
            flexible_occurences = layout_global.getFlexibleWidgetOccurences()
            flexible_widgets = []
            i = 0
            for wid in flexible_widget_ids:
                max_widget = flexible_occurences[i]
                i += 1
                if max_widget:
                    nb_widget = 0
                    for w in widget_ids:
                        if w.startswith(wid):
                            nb_widget += 1
                    if nb_widget >= int(max_widget):
                        continue

                flexible_widgets.append(layout_global[wid])

        rendered = layout_style(layout=layout_structure,
                                datastructure=datastructure,
                                flexible_widgets=flexible_widgets,
                                **kw)
        return rendered

InitializeClass(Layout)


class CPSLayout(Layout):
    """Persistent Layout."""

    meta_type = "CPS Layout"

    security = ClassSecurityInfo()

    def __init__(self, id, **kw):
        self.id = id
        Layout.__init__(self, **kw)

    security.declarePrivate('addWidget')
    def addWidget(self, id, meta_type, **kw):
        """Add a new widget instance."""
        class_ = widgetRegistry.getClass(meta_type)
        widget = class_(id, **kw)
        return self.addSubObject(widget)

    #
    # ZMI
    #

    def all_meta_types(self):
        # List of meta types contained in Folder, for copy/paste support.
        return [
            {'name': mt,
             'action': '',
             'permission': ManagePortal}
            for mt in widgetRegistry.listWidgetMetaTypes()]

    def filtered_meta_types(self):
        # List of types available in Folder menu.
        return [
            {'name': mt,
             'action': 'manage_addCPSWidgetForm/'+mt.replace(' ', ''),
             'permission': ManagePortal}
            for mt in widgetRegistry.listWidgetMetaTypes()]

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

    security.declareProtected(ManagePortal, 'getUnstrippedWidgetMetaType')
    def getUnstrippedWidgetMetaType(self, smt):
        """Get an unstripped version of a widget meta type."""
        smt = smt.replace(' ', '')
        for mt in widgetRegistry.listWidgetMetaTypes():
            if mt.replace(' ', '') == smt:
                return mt
        raise ValueError(smt)

    security.declareProtected(ManagePortal, 'manage_addCPSWidget')
    def manage_addCPSWidget(self, id, meta_type, REQUEST=None, **kw):
        """Add a widget, called from the ZMI."""
        if REQUEST is not None:
            kw.update(REQUEST.form)
            for key in ('id', 'meta_type'):
                if key in kw:
                    del kw[key]
        widget = self.addWidget(id, meta_type, **kw)
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
        used_widgets = []
        duplicate_widgets = []
        for row in rows:
            nrow += 1
            ncell = 0
            somedel, somesplit = 0, 0
            for cell in row:
                ncell += 1
                widget_id = kw.get('cell_%d_%d' % (nrow, ncell), '')
                if widget_id in used_widgets:
                    duplicate_widgets.append(widget_id)
                else:
                    used_widgets.append(widget_id)
                cell['widget_id'] = widget_id
                if kw.get('check_%d_%d' % (nrow, ncell)):
                    if delcell:
                        cell['del'] = 1
                        somedel = 1
                        if cell['widget_id'] in duplicate_widgets:
                            duplicate_widgets.remove(cell['widget_id'])
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
        if duplicate_widgets:
            message = 'Warning: Duplicate widgets: ' + ', '.join(duplicate_widgets)
        else:
            message = 'Changed.'
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_editLayout'
                                      '?manage_tabs_message='+message)

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
