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
from DateTime.DateTime import DateTime
from Globals import InitializeClass
from Acquisition import aq_base
from AccessControl import ClassSecurityInfo
from types import StringType, ListType

from ZPublisher.HTTPRequest import FileUpload
from OFS.Image import cookId, File, Image
from OFS.PropertyManager import PropertyManager
from Products.PythonScripts.standard import structured_text

from Products.CMFCore.CMFCorePermissions import ManageProperties
from Products.CMFCore.utils import getToolByName

from Products.CPSDocument.Widget import CPSWidget
from Products.CPSDocument.Widget import CPSWidgetType
from Products.CPSDocument.WidgetsTool import WidgetTypeRegistry

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

    field_types = ()

    _properties = CPSWidget._properties + (
        {'id': 'html_view', 'type': 'text', 'mode': 'w',
         'label': 'Html for view'},
        {'id': 'html_edit', 'type': 'text', 'mode': 'w',
         'label': 'Html for edit'},
        )
    html_view = ''
    html_edit = ''

    def prepare(self, datastructure, datamodel):
        """Prepare datastructure from datamodel."""
        pass

    def validate(self, datastructure, datamodel):
        """Update datamodel from user data in datastructure."""
        return 1

    def render(self, mode, datastructure, datamodel):
        """Render this widget from the datastructure or datamodel."""
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

