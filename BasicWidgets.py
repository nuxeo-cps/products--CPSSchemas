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

from DateTime.DateTime import DateTime
from Globals import InitializeClass
from Acquisition import aq_parent, aq_inner
from AccessControl import ClassSecurityInfo
from types import ListType, TupleType, StringType
from cgi import escape
from re import compile, search
from urlparse import urlparse
from zLOG import LOG, DEBUG, PROBLEM
from TAL.TALDefs import attrEscape

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
        if key in ('value', ) or value != '':
            attrs.append('%s="%s"' % (key, attrEscape(str(value))))
    res = '<%s %s' % (tagname, ' '.join(attrs))
    if contents is not None:
        res += '>%s</%s>' % (contents, tagname)
    elif tagname in ('input', 'img', 'br', 'hr'):
        res += ' />'
    else:
        res += '>'
    return res


##################################################
class CPSNoneWidget(CPSWidget):
    """None widget.

    Deprecated widget can inherit form this widget, they will
    disapear without breaking the rest of the document.
    """
    meta_type = "CPS None Widget"

    def isHidden(self):
        return 1

    def prepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel."""
        pass

    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel."""
        return 1

    def render(self, mode, datastructure, **kw):
        return ''

InitializeClass(CPSNoneWidget)


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
    field_inits = ({'is_searchabletext': 1,},)

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

    def _extractValue(self, value):
        """Return err and new value."""
        err = None
        if not value:
            v = ''
        else:
            v = value
        try:
            v = v.strip()
        except AttributeError:
            err = 'cpsschemas_err_string'
        else:
            if self.is_required and not v:
                err = 'cpsschemas_err_required'
            elif self.size_max and len(v) > self.size_max:
                err = 'cpsschemas_err_string_too_long'
        return err, v

    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel."""
        widget_id = self.getWidgetId()
        err, v = self._extractValue(datastructure[widget_id])
        if err:
            datastructure.setError(widget_id, err)
            datastructure[widget_id] = v
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
            # XXX TODO should use an other name than kw !
            # XXX change this everywhere
            kw = {'type': 'text',
                  'id'  : self.getHtmlWidgetId(),
                  'name': self.getHtmlWidgetId(),
                  'value': escape(value),
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

class CPSURLWidget(CPSStringWidget):
    """URL widget."""
    meta_type = "CPS URL Widget"
    _properties = CPSStringWidget._properties + (
        {'id': 'target', 'type': 'string', 'mode': 'w',
         'label': 'Target for the link'},)

    target = ''
    css_class = 'url'
    display_width = 72
    size_max = 4096

    netloc_pat = compile(
        # username:passwd (optional)
        r"^([a-z0-9_!.~*\'\(\)-]*:[a-z0-9_!.~*\'\(\)-]*@)?"
        # hostname
        r"(([a-z0-9]|[a-z0-9][a-z0-9-]*[a-z0-9])\.)*"
        r"([a-z0-9]|[a-z0-9][a-z0-9-]*[a-z0-9])"
        # port (optional)
        r"(:[0-9a-z]*)?"
        "$")

    path_pat = compile(
        r"^[a-z0-9$_.+!*'(),;:@&=%/-]*$")

    # See rfc1738 and rfc2396
    # NB: rfc1738 says that "/", ";", "?" can't appear in the query, 
    # but that's not what we see (ex: ?file=/tmp/toto)
    def checkUrl(self, url):
        url = url.lower()
        try:
            scheme, netloc, path, parameters, query, fragment = urlparse(url)
        except:
            return 0

        if netloc and not self.netloc_pat.match(netloc):
            return 0

        if scheme in ('http', 'ftp', 'file', 'gopher', 'telnet',
                      'nttp', 'wais', 'prospero') and not netloc:
            return 0
            
        if scheme in ('http', '', 'ftp'):
            return self.path_pat.match(path)
        else:
            # TODO: match more URL schemes
            return 1
        
    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel."""
        widget_id = self.getWidgetId()
        err, v = self._extractValue(datastructure[widget_id])
        if not err and v and not self.checkUrl(v):
            err = 'cpsschemas_err_url'

        if err:
            datastructure.setError(widget_id, err)
            datastructure[widget_id] = v
        else:
            datamodel = datastructure.getDataModel()
            datamodel[self.fields[0]] = v

        return not err

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        value = escape(datastructure[self.getWidgetId()])
        if mode == 'view':
            target = self.target
            if not target and value.lower().startswith('http'):
                target = 'CPS_Link'
            kw = {'href': value, 'contents': value,
                  'css_class': self.css_class,
                  'target': target}
            return renderHtmlTag('a', **kw )
        return CPSStringWidget.render(self, mode, datastructure, **kw)


