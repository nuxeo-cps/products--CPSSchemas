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

from zLOG import LOG, DEBUG, PROBLEM
from cgi import escape
from DateTime.DateTime import DateTime
from Globals import InitializeClass
from Acquisition import aq_base, aq_parent, aq_inner
from AccessControl import ClassSecurityInfo
from types import ListType, TupleType
try:
    import PIL.Image
except ImportError:
    pass
from ZPublisher.HTTPRequest import FileUpload
from OFS.Image import cookId, File, Image
from OFS.PropertyManager import PropertyManager
from Products.PythonScripts.standard import structured_text, newline_to_br

from Products.CMFCore.CMFCorePermissions import ManageProperties
from Products.CMFCore.utils import getToolByName

from Products.CPSSchemas.Widget import CPSWidget
from Products.CPSSchemas.Widget import CPSWidgetType
from Products.CPSSchemas.WidgetTypesTool import WidgetTypeRegistry

def _isinstance(ob, cls):
    try:
        return isinstance(ob, cls)
    except TypeError:
        # In python 2.1 isinstance() raises TypeError
        # instead of returning 0 for ExtensionClasses.
        return 0


def renderHtmlTag(tagname, **kw):
    """Render an HTML tag."""
    if kw.get('css_class'):
        kw['class'] = kw['css_class']
        del kw['css_class']
    if kw.has_key('contents'):
        contents = kw['contents']
        del kw['contents']
    else:
        contents = None
    attrs = []
    for key, value in kw.items():
        if value is None:
            value = key
        if value != '':
            attrs.append('%s="%s"' % (key, escape(str(value))))
    res = '<%s %s>' % (tagname, ' '.join(attrs))
    if contents is not None:
        res += contents + '</%s>' % tagname
    return res



##################################################

class CPSHtmlWidget(CPSWidget):
    """Html widget."""
    meta_type = "CPS Html Widget"

    _properties = CPSWidget._properties + (
        {'id': 'html_view', 'type': 'text', 'mode': 'w',
         'label': 'Html for view'},
        {'id': 'html_edit', 'type': 'text', 'mode': 'w',
         'label': 'Html for edit'},
        )
    html_view = ''
    html_edit = ''

    def prepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel."""
        pass

    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel."""
        return 1

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        if mode == 'view':
            return self.html_view
        elif mode == 'edit':
            return self.html_edit
        raise RuntimeError('unknown mode %s' % mode)

InitializeClass(CPSHtmlWidget)


class CPSHtmlWidgetType(CPSWidgetType):
    """Html widget type."""
    meta_type = "CPS Html Widget Type"
    cls = CPSHtmlWidget

InitializeClass(CPSHtmlWidgetType)

##################################################

class CPSMethodWidget(CPSWidget):
    """Method widget."""
    meta_type = "CPS Method Widget"

    _properties = CPSWidget._properties + (
        {'id': 'render_method', 'type': 'text', 'mode': 'w',
         'label': 'the zpt or py script method'},)
    render_method = ''

    def prepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel."""
        pass

    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel."""
        return 1

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        meth = getattr(self, self.render_method, None)
        if meth is None:
            msg = "Unknown Render Method %s for widget type %s. " \
            + "Please set or change the 'render_method' attribute on " \
            + "your widget declaration."
            raise RuntimeError(msg % (self.render_method, self.getId()))
        return meth(mode=mode, datastructure=datastructure)

InitializeClass(CPSMethodWidget)


class CPSMethodWidgetType(CPSWidgetType):
    """Method widget type."""
    meta_type = "CPS Method Widget Type"
    cls = CPSMethodWidget

InitializeClass(CPSMethodWidgetType)

##################################################

class CPSStringWidget(CPSWidget):
    """String widget."""
    meta_type = "CPS String Widget"

    field_types = ('CPS String Field',)
    field_inits = ({'is_indexed': 1,},)

    display_width = 20
    size_max = 0
    _properties = CPSWidget._properties + (
        {'id': 'display_width', 'type': 'int', 'mode': 'w',
         'label': 'Display width'},
        {'id': 'size_max', 'type': 'int', 'mode': 'w',
         'label': 'Maximum input width'},
        )

    def prepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel."""
        datamodel = datastructure.getDataModel()
        datastructure[self.getWidgetId()] = str(datamodel[self.fields[0]])

    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel."""
        widget_id = self.getWidgetId()
        value = datastructure[widget_id]
        err = 0
        try:
            v = str(value).strip()
        except ValueError:
            err = 'cpsschemas_err_string'
        else:
            if self.is_required and not v:
                datastructure[widget_id] = ''
                err = 'cpsschemas_err_required'
            elif self.size_max and len(v) > self.size_max:
                err = 'cpsschemas_err_string_too_long'

        if err:
            datastructure.setError(widget_id, err)
        else:
            datamodel = datastructure.getDataModel()
            datamodel[self.fields[0]] = v

        return not err

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        value = datastructure[self.getWidgetId()]
        if mode == 'view':
            return escape(value)
        elif mode == 'edit':
            kw = {'type': 'text',
                  'name': self.getHtmlWidgetId(),
                  'value': value,
                  'size': self.display_width,
                  }
            if self.size_max:
                kw['maxlength'] = self.size_max
            return renderHtmlTag('input', **kw)
        raise RuntimeError('unknown mode %s' % mode)

InitializeClass(CPSStringWidget)


class CPSStringWidgetType(CPSWidgetType):
    """String widget type."""
    meta_type = "CPS String Widget Type"
    cls = CPSStringWidget

InitializeClass(CPSStringWidgetType)

##################################################

