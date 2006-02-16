# -*- coding: iso-8859-15 -*-
# (C) Copyright 2003-2005 Nuxeo SARL <http://nuxeo.com>
# Authors:
# Florent Guillaume <fg@nuxeo.com>
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
"""BasicWidgets

Definition of standard widget types.
"""

import warnings
import string
from DateTime.DateTime import DateTime
from Globals import InitializeClass
from Acquisition import aq_parent, aq_inner
from AccessControl import ClassSecurityInfo
from cgi import escape
from re import compile, search
from urlparse import urlparse

from zLOG import LOG, INFO, DEBUG, PROBLEM
from TAL.TALDefs import attrEscape

from Products.CPSUtil.id import generateFileName
from Products.CPSUtil.file import PersistableFileUpload
from Products.CPSUtil.file import makeFileUploadFromOFSFile
from Products.CPSSchemas.utils import getHumanReadableSize

try:
    import PIL.Image
except ImportError:
    LOG('CPSSchemas', INFO, "No PIL library found so no image resizing will "
                            "be done")

from StringIO import StringIO

from ZPublisher.HTTPRequest import FileUpload
from OFS.Image import cookId, File, Image
from OFS.PropertyManager import PropertyManager
from Products.PythonScripts.standard import structured_text, newline_to_br

from Products.CMFCore.permissions import ManageProperties
from Products.CMFCore.utils import getToolByName

from Products.CPSSchemas.Widget import CPSWidget
from Products.CPSSchemas.Widget import widgetRegistry

from Products.CPSSchemas.MethodVocabulary import MethodVocabularyWithContext

def _isinstance(ob, cls):
    warnings.warn("_isinstance() is deprecated and will be removed in "
                  "CPS 3.4.1. Use isinstance() instead.",
                  DeprecationWarning, stacklevel=2)
    return isinstance(ob, cls)

def renderHtmlTag(tagname, **kw):
    """Render an HTML tag."""
    # The "class" key cannot be used since it is a reserved word in python, so
    # to set the "class" attribute one has to specify the "css_class" key.
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
            continue
        if key in ('value', 'alt') or value != '':
            attrs.append('%s="%s"' % (key, attrEscape(str(value))))
    res = '<%s %s' % (tagname, ' '.join(attrs))
    if contents is not None:
        res += '>%s</%s>' % (contents, tagname)
    elif tagname in ('input', 'img', 'br', 'hr'):
        res += ' />'
    else:
        res += '>'
    return res

# BBB (remove this in CPS-3.6)
def cleanFileName(name):
    return generateFileName(name)


##################################################
class CPSNoneWidget(CPSWidget):
    """None widget.

    Deprecated widget can inherit form this widget, they will
    disapear without breaking the rest of the document.
    """
    meta_type = 'None Widget'

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
    meta_type = 'Html Widget'

    _properties = CPSWidget._properties + (
        {'id': 'html_view', 'type': 'text', 'mode': 'w',
         'label': 'Html for view'},
        {'id': 'html_edit', 'type': 'text', 'mode': 'w',
         'label': 'Html for edit'},
        )
    html_view = ''
    html_edit = ''
    field_types = ('CPS String Field',)

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

widgetRegistry.register(CPSHtmlWidget)

##################################################

class CPSMethodWidget(CPSWidget):
    """Method widget."""
    meta_type = 'Method Widget'

    _properties = CPSWidget._properties + (
        {'id': 'render_method', 'type': 'string', 'mode': 'w',
         'label': 'the zpt or py script method'},
        {'id': 'field_types', 'type': 'lines', 'mode': 'w',
         'label': 'Field types'},)

    field_types = ('CPS String Field',)
    render_method = ''

    def prepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel."""
        datamodel = datastructure.getDataModel()
        if len(self.fields):
            datastructure[self.getWidgetId()] = datamodel[self.fields[0]]
        else:
            datastructure[self.getWidgetId()] = None

    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel."""
        widget_id = self.getWidgetId()
        err = 0
        v = datastructure[widget_id]
        if err:
            datastructure.setError(widget_id, err)
            datastructure[widget_id] = v
        else:
            datamodel = datastructure.getDataModel()
            if len(self.fields):
                datamodel[self.fields[0]] = v

        return not err

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

widgetRegistry.register(CPSMethodWidget)

##################################################

class CPSStringWidget(CPSWidget):
    """String widget."""
    meta_type = 'String Widget'

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

    # Associating the widget label with an input area to improve the widget
    # accessibility.
    has_input_area = True

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
            html_widget_id = self.getHtmlWidgetId()
            kw = {'type': 'text',
                  'id'  : html_widget_id,
                  'name': html_widget_id,
                  'value': escape(value),
                  'size': self.display_width,
                  }
            if self.size_max:
                kw['maxlength'] = self.size_max
            return renderHtmlTag('input', **kw)
        raise RuntimeError('unknown mode %s' % mode)

InitializeClass(CPSStringWidget)

widgetRegistry.register(CPSStringWidget)

##################################################

