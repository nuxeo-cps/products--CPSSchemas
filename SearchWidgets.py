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
from DateTime import DateTime

from Products.CMFCore.utils import getToolByName
from Products.CPSSchemas.Widget import CPSWidget
from Products.CPSSchemas.Widget import widgetRegistry
from Products.CPSSchemas.BasicWidgets import CPSProgrammerCompoundWidget

#
# Search ZCText widget
#
class CPSSearchZCTextWidget(CPSWidget):
    """Search ZCText a enable searching on ZCtext index.

    This widget should be used only on edit mode to buid search form.
    """
    meta_type = 'Search ZCText Widget'
    field_types = ('CPS String Field', 'CPS String Field',
                   'CPS String Field', 'CPS String Field',
                   ) # can handle query up to 4 Zctextindex
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

widgetRegistry.register(CPSSearchZCTextWidget)

#
# Modified widget
#
class CPSSearchModifiedWidget(CPSWidget):
    """Widget to choose last modified time in search form.

    This widget should be used only on edit mode to buid search form.
    """
    meta_type = 'Search Modified Widget'
    field_types = ('CPS String Field',  # the date
                   'CPS String Field',  # the modified-usage
                  )
    times = [0, 1, 30, 91, 182, 365]

    # Associating the widget label with an input area to improve the widget
    # accessibility.
    has_input_area = True

    def prepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel."""
        widget_id = self.getWidgetId()
        datastructure[widget_id] = 0

    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel."""
        widget_id = self.getWidgetId()
        datamodel = datastructure.getDataModel()
        now = DateTime()
        value = escape(datastructure[widget_id])
        try:
            value = int(value)
        except (ValueError, TypeError):
            value = 0
        if value and value in self.times:
            value = now - value
        else:
            value = ''
        datamodel[self.fields[0]] = value
        if value:
            datamodel[self.fields[1]] = 'range:min'
        return 1

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        render_method = 'widget_searchmodified_render'
        value = int(datastructure[self.getWidgetId()])
        meth = getattr(self, render_method, None)
        if meth is None:
            raise RuntimeError("Unknown Render Method %s for widget type %s"
                               % (render_method, self.getId()))
        return meth(mode=mode, value=value)

InitializeClass(CPSSearchModifiedWidget)

widgetRegistry.register(CPSSearchModifiedWidget)

#
# Language widget
#
class CPSSearchLanguageWidget(CPSWidget):
    """Widget to choose a document language in search form.

    This widget should be used only on edit mode to build search forms.
    """
    meta_type = 'Search Language Widget'
    field_types = ('CPS String List Field',)


    def _getLanguageVoc(self):
        """Return the language vocabulary."""
        vocabularies = getToolByName(self, 'portal_vocabularies')
        return vocabularies['language_voc']

    def prepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel."""
        widget_id = self.getWidgetId()
        datastructure[widget_id] = []
        datastructure[widget_id + '_selected'] = 'no'

    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel."""
        widget_id = self.getWidgetId()
        datamodel = datastructure.getDataModel()
        selected = escape(datastructure[widget_id + '_selected'])
        values = datastructure[widget_id]
        if selected != 'yes' or not values:
            return 1
        if isinstance(values, str):
            values = [values]
        vocabulary = self._getLanguageVoc()
        languages = vocabulary.keys()
        v = []
        for value in values:
            if value in languages:
                v.append(value)
        datastructure[widget_id] = v
        datamodel[self.fields[0]] = v
        return 1


    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        render_method = 'widget_searchlanguage_render'
        widget_id = self.getWidgetId()
        value = datastructure[widget_id]
        selected = escape(datastructure[widget_id + '_selected'])
        meth = getattr(self, render_method, None)
        if meth is None:
            raise RuntimeError("Unknown Render Method %s for widget type %s"
                               % (render_method, self.getId()))
        return meth(mode=mode, value=value,
                    selected=selected,
                    vocabulary=self._getLanguageVoc())

InitializeClass(CPSSearchLanguageWidget)

widgetRegistry.register(CPSSearchLanguageWidget)

#
# Sort widget
#
class CPSSearchSortWidget(CPSWidget):
    """Widget to choose a sort mode in a search form.

    This widget should be used only on edit mode to buid search form.
    """
    meta_type = 'Search Sort Widget'
    _properties = CPSWidget._properties + (
        {'id': 'sort_limit', 'type': 'int', 'mode': 'w',
         'label': 'Maximum number of result'},
        )
    field_types = ('CPS String Field',  # sort-on
                   'CPS String Field',  # sort-order
                   'CPS String Field',  # sort-limit
                   )
    sort_limit = 100
    sort_mode_names = ('relevance', 'antechrono', 'chrono',
                       'expires', 'title', 'review_state',
                       'relative_path', 'portal_type')
    sort_modes = {'relevance': ('', ''),
                  'antechrono': ('modified', 'reverse'),
                  'chrono': ('modified', ''),
                  'expires': ('expires', ''),
                  'title': ('Title', ''),
                  'review_state': ('review_state', ''),
                  'portal_type': ('portal_type' , ''),
                  'relative_path': ('relative_path', ''),
                }

    # Associating the widget label with an input area to improve the widget
    # accessibility.
    has_input_area = True

    def prepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel."""
        widget_id = self.getWidgetId()
        datastructure[widget_id] = ''

    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel."""
        widget_id = self.getWidgetId()
        datamodel = datastructure.getDataModel()
        value = escape(datastructure[widget_id])
        if value in self.sort_mode_names:
            sort_on, sort_order = self.sort_modes[value]
            datamodel[self.fields[0]] = sort_on
            if sort_on:
                datamodel[self.fields[1]] = sort_order
                datamodel[self.fields[2]] = self.sort_limit
        return 1

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        render_method = 'widget_searchsort_render'
        value = datastructure[self.getWidgetId()]
        meth = getattr(self, render_method, None)
        if meth is None:
            raise RuntimeError("Unknown Render Method %s for widget type %s"
                               % (render_method, self.getId()))
        return meth(mode=mode, value=value)

InitializeClass(CPSSearchSortWidget)

widgetRegistry.register(CPSSearchSortWidget)

##################################################

class CPSSearchWidget(CPSProgrammerCompoundWidget):
    """Widget for advanced search.
    """
    meta_type = 'Search Widget'
    render_method = 'widget_search_render'
    prepare_validate_method = ''

InitializeClass(CPSSearchWidget)

widgetRegistry.register(CPSSearchWidget)


class CPSSearchLocationWidget(CPSProgrammerCompoundWidget):
    """Widget to display a search location.
    """
    meta_type = 'Search Location Widget'
    render_method = 'widget_searchlocation_render'
    prepare_validate_method = 'widget_searchlocation_prepare_validate'
    field_types = ('CPS String Field',)

InitializeClass(CPSSearchLocationWidget)

widgetRegistry.register(CPSSearchLocationWidget)