class CPSPasswordWidget(CPSStringWidget):
    """Password widget.

    The password widget displays stars in view mode, and in edit mode
    it always starts with an empty string.

    When validating, it doesn't update data if the user entry is empty.
    """

    meta_type = "CPS Password Widget"

    field_types = ('CPS Password Field',)

    def prepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel."""
        # Never fetch the real password.
        datastructure[self.getWidgetId()] = ''

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        value = datastructure[self.getWidgetId()]
        if mode == 'view':
            return "********"
        elif mode == 'edit':
            kw = {'type': 'password',
                  'name': self.getHtmlWidgetId(),
                  'value': value,
                  'size': self.display_width,
                  }
            if self.size_max:
                kw['maxlength'] = self.size_max
            return renderHtmlTag('input', **kw)
        raise RuntimeError('unknown mode %s' % mode)

    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel."""
        widget_id = self.getWidgetId()
        value = datastructure[widget_id]
        err = 0
        try:
            v = str(value).strip()
        except ValueError:
            err = 'cpsschemas_err_string'
        else:
            # In layout_mode == 'edit', an empty password means
            # to not update it.
            if kw.get('layout_mode') == 'edit':
                required = 0
            else:
                required = self.is_required
            if required and not v:
                datastructure[widget_id] = ''
                err = 'cpsschemas_err_required'
            elif self.size_max and len(v) > self.size_max:
                err = 'cpsschemas_err_string_too_long'

        if err:
            datastructure.setError(widget_id, err)
        else:
            if v:
                # Only update if a new password was set.
                datamodel = datastructure.getDataModel()
                datamodel[self.fields[0]] = v

        return not err

InitializeClass(CPSPasswordWidget)

class CPSPasswordWidgetType(CPSStringWidgetType):
    """Password widget type."""
    meta_type = "CPS Password Widget Type"
    cls = CPSPasswordWidget

InitializeClass(CPSPasswordWidgetType)

##################################################

class CPSCheckBoxWidget(CPSWidget):
    """CheckBox widget."""
    meta_type = "CPS CheckBox Widget"

    field_types = ('CPS Int Field',)

    _properties = CPSWidget._properties + (
        {'id': 'display_true', 'type': 'string', 'mode': 'w',
         'label': 'Display for true'},
        {'id': 'display_false', 'type': 'string', 'mode': 'w',
         'label': 'Display for false'},
        )
    display_true = "Yes"
    display_false = "No"

    def prepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel."""
        datamodel = datastructure.getDataModel()
        datastructure[self.getWidgetId()] = not not datamodel[self.fields[0]]

    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel."""
        value = datastructure[self.getWidgetId()]
        datamodel = datastructure.getDataModel()
        datamodel[self.fields[0]] = not not value
        return 1

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        value = datastructure[self.getWidgetId()]
        if mode == 'view':
            # XXX L10N Should expand view mode to be able to do i18n.
            if value:
                return self.display_true
            else:
                return self.display_false
        elif mode == 'edit':
            html_widget_id = self.getHtmlWidgetId()
            kw = {'type': 'checkbox',
                  'name': html_widget_id,
                  }
            if value:
                kw['checked'] = None
            tag = renderHtmlTag('input', **kw)
            default_tag = renderHtmlTag('input',
                                        type='hidden',
                                        name=html_widget_id+':tokens:default',
                                        value='')
            return default_tag+tag
        raise RuntimeError('unknown mode %s' % mode)

InitializeClass(CPSCheckBoxWidget)


class CPSCheckBoxWidgetType(CPSStringWidgetType):
    """CheckBox widget type."""
    meta_type = "CPS CheckBox Widget Type"
    cls = CPSCheckBoxWidget

InitializeClass(CPSCheckBoxWidgetType)

##################################################
# Warning textarea widget code is back to r1.75
# refactored textarea with position and format is now located in
# ExtendWidgets and named CPSTextWidget

class CPSTextAreaWidget(CPSWidget):
    """TextArea widget."""
    meta_type = "CPS TextArea Widget"

    field_types = ('CPS String Field',)
    field_inits = ({'is_indexed': 1,},)

    width = 40
    height = 5
    render_format = 'pre'
    _properties = CPSWidget._properties + (
        {'id': 'width', 'type': 'int', 'mode': 'w',
         'label': 'Width'},
        {'id': 'height', 'type': 'int', 'mode': 'w',
         'label': 'Height'},
        {'id': 'render_format', 'type': 'selection', 'mode': 'w',
         'select_variable': 'all_render_formats',
         'label': 'Render format'},
        )


    all_render_formats = ['pre', 'stx', 'text']

    def prepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel."""
        datamodel = datastructure.getDataModel()
        datastructure[self.getWidgetId()] = str(datamodel[self.fields[0]])

    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel."""
        widget_id = self.getWidgetId()
        value = datastructure[widget_id]
        try:
            v = str(value).strip()
        except ValueError:
            datastructure.setError(widget_id, "cpsschemas_err_textarea")
            return 0
        if self.is_required and not v:
            datastructure[widget_id] = ''
            datastructure.setError(widget_id, "cpsschemas_err_required")
            return 0
        datamodel = datastructure.getDataModel()
        datamodel[self.fields[0]] = v
        return 1

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        value = datastructure[self.getWidgetId()]
        if mode == 'view':
            render_format = self.render_format
            if render_format == 'pre':
                return '<pre>'+escape(value)+'</pre>'
            elif render_format == 'stx':
                return structured_text(value)
            else: # render_format == 'text'
                return '<div>'+newline_to_br(value)+'</div>'
        elif mode == 'edit':
            return renderHtmlTag('textarea',
                                 name=self.getHtmlWidgetId(),
                                 cols=self.width,
                                 rows=self.height,
                                 contents=value)
        raise RuntimeError('unknown mode %s' % mode)

InitializeClass(CPSTextAreaWidget)


class CPSTextAreaWidgetType(CPSWidgetType):
    """TextArea widget type."""
    meta_type = "CPS TextArea Widget Type"
    cls = CPSTextAreaWidget

InitializeClass(CPSTextAreaWidgetType)

##################################################

