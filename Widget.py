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

    def __init__(self, id, **kw):
        self._setId(id)

    security.declarePublic('getWidgetId')
    def getWidgetId(self):
        """Get this widget's id."""
        id = self.getId()
        if hasattr(self, 'getIdUnprefixed'):
            # Inside a FolderWithPrefixedIds.
            return self.getIdUnprefixed(id)
        else:
            # Standalone field.
            return id

    security.declarePublic('getHtmlWidgetId')
    def getHtmlWidgetId(self):
        """Get the html-form version of this widget's id."""
        return widgetname(self.getWidgetId())

    def render(self, mode, datastructure, datamodel):
        """Render this widget in a given mode."""
        raise NotImplementedError

InitializeClass(Widget)


class CPSWidget(Widget):
    """Persistent Widget."""

    meta_type = "CPS Widget"

    security = ClassSecurityInfo()

    def __init__(self, id, **kw):
        Widget.__init__(self, id, **kw)
        self.fields = [id]

    #
    # ZMI
    #

    title = ''
    msgid = ''
    fields = []
    _properties = (
        {'id': 'title', 'type': 'string', 'mode': 'w', 'label': 'Title'},
        {'id': 'msgid', 'type': 'string', 'mode': 'w', 'label': 'Msgid'},
        {'id': 'fields', 'type': 'tokens', 'mode': 'w', 'label': 'Fields'},
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


class CPSWidgetType(SimpleItemWithProperties):
    """Persistent Widget Type."""
    meta_type = "CPS Widget Type"

    security = ClassSecurityInfo()

    cls = None

    def __init__(self, id, **kw):
        self._setId(id)

    security.declarePrivate('makeInstance')
    def makeInstance(self, id, **kw):
        """Create an instance of this widget type."""
        return self.cls(id, **kw)

    #
    # ZMI
    #

    title = ''
    _properties = (
        {'id': 'title', 'type': 'string', 'mode': 'w', 'label': 'Title'},
        )

InitializeClass(CPSWidgetType)