class CPSURLWidget(CPSStringWidget):
    """URL widget."""
    meta_type = 'URL Widget'
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
        r"^[a-z0-9$_.+!*'(),;:@&=%/~-]*$")

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

        if scheme in ('http', 'ftp', 'gopher', 'telnet',
                      'nntp', 'wais', 'prospero') and not netloc:
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
            if len(value) > self.display_width:
                value_for_display = value[:self.display_width] + '...'
            else :
                value_for_display = value
            if not value_for_display:
                return ''
            kw = {'href': value, 'contents': value_for_display,
                  'css_class': self.css_class,
                  'target': self.target.strip()}
            return renderHtmlTag('a', **kw)

        return CPSStringWidget.render(self, mode, datastructure, **kw)


InitializeClass(CPSURLWidget)

widgetRegistry.register(CPSURLWidget)

##################################################

class CPSEmailWidget(CPSStringWidget):
    """Email widget."""
    meta_type = 'Email Widget'
    display_width = 72
    size_max = 256
    email_pat = compile(r"^([-\w_.'+])+@(([-\w])+\.)+([\w]{2,4})$")

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
        if mode == 'view' and value:
            kw = {'href': 'mailto:' + value,
                  'contents': value}
            return renderHtmlTag('a', **kw)
        return CPSStringWidget.render(self, mode, datastructure, **kw)

InitializeClass(CPSEmailWidget)

widgetRegistry.register(CPSEmailWidget)

##################################################

