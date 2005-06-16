# (C) Copyright 2003-2005 Nuxeo SARL <http://nuxeo.com>
# Authors:
# Florent Guillaume <fg@nuxeo.com>
# Encolpe DEGOUTE <edegoute@nuxeo.com>
# M.-A. Darche <madarche@nuxeo.com>
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

Abstract base classes for widgets, graphical representation of data.

Widget is the base widget class
An instance w of it is parametrized, notably by one or several field names.
It can then be rendered by passing it a datastructure.
"""

from zLOG import LOG, DEBUG
from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo

from Products.CMFCore.utils import SimpleItemWithProperties
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import Expression, getEngine
from Products.CMFCore.Expression import SecureModuleImporter

from Products.CPSSchemas.DataModel import WriteAccessError
from Products.CPSSchemas.PropertiesPostProcessor import PropertiesPostProcessor

def widgetname(id):
    """Return the name of the widget as used in HTML forms."""
    return 'widget__' + id


class Widget(PropertiesPostProcessor, SimpleItemWithProperties):
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

    _propertiesBaseClass = SimpleItemWithProperties
    _properties = (
        {'id': 'title', 'type': 'string', 'mode': 'w',
         'label': 'Title'},
        {'id': 'fields', 'type': 'tokens', 'mode': 'w',
         'label': 'Fields'},
        {'id': 'is_required', 'type': 'boolean', 'mode': 'w',
         'label': 'Required widget'},
        {'id': 'label', 'type': 'string', 'mode': 'w',
         'label': 'Label in view layout mode'},
        {'id': 'label_edit', 'type': 'string', 'mode': 'w',
         'label': 'Label in edit layout mode'},
        {'id': 'description', 'type': 'text', 'mode': 'w',
         'label': 'Description'},
        {'id': 'help', 'type': 'text', 'mode': 'w',
         'label': 'Help'},
        {'id': 'is_i18n', 'type': 'boolean', 'mode': 'w',
         'label': 'Label is i18n'},
        # layout mode
        {'id': 'readonly_layout_modes', 'type': 'tokens', 'mode': 'w',
         'label': 'Read-only in layout modes'},
        {'id': 'hidden_layout_modes', 'type': 'tokens', 'mode': 'w',
         'label': 'Hidden in layout modes'},
        {'id': 'hidden_readonly_layout_modes', 'type': 'tokens', 'mode': 'w',
         'label': 'Hidden if readonly in layout modes'},
        {'id': 'hidden_empty', 'type': 'boolean', 'mode': 'w',
         'label': 'Hidden if empty'},
        {'id': 'hidden_if_expr', 'type': 'text', 'mode': 'w',
         'label': "Hidden if (TALES)"},
        {'id': 'widget_mode_expr', 'type': 'text', 'mode': 'w',
         'label': "Widget mode (TALES)"},
        # CSS
        {'id': 'css_class', 'type': 'string', 'mode': 'w',
         'label': 'CSS class for view'},
        {'id': 'css_class_expr', 'type': 'text', 'mode': 'w',
         'label': "CSS class (TALES)"},
        # JavaScript
        {'id': 'javascript_expr', 'type': 'text', 'mode': 'w',
         'label': 'JavaScript (TALES)'},
        )

    fields = []
    is_required = 0
    label = ''
    label_edit = ''
    description = ''
    help = ''
    is_i18n = 0
    css_class = ''
    readonly_layout_modes = []
    hidden_layout_modes = []
    hidden_readonly_layout_modes = []
    hidden_empty = 0
    hidden_if_expr = ''
    widget_mode_expr = ''
    css_class_expr = ''
    javascript_expr = ''

    widget_type = '' # Not a property by default
    field_types = []
    field_inits = [] # default settings for fields created in flexible mode
                     # using the same order as in field_types

    hidden_if_expr_c = None
    widget_mode_expr_c = None
    css_class_expr_c = None
    javascript_expr_c = None

    _properties_post_process_tales = (
        ('hidden_if_expr', 'hidden_if_expr_c'),
        ('widget_mode_expr', 'widget_mode_expr_c'),
        ('css_class_expr', 'css_class_expr_c'),
        ('javascript_expr', 'javascript_expr_c'),
        )

    def __init__(self, id, widgettype, **kw):
        self._setId(id)
        self.widget_type = widgettype
        self.manage_changeProperties(**kw)

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

    #
    # Widget access control
    #
    def _createExpressionContext(self, datamodel, layout_mode):
        """Create an expression context for expression evaluation.

        Used for hidden_if_expr, widget_mode_expr and css_class_expr.
        """
        wftool = getToolByName(self, 'portal_workflow')
        portal = getToolByName(self, 'portal_url').getPortalObject()
        proxy = datamodel._proxy
        if proxy is not None:
            review_state = wftool.getInfoFor(proxy, 'review_state', None)
        else:
            review_state = None
        data = {
            'widget': self,
            'datamodel': datamodel,
            'user': datamodel._acl_cache_user,
            'nothing': None,
            'context': datamodel._context,
            'portal': portal,
            'modules': SecureModuleImporter,
            'proxy': proxy,
            'portal_workflow': wftool,
            'review_state': review_state,
            'layout_mode': layout_mode,
            }
        return getEngine().getContext(data)

    security.declarePrivate('_isReadOnly')
    def _isReadOnly(self, datamodel):
        """Return true if the widget is read-only.

        This checks the managed fields for write access.
        """
        try:
            for field_id in self.fields:
                datamodel.checkWriteAccess(field_id)
        except WriteAccessError:
            return 1
        else:
            return 0

    security.declarePrivate('isReadOnly')
    def isReadOnly(self, datamodel, layout_mode):
        """Return true if the widget is read-only in the layout_mode."""
        if layout_mode in self.readonly_layout_modes:
            return 1
        return self._isReadOnly(datamodel)

    security.declarePrivate('getModeFromLayoutMode')
    def getModeFromLayoutMode(self, layout_mode, datamodel):
        """Get the mode for this widget."""
        if layout_mode in self.hidden_layout_modes:
            return 'hidden'
        if self.hidden_if_expr_c:
            # Creating the context used to evaluate the TALES expression
            expr_context = self._createExpressionContext(datamodel, layout_mode)
            if self.hidden_if_expr_c(expr_context):
                return 'hidden'
        if self.widget_mode_expr_c:
            # Creating the context used to evaluate the TALES expression
            expr_context = self._createExpressionContext(datamodel, layout_mode)
            mode = self.widget_mode_expr_c(expr_context)
            if mode:
                return mode
        readonly = None
        if layout_mode in self.hidden_readonly_layout_modes:
            readonly = self.isReadOnly(datamodel, layout_mode)
            if readonly:
                return 'hidden'
        if layout_mode.startswith('view'):
            return 'view'
        if (layout_mode.startswith('edit') or
            layout_mode.startswith('create') or
            layout_mode.startswith('search')):
            if readonly is None:
                readonly = self.isReadOnly(datamodel, layout_mode)
            if readonly:
                return 'view'
            else:
                return 'edit'
        raise ValueError("Unknown layout mode '%s'" % layout_mode)

    security.declarePrivate('getCssClass')
    def getCssClass(self, layout_mode, datamodel):
        """Get the css class for this widget.

        The returned css class is to be used in the HTML rendering of a widget.

        A widget handles two properties, named css_class and
        css_class_expr. css_class is simply the name of the class to
        use. css_class_expr is an expression that can be used to generate a
        dynamic css class. If css_class_expr is used, css_class property is
        ignored.

        If none of these properties is specified, or if the expression returns
        None, no class is returned.

        In create or edit mode, if the css_class property is used, the class
        returned is the class name suffixed by 'Edit'.
        This is because in create and edit mode one usually doesn't want the
        widgets to have the same appearance that they have in view
        mode. Actually in create and edit mode one prefers to have all the
        widgets with the same neutral presentation.

        The css_class_expr namespace gives access to the layout mode, so this
        default behaviour does not apply to computed css classes.
        """
        if self.css_class_expr_c:
            # Create the context used to evaluate the TALES expression
            expr_context = self._createExpressionContext(datamodel, layout_mode)
            css_class_computed = self.css_class_expr_c(expr_context)
            if css_class_computed:
                css_class = css_class_computed
            else:
                css_class = ''
        else:
            css_class = self.css_class
            # XXX AT: do not append 'Edit' if css class is computed because
            # user has access to the layout mode in the namespace, and is able
            # to control this behaviour more precisely
            if css_class and layout_mode in ('create', 'edit'):
                css_class = css_class + 'Edit'

        return css_class

    security.declarePrivate('getJavascriptCode')
    def getJavaScriptCode(self, layout_mode, datamodel):
        """Get the JavaScript code to display in the widget rendering.

        If the javascript_expr property is not set, return an empty string.
        """
        js_code = ''
        if self.javascript_expr_c:
            # Create the context used to evaluate the TALES expression
            expr_context = self._createExpressionContext(datamodel, layout_mode)
            js_code_computed = self.javascript_expr_c(expr_context)
            if js_code_computed:
                js_code = js_code_computed
        return js_code


    #
    # May be overloaded.
    #
    security.declarePrivate('getFieldTypes')
    def getFieldTypes(self):
        """Get the types of the fields for this widget.

        Used by dynamic widget creation to create its needed fields.
        """
        return self.field_types

    security.declarePrivate('getFieldInits')
    def getFieldInits(self):
        nb_field = len(self.getFieldTypes())
        if len(self.field_inits) == nb_field:
            return self.field_inits
        # return empty inits
        return None

    #
    # To be implemented by widget concrete classes.
    #
    def prepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel."""
        raise NotImplementedError

    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel."""
        raise NotImplementedError

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        raise NotImplementedError

InitializeClass(Widget)


class CPSWidget(Widget):
    """Persistent Widget."""

    meta_type = "CPS Widget"

    security = ClassSecurityInfo()

    def __init__(self, id, widgettype, **kw):
        #self.fields = [id]
        Widget.__init__(self, id, widgettype, **kw)

    security.declarePrivate('isHidden')
    def isHidden(self):
        """Check if the widget is hidden

        Hidden widget are used as template to create flexible widgets.

        Returns true if the widget is hidden.
        """
        return (self.fields and self.fields[0] == '?')

    security.declarePrivate('hide')
    def hide(self):
        """Hide the widget.

        A hidden widget is not displayed or validated, it is used in flexible
        mode to produce new widgets.
        """
        self.fields = ['?']

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

    def __init__(self, id):
        self._setId(id)

    security.declarePrivate('makeInstance')
    def makeInstance(self, id, **kw):
        """Create an instance of this widget type."""
        return self.cls(id, self.getId(), **kw)

    #
    # ZMI
    #
    title = ''
    _properties = (
        {'id': 'title', 'type': 'string', 'mode': 'w', 'label': 'Title'},
        )

InitializeClass(CPSWidgetType)
