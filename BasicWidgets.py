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
"""BasicWidgets

Definition of standard widget types.
"""

from zLOG import LOG, DEBUG
from cgi import escape
from types import IntType, StringType, UnicodeType
from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo

from Products.CMFCore.utils import getToolByName

from Products.CPSDocument.Field import ValidationError
from Products.CPSDocument.Widget import CPSWidget
from Products.CPSDocument.Widget import CPSWidgetType
from Products.CPSDocument.WidgetsTool import WidgetTypeRegistry


##################################################

class CPSStringWidget(CPSWidget):
    """String widget."""
    meta_type = "CPS String Widget"

    def prepare(self, datastructure, datamodel):
        """Prepare datastructure from datamodel."""
        datastructure[self.getWidgetId()] = datamodel[self.fields[0]]

    def validate(self, datastructure, datamodel):
        """Update datamodel from user data in datastructure."""
        id = self.getWidgetId()
        value = datastructure.get(id, '')
        try:
            v = str(value)
        except ValueError:
            datastructure.setError(id, "Bad str received")
            ok = 0
        else:
            datamodel[self.fields[0]] = v
            ok = 1
        return ok

    def render(self, mode, datastructure, datamodel):
        """Render this widget from the datastructure or datamodel."""
        id = self.getWidgetId()
        value = datastructure[id]
        if mode == 'view':
            return escape(value)
        elif mode == 'edit':
            return ('<input type="text" name="%s" value="%s" />'
                    % (escape(self.getHtmlWidgetId()), escape(value)))
        else:
            return '[XXX unknown mode %s]' % mode

InitializeClass(CPSStringWidget)


class CPSStringWidgetType(CPSWidgetType):
    """String widget type."""
    meta_type = "CPS String Widget Type"
    cls = CPSStringWidget

InitializeClass(CPSStringWidgetType)

##################################################

class CPSIntWidget(CPSWidget):
    """Integer widget."""
    meta_type = "CPS Int Widget"

    def prepare(self, datastructure, datamodel):
        """Prepare datastructure from datamodel."""
        datastructure[self.getWidgetId()] = str(datamodel[self.fields[0]])

    def validate(self, datastructure, datamodel):
        """Update datamodel from user data in datastructure."""
        id = self.getWidgetId()
        value = datastructure.get(id, '')
        try:
            v = int(value)
        except ValueError:
            datastructure.setError(id, "Bad int received")
            ok = 0
        else:
            datamodel[self.fields[0]] = v
            ok = 1
        return ok

    def render(self, mode, datastructure, datamodel):
        """Render this widget from the datastructure or datamodel."""
        id = self.getWidgetId()
        value = datastructure[id]
        if mode == 'view':
            return escape(value)
        elif mode == 'edit':
            return ('<input type="text" name="%s" value="%s" />'
                    % (escape(self.getHtmlWidgetId()), escape(value)))
        else:
            return '[XXX unknown mode %s]' % mode

InitializeClass(CPSIntWidget)


class CPSIntWidgetType(CPSWidgetType):
    """Int widget type."""
    meta_type = "CPS Int Widget Type"
    cls = CPSIntWidget

InitializeClass(CPSIntWidgetType)

##################################################

class CPSCustomizableWidget(CPSWidget):
    """Widget with customizable logic and presentation."""
    meta_type = "CPS Customizable Widget"

    security = ClassSecurityInfo()

    _properties = CPSWidget._properties + (
        {'id': 'widget_type', 'type': 'string', 'mode': 'w',
         'label': 'Widget type'},
        )
    widget_type = ''

    def __init__(self, id, widget_type, **kw):
        self.widget_type = widget_type
        CPSWidget.__init__(self, id, **kw)

    security.declarePrivate('_getType')
    def _getType(self):
        """Get the type object for this widget."""
        wtool = getToolByName(self, 'portal_widgets')
        return getattr(wtool, self.widget_type)

    def prepare(self, datastructure, datamodel):
        """Prepare datastructure from datamodel."""
        return self._getType().prepare(self, datastructure, datamodel)

    def validate(self, datastructure, datamodel):
        """Update datamodel from user data in datastructure."""
        return self._getType().validate(self, datastructure, datamodel)

    def render(self, mode, datastructure, datamodel):
        """Render this widget from the datastructure or datamodel."""
        return self._getType().render(self, mode, datastructure, datamodel)

InitializeClass(CPSCustomizableWidget)


class CPSCustomizableWidgetType(CPSWidgetType):
    """Customizable widget type."""
    meta_type = "CPS Customizable Widget Type"

    security = ClassSecurityInfo()

    _properties = CPSWidgetType._properties + (
        {'id': 'prepare_method', 'type': 'string', 'mode': 'w',
         'label': 'Prepare Method'},
        {'id': 'validate_method', 'type': 'string', 'mode': 'w',
         'label': 'Validate Method'},
        {'id': 'render_method', 'type': 'string', 'mode': 'w',
         'label': 'Render Method'},
        )
    prepare_method = ''
    validate_method = ''
    render_method = ''

    security.declarePrivate('makeInstance')
    def makeInstance(self, id, **kw):
        """Create an instance of this widget type."""
        return CPSCustomizableWidget(id, self.getId(), **kw)

    security.declarePrivate('prepare')
    def prepare(self, widget, datastructure, datamodel):
        """Prepare datastructure from datamodel."""
        if not self.prepare_method:
            raise RuntimeError("Missing Prepare Method in widget type %s"
                               % self.getId())
        meth = getattr(widget, self.prepare_method, None)
        if meth is None:
            raise RuntimeError("Unknown Prepare Method %s for widget type %s"
                               % (self.prepare_method, self.getId()))
        return meth(datastructure, datamodel)

    security.declarePrivate('validate')
    def validate(self, widget, datastructure, datamodel):
        """Update datamodel from user data in datastructure."""
        if not self.validate_method:
            raise RuntimeError("Missing Validate Method in widget type %s"
                               % self.getId())
        meth = getattr(widget, self.validate_method, None)
        if meth is None:
            raise RuntimeError("Unknown Validate Method %s for widget type %s"
                               % (self.validate_method, self.getId()))
        return meth(datastructure, datamodel)

    security.declarePrivate('render')
    def render(self, widget, mode, datastructure, datamodel):
        """Render a widget from the datastructure or datamodel."""
        if not self.render_method:
            raise RuntimeError("Missing Render Method in widget type %s"
                               % self.getId())
        meth = getattr(widget, self.render_method, None)
        if meth is None:
            raise RuntimeError("Unknown Render Method %s for widget type %s"
                               % (self.render_method, self.getId()))
        return meth(mode=mode, datastructure=datastructure,
                    datamodel=datamodel)

InitializeClass(CPSCustomizableWidgetType)

#
# Register widget types.
#

WidgetTypeRegistry.register(CPSCustomizableWidgetType, CPSCustomizableWidget)
WidgetTypeRegistry.register(CPSStringWidgetType, CPSStringWidget)
WidgetTypeRegistry.register(CPSIntWidgetType, CPSIntWidget)