class CPSIdentifierWidget(CPSStringWidget):
    """Identifier widget."""
    meta_type = 'Identifier Widget'
    display_width = 30
    size_max = 256

    _properties = CPSStringWidget._properties + (
                    {'id': 'id_pat',
                     'type': 'string', 'mode': 'w',
                     'label': 'Identifier regular expression (raw format)'},)

    id_pat = r'^[a-zA-Z][a-zA-Z0-9@\-\._]*$'

    def _checkIdentifier(self, value):
        id_pat = compile(self.id_pat)
        return id_pat.match(value.lower()) is not None

    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel."""
        widget_id = self.getWidgetId()
        err, v = self._extractValue(datastructure[widget_id])

        if not err and v and not self._checkIdentifier(v):
            err = 'cpsschemas_err_identifier'

        if err:
            datastructure.setError(widget_id, err)
            datastructure[widget_id] = v
        else:
            datamodel = datastructure.getDataModel()
            datamodel[self.fields[0]] = v

        return not err

InitializeClass(CPSIdentifierWidget)

widgetRegistry.register(CPSIdentifierWidget)

##################################################

class CPSHeadingWidget(CPSStringWidget):
    """HTML Heading widget like H1 H2..."""
    meta_type = 'Heading Widget'
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
            dm = datastructure.getDataModel()
            obj = dm.getObject()
            kw = {'contents': value,
                  'style': 'background:url(%s) no-repeat 0px 4px' % obj.getIcon(1)}
            return renderHtmlTag('h%s' % self.level, **kw)
        return CPSStringWidget.render(self, mode, datastructure, **kw)


InitializeClass(CPSHeadingWidget)

widgetRegistry.register(CPSHeadingWidget)

##################################################

class CPSPasswordWidget(CPSStringWidget):
    """Password widget.

    The password widget displays stars in view mode, and in edit mode
    it always starts with an empty string.

    When validating, it doesn't update data if the user entry is empty.
    """

    meta_type = 'Password Widget'
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
            else:
                if not v:
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

widgetRegistry.register(CPSPasswordWidget)

##################################################

class CPSCheckBoxWidget(CPSWidget):
    """CheckBox widget.
       Deprecated, use CPS Boolean Widget !!!"""
    meta_type = 'CheckBox Widget'

    field_types = ('CPS Boolean Field',)

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
                kw['checked'] = 'checked'
            tag = renderHtmlTag('input', **kw)
            default_tag = renderHtmlTag('input',
                                        type='hidden',
                                        name=html_widget_id+':default',
                                        value='')
            return default_tag+tag
        raise RuntimeError('unknown mode %s' % mode)

InitializeClass(CPSCheckBoxWidget)

widgetRegistry.register(CPSCheckBoxWidget)

##################################################
# Warning textarea widget code is back to r1.75
# refactored textarea with position and format is now located in
# ExtendedWidgets and named CPSTextWidget

class CPSTextAreaWidget(CPSWidget):
    """TextArea widget."""
    meta_type = 'TextArea Widget'

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
                ret = '<pre>' + escape(value) + '</pre>'
            elif rformat == 'stx':
                ret = structured_text(value)
            elif rformat == 'text':
                ret = newline_to_br(escape(value))
            elif rformat == 'html':
                ret = value
            else:
                raise RuntimeError("unknown render_format '%s' for '%s'" %
                                   (rformat, self.getId()))
        else:
            raise RuntimeError('unknown mode %s' % mode)

        return ret

InitializeClass(CPSTextAreaWidget)

widgetRegistry.register(CPSTextAreaWidget)

##################################################

class CPSLinesWidget(CPSWidget):
    """Lines widget."""
    meta_type = 'Lines Widget'

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

    # Associating the widget label with an input area to improve the widget
    # accessibility.
    has_input_area = True

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
            html_widget_id = self.getHtmlWidgetId()
            return renderHtmlTag('textarea',
                                 id=html_widget_id,
                                 name=html_widget_id + ':lines',
                                 cols=self.width,
                                 rows=self.height,
                                 contents='\n'.join(value))
        raise RuntimeError('unknown mode %s' % mode)

InitializeClass(CPSLinesWidget)

widgetRegistry.register(CPSLinesWidget)

##################################################

class CPSListWidget(CPSLinesWidget):
    """Abstract list widget"""
    meta_type = 'List Widget'
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

##################################################

class CPSOrderedListWidget(CPSListWidget):
    """Ordered list widget"""
    meta_type = 'Ordered List Widget'
    display = 'ordered'

InitializeClass(CPSOrderedListWidget)

widgetRegistry.register(CPSOrderedListWidget)

##################################################

class CPSUnorderedListWidget(CPSListWidget):
    """Unordered list widget"""
    meta_type = 'Unordered List Widget'
    display = 'unordered'

InitializeClass(CPSUnorderedListWidget)

widgetRegistry.register(CPSUnorderedListWidget)

##################################################

class CPSSelectWidget(CPSWidget):
    """Select widget."""
    meta_type = 'Select Widget'

    field_types = ('CPS String Field',)
    field_inits = ({'is_searchabletext': 1,},)

    _properties = CPSWidget._properties + (
        {'id': 'vocabulary', 'type': 'string', 'mode': 'w',
         'label': 'Vocabulary', 'is_required' : 1},
        {'id': 'translated', 'type': 'boolean', 'mode': 'w',
         'label': 'Is vocabulary translated on display'},
        )
    # XXX make a menu for the vocabulary.
    vocabulary = ''
    translated = False

    # Associating the widget label with an input area to improve the widget
    # accessibility.
    has_input_area = True

    def _getVocabulary(self, datastructure=None):
        """Get the vocabulary object for this widget."""
        context = datastructure.getDataModel().getContext()
        if not isinstance(self.vocabulary, str):
            # this is in case vocabulary directly holds
            # a vocabulary object
            vocabulary = self.vocabulary
        else:
            vtool = getToolByName(self, 'portal_vocabularies')
            vocabulary = vtool.getVocabularyFor(context, self.vocabulary)
        if vocabulary.meta_type == 'CPS Method Vocabulary':
            vocabulary = MethodVocabularyWithContext(vocabulary, context)
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
        portal = getToolByName(self, 'portal_url').getPortalObject()
        cpsmcat = portal.translation_service
        if mode == 'view':
            if self.translated:
                return escape(cpsmcat(vocabulary.getMsgid(value, value)).encode('ISO-8859-15', 'ignore'))
            else:
                return escape(vocabulary.get(value, value))
        elif mode == 'edit':
            html_widget_id = self.getHtmlWidgetId()
            res = renderHtmlTag('select', name=html_widget_id, id=html_widget_id)
            in_selection = 0
            for k, v in vocabulary.items():
                if self.translated:
                    kw = {'value': k,
                          'contents': cpsmcat(vocabulary.getMsgid(k, k)).encode('ISO-8859-15', 'ignore')
                          }
                else:
                    kw = {'value': k, 'contents': v}
                if value == k:
                    kw['selected'] = 'selected'
                    in_selection = 1
                res += renderHtmlTag('option', **kw)
            if value and not in_selection:
                kw = {'value': value, 'contents': 'invalid: '+ str(value),
                      'selected': 'selected'}
                res += renderHtmlTag('option', **kw)
            res += '</select>'
            return res
        raise RuntimeError('unknown mode %s' % mode)

InitializeClass(CPSSelectWidget)

widgetRegistry.register(CPSSelectWidget)

##################################################

class CPSMultiSelectWidget(CPSWidget):
    """MultiSelect widget."""
    meta_type = 'MultiSelect Widget'

    field_types = ('CPS String List Field',)
    field_inits = ({'is_searchabletext': 1,},)

    _properties = CPSWidget._properties + (
        {'id': 'vocabulary', 'type': 'string', 'mode': 'w',
         'label': 'Vocabulary'},
        {'id': 'translated', 'type': 'boolean', 'mode': 'w',
         'label': 'Is vocabulary translated on display'},
        {'id': 'size', 'type': 'int', 'mode': 'w',
         'label': 'Size'},
        {'id': 'format_empty', 'type': 'string', 'mode': 'w',
         'label': 'Format for empty list'},
        )
    # XXX make a menu for the vocabulary.
    vocabulary = ''
    translated = False
    size = 0
    format_empty = ''

    # Associating the widget label with an input area to improve the widget
    # accessibility.
    has_input_area = True

    def _getVocabulary(self, datastructure=None):
        """Get the vocabulary object for this widget."""
        vtool = getToolByName(self, 'portal_vocabularies')
        context = datastructure.getDataModel().getContext()
        vocabulary = vtool.getVocabularyFor(context, self.vocabulary)
        if vocabulary.meta_type == 'CPS Method Vocabulary':
            vocabulary = MethodVocabularyWithContext(vocabulary, context)
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
        if not isinstance(value, (list, tuple)):
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


    def getEntriesHtml(self, entries, vocabulary, translated=False):
        if translated:
            cpsmcat = getToolByName(self, 'translation_service', None)
            if cpsmcat is None:
                translated = False
        values = []
        for entry in entries:
            if translated:
                value = vocabulary.getMsgid(entry, entry)
                value = cpsmcat(value, default=value)
                value = value.encode('ISO-8859-15', 'ignore')
            else:
                value = vocabulary.get(entry, entry)
            values.append(value)
        return escape(', '.join(values))


    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        value = datastructure[self.getWidgetId()]
        vocabulary = self._getVocabulary(datastructure)
        portal = getToolByName(self, 'portal_url').getPortalObject()
        cpsmcat = portal.translation_service
        if mode == 'view':
            if not value:
                # XXX L10N empty format may be subject to i18n.
                return self.format_empty
            # XXX customize view mode, lots of displays are possible
            else:
                return self.getEntriesHtml(value, vocabulary, self.translated)
        elif mode == 'edit':
            html_widget_id = self.getHtmlWidgetId()
            kw = {'name': html_widget_id + ':list',
                  'multiple': 'multiple',
                  'id': html_widget_id,
                  }
            if self.size:
                kw['size'] = self.size
            res = renderHtmlTag('select', **kw)
            for k, v in vocabulary.items():
                if self.translated:
                    label = cpsmcat(vocabulary.getMsgid(k, k), default=k)
                    label = label.encode('ISO-8859-15', 'ignore')
                    kw = {'value': k,
                          'contents': label,
                          }
                else:
                    kw = {'value': k, 'contents': v}
                if k in value:
                    kw['selected'] = 'selected'
                res += renderHtmlTag('option', **kw)
            res += '</select>'
            default_tag = renderHtmlTag('input',
                                        type='hidden',
                                        name=html_widget_id+':tokens:default',
                                        value='')
            return default_tag+res
        raise RuntimeError('unknown mode %s' % mode)

InitializeClass(CPSMultiSelectWidget)

widgetRegistry.register(CPSMultiSelectWidget)

##################################################

class CPSBooleanWidget(CPSWidget):
    """Boolean widget."""
    meta_type = 'Boolean Widget'

    field_types = ('CPS Int Field',)

    _properties = CPSWidget._properties + (
        {'id': 'label_false', 'type': 'string', 'mode': 'w',
         'label': 'False label'},
        {'id': 'label_true', 'type': 'string', 'mode': 'w',
         'label': 'True label'},
        {'id': 'render_format', 'type': 'selection', 'mode': 'w',
         'select_variable': 'render_formats',
         'label': 'Render format'},
        )
    label_false = 'cpsschemas_label_false'
    label_true = 'cpsschemas_label_true'
    render_formats = ('checkbox', 'radio', 'select')
    render_format = render_formats[2]

    def prepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel."""
        datamodel = datastructure.getDataModel()
        datastructure[self.getWidgetId()] = bool(datamodel[self.fields[0]])

    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel."""
        value = datastructure[self.getWidgetId()]

        if self.render_format not in self.render_formats:
            self.render_format = 'select'

        try:
            v = bool(value)
        except (ValueError, TypeError):
            datastructure.setError(self.getWidgetId(),
                                   "cpsschemas_err_boolean")
            return 0
        datamodel = datastructure.getDataModel()
        datamodel[self.fields[0]] = v
        return 1

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        value = datastructure[self.getWidgetId()]
        if value:
            label_value = self.label_true
        else:
            label_value = self.label_false
        render_method = 'widget_boolean_render'
        meth = getattr(self, render_method, None)
        render_format = self.render_format
        if not render_format:
            render_format = 'select'
        if meth is None:
            raise RuntimeError("Unknown Render Method %s for widget type %s"
                               % (render_method, self.getId()))
        return meth(mode=mode, value=value, label_value=label_value,
                    render_format=render_format)

InitializeClass(CPSBooleanWidget)

widgetRegistry.register(CPSBooleanWidget)

##################################################

class CPSIntWidget(CPSWidget):
    """Integer widget."""
    meta_type = 'Int Widget'

    field_types = ('CPS Int Field',)

    _properties = CPSWidget._properties + (
        {'id': 'is_limited', 'type': 'boolean', 'mode': 'w',
         'label': 'Value must be in range'},
        {'id': 'min_value', 'type': 'int', 'mode': 'w',
         'label': 'Range minimum value'},
        {'id': 'max_value', 'type': 'int', 'mode': 'w',
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
        v = datamodel[self.fields[0]]
        if v is None:
            value = ''
        else:
            value = str(v)
            if self.thousands_separator:
                thousands = []
                while value:
                    thousands.insert(0, value[-3:])
                    value = value[:-3]
                value = self.thousands_separator.join(thousands)
        datastructure[self.getWidgetId()] = value

    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel."""
        datamodel = datastructure.getDataModel()
        widget_id = self.getWidgetId()
        value = datastructure[widget_id].strip()
        datastructure[widget_id] = value

        if self.thousands_separator:
            value = value.replace(self.thousands_separator, '')

        if not value:
            if self.is_required:
                datastructure.setError(widget_id, 'cpsschemas_err_required')
                return False
            v = None
        else:
            try:
                v = int(value)
            except (ValueError, TypeError):
                datastructure.setError(widget_id, 'cpsschemas_err_int')
                return False
            if self.is_limited:
                if (v < self.min_value) or (v > self.max_value):
                    datastructure.setError(widget_id,
                                           'cpsschemas_err_int_range')
                    return False

        datamodel[self.fields[0]] = v
        return True

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
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