class CPSStringWidget(CPSWidget):
    """String widget."""
    meta_type = "CPS String Widget"

    field_types = ('CPS String Field',)

    allow_empty = 1
    display_width = 20
    display_maxwidth = 0
    _properties = CPSWidget._properties + (
        {'id': 'allow_empty', 'type': 'boolean', 'mode': 'w',
         'label': 'Allow empty'},
        {'id': 'display_width', 'type': 'int', 'mode': 'w',
         'label': 'Display width'},
        {'id': 'display_maxwidth', 'type': 'int', 'mode': 'w',
         'label': 'Maximum input'},
        )

    def prepare(self, datastructure, datamodel):
        """Prepare datastructure from datamodel."""
        datastructure[self.getWidgetId()] = datamodel[self.fields[0]]

    def validate(self, datastructure, datamodel):
        """Update datamodel from user data in datastructure."""
        widget_id = self.getWidgetId()
        value = datastructure[widget_id]
        try:
            v = str(value)
        except ValueError:
            datastructure.setError(widget_id, "cpsdoc_err_string")
            return 0
        if not self.allow_empty:
            v = v.strip()
            if not v:
                datastructure[widget_id] = v
                datastructure.setError(widget_id, "cpsdoc_err_empty")
                return 0
        datamodel[self.fields[0]] = v
        return 1

    def render(self, mode, datastructure, datamodel):
        """Render this widget from the datastructure or datamodel."""
        value = datastructure[self.getWidgetId()]
        if mode == 'view':
            return escape(value)
        elif mode == 'edit':
            kw = {'type': 'text',
                  'name': self.getHtmlWidgetId(),
                  'value': value,
                  'size': self.display_width,
                  }
            if self.display_maxwidth:
                kw['maxlength'] = self.display_maxwidth
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
    """Password widget."""
    meta_type = "CPS Password Widget"

    field_types = ('CPS Password Field',)

    def render(self, mode, datastructure, datamodel):
        """Render this widget from the datastructure or datamodel."""
        value = datastructure[self.getWidgetId()]
        if mode == 'view':
            return "********"
        elif mode == 'edit':
            kw = {'type': 'password',
                  'name': self.getHtmlWidgetId(),
                  'value': value,
                  'size': self.display_width,
                  }
            if self.display_maxwidth:
                kw['maxlength'] = self.display_maxwidth
            return renderHtmlTag('input', **kw)
        raise RuntimeError('unknown mode %s' % mode)

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

    def prepare(self, datastructure, datamodel):
        """Prepare datastructure from datamodel."""
        datastructure[self.getWidgetId()] = not not datamodel[self.fields[0]]

    def validate(self, datastructure, datamodel):
        """Update datamodel from user data in datastructure."""
        value = datastructure[self.getWidgetId()]
        datamodel[self.fields[0]] = not not value
        return 1

    def render(self, mode, datastructure, datamodel):
        """Render this widget from the datastructure or datamodel."""
        value = datastructure[self.getWidgetId()]
        if mode == 'view':
            # XXX L10N Should expand view mode to be able to do i18n.
            if value:
                return self.display_true
            else:
                return self.display_false
        elif mode == 'edit':
            widget_id = self.getHtmlWidgetId()
            kw = {'type': 'checkbox',
                  'name': widget_id,
                  }
            if value:
                kw['checked'] = None
            tag = renderHtmlTag('input', **kw)
            default_tag = renderHtmlTag('input',
                                        type='hidden',
                                        name=widget_id+':tokens:default',
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

class CPSTextAreaWidget(CPSWidget):
    """TextArea widget."""
    meta_type = "CPS TextArea Widget"

    field_types = ('CPS String Field',)

    allow_empty = 1
    width = 40
    height = 5
    render_mode = 'pre'
    _properties = CPSWidget._properties + (
        {'id': 'allow_empty', 'type': 'boolean', 'mode': 'w',
         'label': 'Allow empty'},
        {'id': 'width', 'type': 'int', 'mode': 'w',
         'label': 'Width'},
        {'id': 'height', 'type': 'int', 'mode': 'w',
         'label': 'Height'},
        {'id': 'render_mode', 'type': 'selection', 'mode': 'w',
         'select_variable': 'all_render_modes',
         'label': 'Render mode'},
        )


    all_render_modes = ['pre', 'stx', 'text']

    def prepare(self, datastructure, datamodel):
        """Prepare datastructure from datamodel."""
        datastructure[self.getWidgetId()] = datamodel[self.fields[0]]

    def validate(self, datastructure, datamodel):
        """Update datamodel from user data in datastructure."""
        widget_id = self.getWidgetId()
        value = datastructure[widget_id]
        try:
            v = str(value)
        except ValueError:
            datastructure.setError(widget_id, "cpsdoc_err_textarea")
            return 0
        if not self.allow_empty:
            v = v.strip()
            if not v:
                datastructure[widget_id] = v
                datastructure.setError(widget_id, "cpsdoc_err_empty")
                return 0
        datamodel[self.fields[0]] = v
        return 1

    def render(self, mode, datastructure, datamodel):
        """Render this widget from the datastructure or datamodel."""
        value = datastructure[self.getWidgetId()]
        if mode == 'view':
            render_mode = self.render_mode
            if render_mode == 'pre':
                return '<pre>'+escape(value)+'</pre>'
            elif render_mode == 'stx':
                return structured_text(value)
            else:
                return escape(value)
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

class CPSSelectWidget(CPSWidget):
    """Select widget."""
    meta_type = "CPS Select Widget"

    field_types = ('CPS String Field',)

    vocabulary = ''
    _properties = CPSWidget._properties + (
        {'id': 'vocabulary', 'type': 'string', 'mode': 'w',
         'label': 'Vocabulary'},
        )
    # XXX make a menu for the vocabulary.

    def _getVocabulary(self):
        """Get the vocabulary object for this widget."""
        vtool = getToolByName(self, 'portal_vocabularies')
        try:
            vocabulary = getattr(vtool, self.vocabulary)
        except AttributeError:
            raise ValueError("Missing vocabulary %s" % self.vocabulary)
        return vocabulary

    def prepare(self, datastructure, datamodel):
        """Prepare datastructure from datamodel."""
        datastructure[self.getWidgetId()] = datamodel[self.fields[0]]

    def validate(self, datastructure, datamodel):
        """Update datamodel from user data in datastructure."""
        widget_id = self.getWidgetId()
        value = datastructure[widget_id]
        try:
            v = str(value)
        except ValueError:
            datastructure.setError(widget_id, "cpsdoc_err_select")
            return 0
        vocabulary = self._getVocabulary()
        if not vocabulary.has_key(value):
            datastructure.setError(widget_id, "cpsdoc_err_select")
            return 0
        datamodel[self.fields[0]] = v
        return 1

    def render(self, mode, datastructure, datamodel):
        """Render this widget from the datastructure or datamodel."""
        value = datastructure[self.getWidgetId()]
        vocabulary = self._getVocabulary()
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

class CPSIntWidget(CPSWidget):
    """Integer widget."""
    meta_type = "CPS Int Widget"

    field_types = ('CPS Int Field',)

    def prepare(self, datastructure, datamodel):
        """Prepare datastructure from datamodel."""
        datastructure[self.getWidgetId()] = str(datamodel[self.fields[0]])

    def validate(self, datastructure, datamodel):
        """Update datamodel from user data in datastructure."""
        value = datastructure[self.getWidgetId()]
        try:
            v = int(value)
        except (ValueError, TypeError):
            datastructure.setError(self.getWidgetId(),
                                   "cpsdoc_err_int")
            ok = 0
        else:
            datamodel[self.fields[0]] = v
            ok = 1
        return ok

    def render(self, mode, datastructure, datamodel):
        """Render this widget from the datastructure or datamodel."""
        value = datastructure[self.getWidgetId()]
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

    security.declarePrivate('getFieldTypes')
    def getFieldTypes(self):
        return self._getType().field_types

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
        ob = CPSCustomizableWidget(id, self.getId(), **kw)
        # Copy user-added properties to the instance.
        for prop in self._properties:
            id = prop['id']
            if id in self._class_props:
                continue
            t = prop['type']
            ob.manage_addProperty(id, '', t)
        return ob

    security.declarePrivate('prepare')
    def prepare(self, widget, datastructure, datamodel):
        """Prepare datastructure from datamodel."""
        if not self.prepare_validate_method:
            raise RuntimeError("Missing Prepare Method in widget type %s"
                               % self.getId())
        meth = getattr(widget, self.prepare_validate_method, None)
        if meth is None:
            raise RuntimeError("Unknown Prepare Method %s for widget type %s"
                               % (self.prepare_validate_method, self.getId()))
        return meth('prepare', datastructure, datamodel)

    security.declarePrivate('validate')
    def validate(self, widget, datastructure, datamodel):
        """Update datamodel from user data in datastructure."""
        if not self.prepare_validate_method:
            raise RuntimeError("Missing Validate Method in widget type %s"
                               % self.getId())
        meth = getattr(widget, self.prepare_validate_method, None)
        if meth is None:
            raise RuntimeError("Unknown Validate Method %s for widget type %s"
                               % (self.prepare_validate_method, self.getId()))
        return meth('validate', datastructure, datamodel)

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

##################################################

class CPSDateWidget(CPSWidget):
    """Date widget."""
    meta_type = "CPS Date Widget"

    field_types = ('CPS DateTime Field',)

    _properties = CPSWidget._properties + (
        {'id': 'allow_none', 'type': 'boolean', 'mode': 'w',
         'label': 'Allow empty date'},
        {'id': 'view_format', 'type': 'string', 'mode': 'w',
         'label': 'View format'},
        {'id': 'view_format_none', 'type': 'string', 'mode': 'w',
         'label': 'View format empty'},
        )
    allow_none = 0
    view_format = "%d/%m/%Y" # XXX unused for now
    view_format_none = "-"

    def prepare(self, datastructure, datamodel):
        """Prepare datastructure from datamodel."""
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

    def validate(self, datastructure, datamodel):
        """Update datamodel from user data in datastructure."""
        field_id = self.fields[0]
        widget_id = self.getWidgetId()

        d = datastructure[widget_id+'_d'].strip()
        m = datastructure[widget_id+'_m'].strip()
        y = datastructure[widget_id+'_y'].strip()

        if self.allow_none and not (d+m+y):
            datamodel[field_id] = None
            return 1

        try:
            v = DateTime(int(y), int(m), int(d))
        except (ValueError, TypeError, DateTime.DateTimeError,
                DateTime.SyntaxError, DateTime.DateError):
            datastructure.setError(widget_id, 'cpsdoc_err_date')
            return 0
        else:
            datamodel[field_id] = v
            return 1

    def render(self, mode, datastructure, datamodel):
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

class CPSFileWidget(CPSWidget):
    """File widget."""
    meta_type = "CPS File Widget"

    field_types = ('CPS File Field',)

    _properties = CPSWidget._properties + (
        {'id': 'deletable', 'type': 'boolean', 'mode': 'w',
         'label': 'Deletable'},
        )
    deletable = 1

    def prepare(self, datastructure, datamodel):
        """Prepare datastructure from datamodel."""
        widget_id = self.getWidgetId()
        datastructure[widget_id] = datamodel[self.fields[0]]
        datastructure[widget_id+'_choice'] = '' # make update from request work

    def validate(self, datastructure, datamodel):
        """Update datamodel from user data in datastructure."""
        field_id = self.fields[0]
        widget_id = self.getWidgetId()
        choice = datastructure[widget_id+'_choice']
        if choice == 'keep':
            # XXX check SESSION
            ok = 1
        elif choice == 'delete':
            datamodel[field_id] = None
            ok = 1
        else: # 'change'
            file = datastructure[widget_id]
            if _isinstance(file, FileUpload):
                fileid, filetitle = cookId('', '', file)
                file = File(fileid, filetitle, file)
                LOG('CPSFileWidget', DEBUG, 'validate change set %s' % `file`)
                datamodel[field_id] = file
                ok = 1
            else:
                LOG('CPSFileWidget', DEBUG, 'unvalidate change set %s' % `file`)
                datastructure.setError(widget_id, 'cpsdoc_err_file')
                ok = 0
        if ok:
            self.prepare(datastructure, datamodel)
        return ok

    def render(self, mode, datastructure, datamodel):
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
                    datamodel=datamodel, current_name=current_name)

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
        {'id': 'maxsize', 'type': 'int', 'mode': 'w',
         'label': 'maximum image size'},
        {'id': 'display_width', 'type': 'int', 'mode': 'w',
         'label': 'Display width'},
        {'id': 'display_height', 'type': 'int', 'mode': 'w',
         'label': 'Display height'},
        )

    deletable = 1
    maxsize = 2*1024*1024
    display_height = 0
    display_width = 0

    def prepare(self, datastructure, datamodel):
        """Prepare datastructure from datamodel."""
        widget_id = self.getWidgetId()
        datastructure[widget_id] = datamodel[self.fields[0]]
        datastructure[widget_id + '_choice'] = '' # make update from request work

    def validate(self, datastructure, datamodel):
        """Update datamodel from user data in datastructure."""
        field_id = self.fields[0]
        widget_id = self.getWidgetId()

        choice = datastructure[widget_id+'_choice']
        if choice == 'keep':
            # XXX check SESSION
            ok = 1
        elif choice == 'delete':
            datamodel[field_id] = None
            ok = 1
        else: # 'change'
            # XXX handle maxsize
            file = datastructure[widget_id]
            if _isinstance(file, FileUpload):
                fileid, filetitle = cookId('', '', file)
                file = Image(fileid, filetitle, file)
                LOG('CPSImageWidget', DEBUG, 'validate change set %s' % `file`)
                datamodel[field_id] = file
                ok = 1
            else:
                LOG('CPSImageWidget', DEBUG,
                    'unvalidate change set %s' % `file`)
                datastructure.setError(widget_id, 'cpsdoc_err_image')
                ok = 0
        if ok:
            self.prepare(datastructure, datamodel)
        return ok

    def render(self, mode, datastructure, datamodel):
        """Render this widget from the datastructure or datamodel."""
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
        return meth(mode=mode, datastructure=datastructure,
                    datamodel=datamodel,
                    current_name=current_name)