class CPSLinesWidget(CPSWidget):
    """Lines widget."""
    meta_type = "CPS Lines Widget"

    field_types = ('CPS String List Field',)
    field_inits = ({'is_indexed': 1,},)

    width = 30
    height = 5

    _properties = CPSWidget._properties + (
        {'id': 'width', 'type': 'int', 'mode': 'w',
         'label': 'Width'},
        {'id': 'height', 'type': 'int', 'mode': 'w',
         'label': 'Height'},
        )


    def prepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel."""
        datamodel = datastructure.getDataModel()
        value = datamodel[self.fields[0]]
        if value == '':
            # Buggy Zope :lines prop may give us '' instead of [] for default.
            value = []
        # XXX make a copy of the list ?
        datastructure[self.getWidgetId()] = value

    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel."""
        widget_id = self.getWidgetId()
        value = datastructure[widget_id]
        v = value # Zope handle :lines automagically
        if self.is_required and (not v or v == ['']):
            # Empty textarea is returned as ['']
            datastructure[widget_id] = ''
            datastructure.setError(widget_id, "cpsschemas_err_required")
            return 0
        datamodel = datastructure.getDataModel()
        datamodel[self.fields[0]] = v
        return 1

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        value = datastructure[self.getWidgetId()]
        if mode == 'view':
            if not value:
                # XXX L10N empty format may be subject to i18n.
                return self.format_empty
            # XXX customize view mode, lots of displays are possible
            return ', '.join([escape(i) for i in value])
        elif mode == 'edit':
            return renderHtmlTag('textarea',
                                 name=self.getHtmlWidgetId()+":lines",
                                 cols=self.width,
                                 rows=self.height,
                                 contents='\n'.join(value))
        raise RuntimeError('unknown mode %s' % mode)

InitializeClass(CPSLinesWidget)


class CPSLinesWidgetType(CPSWidgetType):
    """Lines widget type."""
    meta_type = "CPS Lines Widget Type"
    cls = CPSLinesWidget

InitializeClass(CPSLinesWidgetType)

##################################################

class CPSSelectWidget(CPSWidget):
    """Select widget."""
    meta_type = "CPS Select Widget"

    field_types = ('CPS String Field',)
    field_inits = ({'is_indexed': 1,},)

    vocabulary = ''
    _properties = CPSWidget._properties + (
        {'id': 'vocabulary', 'type': 'string', 'mode': 'w',
         'label': 'Vocabulary'},
        )
    # XXX make a menu for the vocabulary.

    def _getVocabulary(self, datastructure=None):
        """Get the vocabulary object for this widget."""
        vtool = getToolByName(self, 'portal_vocabularies')
        try:
            vocabulary = getattr(vtool, self.vocabulary)
        except AttributeError:
            raise ValueError("Missing vocabulary %s" % self.vocabulary)
        return vocabulary

    def prepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel."""
        datamodel = datastructure.getDataModel()
        datastructure[self.getWidgetId()] = datamodel[self.fields[0]]

    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel."""
        widget_id = self.getWidgetId()
        value = datastructure[widget_id]
        try:
            v = str(value)
        except ValueError:
            datastructure.setError(widget_id, "cpsschemas_err_select")
            return 0
        vocabulary = self._getVocabulary(datastructure)
        if not vocabulary.has_key(value):
            datastructure.setError(widget_id, "cpsschemas_err_select")
            return 0
        datamodel = datastructure.getDataModel()
        datamodel[self.fields[0]] = v
        return 1

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        value = datastructure[self.getWidgetId()]
        vocabulary = self._getVocabulary(datastructure)
        if mode == 'view':
            return escape(vocabulary.get(value, value))
        elif mode == 'edit':
            res = renderHtmlTag('select',
                                name=self.getHtmlWidgetId())
            for k, v in vocabulary.items():
                kw = {'value': k, 'contents': v}
                if value == k:
                    kw['selected'] = None
                res += renderHtmlTag('option', **kw)
            res += '</select>'
            return res
        raise RuntimeError('unknown mode %s' % mode)

InitializeClass(CPSSelectWidget)


class CPSSelectWidgetType(CPSWidgetType):
    """Select widget type."""
    meta_type = "CPS Select Widget Type"
    cls = CPSSelectWidget

InitializeClass(CPSSelectWidgetType)

##################################################

class CPSMultiSelectWidget(CPSWidget):
    """MultiSelect widget."""
    meta_type = "CPS MultiSelect Widget"

    field_types = ('CPS String List Field',)
    field_inits = ({'is_indexed': 1,},)

    _properties = CPSWidget._properties + (
        {'id': 'vocabulary', 'type': 'string', 'mode': 'w',
         'label': 'Vocabulary'},
        {'id': 'size', 'type': 'int', 'mode': 'w',
         'label': 'Size'},
        {'id': 'format_empty', 'type': 'string', 'mode': 'w',
         'label': 'Format for empty list'},
        )
    # XXX make a menu for the vocabulary.
    vocabulary = ''
    size = 0
    format_empty = ''

    def _getVocabulary(self, datastructure=None):
        """Get the vocabulary object for this widget."""
        vtool = getToolByName(self, 'portal_vocabularies')
        try:
            vocabulary = getattr(vtool, self.vocabulary)
        except AttributeError:
            raise ValueError("Missing vocabulary %s" % self.vocabulary)
        return vocabulary

    def prepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel."""
        datamodel = datastructure.getDataModel()
        value = datamodel[self.fields[0]]
        if value == '':
            # Buggy Zope :lines prop may give us '' instead of [] for default.
            value = []
        # XXX make a copy of the list ?
        datastructure[self.getWidgetId()] = value

    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel."""
        widget_id = self.getWidgetId()
        value = datastructure[widget_id]
        if (not _isinstance(value, ListType) and
            not _isinstance(value, TupleType)):
            datastructure.setError(widget_id, "cpsschemas_err_multiselect")
            return 0
        vocabulary = self._getVocabulary(datastructure)
        v = []
        for i in value:
            try:
                i = str(i)
            except ValueError:
                datastructure.setError(widget_id, "cpsschemas_err_multiselect")
                return 0
            if not vocabulary.has_key(i):
                datastructure.setError(widget_id, "cpsschemas_err_multiselect")
                return 0
            v.append(i)
        datamodel = datastructure.getDataModel()
        datamodel[self.fields[0]] = v
        return 1

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        value = datastructure[self.getWidgetId()]
        vocabulary = self._getVocabulary(datastructure)
        if mode == 'view':
            if not value:
                # XXX L10N empty format may be subject to i18n.
                return self.format_empty
            # XXX customize view mode, lots of displays are possible
            return ', '.join([escape(vocabulary.get(i, i)) for i in value])
        elif mode == 'edit':
            html_widget_id = self.getHtmlWidgetId()
            kw = {'name': html_widget_id+':list',
                  'multiple': None,
                  }
            if self.size:
                kw['size'] = self.size
            res = renderHtmlTag('select', **kw)
            for k, v in vocabulary.items():
                kw = {'value': k, 'contents': v}
                if k in value:
                    kw['selected'] = None
                res += renderHtmlTag('option', **kw)
            res += '</select>'
            default_tag = renderHtmlTag('input',
                                        type='hidden',
                                        name=html_widget_id+':tokens:default',
                                        value='')
            return default_tag+res
        raise RuntimeError('unknown mode %s' % mode)