widgetRegistry.register(CPSIntWidget)

#######################################################

class CPSLongWidget(CPSIntWidget):
    """Long Widget

    This widget is DEPRECATED, use the identical Int Widget instead.
    """
    meta_type = 'Long Widget'

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        warnings.warn("The Long Widget (%s/%s) is deprecated and will be "
                      "removed in CPS 3.5.0. Use a Int Widget instead" %
                      (aq_parent(aq_inner(self)).getId(), self.getWidgetId()),
                      DeprecationWarning)
        CPSIntWidget.render(self, mode, datastructure, **kw)

InitializeClass(CPSLongWidget)

widgetRegistry.register(CPSLongWidget)

##################################################

class CPSFloatWidget(CPSWidget):
    """Float number widget."""
    meta_type = 'Float Widget'

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
    # XXX: find a way to localized thousands_separator and decimals_separator
    thousands_separator = ''
    decimals_separator = '.'
    decimals_number = 0

    def prepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel."""
        datamodel = datastructure.getDataModel()
        v = datamodel[self.fields[0]]
        if v is None:
            value = ''
        else:
            if self.decimals_number:
                value = ('%%0.%df' % self.decimals_number) % v
            else:
                value = str(v)
            if self.thousands_separator:
                intpart, decpart = value.split('.')
                thousands = []
                while intpart:
                    thousands.insert(0, intpart[-3:])
                    intpart = intpart[:-3]
                value = (self.thousands_separator.join(thousands) + '.' +
                         decpart)
            if self.decimals_separator:
                value = value.replace('.', self.decimals_separator)
        datastructure[self.getWidgetId()] = value

    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel."""
        datamodel = datastructure.getDataModel()
        widget_id = self.getWidgetId()
        value = datastructure[widget_id].strip()
        datastructure[widget_id] = value

        if self.thousands_separator:
            value = value.replace(self.thousands_separator, '')
        if self.decimals_separator:
            value = value.replace(self.decimals_separator, '.')

        if not value:
            if self.is_required:
                datastructure.setError(widget_id, 'cpsschemas_err_required')
                return False
            v = None
        else:
            try:
                v = float(value)
            except (ValueError, TypeError):
                datastructure.setError(widget_id, 'cpsschemas_err_float')
                return False

            if self.is_limited:
                if (v < self.min_value) or (v > self.max_value):
                    datastructure.setError(widget_id,
                                           'cpsschemas_err_float_range')
                    return False

        datamodel[self.fields[0]] = v
        return True

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        value = datastructure[self.getWidgetId()]
        if mode == 'view':
            return escape(value)
        elif mode == 'edit':
            return renderHtmlTag('input',
                                 type='text',
                                 name=self.getHtmlWidgetId(),
                                 value=value)
        raise RuntimeError('unknown mode %s' % mode)