InitializeClass(CPSImageWidget)


class CPSImageWidgetType(CPSWidgetType):
    """Image widget type."""
    meta_type = "CPS Image Widget Type"
    cls = CPSImageWidget

    # XXX: TBD

InitializeClass(CPSImageWidgetType)

#################################################

class CPSRichTextEditorWidget(CPSTextAreaWidget):
    """Rich Text Editor widget."""
    meta_type = "CPS Rich Text EditorWidget"

    field_types = ('CPS String Field',)

    width = 40
    height = 5
    render_mode = 'pre'
    _properties = CPSWidget._properties + (
        {'id': 'width', 'type': 'int', 'mode': 'w',
         'label': 'Width'},
        {'id': 'height', 'type': 'int', 'mode': 'w',
         'label': 'Height'},
        {'id': 'render_mode', 'type': 'selection', 'mode': 'w',
         'select_variable': 'all_render_modes',
         'label': 'Render mode'},
        )


    all_render_modes = ['pre', 'stx', 'text']

    def prepare(self, datastructure, datamodel):
        """Prepare datastructure from datamodel."""
        datastructure[self.getWidgetId()] = datamodel[self.fields[0]]

    def validate(self, datastructure, datamodel):
        """Update datamodel from user data in datastructure."""
        value = datastructure[self.getWidgetId()]
        try:
            v = str(value)
        except ValueError:
            datastructure.setError(self.getWidgetId(),
                                   "cpsdoc_err_textarea")
            ok = 0
        else:
            datamodel[self.fields[0]] = v
            ok = 1
        return ok

    def render(self, mode, datastructure, datamodel):
        """Render this widget from the datastructure or datamodel."""
        # XXXX
        # Not finished !! Just for tests
        value = datastructure[self.getWidgetId()]
        if mode == 'view':
            # To change
            return structured_text(value)
        elif mode == 'edit':
            #
            # XXXX : version that has to work
            # For multiple rte within popup's
            #
            #return """
            #<script language="JavaScript" type="text/javascript">
            #<!--
            #function change_content(to_put) {
            #  form = document.getElementById('form') ;
            #  w = form.getElementById('%s') ;
            #  wt.value = to_put ;
            #}
            #//-->
            #</script>
            #
            #<script language="JavaScript" type="text/javascript">
            #function open_rte_edit(value, input_id) {
            #  args='?value='+value+'&input_id='+input_id ;
            #  selector_window = window.open('widget_rte_edit'+args, '%s', 'toolbar=0, scrollbars=0, location=0, statusbar=0, menubar=0, resizable=0, dependent=1, width=500, height=400')
            #  if(!selector_window.opener) selector_window.opener = window
            #}
            #//-->
            #</script>
            #%s
            #<a href="javascript:open_rte_edit('%s', '%s')">Editer</a>
            #<a href="javascript:change_content()">Change</a>
            #""" %(self.getHtmlWidgetId(),
            #      self.getHtmlWidgetId(),
            #      renderHtmlTag('textarea',
            #                    name=self.getHtmlWidgetId(),
            #                    cols=self.width,
            #                    rows=self.height,
            #                    contents=value,
            #                    css_class=self.css_class),
            #      str(value), self.getHtmlWidgetId() )

            #
            # Tmp dirty solution
            #
            render_method = 'widget_rte_render'
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
                        datamodel=datamodel,
                        current_name=current_name)