InitializeClass(CPSURLWidget)

class CPSURLWidgetType(CPSWidgetType):
    """URL widget type."""
    meta_type = "CPS URL Widget Type"
    cls = CPSURLWidget

InitializeClass(CPSURLWidgetType)

##################################################

class CPSEmailWidget(CPSStringWidget):
    """Email widget."""
    meta_type = "CPS Email Widget"
    css_class = "url"
    display_width = 72
    size_max = 256
    email_pat = compile(r"^([-\w_.+])+@(([-\w])+\.)+([\w]{2,4})$")

    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel."""
        widget_id = self.getWidgetId()
        err, v = self._extractValue(datastructure[widget_id])
        # no validation in search mode
        if not err and kw.get('layout_mode') != 'search' and \
               v and not self.email_pat.match(v):
            err = 'cpsschemas_err_email'

        if err:
            datastructure.setError(widget_id, err)
        else:
            datamodel = datastructure.getDataModel()
            datamodel[self.fields[0]] = v

        return not err

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        value = escape(datastructure[self.getWidgetId()])
        if mode == 'view':
            kw = {'href': 'mailto:' + value,
                  'contents': value}
            return renderHtmlTag('a', **kw)
        return CPSStringWidget.render(self, mode, datastructure, **kw)

InitializeClass(CPSEmailWidget)

class CPSEmailWidgetType(CPSWidgetType):
    """Email widget type."""
    meta_type = "CPS Email Widget Type"
    cls = CPSEmailWidget

InitializeClass(CPSEmailWidgetType)

##################################################

class CPSIdentifierWidget(CPSStringWidget):
    """Identifier widget."""
    meta_type = "CPS Identifier Widget"
    display_width = 30
    size_max = 256
    id_pat = compile(r"^[a-zA-Z][a-zA-Z0-9@\-\._]*$")

    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel."""
        widget_id = self.getWidgetId()
        err, v = self._extractValue(datastructure[widget_id])
        if not err and v and not self.id_pat.match(v.lower()):
            err = 'cpsschemas_err_identifier'

        if err:
            datastructure.setError(widget_id, err)
            datastructure[widget_id] = v
        else:
            datamodel = datastructure.getDataModel()
            datamodel[self.fields[0]] = v

        return not err

InitializeClass(CPSIdentifierWidget)

class CPSIdentifierWidgetType(CPSWidgetType):
    """Identifier widget type."""
    meta_type = "CPS Identifier Widget Type"
    cls = CPSIdentifierWidget

InitializeClass(CPSIdentifierWidgetType)


##################################################

class CPSHeadingWidget(CPSStringWidget):
    """HTML Heading widget like H1 H2..."""
    meta_type = "CPS Heading Widget"
    display_width = 72
    size_max = 128
    _properties = CPSStringWidget._properties + (
        {'id': 'level', 'type': 'selection', 'mode': 'w',
         'select_variable': 'all_levels',
         'label': 'There are six levels of headings in HTML'},
        )
    all_levels = ['1', '2', '3', '4', '5', '6']
    level = all_levels[0]

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        value = escape(datastructure[self.getWidgetId()])
        if mode == 'view':
            kw = {'contents': value}
            return renderHtmlTag('h%s' % self.level, **kw)
        return CPSStringWidget.render(self, mode, datastructure, **kw)


InitializeClass(CPSHeadingWidget)

class CPSHeadingWidgetType(CPSWidgetType):
    """CPS Heading widget type."""
    meta_type = "CPS Heading Widget Type"
    cls = CPSHeadingWidget

InitializeClass(CPSHeadingWidgetType)


##################################################