InitializeClass(CPSFloatWidget)

widgetRegistry.register(CPSFloatWidget)

##################################################
# Warning Date widget code is back to r1.49
# refactored date widget is now located in
# ExtendWidgets and named CPSDateTimeWidget

class CPSDateWidget(CPSWidget):
    """Date widget."""
    meta_type = 'Date Widget'

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
            d = '%02i' % v.day()
            m = '%02i' % v.month()
            y = '%04i' % v.year()
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

widgetRegistry.register(CPSDateWidget)

##################################################

class CPSFileWidget(CPSWidget):
    """File widget.

    The DataStructure stores either a FileUpload or None.

    A FileUpload itself has a filename. In addition, the DataStructure
    hold a title.

    When stored in the DataModel, the filename is used as File id
    and the title as File title.
    """
    meta_type = 'File Widget'

    field_types = ('CPS File Field',)

    _properties = CPSWidget._properties + (
        {'id': 'size_max', 'type': 'int', 'mode': 'w',
         'label': 'Maximum file size'},
        )
    size_max = 4*1024*1024

    def getHumanReadableSize(self, size):
        """ get human readable size
        """
        hr = getHumanReadableSize(size)
        cpsmcat = getToolByName(self, 'translation_service')
        return str(hr[0]) + ' ' + cpsmcat(hr[1]).encode('ISO-8859-15',
                                                        'ignore')

    def getFileInfo(self, datastructure):
        """Get the file info from the datastructure."""
        widget_id = self.getWidgetId()
        fileupload = datastructure[widget_id]
        dm = datastructure.getDataModel()
        field_id = self.fields[0]
        if fileupload:
            empty_file = False
            session_file = isinstance(fileupload, PersistableFileUpload)
            current_name = cleanFileName(fileupload.filename)
            current_title = datastructure[widget_id + '_title']
            fileupload.seek(0, 2) # end of file
            size = fileupload.tell()
            fileupload.seek(0)
            file = dm[field_id] # last stored file
            if file is not None:
                last_modified = str(file._p_mtime or '')
            else:
                last_modified = ''
        else:
            empty_file = True
            session_file = False
            current_name = ''
            current_title = ''
            size = 0
            last_modified = ''

        # Find the URL for the file  XXX Refactor this!

        # get the adapter
        for adapter in dm._adapters:
            if adapter.getSchema().has_key(field_id):
                break # Note: 'adapter' is still the right one
        else:
            raise ValueError('No schema for field %r' % field_id)

        # get the content_url from the adapter
        content_url = None
        ob = dm.getProxy()
        if ob is None:
            # non proxy case
            ob = dm.getObject()
        if ob is None:
            # Not stored in the ZODB.
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
                # some adapters does not have _getContentUrl
                if getattr(adapter, '_getContentUrl', None) is not None:
                    content_url = adapter._getContentUrl(entry_id, field_id)
        else:
            content_url = adapter._getContentUrl(ob, field_id, current_name)

        # get the mimetype
        registry = getToolByName(self, 'mimetypes_registry')
        mimetype = (registry.lookupExtension(current_name.lower()) or
                    registry.lookupExtension('file.bin'))

        file_info = {
            'empty_file': empty_file,
            'session_file': session_file,
            'current_name': current_name,
            'current_title': current_title,
            'size': size,
            'last_modified': last_modified,
            'content_url': content_url,
            'mimetype': mimetype,
            }

        return file_info

    def prepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel."""
        datamodel = datastructure.getDataModel()
        widget_id = self.getWidgetId()
        file = datamodel[self.fields[0]]
        datastructure[widget_id] = makeFileUploadFromOFSFile(file)
        datastructure[widget_id + '_choice'] = ''
        if file is not None:
            title = file.title
        else:
            title = ''
        datastructure[widget_id + '_title'] = title

    def unprepare(self, datastructure):
        # Remove costly things already stored from the datastructure
        del datastructure[self.getWidgetId()]

    def checkFileName(self, fileid, mimetype):
        return '', {}

    def makeFile(self, fileid, fileupload, datastructure):
        return File(fileid, fileid, fileupload)

    def otherProcessing(self, choice, datastructure):
        return

    def validate(self, datastructure, **kw):
        """Update datamodel from user data in datastructure."""
        datamodel = datastructure.getDataModel()
        field_id = self.fields[0]
        widget_id = self.getWidgetId()
        choice = datastructure[widget_id+'_choice']
        store = False

        if choice == 'delete':
            if self.is_required:
                return self.validateError('cpsschemas_err_required', {},
                                          datastructure)
            datamodel[field_id] = None
        elif choice == 'keep':
            fileupload = datastructure[widget_id]
            if isinstance(fileupload, PersistableFileUpload):
                # Keeping something from the session means we
                # actually want to store it.
                store = True
            else:
                # Nothing to change, don't pollute datastructure
                # with something costly already stored
                self.unprepare(datastructure)
        elif choice == 'change':
            fileupload = datastructure[widget_id]
            if not fileupload:
                return self.validateError('cpsschemas_err_file_empty', {},
                                          datastructure)
            if not isinstance(fileupload, FileUpload):
                return self.validateError('cpsschemas_err_file', {},
                                          datastructure)
            fileupload.seek(0, 2) # end of file
            size = fileupload.tell()
            if not size:
                return self.validateError('cpsschemas_err_file_empty', {},
                                          datastructure)
            if self.size_max and size > self.size_max:
                max_size_str = self.getHumanReadableSize(self.size_max)
                err = 'cpsschemas_err_file_too_big ${max_size}'
                err_mapping = {'max_size': max_size_str}
                return self.validateError(err, err_mapping, datastructure)
            store = True

        self.otherProcessing(choice, datastructure)

        if store:
            # Find file id
            fileupload.seek(0)
            fileid = cookId('', '', fileupload)[0].strip()
            if not fileid:
                fileid = 'file.bin'
            registry = getToolByName(self, 'mimetypes_registry')
            mimetype = registry.lookupExtension(fileid.lower())
            err, err_mapping = self.checkFileName(fileid, mimetype)
            if err:
                return self.validateError(err, err_mapping, datastructure)
            # Create file
            file = self.makeFile(fileid, fileupload, datastructure)
            # Fixup mimetype
            if mimetype and file.content_type != mimetype.normalized():
                file.content_type = mimetype.normalized()
            # Store
            datamodel[field_id] = file

        # Update title

        file = datamodel[field_id]
        if file is not None and choice != 'change':
            title = datastructure[widget_id + '_title'].strip()
            if not title:
                title = file.getId()
            title = cleanFileName(title)
            if title != file.title:
                file.title = title

        return True

    def validateError(self, err, err_mapping, datastructure):
        LOG(self.__class__.__name__, DEBUG, "Validation error %s" % err)
        # Do not keep rejected file, revert to older
        self.unprepare(datastructure)
        datastructure.setError(self.getWidgetId(), err, err_mapping)
        return False

    def render(self, mode, datastructure, **kw):
        """Render this widget from the datastructure or datamodel."""
        render_method = 'widget_file_render'
        meth = getattr(self, render_method, None)
        if meth is None:
            raise RuntimeError("Unknown Render Method %s for widget type %s"
                               % (render_method, self.getId()))
        file_info = self.getFileInfo(datastructure)

        return meth(mode=mode, datastructure=datastructure, **file_info)

InitializeClass(CPSFileWidget)

widgetRegistry.register(CPSFileWidget)

##################################################

class CPSImageWidget(CPSFileWidget):
    """Image widget."""
    meta_type = 'Image Widget'

    field_types = ('CPS Image Field',)

    _properties = CPSFileWidget._properties + (
        {'id': 'display_width', 'type': 'int', 'mode': 'w',
         'label': 'Display width'},
        {'id': 'display_height', 'type': 'int', 'mode': 'w',
         'label': 'Display height'},
        {'id': 'allow_resize', 'type': 'boolean', 'mode': 'w',
         'label': 'Enable to resize img to lower size'},
        )

    display_height = 0
    display_width = 0
    allow_resize = 0

    def getImageInfo(self, datastructure):
        """Get the image info from the datastructure."""
        image_info = self.getFileInfo(datastructure)

        if image_info['empty_file']:
            tag = ''
            height = 0
            width = 0
        else:
            image = datastructure[self.getWidgetId()]
            from OFS.Image import getImageInfo
            image.seek(0)
            data = image.read(24)
            ct, width, height = getImageInfo(data)

            if width < 0:
                width = None
            if height < 0:
                height = None

            if (self.allow_resize
                and height is not None
                and width  is not None):
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

            title = image_info['current_title']
            alt = title or ''
            if height is None or width is None:
                tag = renderHtmlTag('img', src=image_info['content_url'],
                                    alt=alt, title=title)
            else:
                tag = renderHtmlTag('img', src=image_info['content_url'],
                                    width=str(width), height=str(height),
                                    alt=alt, title=title)

        image_info['height'] = height
        image_info['width'] = width
        image_info['image_tag'] = tag
        return image_info

    def getResizedImage(self, file, fileid, filetitle, resize_op):
        """Get the resized image from information in datastructure"""
        file = StringIO(str(file.data)) # XXX use OFSFileIO
        size = (self.display_width,
                self.display_height)
        for s in self.getImgSizes():
            if s['id'] == resize_op:
                resize = s['size']
                break
        else:
            resize = None
        if resize and resize < size:
            size = resize
        if size[0] and size[1]:
            try:
                img = PIL.Image.open(file)
                img.thumbnail(size,
                              resample=PIL.Image.ANTIALIAS)
                file.seek(0)
                img.save(file, format=img.format)
            except (NameError, IOError, ValueError, SystemError):
                LOG('CPSImageWidget', PROBLEM,
                    "Failed to resize file %s keep original" \
                    % fileid)
        image = Image(fileid, filetitle, file)
        return image

    def prepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel."""
        CPSFileWidget.prepare(self, datastructure, **kw)
        if self.allow_resize:
            datastructure[self.getWidgetId() + '_resize'] = ''

    def maybeKeepOriginal(self, image, datastructure):
        return

    def makeFile(self, fileid, fileupload, datastructure):
        image = Image(fileid, fileid, fileupload)
        if self.allow_resize:
            self.maybeKeepOriginal(image, datastructure)
            resize_op = datastructure[self.getWidgetId() + '_resize']
            image = self.getResizedImage(image, fileid, fileid, resize_op)
        return image

    def checkFileName(self, fileid, mimetype):
        if mimetype and mimetype.normalized().startswith('image'):
            return '', {}
        return 'cpsschemas_err_image', {}

    def render(self, mode, datastructure, **kw):
        render_method = 'widget_image_render'
        meth = getattr(self, render_method, None)
        if meth is None:
            raise RuntimeError("Unknown Render Method %s for widget type %s"
                               % (render_method, self.getId()))
        img_info = self.getImageInfo(datastructure)
        return meth(mode=mode, datastructure=datastructure, **img_info)