InitializeClass(CPSMultiSelectWidget)


class CPSMultiSelectWidgetType(CPSWidgetType):
    """MultiSelect widget type."""
    meta_type = "CPS MultiSelect Widget Type"
    cls = CPSMultiSelectWidget

InitializeClass(CPSMultiSelectWidgetType)

##################################################

class CPSIntWidget(CPSWidget):
    """Integer widget."""
    meta_type = "CPS Int Widget"

    field_types = ('CPS Int Field',)

    _properties = CPSWidget._properties + (
        {'id': 'is_limited', 'type': 'boolean', 'mode': 'w',
         'label': 'Value must be in range'},
        {'id': 'min_value', 'type': 'float', 'mode': 'w',
         'label': 'Range minimum value'},
        {'id': 'max_value', 'type': 'float', 'mode': 'w',
         'label': 'Range maximum value'},
        {'id': 'thousands_separator', 'type': 'string', 'mode': 'w',
         'label': 'Thousands separator'},
        )

    is_limited = 0
    min_value = 0
    max_value = 0
    thousands_separator = ''

    def prepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel."""
        datamodel = datastructure.getDataModel()
        datastructure[self.getWidgetId()] = str(datamodel[self.fields[0]])

    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel."""
        value = datastructure[self.getWidgetId()]

        #put value back in a python-parsable state as thousands
        #separator might not be std representations understood by python
        if self.thousands_separator:
            value = value.replace(self.thousands_separator,'')

        try:
            v = int(value)
        except (ValueError, TypeError):
            datastructure.setError(self.getWidgetId(),
                                   "cpsschemas_err_int")
            return 0

        if self.is_limited:
            if (v < self.min_value) or (v > self.max_value):
                datastructure.setError(self.getWidgetId(),
                                       "cpsschemas_err_int_range")
                return 0

        datamodel = datastructure.getDataModel()
        datamodel[self.fields[0]] = v
        return 1

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        value = str(datastructure.getDataModel()[self.getWidgetId()])
        #format number according to widget prefs
        if self.thousands_separator:
            thousands = []
            while value:
                thousands.insert(0, value[-3:])
                value = value[:-3]
            value = self.thousands_separator.join(thousands)

        if mode == 'view':
            return escape(value)
        elif mode == 'edit':
            return renderHtmlTag('input',
                                 type='text',
                                 name=self.getHtmlWidgetId(),
                                 value=value)
        raise RuntimeError('unknown mode %s' % mode)

InitializeClass(CPSIntWidget)


class CPSIntWidgetType(CPSWidgetType):
    """Int widget type."""
    meta_type = "CPS Int Widget Type"
    cls = CPSIntWidget

InitializeClass(CPSIntWidgetType)

#######################################################

class CPSLongWidget(CPSWidget):
    """Long Widget with limits"""
    meta_type = "CPS Long Widget"

    field_types = ('CPS Long Field',)

    _properties = CPSWidget._properties + (
        {'id': 'is_limited', 'type': 'boolean', 'mode': 'w',
         'label': 'Value must be in range'},
        {'id': 'min_value', 'type': 'int', 'mode': 'w',
         'label': 'Range minimum value'},
        {'id': 'max_value', 'type': 'int', 'mode': 'w',
         'label': 'Range maximum  value'},
        {'id': 'thousands_separator', 'type': 'string', 'mode': 'w',
         'label': 'Thousands separator'},
        )

    is_limited = 0
    min_value = 0
    max_value = 0
    thousands_separator = ''

    def prepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel."""
        datamodel = datastructure.getDataModel()
        datastructure[self.getWidgetId()] = str(datamodel[self.fields[0]])

    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel."""
        datamodel = datastructure.getDataModel()
        widget_id = self.getWidgetId()
        value = datastructure[widget_id]

        #put value back in a python-parsable state as thousands
        #separator might not be std representations understood by python
        if self.thousands_separator:
            value = value.replace(self.thousands_separator,'')

        if not value and self.is_required:
            datastructure[widget_id] = 0
            datastructure.setError(widget_id, "cpsschemas_err_required")
            return 0
        try:
            v = long(value)
        except (ValueError, TypeError):
            datastructure.setError(widget_id, "cpsschemas_err_int")
            ok = 0
        else:
            if self.is_limited and (v < self.min_value or v > self.max_value):
                datastructure.setError(widget_id,
                                       "cpsschemas_err_long_range")
                ok = 0
            else:
                datamodel[self.fields[0]] = v
                ok = 1
        return ok

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        value = str(datastructure.getDataModel()[self.getWidgetId()])
        #format number according to widget prefs
        if self.thousands_separator:
            thousands = []
            while value:
                thousands.insert(0, value[-3:])
                value = value[:-3]
            value = self.thousands_separator.join(thousands)
        if mode == 'view':
            return escape(value)
        elif mode == 'edit':
            return renderHtmlTag('input',
                                 type='text',
                                 name=self.getHtmlWidgetId(),
                                 value=value)
        raise RuntimeError('unknown mode %s' % mode)

