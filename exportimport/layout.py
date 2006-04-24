# (C) Copyright 2005 Nuxeo SAS <http://nuxeo.com>
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
# 02111-1307, USA.2
#
# $Id$
"""Layout Tool XML Adapter.
"""

from Acquisition import aq_base
from zope.app import zapi
from zope.component import adapts
from zope.interface import implements
import Products
from ZODB.loglevels import BLATHER as VERBOSE
from Products.CMFCore.utils import getToolByName
from Products.GenericSetup.utils import exportObjects
from Products.GenericSetup.utils import importObjects
from Products.GenericSetup.utils import XMLAdapterBase
from Products.GenericSetup.utils import ObjectManagerHelpers
from Products.GenericSetup.utils import PropertyManagerHelpers
from Products.CPSUtil.PropertiesPostProcessor import (
    PostProcessingPropertyManagerHelpers)

from Products.GenericSetup.interfaces import INode
from Products.GenericSetup.interfaces import IBody
from Products.GenericSetup.interfaces import ISetupEnviron

from Products.CPSUtil.interfaces import IForceBodySetupEnviron

from Products.CPSSchemas.interfaces import ILayoutTool
from Products.CPSSchemas.interfaces import ILayout
from Products.CPSSchemas.interfaces import IWidget


_marker = object()

TOOL = 'portal_layouts'
NAME = 'layouts'

def exportLayoutTool(context):
    """Export Layout tool, layouts and widgets as a set of XML files.
    """
    site = context.getSite()
    tool = getToolByName(site, TOOL, None)
    if tool is None:
        logger = context.getLogger(NAME)
        logger.info("Nothing to export.")
        return
    exportObjects(tool, '', context)

def importLayoutTool(context):
    """Import Layout tool, layouts and widgets from XML files.
    """
    site = context.getSite()
    tool = getToolByName(site, TOOL)
    importObjects(tool, '', context)

class LayoutToolXMLAdapter(XMLAdapterBase, ObjectManagerHelpers,
                           PropertyManagerHelpers):
    """XML importer and exporter for Layout tool.
    """

    adapts(ILayoutTool, ISetupEnviron)
    implements(IBody)

    _LOGGER_ID = NAME
    name = NAME

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('object')
        node.appendChild(self._extractProperties())
        node.appendChild(self._extractLayouts())
        self._logger.info("Layout tool exported.")
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        if self.environ.shouldPurge():
            self._purgeProperties()
            self._purgeLayouts()
        self._initProperties(node)
        self._initLayouts(node)
        self._logger.info("Layout tool imported.")

    node = property(_exportNode, _importNode)

    def _extractLayouts(self):
        fragment = self._doc.createDocumentFragment()
        items = self.context.objectItems()
        items.sort()
        for id, ob in items:
            exporter = zapi.queryMultiAdapter((ob, self.environ), INode)
            if not exporter:
                raise ValueError("Layout %s cannot be adapted to INode" % ob)
            child = exporter._getObjectNode('object', False)
            fragment.appendChild(child)
        return fragment

    def _purgeLayouts(self):
        self._purgeObjects()

    def _initLayouts(self, node):
        self._initObjects(node)

class LayoutXMLAdapter(XMLAdapterBase, PostProcessingPropertyManagerHelpers):
    """XML importer and exporter for a layout.
    """

    adapts(ILayout, ISetupEnviron)
    implements(IBody)

    _LOGGER_ID = NAME

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('object')
        node.appendChild(self._extractProperties())
        node.appendChild(self._extractWidgets())
        node.appendChild(self._extractTable())
        self._logger.info("Layout %r exported." % self.context.getId())
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        if self.environ.shouldPurge():
            self._purgeProperties()
            self._purgeWidgets()
            self._purgeTable()
        self._initProperties(node)
        self._initWidgets(node)
        self._initTable(node)
        self._logger.info("Layout %r imported." % self.context.getId())

    node = property(_exportNode, _importNode)

    def _extractWidgets(self):
        layout = self.context
        fragment = self._doc.createDocumentFragment()
        items = layout.items()
        items.sort()
        for widget_id, widget in items:
            exporter = zapi.queryMultiAdapter((widget, self.environ), INode)
            if not exporter:
                raise ValueError("Widget %s cannot be adapted to INode" %
                                 widget)
            child = exporter.node
            fragment.appendChild(child)
        return fragment

    def _purgeWidgets(self):
        layout = self.context
        for id in list(layout.objectIds()):
            layout._delObject(id)

    def _initWidgets(self, node):
        layout = self.context
        for child in node.childNodes:
            if child.nodeName != 'widget':
                continue
            widget_id = str(child.getAttribute('name'))
            meta_type = child.getAttribute('meta_type')
            __traceback_info__ = 'widget: %s' % widget_id

            if child.hasAttribute('remove'):
                if layout.has_key(widget_id):
                    layout.delSubObject(widget_id)
                    msg = "Widget %s removed"
                    self._logger.log(VERBOSE, msg)
                else:
                    msg = "Attempt of removing "
                    "non-existent widget %s" % widget_id
                    self._logger.warning(msg)
                continue

            old_state = None
            if layout.has_key(widget_id) and meta_type:
                widget = layout[widget_id]
                if widget.meta_type != str(meta_type):
                    # Need to transtype the widget
                    old_state = widget.__dict__.copy()
                    layout.delSubObject(widget_id)

            if not layout.has_key(widget_id):
                meta_type = str(meta_type)
                for mt in Products.meta_types:
                    if mt['name'] == meta_type:
                        break
                else:
                    raise ValueError("Unknown meta_type %r" % meta_type)

                klass = mt['instance']
                widget = klass(widget_id)

                widget = layout.addSubObject(widget)
            else:
                widget = layout[widget_id]

            if old_state:
                # Transtyping: copy previous state
                widget.__dict__.update(old_state)

            importer = zapi.queryMultiAdapter((widget, self.environ), INode)
            if not importer:
                raise ValueError("Widget %s cannot be adapted to INode" %
                                 widget)

            importer.node = child # calls _importNode

    def _extractTable(self):
        layout = self.context
        layoutdef = layout.getLayoutDefinition()
        table_node = self._doc.createElement('table')
        for row in layoutdef['rows']:
            row_node = self._doc.createElement('row')
            table_node.appendChild(row_node)
            for cell in row:
                cell_node = self._doc.createElement('cell')
                cell_node.setAttribute('name', cell['widget_id'])
                ncols = cell.get('ncols', 1)
                if ncols != 1:
                    cell_node.setAttribute('ncols', str(ncols))
                row_node.appendChild(cell_node)
        return table_node

    def _purgeTable(self):
        self.context.setLayoutDefinition({'rows': []})

    def _initTable(self, node):
        for table_node in node.childNodes:
            if table_node.nodeName != 'table':
                continue
            # nopurge is this restrictive for backwards compatibility
            # with CPS 3.4.0
            if table_node.getAttribute('purge') == 'False':
                rows = self.context.getLayoutDefinition()['rows']
            else:
                rows = []
            for row_node in table_node.childNodes:
                if row_node.nodeName != 'row':
                    continue
                row = []
                for cell_node in row_node.childNodes:
                    if cell_node.nodeName != 'cell':
                        continue
                    name = str(cell_node.getAttribute('name'))
                    cell = {'widget_id': name}
                    if cell_node.hasAttribute('ncols'):
                        ncols = int(cell_node.getAttribute('ncols'))
                        cell['ncols'] = ncols
                    row.append(cell)
                rows.append(row)
            break
        else: # no <table> node, do nothing
            return
        self.context.setLayoutDefinition({'rows': rows})