InitializeClass(CPSImageWidget)

widgetRegistry.register(CPSImageWidget)

##################################################

class CPSCompoundWidget(CPSWidget):
    """Widget with customizable logic and presentation.

    Allows the use of other widgets to do the rendering.
    """
    meta_type = 'Compound Widget'

    _properties = (
        CPSWidget._properties[:2] + (
        {'id': 'widget_ids', 'type': 'tokens', 'mode': 'w',
         'label': 'Widget ids'},
        {'id': 'render_method', 'type': 'string', 'mode': 'w',
         'label': 'Render Method'},
        {'id': 'prepare_validate_method', 'type': 'string', 'mode': 'w',
         'label': 'Prepare & Validate Method'},
        ) + CPSWidget._properties[2:]
        )
    widget_ids = []
    widget_type = None # Compat with old instances
    render_method = 'widget_compound_default_render'
    prepare_validate_method = ''

    _old_render_methods = {
        'Link Widget': 'widget_link_render',
        'Text Image Widget': 'widget_textimage_render',
        'Search Widget': 'widget_search_render',
        'Image Link Widget': 'widget_imagelink_render',
        'Search Location Widget': 'widget_searchlocation_render',
        }

    def _getRenderMethod(self):
        """Get the render method."""
        name = self._old_render_methods.get(self.widget_type,
                                            self.render_method)
        meth = getattr(self, name, None)
        if meth is None:
            raise RuntimeError("Unknown render method %r for widget %s" %
                               (name, self.getWidgetId()))
        return meth

    _old_prepare_validate_methods = {
        'Link Widget': '',
        'Text Image Widget': 'widget_textimage_prepare_validate',
        'Search Widget': '',
        'Image Link Widget': 'widget_imagelink_prepare_validate',
        'Search Location Widget': 'widget_searchlocation_prepare_validate',
        }


    def _getPrepareValidateMethod(self):
        """Get the prepare/validate method."""
        # Compatibility for old instances
        name = self._old_prepare_validate_methods.get(self.widget_type,
                                               self.prepare_validate_method)
        if not name:
            meth = lambda *args, **kw: True
        else:
            meth = getattr(self, name, None)
        if meth is None:
            raise RuntimeError("Unknown prepare/validate method '%s' "
                               "for widget %s" % (name, self.getWidgetId()))
        return meth

    def getFieldTypes(self):
        """Get field types from the underlying widgets."""
        return [] #X XXX

    def getFieldInits(self):
        """Get field inits from the underlying widgets."""
        return [] # XXX

    def prepare(self, datastructure, **kw):
        """Prepare the underlying widgets."""
        # Prepare each widget
        layout = aq_parent(aq_inner(self))
        for widget_id in self.widget_ids:
            widget = layout[widget_id]
            widget.prepare(datastructure, **kw)
        # Now prepare compound
        prepare = self._getPrepareValidateMethod()
        return prepare('prepare', datastructure)

    def validate(self, datastructure, **kw):
        """Validate the underlying widgets."""
        validate = self._getPrepareValidateMethod()
        # Pre-validate compound (may fixup the datastructure)
        ret = validate('prevalidate', datastructure)
        if not ret and ret is not None:
            # None is allowed to mean "ok"
            return False
        # Now validate each widget
        layout = aq_parent(aq_inner(self))
        ret = True
        for widget_id in self.widget_ids:
            widget = layout[widget_id]
            ret = widget.validate(datastructure, **kw) and ret
        # Post-validate
        return ret and validate('validate', datastructure)

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        layout = aq_parent(aq_inner(self))
        widget_infos = kw['widget_infos']
        cells = []
        for widget_id in self.widget_ids:
            cell = {}
            # widget, widget_mode, css_class
            cell.update(widget_infos[widget_id])
            widget = layout[widget_id]
            widget_mode = cell['widget_mode']
            rendered = widget.render(widget_mode, datastructure, **kw)
            rendered = rendered.strip()
            cell['widget_rendered'] = rendered
            if not widget.hidden_empty or rendered:
                # do not add widgets to be hidden when empty
                cells.append(cell)
        render = self._getRenderMethod()
        return render(mode=mode, datastructure=datastructure,
                      cells=cells, **kw)