InitializeClass(CPSLongWidget)


class CPSLongWidgetType(CPSWidgetType):
    """Long with limits widget type."""
    meta_type = "CPS Long Widget Type"
    cls = CPSLongWidget

InitializeClass(CPSLongWidgetType)


##################################################

class CPSFloatWidget(CPSWidget):
    """Float number widget."""
    meta_type = "CPS Float Widget"

    field_types = ('CPS Float Field',)

    _properties = CPSWidget._properties + (
        {'id': 'is_limited', 'type': 'boolean', 'mode': 'w',
         'label': 'Value must be in range'},
        {'id': 'min_value', 'type': 'float', 'mode': 'w',
         'label': 'Range minimum value'},
        {'id': 'max_value', 'type': 'float', 'mode': 'w',
         'label': 'Range maximum value'},
        {'id': 'thousands_separator', 'type': 'string', 'mode': 'w',
         'label': 'Thousands separator'},
        {'id': 'decimals_separator', 'type': 'string', 'mode': 'w',
         'label': 'Decimal separator'},
        {'id': 'decimals_number', 'type': 'int', 'mode': 'w',
         'label': 'Number of decimals'},
            )

    is_limited = 0
    min_value = 0.0
    max_value = 0.0
    thousands_separator = ''
    decimals_separator = ','
    decimals_number = 0

    def prepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel."""
        datamodel = datastructure.getDataModel()
        datastructure[self.getWidgetId()] = str(datamodel[self.fields[0]])

    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel."""
        value = datastructure[self.getWidgetId()]

        #put value back in a python-parsable state as decimal/thousands
        #separators might not be std representations understood by python
        if self.thousands_separator:
            value = value.replace(self.thousands_separator,'')
        if self.decimals_separator:
            value = value.replace(self.decimals_separator,'.')

        try:
            v = float(value)
        except (ValueError, TypeError):
            datastructure.setError(self.getWidgetId(),
                                   "cpsschemas_err_float")
            return 0

        if self.is_limited:
            if (v < self.min_value) or (v > self.max_value):
                datastructure.setError(self.getWidgetId(),
                                       "cpsschemas_err_float_range")
                return 0

        datamodel = datastructure.getDataModel()
        datamodel[self.fields[0]] = v
        return 1

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        value = str(datastructure.getDataModel()[self.getWidgetId()])
        #format number according to widget prefs
        if self.decimals_number:
            v = float(value)
            value = ("%0." + str(self.decimals_number) + "f") % v
        if self.thousands_separator:
            intpart, decpart = value.split('.')
            thousands = []
            while intpart:
                thousands.insert(0, intpart[-3:])
                intpart = intpart[:-3]
            value = self.thousands_separator.join(thousands)
            value = ''.join([value, '.', decpart])
        if self.decimals_separator:
            value = value.replace('.', self.decimals_separator)

        if mode == 'view':
            return escape(value)
        elif mode == 'edit':
            return renderHtmlTag('input',
                                 type='text',
                                 name=self.getHtmlWidgetId(),
                                 value=value)
        raise RuntimeError('unknown mode %s' % mode)

InitializeClass(CPSFloatWidget)


class CPSFloatWidgetType(CPSWidgetType):
    """Float widget type."""
    meta_type = "CPS Float Widget Type"
    cls = CPSFloatWidget

InitializeClass(CPSFloatWidgetType)


##################################################
# Warning Date widget code is back to r1.49
# refactored date widget is now located in
# ExtendWidgets and named CPSDateTimeWidget

