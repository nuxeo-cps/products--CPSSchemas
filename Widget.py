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
"""Widget

Base classes for widgets, graphical representation of data.

Widget is the base widget class
An instance w of it is parametrized, notably by one or several field names.
It can then be rendered by passing it a datastructure.
"""

from zLOG import LOG, DEBUG
from copy import deepcopy
from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo
from Persistence import Persistent

from OFS.Folder import Folder

from Products.CMFCore.CMFCorePermissions import View, ModifyPortalContent
from Products.CMFCore.CMFCorePermissions import ManagePortal
from Products.CMFCore.utils import SimpleItemWithProperties


def widgetname(id):
    """Return the name of the widget as used in HTML forms."""
    return 'widget__'+id


class Widget(SimpleItemWithProperties):
    """Basic Widget Class.

    A widget is used as a component of a layout, to display or receive
    input for some data.

    A widget is responsible for turning one or several basic data types
    from a datastructure into a visible representation, and doing the
    opposite when input is received. When rendering, the widget has
    access to the datastructure to render but also to the datamodel to
    be able to render available choices in a vocabulary for instance.

    A widget can be "rendered" in several modes, the basic ones are:

    - view: the standard rendering view,

    - edit: the standard editing view,

    - modify: a pseudo-view that parses user input into the
      datastructure.

    A widget may have some additional parameters that describe certain
    aspects of its graphical representation or behavior.
    """

    security = ClassSecurityInfo()

    def __init__(self, **kw):
        pass

    def render(self, mode, datastructure, datamodel):
        """Render this widget in a given mode."""
        raise NotImplementedError

InitializeClass(Widget)


class CPSWidget(Widget):
    """Persistent Widget."""

    meta_type = "CPS Widget"

    security = ClassSecurityInfo()

    def __init__(self, id, **kw):
        Widget.__init__(self, **kw)
        self.id = id
        if self.hasProperty('field'):
            self.field = id

    #
    # ZMI
    #

    title = ''
    msgid = ''
    field = ''
    _properties = (
        {'id': 'title', 'type': 'string', 'mode': 'w', 'label': 'Title'},
        {'id': 'msgid', 'type': 'string', 'mode': 'w', 'label': 'Msgid'},
        {'id': 'field', 'type': 'string', 'mode': 'w', 'label': 'Field'},
        )

InitializeClass(CPSWidget)


addCPSWidgetForm = DTMLFile('zmi/widget_addform', globals())

def addCPSWidget(container, id, REQUEST=None):
    """Add a CPS Widget."""
    ob = CPSWidget(id)
    container._setObject(id, ob)
    ob = container._getOb(id)
    if REQUEST is not None:
        REQUEST.RESPONSE.redirect(ob.absolute_url() + "/manage_main")


class WidgetRegistry:
    """Registry of the available widget types."""

    def __init__(self):
        self._widget_types = []
        self._widget_classes = {}

    def register(self, cls):
        """Register a class for a widget."""
        widget_type = cls.meta_type
        self._widget_types.append(widget_type)
        self._widget_classes[widget_type] = cls

    def listWidgetTypes(self):
        """Return the list of widget types."""
        return self._widget_types[:]

    def makeWidget(self, widget_type, id, **kw):
        """Factory to make a widget of the given type."""
        return self._widget_classes[widget_type](id, **kw)

# Singleton
WidgetRegistry = WidgetRegistry()