class CPSPasswordWidget(CPSStringWidget):
    """Password widget.

    The password widget displays stars in view mode, and in edit mode
    it always starts with an empty string.

    When validating, it doesn't update data if the user entry is empty.
    """

    meta_type = "CPS Password Widget"
    _properties = CPSStringWidget._properties + (
        {'id': 'password_widget', 'type': 'string', 'mode': 'w',
         'label': 'Password widget to compare with'},
        {'id': 'check_lower', 'type': 'boolean', 'mode': 'w',
         'label': 'Checking at least one lower case [a-z]'},
        {'id': 'check_upper', 'type': 'boolean', 'mode': 'w',
         'label': 'Checking at least one upper case [A-Z]'},
        {'id': 'check_digit', 'type': 'boolean', 'mode': 'w',
         'label': 'Checking at least one digit [0-9]'},
        {'id': 'check_extra', 'type': 'boolean', 'mode': 'w',
         'label': 'Checking at least one extra char other than [a-zA-Z0-9]'},
        {'id': 'size_min', 'type': 'int', 'mode': 'w',
         'label': 'Checking minimum size',}
        )

    field_types = ('CPS Password Field',)
    password_widget = ''
    check_lower = 0
    check_upper = 0
    check_digit = 0
    check_extra = 0
    display_width = 8
    size_min = 5
    size_max = 8

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
            if self.password_widget:
                # here we only check that that our confirm match the pwd
                pwidget_id = self.password_widget
                pvalue = datastructure[pwidget_id]
                datastructure[widget_id] = ''
                datastructure[pwidget_id] = ''
                pv = str(pvalue).strip()
                if pv and v != pv:
                    err = 'cpsschemas_err_password_mismatch'
            elif not v:
                if self.is_required:
                    datamodel = datastructure.getDataModel()
                    if not datamodel[self.fields[0]]:
                        err = 'cpsschemas_err_required'
            else:
                # checking pw consistancy
                len_v = len(v)
                if not err and self.size_max and len_v > self.size_max:
                    err = 'cpsschemas_err_string_too_long'
                if not err and self.size_min and len_v < self.size_min:
                    err = 'cpsschemas_err_password_size_min'
                if not err and self.check_lower and not search(r'[a-z]', v):
                    err = 'cpsschemas_err_password_lower'
                if not err and self.check_upper and not search(r'[A-Z]', v):
                    err = 'cpsschemas_err_password_upper'
                if not err and self.check_digit and not search(r'[0-9]', v):
                    err = 'cpsschemas_err_password_digit'
                if not err and self.check_extra and not search(r'[^a-zA-Z0-9]',
                                                               v):
                    err = 'cpsschemas_err_password_extra'

        if err:
            datastructure[widget_id] = ''
            datastructure.setError(widget_id, err)
        elif v:
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
                                        name=html_widget_id+':default',
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
    field_inits = ({'is_searchabletext': 1,},)

    _properties = CPSWidget._properties + (
        {'id': 'width', 'type': 'int', 'mode': 'w',
         'label': 'Width'},
        {'id': 'height', 'type': 'int', 'mode': 'w',
         'label': 'Height'},
        {'id': 'render_format', 'type': 'selection', 'mode': 'w',
         'select_variable': 'all_render_formats',
         'label': 'Render format'},
        )
    all_render_formats = ['text', 'pre', 'stx', 'html']
    width = 40
    height = 5
    render_format = all_render_formats[0]

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
        if mode == 'edit':
            ret = renderHtmlTag('textarea',
                                name=self.getHtmlWidgetId(),
                                cols=self.width,
                                rows=self.height,
                                contents=value)
        elif mode == 'view':
            rformat = self.render_format
            if rformat == 'pre':
                ret = '<pre>'+escape(value)+'</pre>'
            elif rformat == 'stx':
                ret = structured_text(value)
            elif rformat == 'text':
                ret = newline_to_br(value)
            elif rformat == 'html':
                ret = value
            else:
                raise RuntimeError("unknown render_format '%s' for '%s'" %
                                   (render_format, self.getId()))
        else:
            raise RuntimeError('unknown mode %s' % mode)

        return ret

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
    field_inits = ({'is_searchabletext': 1,},)

    width = 40
    height = 5
    format_empty = ''

    _properties = CPSWidget._properties + (
        {'id': 'width', 'type': 'int', 'mode': 'w',
         'label': 'Width'},
        {'id': 'height', 'type': 'int', 'mode': 'w',
         'label': 'Height'},
        {'id': 'format_empty', 'type': 'string', 'mode': 'w',
         'label': 'Format for empty list'},
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
        if value == ['']:
            # Buggy Zope :lines prop may give us [''] instead of []
            value = []
        v = value # Zope handle :lines automagically
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
            if not value:
                # XXX L10N empty format may be subject to i18n.
                return self.format_empty
            # XXX customize view mode, lots of displays are possible
            return ', '.join([escape(i) for i in value])
        elif mode == 'edit':
            return renderHtmlTag('textarea',
                                 id=self.getHtmlWidgetId(),
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

class CPSListWidget(CPSLinesWidget):
    """Abstract list widget"""
    meta_type = "CPS List Widget"
    display = None

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        if not self.display:
            raise NotImplementedError
        value = datastructure[self.getWidgetId()]
        meth = getattr(self, 'widget_list_render', None)
        if meth is None:
            raise RuntimeError(
                "Unknown Render Method widget_list_render for widget type %s"
                    % self.getId())
        return meth(mode=mode, value=value)

InitializeClass(CPSListWidget)


class CPSListWidgetType(CPSLinesWidgetType):
    """Abstract list widget type."""
    meta_type = "CPS List Widget Type"
    cls = CPSListWidget

InitializeClass(CPSListWidgetType)


##################################################

class CPSOrderedListWidget(CPSListWidget):
    """Ordered list widget"""
    meta_type = "CPS Ordered List Widget"
    display = 'ordered'

InitializeClass(CPSOrderedListWidget)


class CPSOrderedListWidgetType(CPSListWidgetType):
    """Ordered list widget type"""
    meta_type = "CPS Ordered List Widget Type"
    cls = CPSOrderedListWidget

InitializeClass(CPSOrderedListWidgetType)


##################################################

class CPSUnorderedListWidget(CPSListWidget):
    """Unordered list widget"""
    meta_type = "CPS Unordered List Widget"
    display = 'unordered'

InitializeClass(CPSOrderedListWidget)


class CPSUnorderedListWidgetType(CPSListWidgetType):
    """Unordered list widget type"""
    meta_type = "CPS Unordered List Widget Type"
    cls = CPSUnorderedListWidget

InitializeClass(CPSUnorderedListWidgetType)



##################################################

class CPSSelectWidget(CPSWidget):
    """Select widget."""
    meta_type = "CPS Select Widget"

    field_types = ('CPS String Field',)
    field_inits = ({'is_searchabletext': 1,},)

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
            raise ValueError("Missing vocabulary '%s' for widget '%s'" %
                             (self.vocabulary, self.getWidgetId()))
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
            in_selection = 0
            for k, v in vocabulary.items():
                kw = {'value': k, 'contents': v}
                if value == k:
                    kw['selected'] = None
                    in_selection = 1
                res += renderHtmlTag('option', **kw)
            if value and not in_selection:
                kw = {'value': value, 'contents': 'invalid: '+value,
                      'selected': None}
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
    field_inits = ({'is_searchabletext': 1,},)

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
            raise ValueError("Missing vocabulary '%s' for widget '%s'" %
                             (self.vocabulary, self.getWidgetId()))
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
        if self.is_required and not len(v):
            datastructure.setError(widget_id, "cpsschemas_err_required")
            return 0
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

class CPSBooleanWidget(CPSWidget):
    """Boolean widget."""
    meta_type = "CPS Boolean Widget"

    field_types = ('CPS Int Field',)

    # XXX should extend with a property to choose rendering
    # between checkbox, select or radio button (and replace chekbox widget)
    _properties = CPSWidget._properties + (
        {'id': 'label_false', 'type': 'string', 'mode': 'w',
         'label': 'False label'},
        {'id': 'label_true', 'type': 'string', 'mode': 'w',
         'label': 'True label'},
        )
    label_false = 'cpsschemas_label_false'
    label_true = 'cpsschemas_label_true'

    def prepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel."""
        datamodel = datastructure.getDataModel()
        datastructure[self.getWidgetId()] = str(datamodel[self.fields[0]])

    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel."""
        value = datastructure[self.getWidgetId()]

        try:
            v = int(value)
        except (ValueError, TypeError):
            datastructure.setError(self.getWidgetId(),
                                   "cpsschemas_err_boolean")
            return 0
        if v not in (0, 1):
            datastructure.setError(self.getWidgetId(),
                                   "cpsschemas_err_boolean")
            return 0
        datamodel = datastructure.getDataModel()
        datamodel[self.fields[0]] = v
        return 1

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        value = datastructure.getDataModel()[self.getWidgetId()]
        if value and str(value) != '0':
            label_value = self.label_true
        else:
            label_value = self.label_false
        render_method = 'widget_boolean_render'
        meth = getattr(self, render_method, None)
        if meth is None:
            raise RuntimeError("Unknown Render Method %s for widget type %s"
                               % (render_method, self.getId()))
        return meth(mode=mode, value=value, label_value=label_value)

InitializeClass(CPSBooleanWidget)


class CPSBooleanWidgetType(CPSWidgetType):
    """Boolean widget type."""
    meta_type = "CPS Boolean Widget Type"
    cls = CPSBooleanWidget

InitializeClass(CPSBooleanWidgetType)

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
        {'id': 'use_javascript', 'type': 'boolean', 'mode': 'w',
         'label': 'Use Javascript'},
        )
    view_format = "%d/%m/%Y" # XXX unused for now
    view_format_none = "-"
    use_javascript = 0

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
        if self.use_javascript:
            js_onKeyPress = """if (navigator.appName == 'Netscape') 
                { var key = event.which } else { var key = event.keyCode };
                if ( key < 32 ) { return true; }
                if ( key < 48 || key > 57 ) { return false; }"""

            js_onKeyUp = """if (navigator.appName == 'Netscape') 
                { var key = event.which } else { var key = event.keyCode };
                if ( key < 32 ) { return true; }
                if ( this.value > %(max_value)s ) { return false};
                if ( this.value >= %(low_trigger)s || 
                     this.value.length >= %(max_size)s ) {
                    form.%(next_widget)s.focus() }
                 """
        else:
            js_onKeyPress = ""
            js_onKeyUp = ""
                                             
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
                                 maxlength=2,
                                 onKeyPress=js_onKeyPress,
                                 onKeyUp=js_onKeyUp % {
                                    'max_value': '31',
                                    'max_size': '2',
                                    'low_trigger': '4',
                                    'next_widget': html_widget_id+'_m',
                                 })
            mtag = renderHtmlTag('input',
                                 type='text',
                                 name=html_widget_id+'_m',
                                 value=m,
                                 size=2,
                                 maxlength=2,
                                 onKeyPress=js_onKeyPress,
                                 onKeyUp=js_onKeyUp % {
                                    'max_value': '12',
                                    'max_size': '2',
                                    'low_trigger': '2',
                                    'next_widget': html_widget_id+'_y',
                                 })
            ytag = renderHtmlTag('input',
                                 type='text',
                                 name=html_widget_id+'_y',
                                 value=y,
                                 size=6,
                                 maxlength=6,
                                 onKeyPress=js_onKeyPress,
                                 )
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

    def getFileInfo(self, datastructure):
        """Get the file info from the datastructure."""
        file = datastructure[self.getWidgetId()]
        size = 0
        last_modified = ''
        if file:
            if _isinstance(file, File):
                current_name = file.title_or_id()
                size = file.get_size()
                last_modified = str(file._p_mtime)
            else:
                current_name = self.getWidgetId()
            empty_file = 0
        else:
            current_name = ''
            empty_file = 1

        # The attached file current name should not contain spaces otherwise it
        # causes problem when used by the ExternalEditor.
        current_name = current_name.replace(' ', '_')

        # XXX This is a total mess, it needs refactoring.

        dm = datastructure.getDataModel()
        field_id = self.fields[0]
        for adapter in dm._adapters:
            if adapter.getSchema().has_key(field_id):
                break # Note: 'adapter' is still the right one

        ob = dm.getProxy()
        if ob is None: # Not stored in the ZODB.
            # StorageAdapters that do not store the object in
            # ZODB takes the entry_id instead of object.
            # Get the entry_id from the datamodel context(typically
            # a directory).
            id_field = getattr(dm.getContext(), 'id_field', None)
            if id_field:
                entry_id = datastructure[id_field]
            else:
                # No object passed, and no id_field
                entry_id = None
            if entry_id:
                content_url = adapter._getContentUrl(entry_id, field_id)
            else:
                content_url = None
        else:
            content_url = adapter._getContentUrl(ob, field_id, current_name)

        registry = getToolByName(self, 'mimetypes_registry')
        mimetype = registry.lookupExtension(current_name.lower()) or\
                   registry.lookupExtension('fake.bin')

        return {'empty_file': empty_file,
                'content_url': content_url,
                'current_name': current_name,
                'mimetype': mimetype,
                'size': size,
                'last_modified': last_modified,
               }

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

        if choice == 'delete':
            datamodel[field_id] = None
        elif choice == 'change' and datastructure.get(widget_id):
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
                    fileid = cookId('', '', file)[0]
                    file = File(fileid, fileid, file)
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

        if kw['layout_mode'] == 'create':
            file_info = {'empty_file': 1,
                         'content_url': '',
                         'current_name': '-',
                         'mimetype': '',
                         'last_modified': '',
                        }
        else:
            file_info = self.getFileInfo(datastructure)

        return meth(mode=mode, datastructure=datastructure,
                    **file_info)