class CPSDateWidget(CPSWidget):
    """Date widget."""
    meta_type = "CPS Date Widget"

    field_types = ('CPS DateTime Field',)

    _properties = CPSWidget._properties + (
        {'id': 'view_format', 'type': 'string', 'mode': 'w',
         'label': 'View format'},
        {'id': 'view_format_none', 'type': 'string', 'mode': 'w',
         'label': 'View format empty'},
        )
    view_format = "%d/%m/%Y" # XXX unused for now
    view_format_none = "-"

    def prepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel."""
        datamodel = datastructure.getDataModel()
        v = datamodel[self.fields[0]]
        widget_id = self.getWidgetId()
        if v is not None:
            d = str(v.day())
            m = str(v.month())
            y = str(v.year())
        else:
            d = m = y = ''
        datastructure[widget_id+'_d'] = d
        datastructure[widget_id+'_m'] = m
        datastructure[widget_id+'_y'] = y

    def validate(self, datastructure, **kw):
        """Update datamodel from user data in datastructure."""
        datamodel = datastructure.getDataModel()
        field_id = self.fields[0]
        widget_id = self.getWidgetId()

        d = datastructure[widget_id+'_d'].strip()
        m = datastructure[widget_id+'_m'].strip()
        y = datastructure[widget_id+'_y'].strip()

        if not (d+m+y):
            if self.is_required:
                datastructure[widget_id] = ''
                datastructure.setError(widget_id, "cpsschemas_err_required")
                return 0
            else:
                datamodel[field_id] = None
                return 1

        try:
            v = DateTime(int(y), int(m), int(d))
        except (ValueError, TypeError, DateTime.DateTimeError,
                DateTime.SyntaxError, DateTime.DateError):
            datastructure.setError(widget_id, 'cpsschemas_err_date')
            return 0
        else:
            datamodel[field_id] = v
            return 1

    def render(self, mode, datastructure, **kw):
        """Render this widget from the datastructure or datamodel."""
        widget_id = self.getWidgetId()
        d = datastructure[widget_id+'_d']
        m = datastructure[widget_id+'_m']
        y = datastructure[widget_id+'_y']
        if mode == 'view':
            if not (d+m+y):
                return escape(self.view_format_none)
            else:
                # XXX customize format
                return escape(d+'/'+m+'/'+y)
        elif mode == 'edit':
            html_widget_id = self.getHtmlWidgetId()
            dtag = renderHtmlTag('input',
                                 type='text',
                                 name=html_widget_id+'_d',
                                 value=d,
                                 size=2,
                                 maxlength=2)
            mtag = renderHtmlTag('input',
                                 type='text',
                                 name=html_widget_id+'_m',
                                 value=m,
                                 size=2,
                                 maxlength=2)
            ytag = renderHtmlTag('input',
                                 type='text',
                                 name=html_widget_id+'_y',
                                 value=y,
                                 size=6,
                                 maxlength=6)
            # XXX customize format
            return dtag + '/' + mtag + '/' + ytag
        raise RuntimeError('unknown mode %s' % mode)

InitializeClass(CPSDateWidget)


class CPSDateWidgetType(CPSWidgetType):
    """Date widget type."""
    meta_type = "CPS Date Widget Type"
    cls = CPSDateWidget

InitializeClass(CPSDateWidgetType)

##################################################
# Warning File widget code is back to r1.47
# refactored file widget with html preview and text extraction is in
# ExtendWidgets and named CPSAttachedFileWidget

##################################################

class CPSFileWidget(CPSWidget):
    """File widget."""
    meta_type = "CPS File Widget"

    field_types = ('CPS File Field',)

    _properties = CPSWidget._properties + (
        {'id': 'deletable', 'type': 'boolean', 'mode': 'w',
         'label': 'Deletable'},
        {'id': 'size_max', 'type': 'int', 'mode': 'w',
         'label': 'Maximum file size'},
        )
    deletable = 1
    size_max = 4*1024*1024

    def prepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel."""
        datamodel = datastructure.getDataModel()
        widget_id = self.getWidgetId()
        datastructure[widget_id] = datamodel[self.fields[0]]
        # make update from request work
        datastructure[widget_id + '_choice'] = ''


    def validate(self, datastructure, **kw):
        """Update datamodel from user data in datastructure."""
        datamodel = datastructure.getDataModel()
        field_id = self.fields[0]
        widget_id = self.getWidgetId()
        choice = datastructure[widget_id+'_choice']
        err = 0
        if choice == 'keep':
            # XXX check SESSION
            pass
        elif choice == 'delete':
            datamodel[field_id] = None
        else: # 'change'
            file = datastructure[widget_id]
            if not _isinstance(file, FileUpload):
                err = 'cpsschemas_err_file'
            else:
                ms = self.size_max
                if file.read(1) == '':
                    err = 'cpsschemas_err_file_empty'
                elif ms and len(file.read(ms)) == ms:
                    err = 'cpsschemas_err_file_too_big'
                else:
                    file.seek(0)
                    fileid, filetitle = cookId('', '', file)
                    file = File(fileid, filetitle, file)
                    LOG('CPSFileWidget', DEBUG,
                        'validate change set %s' % `file`)
                    datamodel[field_id] = file
        if err:
            datastructure.setError(widget_id, err)
            LOG('CPSFileWidget', DEBUG,
                'error %s on %s' % (err, `file`))
        else:
            self.prepare(datastructure)

        return not err

    def render(self, mode, datastructure, **kw):
        """Render this widget from the datastructure or datamodel."""
        render_method = 'widget_file_render'
        meth = getattr(self, render_method, None)
        if meth is None:
            raise RuntimeError("Unknown Render Method %s for widget type %s"
                               % (render_method, self.getId()))
        value = datastructure[self.getWidgetId()]
        if hasattr(aq_base(value), 'getId'):
            current_name = value.getId()
        else:
            current_name = '-'
        return meth(mode=mode, datastructure=datastructure,
                    current_name=current_name)

InitializeClass(CPSFileWidget)


class CPSFileWidgetType(CPSWidgetType):
    """File widget type."""
    meta_type = "CPS File Widget Type"
    cls = CPSFileWidget

InitializeClass(CPSFileWidgetType)

##################################################