InitializeClass(CPSCompoundWidget)

widgetRegistry.register(CPSCompoundWidget)


class CPSProgrammerCompoundWidget(CPSCompoundWidget):
    """Base class for compound widgets defined in code.

    They don't need to have the "method" fields customizable,
    because these are defined by their class.
    """
    meta_type = 'Code Compound Widget'
    _properties = (
        CPSCompoundWidget._properties[:3] +
        # skip render_method
        # skip prepare_validate_method
        CPSCompoundWidget._properties[5:]
        )
    field_types = ()

InitializeClass(CPSProgrammerCompoundWidget)


class CPSCustomizableWidget(CPSCompoundWidget):
    """Obsolete customizable widget.

    Obsolete, kept for old instances. CPSCompoundWidget should
    be used for new widgets.
    """
    meta_type = 'Obsolete Customizable Widget'

InitializeClass(CPSCustomizableWidget)

##################################################

class CPSBylineWidget(CPSWidget):
    """Byline widget showing credentials and document status."""
    meta_type = 'Byline Widget'

    def prepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel."""
        pass
            
    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel."""
        return 1

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        datamodel = datastructure.getDataModel()
        # get the object containing this widget
        if datamodel.getObject():
            value = datamodel.getObject().aq_inner.aq_parent
        else:
            value = None
        render_method = 'widget_byline_render'
        meth = getattr(self, render_method, None)
        if meth is None:
            raise RuntimeError("Unknown Render Method %s for widget type %s"
                               % (render_method, self.getId()))
        return meth(mode=mode, value=value)


InitializeClass(CPSBylineWidget)

widgetRegistry.register(CPSBylineWidget)