InitializeClass(CPSRichTextEditorWidget)

class CPSRichTextEditorWidgetType(CPSWidgetType):
    """ RTE widget type """
    meta_type = "CPS Rich Text Editor Widget Type "
    cls = CPSRichTextEditorWidget

InitializeClass(CPSRichTextEditorWidgetType)


##################################################

#
# Register widget types.
#

WidgetTypeRegistry.register(CPSCustomizableWidgetType, CPSCustomizableWidget)
WidgetTypeRegistry.register(CPSStringWidgetType, CPSStringWidget)
WidgetTypeRegistry.register(CPSPasswordWidgetType, CPSPasswordWidget)
WidgetTypeRegistry.register(CPSCheckBoxWidgetType, CPSCheckBoxWidget)
WidgetTypeRegistry.register(CPSTextAreaWidgetType, CPSTextAreaWidget)
WidgetTypeRegistry.register(CPSIntWidgetType, CPSIntWidget)
WidgetTypeRegistry.register(CPSDateWidgetType, CPSDateWidget)
WidgetTypeRegistry.register(CPSFileWidgetType, CPSFileWidget)
WidgetTypeRegistry.register(CPSImageWidgetType, CPSImageWidget)
WidgetTypeRegistry.register(CPSHtmlWidgetType, CPSHtmlWidget)
WidgetTypeRegistry.register(CPSRichTextEditorWidgetType, CPSRichTextEditorWidget)
WidgetTypeRegistry.register(CPSSelectWidgetType, CPSSelectWidget)