InitializeClass(CPSFileWidget)


class CPSFileWidgetType(CPSWidgetType):
    """File widget type."""
    meta_type = "CPS File Widget Type"
    cls = CPSFileWidget

InitializeClass(CPSFileWidgetType)

##################################################

class CPSImageWidget(CPSFileWidget):
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
        err = None
        if choice == 'delete':
            datamodel[field_id] = None
        elif choice == 'change' and datastructure.get(widget_id):
            file = datastructure[widget_id]
            if type(file) is StringType:
                file = Image('-', '', file)
            elif not _isinstance(file, FileUpload):
                err = 'cpsschemas_err_file'
            else:
                ms = self.size_max
                if file.read(1) == '':
                    err = 'cpsschemas_err_file_empty'
                elif ms and len(file.read(ms)) == ms:
                    err = 'cpsschemas_err_file_too_big'
                else:
                    file.seek(0)
                    fileid = cookId('', '', file)[0]
                    registry = getToolByName(self, 'mimetypes_registry')
                    mimetype = registry.lookupExtension(fileid.lower())
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
                                img.save(file, format=img.format)
                            except (NameError, IOError, ValueError):
                                LOG('CPSImageWidget', PROBLEM,
                                    "Failed to resize file %s keep original" \
                                    % fileid)
                        file = Image(fileid, fileid, file)
                        LOG('CPSImageWidget', DEBUG,
                            'validate change set %s' % `file`)
                        datamodel[field_id] = file


        if err:
            datastructure.setError(widget_id, err)
            LOG('CPSImageWidget', DEBUG,
                'error %s on %s' % (err, `file`))
        # reset datastructure
        datastructure[widget_id] = datamodel[self.fields[0]]
        datastructure[widget_id + '_choice'] = ''
        if self.allow_resize:
            datastructure[widget_id + '_resize'] = ''

        return not err


    def getImageInfo(self, datastructure):
        """Get the image info from the datastructure."""
        image_info = self.getFileInfo(datastructure)
        image = datastructure[self.getWidgetId()]

        if image:
            if not _isinstance(image, Image):
                image = Image(self.getWidgetId(), '', image)
        if image_info['empty_file']:
            tag = ''
        else:
            height = int(getattr(image, 'height', 0))
            width = int(getattr(image,'width', 0))
            if self.allow_resize:
                z_w = z_h = 1
                h = int(self.display_height)
                w = int(self.display_width)
                if w and h:
                    if w < width:
                        z_w = w / float(width)
                    if h < height:
                        z_h = h / float(height)
                    zoom = min(z_w, z_h)
                    width = int(zoom * width)
                    height = int(zoom * height)

            title = getattr(image, 'title', None)
            tag = renderHtmlTag('img', src=image_info['content_url'],
                    width=str(width), height=str(height), border='0',
                    alt=title, title=title)

        image_info['image_tag'] = tag
        return image_info

    def render(self, mode, datastructure, **kw):

        render_method = 'widget_image_render'
        meth = getattr(self, render_method, None)
        if meth is None:
            raise RuntimeError("Unknown Render Method %s for widget type %s"
                               % (render_method, self.getId()))
        if kw['layout_mode'] == 'create':
            img_info = {'empty_file': 1,
                        'content_url': '',
                        'image_tag': '',
                        'current_name': '-',
                        'mimetype': '',
                        'last_modified': '',
                       }
        else:
            img_info = self.getImageInfo(datastructure)

        return meth(mode=mode, datastructure=datastructure, **img_info)

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
        CPSWidget._properties[:2] + (
        {'id': 'widget_ids', 'type': 'tokens', 'mode': 'w',
         'label': 'Widget ids'},
        {'id': 'widget_type', 'type': 'string', 'mode': 'w',
         'label': 'Widget type'},
        ) + CPSWidget._properties[2:]
        )
    widget_ids = []
    widget_type = ''

    security.declarePrivate('_getType')
    def _getType(self):
        """Get the type object for this widget."""
        wtool = getToolByName(self, 'portal_widget_types')
        return getattr(wtool, self.widget_type)

    security.declarePrivate('_getRenderMethod')
    def _getRenderMethod(self):
        """Get the render method."""
        wtool = getToolByName(self, 'portal_widget_types')
        wt = getattr(wtool, self.widget_type)
        return wt.getRenderMethod(self)

    security.declarePrivate('getFieldTypes')
    def getFieldTypes(self):
        """Get field types from the underlying widgets."""
        return []

    security.declarePrivate('getFieldInits')
    def getFieldInits(self):
        """Get field inits from the underlying widgets."""
        return []

    def prepare(self, datastructure, **kw):
        """Prepare the underlying widgets."""
        layout = aq_parent(aq_inner(self))
        for widget_id in self.widget_ids:
            widget = layout[widget_id]
            widget.prepare(datastructure, **kw)
        self._getType().prepare(self, datastructure)

    def validate(self, datastructure, **kw):
        """Validate the underlying widgets."""
        layout = aq_parent(aq_inner(self))
        ret = 1
        self._getType().validate(self, datastructure, post_validate=0)
        for widget_id in self.widget_ids:
            widget = layout[widget_id]
            ret = widget.validate(datastructure, **kw) and ret

        return ret and self._getType().validate(self, datastructure)

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
        {'id': 'prepare_validate_method', 'type': 'string', 'mode': 'w',
         'label': 'Prepare & Validate Method'},
        )
    render_method = ''
    prepare_validate_method = None

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

    def prepare(self, widget, datastructure):
        if not self.prepare_validate_method:
            return
        meth = getattr(widget, self.prepare_validate_method, None)
        if meth:
            return meth('prepare', datastructure)
        raise RuntimeError("Unknown Validate Method %s for widget type %s"
                           % (self.prepare_validate_method, self.getId()))

    def validate(self, widget, datastructure, post_validate=1):
        if not self.prepare_validate_method:
            return 1
        meth = getattr(widget, self.prepare_validate_method, None)
        if meth:
            return meth('validate', datastructure, post_validate)
        raise RuntimeError("Unknown Validate Method %s for widget type %s"
                           % (self.prepare_validate_method, self.getId()))