class WidgetXMLAdapter(XMLAdapterBase, PostProcessingPropertyManagerHelpers):
    """XML importer and exporter for a widget.
    """

    adapts(IWidget, ISetupEnviron)
    implements(IBody)

    _LOGGER_ID = NAME

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        name = self.context.getWidgetId()
        node = self._getObjectNode('widget')
        node.setAttribute('name', name)
        node.appendChild(self._extractProperties(skip_defaults=True))
        msg = "Widget %r exported." % name
        self._logger.log(VERBOSE, msg)
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        if self.environ.shouldPurge():
            self._purgeProperties()
        self._initProperties(node)
        msg = "Widget %r imported." % self.context.getWidgetId()
        self._logger.log(VERBOSE, msg)

    node = property(_exportNode, _importNode)

    def _exportBody(self):
        """Export the object as a file body.
        """
        # We don't want file body export, just nodes, except when the context
        # requires it
        if not IForceBodySetupEnviron.providedBy(self.environ):
            return
        return XMLAdapterBase._exportBody(self)

    def _importBody(self, node):
        """Import the object from the file body.
        """
        return

    body = property(_exportBody, _importBody)

    # customized from default
    def _purgeProperties(self):
        ob = self.context
        for prop_map in ob._propertyMap():
            mode = prop_map.get('mode', 'wd')
            if 'w' not in mode:
                continue
            prop_id = prop_map['id']
            if 'd' in mode and not prop_id == 'title':
                ob._delProperty(prop_id)
            else:
                # reset to default
                if prop_id in ob.__dict__:
                    delattr(ob, prop_id)

    # customized from default
    def _extractProperties(self, skip_defaults=False):
        ob = self.context
        fragment = self._doc.createDocumentFragment()

        for prop_map in ob._propertyMap():
            prop_id = prop_map['id']
            if prop_id == 'i18n_domain':
                continue

            # Local customization: don't export read-only nodes
            if 'w' not in prop_map.get('mode', 'wd'):
                continue

            prop = ob.getProperty(prop_id)

            # Local customization:
            # don't export nodes with values equal to default
            if skip_defaults:
                cls_prop = getattr(ob.__class__, prop_id, _marker)
                if prop == cls_prop:
                    continue
                if (prop_map['type'] == 'boolean'
                    and bool(prop) == bool(cls_prop)):
                    continue

            node = self._doc.createElement('property')
            node.setAttribute('name', prop_id)

            if isinstance(prop, (tuple, list)):
                for value in prop:
                    child = self._doc.createElement('element')
                    child.setAttribute('value', value)
                    node.appendChild(child)
            else:
                if prop_map.get('type') == 'boolean':
                    prop = str(bool(prop))
                elif not isinstance(prop, basestring):
                    prop = str(prop)
                child = self._doc.createTextNode(prop)
                node.appendChild(child)

            if 'd' in prop_map.get('mode', 'wd') and not prop_id == 'title':
                type = prop_map.get('type', 'string')
                node.setAttribute('type', type)
                select_variable = prop_map.get('select_variable', None)
                if select_variable is not None:
                    node.setAttribute('select_variable', select_variable)

            if hasattr(self, '_i18n_props') and prop_id in self._i18n_props:
                node.setAttribute('i18n:translate', '')

            fragment.appendChild(node)

        return fragment
