# (C) Copyright 2005 Nuxeo SARL <http://nuxeo.com>
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
"""Search Widgets.

Widget used to build search forms.
"""

from zLOG import LOG, DEBUG, TRACE
from cgi import escape
from Globals import InitializeClass

from Products.CMFCore.utils import getToolByName
from Products.CPSSchemas.WidgetTypesTool import WidgetTypeRegistry
from Products.CPSSchemas.Widget import CPSWidgetType, CPSWidget


#
# Search ZCText widget
#
class CPSSearchZCTextWidget(CPSWidget):
    """Search ZCText a enable searching on ZCtext index.

    This widget should be used only on edit mode to buid search form.
    """
    meta_type = "CPS Search ZCText Widget"
    _properties = CPSWidget._properties
    field_types = ('CPS String Field','CPS String Field',
                   'CPS String Field','CPS String Field',
                   )                    # can handle query up to 4 Zctextindex
    operators = ('and', 'exact', 'or', 'not')

    def prepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel."""
        wid = self.getWidgetId()
        for operator in self.operators:
            key = wid + '_' + operator
            key_field = key + '_field'
            if not datastructure.has_key(key):
                datastructure[key] = ''
                datastructure[key_field] = self.fields[0]

    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel."""
        # convert input into zctextindex query
        widget_id = self.getWidgetId()
        datamodel = datastructure.getDataModel()
        fields = {}
        for operator in self.operators:
            value = escape(datastructure[widget_id + '_' + operator])
            field = escape(
                datastructure[widget_id + '_' + operator + '_field'])
            if value:
                words = value.split()
                if operator == 'and':
                    value = ' AND '.join(words)
                    pass
                elif operator == 'exact':
                    value = '"' + value + '"'
                elif operator == 'not':
                    value = ' AND '.join(['NOT '+word for word in words])
                elif operator == 'or':
                    if len(words) > 1:
                        value = '(' + ' OR '.join(words) + ')'
            value = value.strip()
            if not value:
                continue
            if not fields.has_key(field):
                fields[field] = [value]
            else:
                fields[field].append(value)

        for field in fields:
            if fields[field] and field in self.fields:
                datamodel[field] = ' AND '.join(fields[field]).strip()
        return 1

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        render_method = 'widget_searchzctext_render'
        meth = getattr(self, render_method, None)
        if meth is None:
            raise RuntimeError("Unknown Render Method %s for widget type %s"
                               % (render_method, self.getId()))
        return meth(mode=mode, datastructure=datastructure)

InitializeClass(CPSSearchZCTextWidget)


class CPSSearchZCTextWidgetType(CPSWidgetType):
    """Widget Type."""
    meta_type = "CPS Search ZCText Widget Type"
    cls = CPSSearchZCTextWidget

InitializeClass(CPSSearchZCTextWidgetType)



##################################################

WidgetTypeRegistry.register(CPSSearchZCTextWidgetType,
                            CPSSearchZCTextWidget)