class CPSImageWidget(CPSWidget):
    """Image widget."""
    meta_type = "CPS Image Widget"

    field_types = ('CPS Image Field',)

    _properties = CPSWidget._properties + (
        {'id': 'deletable', 'type': 'boolean', 'mode': 'w',
         'label': 'Deletable'},
        {'id': 'size_max', 'type': 'int', 'mode': 'w',
         'label': 'maximum image size'},
        {'id': 'display_width', 'type': 'int', 'mode': 'w',
         'label': 'Display width'},
        {'id': 'display_height', 'type': 'int', 'mode': 'w',
         'label': 'Display height'},
        {'id': 'allow_resize', 'type': 'boolean', 'mode': 'w',
         'label': 'Enable to resize img to lower size'},
        )

    deletable = 1
    size_max = 2*1024*1024
    display_height = 0
    display_width = 0
    allow_resize = 0

    def prepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel."""
        datamodel = datastructure.getDataModel()
        widget_id = self.getWidgetId()
        datastructure[widget_id] = datamodel[self.fields[0]]
        # make update from request work
        datastructure[widget_id + '_choice'] = ''
        if self.allow_resize:
            datastructure[widget_id + '_resize'] = ''

    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel."""
        datamodel = datastructure.getDataModel()
        field_id = self.fields[0]
        widget_id = self.getWidgetId()
        choice = datastructure[widget_id+'_choice']
        err = 0
        if choice == 'delete':
            datamodel[field_id] = None
        elif choice == 'change' or datastructure.get(widget_id):
            file = datastructure[widget_id]
            if not _isinstance(file, FileUpload):
                err = 'cpsschemas_err_file'
            else:
                ms = self.size_max
                if file.read(1) == '':
                    err = 'cpsschemas_err_file_empty'
                elif ms and len(file.read(ms)) == ms:
                    err = 'cpsschemas_err_file_too_big'
                else:
                    file.seek(0)
                    fileid, filetitle = cookId('', '', file)
                    registry = getToolByName(self, 'mimetypes_registry')
                    mimetype = registry.lookupExtension(filetitle)
                    if (not mimetype or
                        not mimetype.normalized().startswith('image')):
                        err = 'cpsschemas_err_image'
                    else:
                        size = (self.display_width,
                                self.display_height)
                        if self.allow_resize:
                            resize_op = datastructure[widget_id + '_resize']
                            resize = None
                            for s in self.getImgSizes():
                                if s['id'] == resize_op:
                                    resize = s['size']
                            if resize and resize < size:
                                size = resize
                        if size[0] and size[1]:
                            try:
                                img = PIL.Image.open(file)
                                img.thumbnail(size,
                                              resample=PIL.Image.ANTIALIAS)
                                file.seek(0)
                                img.save(file,
                                         format=mimetype.extensions[0])
                            except (NameError, IOError, ValueError):
                                LOG('CPSImageWidget', PROBLEM,
                                    "Failed to resize file %s keep original" \
                                    % filetitle)
                        file = Image(fileid, filetitle, file)
                        LOG('CPSImageWidget', DEBUG,
                            'validate change set %s' % `file`)
                        datamodel[field_id] = file

        if err:
            datastructure.setError(widget_id, err)
            LOG('CPSImageWidget', DEBUG,
                'error %s on %s' % (err, `file`))
        else:
            datastructure[widget_id] = datamodel[self.fields[0]]
            datastructure[widget_id + '_choice'] = ''
            if self.allow_resize:
                datastructure[widget_id + '_resize'] = ''

        return not err


    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        render_method = 'widget_image_render'
        meth = getattr(self, render_method, None)
        if meth is None:
            raise RuntimeError("Unknown Render Method %s for widget type %s"
                               % (render_method, self.getId()))
        value = datastructure[self.getWidgetId()]
        if hasattr(aq_base(value), 'getId'):
            current_name = value.getId()
        else:
            current_name = '-'
        mimetype = None
        registry = getToolByName(self, 'mimetypes_registry')
        mimetype = registry.lookupExtension(current_name)
        return meth(mode=mode, datastructure=datastructure,
                    current_name=current_name, mimetype=mimetype)

InitializeClass(CPSImageWidget)


class CPSImageWidgetType(CPSWidgetType):
    """Image widget type."""
    meta_type = "CPS Image Widget Type"
    cls = CPSImageWidget

    # XXX: TBD

InitializeClass(CPSImageWidgetType)

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

    security.declarePrivate('_getType')
    def _getType(self):
        """Get the type object for this widget."""
        wtool = getToolByName(self, 'portal_widget_types')
        return getattr(wtool, self.widget_type)

    security.declarePrivate('getFieldTypes')
    def getFieldTypes(self):
        return self._getType().field_types

    def prepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel."""
        return self._getType().prepare(self, datastructure)

    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel."""
        return self._getType().validate(self, datastructure)

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        return self._getType().render(self, mode, datastructure)

InitializeClass(CPSCustomizableWidget)


class CPSCustomizableWidgetType(CPSWidgetType):
    """Customizable widget type."""
    meta_type = "CPS Customizable Widget Type"
    cls = CPSCustomizableWidget

    security = ClassSecurityInfo()

    _properties = CPSWidgetType._properties + (
        {'id': 'field_types', 'type': 'lines', 'mode': 'w',
         'label': 'Field types'},
        {'id': 'prepare_validate_method', 'type': 'string', 'mode': 'w',
         'label': 'Prepare & Validate Method'},
        {'id': 'render_method', 'type': 'string', 'mode': 'w',
         'label': 'Render Method'},
        )
    field_types = []
    prepare_validate_method = ''
    render_method = ''
    _class_props = [p['id'] for p in _properties]

    # Make properties editable.

    def manage_propertiesForm(self, REQUEST, *args, **kw):
        """Override to make the properties editable."""
        return PropertyManager.manage_propertiesForm(
            self, self, REQUEST, *args, **kw)

    security.declareProtected(ManageProperties, 'manage_addProperty')
    security.declareProtected(ManageProperties, 'manage_delProperties')

    # API

    security.declarePrivate('makeInstance')
    def makeInstance(self, id, **kw):
        """Create an instance of this widget type."""
        ob = CPSWidgetType.makeInstance(self, id, **kw)
        # Copy user-added properties to the instance.
        for prop in self._properties:
            id = prop['id']
            if id in self._class_props:
                continue
            t = prop['type']
            ob.manage_addProperty(id, '', t)
        return ob

    security.declarePrivate('prepare')
    def prepare(self, widget, datastructure):
        """Prepare datastructure from datamodel."""
        if not self.prepare_validate_method:
            raise RuntimeError("Missing Prepare Method in widget type %s"
                               % self.getId())
        meth = getattr(widget, self.prepare_validate_method, None)
        if meth is None:
            raise RuntimeError("Unknown Prepare Method %s for widget type %s"
                               % (self.prepare_validate_method, self.getId()))
        return meth('prepare', datastructure)

    security.declarePrivate('validate')
    def validate(self, widget, datastructure):
        """Validate datastructure and update datamodel."""
        if not self.prepare_validate_method:
            raise RuntimeError("Missing Validate Method in widget type %s"
                               % self.getId())
        meth = getattr(widget, self.prepare_validate_method, None)
        if meth is None:
            raise RuntimeError("Unknown Validate Method %s for widget type %s"
                               % (self.prepare_validate_method, self.getId()))
        return meth('validate', datastructure)

    security.declarePrivate('render')
    def render(self, widget, mode, datastructure):
        """Render a widget from the datastructure or datamodel."""
        if not self.render_method:
            raise RuntimeError("Missing Render Method in widget type %s"
                               % self.getId())
        meth = getattr(widget, self.render_method, None)
        if meth is None:
            raise RuntimeError("Unknown Render Method %s for widget type %s"
                               % (self.render_method, self.getId()))
        return meth(mode=mode, datastructure=datastructure)

