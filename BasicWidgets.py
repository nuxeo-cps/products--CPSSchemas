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

from Products.CPSDocument.Field import ValidationError
from Products.CPSDocument.Widget import CPSWidget, WidgetRegistry
from Products.CPSDocument.Widget import widgetname


class CPSStringWidget(CPSWidget):
    """String widget."""
    meta_type = "CPS String Widget"

    def prepare(self, datastructure, datamodel):
        """Prepare datastructure from datamodel."""
        datastructure[self.id] = datamodel[self.field]

    def validate(self, datastructure, datamodel):
        """Update datamodel from user data in datastructure."""
        id = self.id
        value = datastructure.get(id, '')
        try:
            v = str(value)
        except ValueError:
            datastructure.setError(id, "Bad str received")
            ok = 0
        else:
            datamodel[self.field] = v
            ok = 1
        return ok

    def render(self, mode, datastructure, datamodel):
        """Render this widget from the datastructure or datamodel."""
        id = self.id
        value = datastructure[id]
        if mode == 'view':
            return escape(value)
        elif mode == 'edit':
            return ('<input type="text" name="%s" value="%s" />'
                    % (escape(widgetname(id)), escape(value)))
        else:
            return '[XXX unknown mode %s]' % mode


class CPSIntWidget(CPSWidget):
    """Integer widget."""
    meta_type = "CPS Int Widget"

    def prepare(self, datastructure, datamodel):
        """Prepare datastructure from datamodel."""
        datastructure[self.id] = str(datamodel[self.field])

    def validate(self, datastructure, datamodel):
        """Update datamodel from user data in datastructure."""
        id = self.id
        value = datastructure.get(id, '')
        try:
            v = int(value)
        except ValueError:
            datastructure.setError(id, "Bad int received")
            ok = 0
        else:
            datamodel[self.field] = v
            ok = 1
        return ok

    def render(self, mode, datastructure, datamodel):
        """Render this widget from the datastructure or datamodel."""
        id = self.id
        value = datastructure[id]
        if mode == 'view':
            return escape(value)
        elif mode == 'edit':
            return ('<input type="text" name="%s" value="%s" />'
                    % (escape(widgetname(id)), escape(value)))
        else:
            return '[XXX unknown mode %s]' % mode


InitializeClass(CPSIntWidget)


# Register widget classes

WidgetRegistry.register(CPSStringWidget)
WidgetRegistry.register(CPSIntWidget)