InitializeClass(CPSCompoundWidgetType)


##################################################

#
# Register widget types.
#

WidgetTypeRegistry.register(CPSCustomizableWidgetType)
WidgetTypeRegistry.register(CPSCompoundWidgetType)
WidgetTypeRegistry.register(CPSStringWidgetType)
WidgetTypeRegistry.register(CPSURLWidgetType)
WidgetTypeRegistry.register(CPSEmailWidgetType)
WidgetTypeRegistry.register(CPSIdentifierWidgetType)
WidgetTypeRegistry.register(CPSHeadingWidgetType)
WidgetTypeRegistry.register(CPSPasswordWidgetType)
WidgetTypeRegistry.register(CPSCheckBoxWidgetType)
WidgetTypeRegistry.register(CPSTextAreaWidgetType)
WidgetTypeRegistry.register(CPSLinesWidgetType)
WidgetTypeRegistry.register(CPSBooleanWidgetType)
WidgetTypeRegistry.register(CPSIntWidgetType)
WidgetTypeRegistry.register(CPSLongWidgetType)
WidgetTypeRegistry.register(CPSFloatWidgetType)
WidgetTypeRegistry.register(CPSDateWidgetType)
WidgetTypeRegistry.register(CPSFileWidgetType)
WidgetTypeRegistry.register(CPSImageWidgetType)
WidgetTypeRegistry.register(CPSHtmlWidgetType)
WidgetTypeRegistry.register(CPSMethodWidgetType)
WidgetTypeRegistry.register(CPSSelectWidgetType)
WidgetTypeRegistry.register(CPSMultiSelectWidgetType)
WidgetTypeRegistry.register(CPSOrderedListWidgetType)
WidgetTypeRegistry.register(CPSUnorderedListWidgetType)