InitializeClass(CPSCustomizableWidgetType)


##################################################

class CPSCompoundWidget(CPSWidget):
    """Widget aggregating several widgets."""
    meta_type = "CPS Compound Widget"

    security = ClassSecurityInfo()

    _properties = (
        CPSWidget._properties[:1] + (
        # Skip fields, which is computed.
        {'id': 'widget_ids', 'type': 'tokens', 'mode': 'w',
         'label': 'Widget ids'},
        {'id': 'widget_type', 'type': 'string', 'mode': 'w',
         'label': 'Widget type'},
        ) + CPSWidget._properties[2:]
        )
    widget_ids = []
    widget_type = ''

    security.declarePrivate('_getRenderMethod')
    def _getRenderMethod(self):
        """Get the render method."""
        wtool = getToolByName(self, 'portal_widget_types')
        wt = getattr(wtool, self.widget_type)
        return wt.getRenderMethod(self)

    security.declarePrivate('getFieldTypes')
    def getFieldTypes(self):
        """Get field types from the underlying widgets."""
        layout = aq_parent(aq_inner(self))
        field_types = []
        for widget_id in self.widget_ids:
            widget = layout[widget_id]
            fts = widget.getFieldTypes()
            field_types.extend(fts)
        return field_types

    security.declarePrivate('getFieldInits')
    def getFieldInits(self):
        """Get field inits from the underlying widgets."""
        layout = aq_parent(aq_inner(self))
        field_inits = []
        for widget_id in self.widget_ids:
            widget = layout[widget_id]
            fts = widget.getFieldTypes()
            fis = widget.getFieldInits() or ()
            if len(fis) != len(fts):
                fis = [{} for ft in fts]
            field_inits.extend(fis)
        return field_inits

    def prepare(self, datastructure, **kw):
        """Prepare the underlying widgets."""
        layout = aq_parent(aq_inner(self))
        for widget_id in self.widget_ids:
            widget = layout[widget_id]
            widget.prepare(datastructure, **kw)

    def validate(self, datastructure, **kw):
        """Validate the underlying widgets."""
        layout = aq_parent(aq_inner(self))
        ok = 1
        for widget_id in self.widget_ids:
            widget = layout[widget_id]
            ok = widget.validate(datastructure, **kw) and ok
        return ok

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        layout = aq_parent(aq_inner(self))
        widget_infos = kw['widget_infos']
        render = self._getRenderMethod()
        cells = []
        for widget_id in self.widget_ids:
            cell = {}
            cell.update(widget_infos[widget_id]) # widget, widget_mode
            widget = layout[widget_id]
            widget_mode = cell['widget_mode']
            rendered = widget.render(widget_mode, datastructure, **kw)
            rendered = rendered.strip()
            cell['widget_rendered'] = rendered
            cells.append(cell)
        return render(mode=mode, datastructure=datastructure,
                      cells=cells)

InitializeClass(CPSCompoundWidget)


class CPSCompoundWidgetType(CPSWidgetType):
    """Compound widget type."""
    meta_type = "CPS Compound Widget Type"
    cls = CPSCompoundWidget

    security = ClassSecurityInfo()

    _properties = CPSWidgetType._properties + (
        {'id': 'render_method', 'type': 'string', 'mode': 'w',
         'label': 'Render Method'},
        )
    render_method = ''

    # API

    security.declarePrivate('getRenderMethod')
    def getRenderMethod(self, widget):
        """Get the render method."""
        if not self.render_method:
            raise RuntimeError("Missing Render Method in widget type %s"
                               % self.getId())
        meth = getattr(widget, self.render_method, None)
        if meth is None:
            raise RuntimeError("Unknown Render Method %s for widget type %s"
                               % (self.render_method, self.getId()))
        return meth

InitializeClass(CPSCompoundWidgetType)


##################################################

#
# Register widget types.
#

WidgetTypeRegistry.register(CPSCustomizableWidgetType, CPSCustomizableWidget)
WidgetTypeRegistry.register(CPSCompoundWidgetType, CPSCompoundWidget)
WidgetTypeRegistry.register(CPSStringWidgetType, CPSStringWidget)
WidgetTypeRegistry.register(CPSPasswordWidgetType, CPSPasswordWidget)
WidgetTypeRegistry.register(CPSCheckBoxWidgetType, CPSCheckBoxWidget)
WidgetTypeRegistry.register(CPSTextAreaWidgetType, CPSTextAreaWidget)
WidgetTypeRegistry.register(CPSLinesWidgetType, CPSLinesWidget)
WidgetTypeRegistry.register(CPSIntWidgetType, CPSIntWidget)
WidgetTypeRegistry.register(CPSLongWidgetType, CPSLongWidget)
WidgetTypeRegistry.register(CPSFloatWidgetType, CPSFloatWidget)
WidgetTypeRegistry.register(CPSDateWidgetType, CPSDateWidget)
WidgetTypeRegistry.register(CPSFileWidgetType, CPSFileWidget)
WidgetTypeRegistry.register(CPSImageWidgetType, CPSImageWidget)
WidgetTypeRegistry.register(CPSHtmlWidgetType, CPSHtmlWidget)
WidgetTypeRegistry.register(CPSMethodWidgetType, CPSMethodWidget)
WidgetTypeRegistry.register(CPSSelectWidgetType, CPSSelectWidget)
WidgetTypeRegistry.register(CPSMultiSelectWidgetType, CPSMultiSelectWidget)
