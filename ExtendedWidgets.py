# (C) Copyright 2003-2009 Nuxeo SA <http://nuxeo.com>
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
"""Extended widget types.

Definition of extended widget types.
"""

from logging import getLogger
import warnings
import zipfile
import operator
import os
from tempfile import mkstemp
from cgi import escape
from re import match

from Globals import InitializeClass
from Acquisition import aq_base, aq_parent, aq_inner
from DateTime.DateTime import DateTime

from Products.PythonScripts.standard import newline_to_br
from Products.PythonScripts.standard import structured_text
from reStructuredText import HTML

from Products.CMFCore.utils import getToolByName

from Products.CPSUtil.html import XhtmlSanitizer
from Products.CPSUtil.html import renderHtmlTag
from Products.CPSUtil.text import get_final_encoding
from Products.CPSUtil.resourceregistry import JSGlobalMethodResource
from Products.CPSUtil.resourceregistry import JSLocalMethodResource
from Products.CPSUtil.resourceregistry import HtmlResource
from Products.CPSSchemas.Widget import CPSWidget
from Products.CPSSchemas.BasicWidgets import CPSSelectWidget
from Products.CPSSchemas.BasicWidgets import CPSMultiSelectWidget
from Products.CPSSchemas.BasicWidgets import CPSStringWidget
from Products.CPSSchemas.BasicWidgets import CPSImageWidget
from Products.CPSSchemas.BasicWidgets import CPSFileWidget
from Products.CPSSchemas.widgets.compound import CPSProgrammerCompoundWidget
from Products.CPSSchemas.swfHeaderData import analyseContent

warnings.warn("Products.CPSchemas.ExtendedWidgets is currently been split and "
              "will be kept as a compatibility alias or holding deprecated "
              "widgets only. It should disappear in CPS 3.6",
              DeprecationWarning, stacklevel=2)

from widgets.select import CPSGenericSelectWidget
from widgets.select import CPSGenericMultiSelectWidget
from widgets.select import CPSExtendedSelectWidget

logger = getLogger('Products.CPSSChemas.ExtendedWidgets')

register_js = JSGlobalMethodResource.register

TINY_MCE_RSRC = register_js('tiny_mce.js')

DISPLAY_TINY_MCE_RSRC = JSLocalMethodResource.register('display_tiny_mce.js',
                                                       depends=TINY_MCE_RSRC)

FCK_EDITOR_RSRC = register_js('fckeditor.js')

FCK_EDITOR_FORM_RSRC = register_js('fckeditor_form.js',
                                   depends=(FCK_EDITOR_RSRC,))

POPUP_RTE_RSRC = HtmlResource.register('popup_rte_script', """
    <script type="text/javascript">
     function popup_rte(input_id, label_edit) {
       var args, value;
       var width = 640;
       var height = 520;
       value = document.getElementById(input_id).value;
       args = '?input_id='+input_id+'&amp;label_edit='+escape(label_edit);
       str_window_features = 'toolbar=0,scrollbars=0,location=0,statusbar=0,menubar=0,resizable=1,dependent=1,width=' + width + ',height=' + height;
       popup = window.open(popup_editor_form + args, input_id, str_window_features);
       return false;
     }
    </script>
""")

RTE_RESOURCES = dict(tinymce=(DISPLAY_TINY_MCE_RSRC,),
                     fckeditor=(FCK_EDITOR_RSRC, FCK_EDITOR_FORM_RSRC),
                     )

##################################################
# previously named CPSTextAreaWidget in BasicWidget r1.78
class CPSTextWidget(CPSStringWidget):
    """Text widget."""
    meta_type = 'Text Widget'

    # Warning if configurable the widget require field[1] and field[2]
    field_types = ('CPS String Field',  # text value
                   'CPS String Field',  # render_position if configurable
                   'CPS String Field')  # render_format if configurable
    field_inits = ({'is_searchabletext': 1,}, {}, {})

    _properties = CPSWidget._properties + (
        {'id': 'width', 'type': 'int', 'mode': 'w',
         'label': 'Width'},
        {'id': 'height', 'type': 'int', 'mode': 'w',
         'label': 'Height'},
        {'id': 'size_max', 'type': 'int', 'mode': 'w',
         'label': 'Max Size'},
        {'id': 'xhtml_sanitize', 'type': 'selection', 'mode': 'w',
         'select_variable': 'all_xhtml_sanitize_options',
         'label': 'XHTML sanitize the content'},
        {'id': 'xhtml_sanitize_system',
         'type': 'string', 'mode': 'w',
         'label': 'XHTML sanitize through system command line '
         '(use %(encoding)s for current encoding, %(file)s for the tmp file)'},
        {'id': 'file_uploader', 'type': 'boolean', 'mode': 'w',
         'label': 'Add a file uploader to the widget UI'},

        {'id': 'html_editor_type', 'type': 'string', 'mode': 'w',
         'label': 'The name of the HTML editor to use'},

        {'id': 'html_editor_position', 'type': 'selection', 'mode': 'w',
         'select_variable': 'all_html_editor_positions',
         'label': 'HTML rich text editor position'},
        {'id': 'render_format', 'type': 'selection', 'mode': 'w',
         'select_variable': 'all_render_formats',
         'label': 'Render format'},
        {'id': 'render_position', 'type': 'selection', 'mode': 'w',
         'select_variable': 'all_render_positions',
         'label': 'Render position'},
        {'id': 'configurable', 'type': 'selection', 'mode': 'w',
         'select_variable': 'all_configurable',
         'label': 'What is user configurable (require extra fields)'},
        )
    all_xhtml_sanitize_options = ['no', 'builtin', 'system']
    all_configurable = ['nothing', 'position', 'format', 'position and format']
    all_render_positions = ['normal', 'col_left', 'col_right']
    all_render_formats = ['text', 'html', 'rst']
    all_html_editor_positions = ['popup', 'embedded']

    width = 40
    height = 5
    size_max = 2*1024*1024
    xhtml_sanitize = False
    # Notes about using tidy :
    # * force-output makes tidy produce an output even if errors were found.
    # * show-body-only outputs only the content of the body tag.
    # * write-back modifies the file in place.
    xhtml_sanitize_system = 'tidy -indent -wrap 80 --input-encoding %(encoding)s --output-encoding %(encoding)s --force-output yes --clean yes --drop-font-tags yes --drop-proprietary-attributes yes --show-body-only yes --write-back yes --output-xhtml yes --show-errors 0 --show-warnings no --hide-comments no %(file)s 2>/dev/null'
    file_uploader = False

    # Possible values are "tinymce" and "fckeditor"
    html_editor_type = 'tinymce'

    render_position = all_render_positions[0]
    render_format = all_render_formats[0]
    html_editor_position = all_html_editor_positions[0]
    configurable = 'nothing'
    input_encoding = 'unicode'
    output_encoding = 'unicode'

    # Associating the widget label with an input area to improve the widget
    # accessibility.
    has_input_area = True

    xhtml_sanitizer = XhtmlSanitizer()

    tidy_encodings = {'utf-8': 'utf8',
                      'iso-8859-15': 'latin1'}

    def prepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel."""
        datamodel = datastructure.getDataModel()
        widget_id = self.getWidgetId()
        datastructure[widget_id] = datamodel[self.fields[0]]
        rposition = self.render_position
        rformat = self.render_format
        if self.configurable != 'nothing':
            if len(self.fields) > 1:
                v  = datamodel[self.fields[1]]
                if v in self.all_render_positions:
                    rposition = v
            if len(self.fields) > 2:
                v = datamodel[self.fields[2]]
                if v in self.all_render_formats:
                    rformat = v
        datastructure[widget_id + '_fileupload'] = None
        datastructure[widget_id + '_rposition'] = rposition
        datastructure[widget_id + '_rformat'] = rformat

    def make_xhtml_sanitize_cmd(self, **kw):
        """Provide the xhtml sanitizing command

        >>> wid = CPSTextWidget('the_widget')
        >>> wid.manage_changeProperties(
        ...     xhtml_sanitize_system="on %(file)s use %(encoding)s")
        >>> wid.make_xhtml_sanitize_cmd(file='/tmp/tmpfile', encoding='utf8')
        'on /tmp/tmpfile use utf8'

        There are a few specific rules for (default) tidy:
        >>> wid.manage_changeProperties(
        ...     xhtml_sanitize_system="tidy --char-encoding=%(encoding)s "
        ...                           "%(file)s")
        >>> wid.make_xhtml_sanitize_cmd(file='tmpfile', encoding='utf-8')
        'tidy --char-encoding=utf8 tmpfile'
        >>> wid.make_xhtml_sanitize_cmd(file='tmpfile', encoding='iso-8859-15')
        'tidy --char-encoding=latin1 tmpfile'

        Old style prop as before #2186:
        >>> wid.manage_changeProperties(
        ...     xhtml_sanitize_system="on %s work as usual")
        >>> wid.make_xhtml_sanitize_cmd(file='/tmp/tmpfile', encoding='utf8')
        'on /tmp/tmpfile work as usual'

        The file kw arg is in that case implicit and really needed:
        >>> try: wid.make_xhtml_sanitize_cmd(encoding='hop')
        ... except KeyError, e: print e
        'file'
        """
        fmt_cmd = self.xhtml_sanitize_system
        if fmt_cmd.startswith('tidy '):
            encoding = kw.get('encoding', '').strip().lower()
            kw['encoding'] = self.tidy_encodings.get(encoding, encoding)

        if '%(file)s' in fmt_cmd:
            return fmt_cmd % kw

        # old style, see #2186
        return fmt_cmd % kw['file']


    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel."""
        widget_id = self.getWidgetId()
        file_upload = datastructure.get(widget_id + '_fileupload', None)
        file_upload_valid = False
        if file_upload is not None:
            ms = self.size_max
            file_upload.seek(0)
            read_size = len(file_upload.read(ms + 1))
            if read_size > ms:
                # Size is expressed in human readable value
                max_size_str = self.getHumanReadableSize(ms)
                err = 'cpsschemas_err_file_too_big ${max_size}'
                err_mapping = {'max_size': max_size_str}
                return self.doesNotValidate(err, err_mapping,
                                            file, datastructure)
            file_upload.seek(0)
            value = file_upload.read()
            read_size = len(value)
            if read_size > 0:
                file_upload_valid = True
        if not file_upload_valid:
            value = datastructure[widget_id]
        err, v = self._extractValue(value)

        if err:
            datastructure.setError(widget_id, err)
            datastructure[widget_id] = v
        else:
            datamodel = datastructure.getDataModel()
            # Validating rposition and rformat entered by the user and
            # correcting them if necessary.
            if self.configurable != 'nothing':
                if len(self.fields) < 2:
                    raise ValueError("Widget %s: user configurable format "
                                     "& position need extra fields" % widget_id)
                if len(self.fields) > 1:
                    rposition = datastructure[widget_id + '_rposition']
                    if rposition and rposition in self.all_render_positions:
                        datamodel[self.fields[1]] = rposition
                if len(self.fields) > 2:
                    rformat = datastructure[widget_id + '_rformat']
                    if rformat and rformat in self.all_render_formats:
                        datamodel[self.fields[2]] = rformat
            else:
                # Defaulting to the widget property since no fields are used to
                # store the format or the position.
                rformat = self.render_format
            if rformat == 'html':
                if self.xhtml_sanitize == 'builtin':
                    self.xhtml_sanitizer.reset()
                    self.xhtml_sanitizer.feed(v)
                    v = self.xhtml_sanitizer.getResult()
                elif self.xhtml_sanitize == 'system':
                    file_to_clean_fd, file_to_clean_path = mkstemp(
                        suffix=".xhtml",
                        prefix="cps-schemas",
                        )
                    file_to_clean = os.fdopen(file_to_clean_fd, 'w')
                    encoding = get_final_encoding(self)
                    file_to_clean.write(v.encode(encoding))
                    file_to_clean.close()

                    cmd = self.make_xhtml_sanitize_cmd(encoding=encoding,
                                                       file=file_to_clean_path)
                    os.system(cmd)

                    file_to_clean = open(file_to_clean_path)
                    v = file_to_clean.read()
                    v = v.decode(encoding)
                    file_to_clean.close()
                    os.remove(file_to_clean_path)

            datamodel[self.fields[0]] = v
            if file_upload_valid or self.xhtml_sanitize:
                # If the file_upload is valid we update the datastructure so
                # that the immediate view after the modification has been done
                # shows the content of the file upload instead of the old value.
                self.prepare(datastructure)
        return not err

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        render_method = 'widget_text_render'
        meth = getattr(self, render_method, None)
        if meth is None:
            raise RuntimeError("Unknown Render Method %s for widget type %s"
                               % (render_method, self.getId()))
        widget_id = self.getWidgetId()
        value = datastructure[widget_id]
        if not value.strip() and self.hidden_empty and mode == 'view':
            return '' # See #2115
        rposition = datastructure[widget_id + '_rposition']
        rformat = datastructure[widget_id + '_rformat']
        if mode == 'view':
            if rformat == 'text':
                value = newline_to_br(escape(value))
            elif rformat == 'html':
                pass
            elif rformat == 'rst':
                encs = [self.input_encoding, self.output_encoding]
                encs = [enc == 'unicode' and get_final_encoding(self)
                        for enc in encs]
                in_enc, out_enc = encs
                value = HTML(value,
                             output_encoding=out_enc,
                             input_encoding=in_enc,
                             initial_header_level=2, report_level=0)
            # The pre render format is not a proposed choice in the UI anymore.
            # BBB compatibility code, will be removed in CPS 3.5.0.
            elif rformat == 'pre':
                value = '<pre>' + escape(value) + '</pre>'
            # The stx render format is not a proposed choice in the UI anymore.
            # BBB compatibility code, will be removed in CPS 3.5.0.
            elif rformat == 'stx':
                value = structured_text(value)
            else:
                RuntimeError("unknown render_format '%s' for '%s'" %
                             (rformat, self.getId()))
            if rposition == 'col_left':
                cssclass = 'dcolleft'
            elif rposition == 'col_right':
                cssclass = 'dcolright'
            else:
                cssclass = 'ddefault'
            return '<div class="%s">\n%s\n</div>' % (cssclass, value)
        if mode == 'edit' and rformat == 'html':
            position = self.html_editor_position
            if position == 'embedded':
                for rid in RTE_RESOURCES[self.html_editor_type]:
                    self.requireResource(rid)
            elif position == 'popup':
                self.requireResource('popup_rte_script')

        return meth(mode=mode, datastructure=datastructure, value=value,
                    file_uploader=self.file_uploader,
                    html_editor_type=self.html_editor_type,
                    render_position=rposition, render_format=rformat,
                    html_editor_position=self.html_editor_position,
                    configurable=str(self.configurable))

InitializeClass(CPSTextWidget)

##################################################
# previously named CPSDateWidget in BasicWidget r1.78
class CPSDateTimeWidget(CPSWidget):
    """DateTime widget.

    A widget that displays and makes it possible to edit a DateTime object.
    View and edit mode can be done in the ISO 8601 date format (YYYY-mm-dd)
    or in a localized format (mm/dd/YYYY for English and dd/mm/YYYY for the rest
    of the world) cf. http://www.w3.org/TR/NOTE-datetime
    """
    meta_type = 'DateTime Widget'

    field_types = ('CPS DateTime Field',)

    _properties = CPSWidget._properties + (
        {'id': 'view_format', 'type': 'string', 'mode': 'w',
         'label': 'View format (short, medium or long)'},
        {'id': 'time_setting', 'type': 'boolean', 'mode': 'w',
         'label': 'Enabling the setting of time of the day'},
        {'id': 'time_hour_default', 'type': 'string', 'mode': 'w',
         'label': 'default hour for time'},
        {'id': 'time_minutes_default', 'type': 'string', 'mode': 'w',
         'label': 'default minutes for time'},
        {'id': 'must_future', 'type': 'boolean', 'mode': 'w',
         'label': 'Must value be in the (lax) future if provided ?'},
        {'id': 'must_past', 'type': 'boolean', 'mode': 'w',
         'label': 'Must value be in the (lax) past if provided ?'},
        )
    # When will CPS default to the more sensible ISO 8601 date format?
    #view_format = 'iso8601_medium_easy'
    view_format = 'medium'
    time_setting = 1
    time_hour_default = '12'
    time_minutes_default = '00'
    must_past = False
    must_future = False

    # Associating the widget label with an input area to improve the widget
    # accessibility.
    has_input_area = True

    def getDateTimeInfo(self, value, mode=None, layout_mode=None):
        """Return a tuple that is used to set the datastructure

        Called in prepare when mode is not known, and called again in render
        when mode is known, because a default value has to be provided in edit
        mode (current date time).
        """
        # default values
        date = ''
        hour = ''
        minute = ''

        # value is set to current time if:
        # - value is not alrady set and
        # - widget is required an
        # - mode is 'edit' or 'create'
        if (not value and self.isRequired(layout_mode=layout_mode)
            and mode in ['edit', 'create']):
            value = DateTime()

        if value == 'None':
            value = None
        if value:
            # Backward compatibility test, this logic is not used by the
            # current code.
            if isinstance(value, str):
                value = DateTime(value)
            d = str(value.day())
            m = str(value.month())
            y = str(value.year())
            if self.view_format.startswith('iso8601'):
                date = '%s-%s-%s' % (y, m, d)
            else:
                locale = self.translation_service.getSelectedLanguage()
                if locale in ('en', 'hu'):
                    date = '%s/%s/%s' % (m, d, y)
                else:
                    date = '%s/%s/%s' % (d, m, y)
            hour = str(value.h_24())
            minute = str(value.minute())

        # if hour and minute are not set, set default values
        hour = hour or self.time_hour_default
        minute = minute or self.time_minutes_default

        return (value, date, hour, minute)

    def prepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel."""
        datamodel = datastructure.getDataModel()
        v = datamodel[self.fields[0]]

        # get date time info, mode is not known here
        v, date, hour, minute = self.getDateTimeInfo(v, mode=None)

        widget_id = self.getWidgetId()
        datastructure[widget_id] = v
        datastructure[widget_id + '_date'] = date
        datastructure[widget_id + '_hour'] = hour or self.time_hour_default
        datastructure[widget_id + '_minute'] = minute or self.time_minutes_default

    def validate(self, datastructure, layout_mode=None, **kw):
        """Validate datastructure and update datamodel."""
        datamodel = datastructure.getDataModel()
        field_id = self.fields[0]
        widget_id = self.getWidgetId()

        date = datastructure[widget_id + '_date'].strip()
        hour = datastructure[widget_id + '_hour'].strip() or \
               self.time_hour_default
        minute = datastructure[widget_id + '_minute'].strip() or \
                 self.time_minutes_default

        if not (date):
            if self.isRequired(layout_mode=layout_mode):
                datastructure[widget_id] = ''
                datastructure.setError(widget_id, 'cpsschemas_err_required')
                return 0
            else:
                datamodel[field_id] = None
                return 1

        if self.view_format.startswith('iso8601'):
            if match(r'^[0-9]+-[0-9]{2}-[0-9]{2}', date) is not None:
                y, m, d = date.split('-')
            else:
                datastructure.setError(widget_id, 'cpsschemas_err_date')
                return 0
        else:
            if match(r'^[0-9]?[0-9]/[0-9]?[0-9]/[0-9]{2,4}$', date) is not None:
                locale = self.translation_service.getSelectedLanguage()
                if locale in ('en', 'hu'):
                    m, d, y = date.split('/')
                else:
                    d, m, y = date.split('/')
            else:
                datastructure.setError(widget_id, 'cpsschemas_err_date')
                return 0

        try:
            v = DateTime(int(y), int(m), int(d), int(hour), int(minute))
        except (ValueError, TypeError, DateTime.DateTimeError,
                DateTime.SyntaxError, DateTime.DateError):
            datastructure.setError(widget_id, 'cpsschemas_err_date')
            return 0

        if self.must_future or self.must_past: # avoid one more costly DateTime
            now = DateTime()
            if self.must_future:
                if now > v:
                    datastructure.setError(widget_id,
                                           'cpsschemas_err_date_must_future')
                    return False

            elif now < v:
                datastructure.setError(widget_id,
                                       'cpsschemas_err_date_must_past')
                return False

        datastructure[widget_id] = v
        datamodel[field_id] = v
        return True

    def render(self, mode, datastructure, layout_mode=None, **kw):
        """Render in mode from datastructure."""
        render_method = 'widget_datetime_render'
        meth = getattr(self, render_method, None)
        if meth is None:
            raise RuntimeError("Unknown Render Method %s for widget type %s"
                               % (render_method, self.getId()))

        # XXX AT: datastructure has to be set again here, in case we're in edit
        # or create mode, because a default value has to be provided.
        if mode in ['edit', 'create']:
            datamodel = datastructure.getDataModel()
            v = datamodel[self.fields[0]]
            v, date, hour, minute = self.getDateTimeInfo(
                v, mode=mode, layout_mode=layout_mode)
            widget_id = self.getWidgetId()
            datastructure[widget_id] = v
            datastructure[widget_id + '_date'] = date
            datastructure[widget_id + '_hour'] = hour or self.time_hour_default
            datastructure[widget_id + '_minute'] = minute or self.time_minutes_default

        return meth(mode=mode, datastructure=datastructure)


InitializeClass(CPSDateTimeWidget)

##################################################
class CPSAttachedFileWidget(CPSFileWidget):
    """AttachedFile widget."""
    meta_type = 'AttachedFile Widget'

    field_types = ('CPS File Field',   # File
                   'CPS String Field', # Plain text for indexing (optional)
                   'CPS File Field',   # Preview (HTML, optional)
                   'CPS SubObjects Field',)

    field_inits = ({'is_searchabletext': 0,
                    'suffix_text': '_f1', # _f# are autocomputed field ext
                    'suffix_html': '_f2',
                    'suffix_html_subfiles': '_f3',
                    },
                   {'is_searchabletext': 1, 'validate_none': True}, {}, {},
                   )

    _properties = CPSFileWidget._properties + (
        {'id': 'display_html_preview', 'type': 'boolean', 'mode': 'w',
         'label': 'Display link to HTML preview in view mode'},
        {'id': 'display_printable_version', 'type': 'boolean', 'mode': 'w',
         'label': 'Display link to printable version in view mode'},
        {'id': 'allowed_suffixes', 'type': 'tokens', 'mode': 'w',
         'label': 'Allowed file suffixes (ex: .html .odt)'},
        )
    display_html_preview = True
    display_printable_version = True
    allowed_suffixes = []

    def prepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel."""
        CPSFileWidget.prepare(self, datastructure, **kw)
        datamodel = datastructure.getDataModel()
        widget_id = self.getWidgetId()

        # Compute preview info for widget.
        if len(self.fields) > 2 and datamodel.get(self.fields[2]) is not None:
            preview_id = self.fields[2]
        else:
            preview_id = None
        datastructure[widget_id + '_preview'] = preview_id

    def checkFileName(self, fileid, mimetype):
        if self.allowed_suffixes:
            base, suffix = os.path.splitext(fileid)
            if suffix not in self.allowed_suffixes:
                err = 'cpsschemas_err_file_bad_suffix ${allowed_file_suffixes}'
                err_mapping = {'allowed_file_suffixes':
                               ' '.join(self.allowed_suffixes)}
                return err, err_mapping
        return '', {}

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        render_method = 'widget_attachedfile_render'
        meth = getattr(self, render_method, None)
        if meth is None:
            raise RuntimeError("Unknown Render Method %s for widget type %s"
                               % (render_method, self.getId()))
        file_info = self.getFileInfo(datastructure)

        return meth(mode=mode, datastructure=datastructure,
                    **file_info)

InitializeClass(CPSAttachedFileWidget)

##################################################

class CPSZippedHtmlWidget(CPSAttachedFileWidget):
    """CPS ZippedHtml widget.

    A zip file that contains html which can be viewed online.
    Use index.html or any html file from the zip as preview page.
    """

    meta_type = 'ZippedHtml Widget'

    size_max = 1024*1024

    # FIXME checkFileName() from ancestor is never called after changeset [30791]
    # We need to fix it over there.
    #allowed_suffixes = ['.zip']

    def _is_zipfile(self, datastructure, **kw):
        # Check the zip file validity
        choice = datastructure[self.getWidgetId()+'_choice']
        if choice == 'change':
            validated = False
            file_upload = datastructure.get(self.getWidgetId())
            try:
                zf = zipfile.ZipFile(file_upload, 'r')
            except zipfile.BadZipfile:
                pass
            else:
                if zf.testzip() is None:
                    validated = True
                    zf.close()
            return validated
        return True

    def validate(self, datastructure, **kw):
        # Validate datastructure and update datamodel.
        return (CPSAttachedFileWidget.validate(self, datastructure, **kw) and
                self._is_zipfile(datastructure, **kw))

    def _getIndexPath(self, datastructure):
        file_upload = datastructure.get(self.getWidgetId())
        # Creation time
        if not file_upload:
            return ''
        # Here the zipfile has been validated already.
        zf = zipfile.ZipFile(file_upload, 'r')
        all_files = [info.filename for info in zf.infolist()]
        html_files = [f for f in all_files
                      if (f.lower().endswith('.html') or
                          f.lower().endswith('.htm'))]
        index_files = [f for f in html_files
                       if f.lower().find('index.htm') >= 0]
        index_path = None
        if index_files:
            index_path = index_files[0]
        elif html_files:
            index_path = html_files[0]
        zf.close()
        return index_path

    def render(self, mode, datastructure, **kw):
        render_method = 'widget_zippedhtml_render'
        meth = getattr(self, render_method, None)
        if meth is None:
            raise RuntimeError("Unknown Render Method %s for widget type %s"
                               % (render_method, self.getId()))
        file_info = self.getFileInfo(datastructure)
        file_info['index_path'] = self._getIndexPath(datastructure)
        return meth(mode=mode, datastructure=datastructure, **file_info)

InitializeClass(CPSZippedHtmlWidget)

#################################################

class CPSRichTextEditorWidget(CPSWidget):
    """Rich Text Editor widget.

    THIS WIDGET SHOULD NOT BE USED AND IS DEPRECATED.

    Use the Text Widget which provides both HTML and text formats.
    """
    meta_type = 'Rich Text Editor Widget'

    field_types = ('CPS String Field',)
    field_inits = ({'is_searchabletext': 1,},)

    width = 40
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
        datastructure[self.getWidgetId()] = datamodel[self.fields[0]]

    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel."""
        value = datastructure[self.getWidgetId()]
        try:
            v = str(value)
        except ValueError:
            datastructure.setError(self.getWidgetId(),
                                   "cpsschemas_err_textarea")
            ok = 0
        else:
            datamodel = datastructure.getDataModel()
            datamodel[self.fields[0]] = v
            ok = 1
        return ok

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        warnings.warn("The Rich Text Editor Widget (%s/%s) is deprecated "
                      "and will be removed in CPS 3.5.0. Use a Text Widget "
                      "instead" % (aq_parent(aq_inner(self)).getId(),
                                   self.getWidgetId()), DeprecationWarning)
        value = datastructure[self.getWidgetId()]
        if mode == 'view':
            # Return HTML directly
            return value
        elif mode == 'edit':
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
                        current_name=current_name)
        raise RuntimeError("unknown mode %s" % mode)

InitializeClass(CPSRichTextEditorWidget)

##########################################

class CPSInternalLinksWidget(CPSWidget):
    """Internal Links widget."""
    meta_type = 'InternalLinks Widget'

    field_types = ('CPS String List Field',)
    field_inits = ({'is_searchabletext': 1,},)

    _properties = CPSWidget._properties + (
        {'id': 'new_window', 'type': 'boolean', 'mode': 'w',
         'label': 'Display in a new window'},
        {'id': 'size', 'type': 'int', 'mode': 'w',
         'label': 'Links displayed'},
        {'id': 'absolute', 'type': 'boolean', 'mode': 'w',
         'label': 'Links displayed with absolute URL'},
        )
    new_window = 0
    size = 0
    absolute = False

    def prepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel."""
        datamodel = datastructure.getDataModel()
        datastructure[self.getWidgetId()] = datamodel[self.fields[0]]

    def validate(self, datastructure, layout_mode=None, **kw):
        """Validate datastructure and update datamodel."""
        widget_id = self.getWidgetId()
        value = datastructure[widget_id]
        err = 0
        if (value == [] or value == ['']) and self.isRequired(
            layout_mode=layout_mode):
            err = 'cpsschemas_err_required'
        v = []


        for line in value:
            if line.strip():
                v.append(line)

        if err:
            datastructure.setError(widget_id, err)
        else:
            datamodel = datastructure.getDataModel()
            datamodel[self.fields[0]] = v
            self.prepare(datastructure)

        return not err

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        if mode not in ('view', 'edit'):
            raise RuntimeError('unknown mode %s' % mode)

        render_method = 'widget_internallinks_render'
        meth = getattr(self, render_method, None)

        return meth(mode=mode, datastructure=datastructure)

InitializeClass(CPSInternalLinksWidget)

##################################################

class CPSPhotoWidget(CPSImageWidget):
    """Photo widget."""
    meta_type = 'Photo Widget'

    field_types = ('CPS Image Field',   # Image
                   'CPS String Field',  # Caption
                   'CPS String Field',  # render_position if configurable
                   'CPS Image Field',   # Original photo
                   'CPS String Field',  # Title
                   'CPS String Field',  # Alternate text for accessibility
                   )
    field_inits = ({}, {'is_searchabletext': 1,}, {}, {}, {}, {})

    _properties = CPSImageWidget._properties + (
        {'id': 'render_position', 'type': 'selection', 'mode': 'w',
         'select_variable': 'all_render_positions',
         'label': 'Render position'},
        {'id': 'configurable', 'type': 'selection', 'mode': 'w',
         'select_variable': 'all_configurable',
         'label': 'What is user configurable, require extra fields'},
        {'id': 'keep_original', 'type': 'boolean', 'mode': 'w',
         'label': 'Keep original image'},
        )
    all_configurable = ['nothing', 'position']
    all_render_positions = ['left', 'center', 'right']

    allow_resize = True
    render_position = all_render_positions[0]
    configurable = all_configurable[0]
    keep_original = True

    def prepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel."""
        CPSImageWidget.prepare(self, datastructure, **kw)
        datamodel = datastructure.getDataModel()
        widget_id = self.getWidgetId()

        if len(self.fields) > 1:
            datastructure[widget_id + '_subtitle'] = datamodel[self.fields[1]]
        else:
            datastructure[widget_id + '_subtitle'] = ''

        rposition = self.render_position
        if self.configurable != 'nothing':
            if len(self.fields) > 2:
                v = datamodel[self.fields[2]]
                if v in self.all_render_positions:
                    rposition = v
        datastructure[widget_id + '_rposition'] = rposition

        if self.keep_original and len(self.fields) > 3:
            datastructure[widget_id + '_resize_kept'] = ''

        title = ''
        if len(self.fields) > 4:
            title = datamodel[self.fields[4]]
        datastructure[widget_id + '_title'] = title

        alt = ''
        if len(self.fields) > 5:
            alt = datamodel[self.fields[5]]
            # Defaulting to the file name if there is an image file and if no
            # alt has been given yet. This is the case when the document is
            # created.
            if not alt:
                alt = datastructure[widget_id + '_filename']
        datastructure[widget_id + '_alt'] = alt

    def otherProcessing(self, choice, datastructure):
        datamodel = datastructure.getDataModel()
        widget_id = self.getWidgetId()

        # Caption
        if len(self.fields) > 1:
            subtitle = datastructure[widget_id + '_subtitle']
            datamodel[self.fields[1]] = subtitle

        # Title
        if len(self.fields) > 4:
            title = datastructure[widget_id + '_title']
            datamodel[self.fields[4]] = title

        # Alt
        if len(self.fields) > 5:
            alt = datastructure[widget_id + '_alt']
            datamodel[self.fields[5]] = alt

        # Position
        if self.configurable != 'nothing' and len(self.fields) > 2:
            rposition = datastructure[widget_id + '_rposition']
            if rposition and rposition in self.all_render_positions:
                datamodel[self.fields[2]] = rposition

        # Resize
        if choice != 'resize':
            return
        if not self.canKeepOriginal():
            return
        image = datamodel[self.fields[0]]
        original_image = datamodel[self.fields[3]]
        if original_image is None and image is None:
            return

        if original_image is None:
            original_image = image
            datamodel[self.fields[3]] = original_image

        filename = original_image.title
        resize_op = datastructure[widget_id + '_resize_kept']
        image = self.getResizedImage(original_image, filename, resize_op)
        datamodel[self.fields[0]] = image

    def canKeepOriginal(self):
        return (self.keep_original and
                self.allow_resize and
                len(self.fields) > 3)

    def maybeKeepOriginal(self, image, datastructure):
        if self.canKeepOriginal():
            datamodel = datastructure.getDataModel()
            datamodel[self.fields[3]] = image

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        render_method = 'widget_photo_render'
        meth = getattr(self, render_method, None)
        if meth is None:
            raise RuntimeError("Unknown Render Method %s for widget type %s"
                               % (render_method, self.getId()))

        widget_id = self.getWidgetId()
        rposition = datastructure[widget_id + '_rposition']
        subtitle = datastructure[widget_id + '_subtitle']

        img_info = self.getImageInfo(datastructure, dump_cid_parts=True, **kw)
        return meth(mode=mode, datastructure=datastructure,
                    subtitle=subtitle,
                    render_position=rposition,
                    configurable=str(self.configurable),
                    **img_info)

InitializeClass(CPSPhotoWidget)


class CPSRangeListWidget(CPSWidget):
    """Range List widget."""
    meta_type = 'Range List Widget'

    field_types = ('CPS Range List Field',)
    field_inits = ({'is_searchabletext': 1,},)

    _properties = CPSWidget._properties + (
        {'id': 'display_width', 'type': 'int', 'mode': 'w',
         'label': 'Display width'},
        {'id': 'format_empty', 'type': 'string', 'mode': 'w',
         'label': 'Format for empty list'},
        )

    display_width = 0
    format_empty = ''

    def prepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel."""
        datamodel = datastructure.getDataModel()
        value = datamodel[self.fields[0]]
        datastructure[self.getWidgetId()] = value


    def validate(self, datastructure, layout_mode=None, **kw):
        """Validate datastructure and update datamodel."""
        widget_id = self.getWidgetId()
        value = datastructure[widget_id]
        if not isinstance(value, list):
            datastructure.setError(widget_id, "cpsschemas_err_rangelist")
            return 0
        v = []
        for i in value:
            i = i.split('-')
            if len(i) == 1:
                try:
                    i[0] = int(i[0])
                except ValueError:
                    datastructure.setError(widget_id, "cpsschemas_err_rangelist")
                    return 0
                v.append((i[0],))
            elif len(i) == 2:
                try:
                    i[0] = int(i[0])
                    i[1] = int(i[1])
                except ValueError:
                    datastructure.setError(widget_id, "cpsschemas_err_rangelist")
                    return 0
                v.append((i[0], i[1]))
            else:
                datastructure.setError(widget_id, "cpsschemas_err_rangelist")
                return 0
        if not v and self.isRequired(layout_mode=layout_mode):
            datastructure.setError(widget_id, "cpsschemas_err_required")
            return 0
        datamodel = datastructure.getDataModel()
        datamodel[self.fields[0]] = v
        return 1

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        value = datastructure[self.getWidgetId()]
        res = ''

        for i in value:
            if isinstance(i, str):
                res += i + ' '
            elif len(i) == 1:
                res += str(i[0]) + ' '
            else:
                res += str(i[0]) + '-' + str(i[1]) + ' '

        if mode == 'view':
            return escape(res)
        elif mode == 'edit':
            return renderHtmlTag('input',
                                 type='text',
                                 id=self.getHtmlWidgetId(),
                                 name=self.getHtmlWidgetId()+":tokens",
                                 value=escape(res),
                                 size=self.display_width,
                                 )
        raise RuntimeError('unknown mode %s' % mode)

InitializeClass(CPSRangeListWidget)

##################################################

class CPSDateTimeRangeWidget(CPSProgrammerCompoundWidget):
    """Date Time Range widget.

    A special compound widget that provides validation of the range and
    control over validation of sub-widgets.

    """
    meta_type = 'DateTime Range Widget'

    _properties = CPSProgrammerCompoundWidget._properties + (
        dict(id='render_method', type='string', mode='w',
             label='Render Method'),
        # GR TODO: move skip_validate_if_expr to CPSWidget
        # (no time to check on widget classes that rely on ordering of
        # CPSWidget props to define theirs right now)
        dict(id='skip_validate_if_expr', type='string', mode='w',
             label="Skip validation if expression"))

    _properties_post_process_tales = (
        CPSProgrammerCompoundWidget._properties_post_process_tales + (
        ('skip_validate_if_expr', 'skip_validate_if_expr_c'),)
        )

    render_method = 'widget_compound_default_render'
    skip_validate_if_expr = ''
    skip_validate_if_expr_c = None

    def prepare(self, ds, **kw):
        """Prepare datastructure from datamodel."""
        # Nothing to do : preparation of all widgets in the layout is automatic.
        pass

    def validate(self, ds, layout_mode=None, **kw):
        dm = ds.getDataModel()
        skip_expr = self.skip_validate_if_expr_c
        if skip_expr is not None:
            econtext = self._createExpressionContext(dm, kw.get('layout_mode'))
            if skip_expr(econtext):
                return True

        subs = self._getSubWidgets()
        for widget in subs:
            if not widget.validate(ds, **kw):
                return False

        wid = self.getWidgetId()
        begin, end = [dm[widget.fields[0]] for widget in subs]
        if self.isRequired(layout_mode=layout_mode):
            if begin is None and end is None:
                ds.setError(wid, 'cpsschemas_err_required')
                return False

        # None is earlier than all actual datetimes
        # but None for end should mean unbound future
        if begin > end and end is not None:
            ds.setError(wid, 'cpsschemas_err_datetime_range_sgs')
            return False

        return True

    # render method of CPSCompoundWidget is fine
    # and controlled by a property on this widget

InitializeClass(CPSDateTimeRangeWidget)

##################################################

class CPSDocumentLanguageSelectWidget(CPSWidget):
    """Document Language Selection widget."""
    meta_type = 'Document Language Select Widget'

    field_types = ('CPS String Field',)
    field_inits = ({'is_searchabletext': 0,},)

    def prepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel."""
        datamodel = datastructure.getDataModel()
        value = datamodel[self.fields[0]]
        datastructure[self.getWidgetId()] = value


    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel."""
        return 1

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        res = ''
        datamodel = datastructure.getDataModel()
        proxy = datamodel.getProxy()
        if proxy is None:
            return res
        proxy_url = proxy.absolute_url()
        languages = proxy.getProxyLanguages()
        if len(languages) <= 1:
            return res
        current_language = datamodel[self.fields[0]]
        translation_service = getToolByName(self, 'translation_service')
        if translation_service is not None:
            mcat = translation_service
        else:
            def mcat(msgid):
                return msgid

        for language in languages:
            language_title = mcat('label_language_%s'% language,
                                  default=language)
            contents = language
            if current_language != language:
                contents = renderHtmlTag('a', href='%s/switchLanguage/%s' %
                                         (proxy_url, language),
                                         title=language_title,
                                         contents=contents,
                                         css_class='availableLang')
            else:
                contents = renderHtmlTag('span', contents=contents,
                                         title=language_title,
                                         css_class='selectedLang')
            contents += ' '
            res += renderHtmlTag('li', contents=contents)
        res = renderHtmlTag('ul', contents=res)
        res = '<div class="headerActions">%s</div>' % res
        return res

InitializeClass(CPSDocumentLanguageSelectWidget)

##################################################

class CPSSubjectWidget(CPSMultiSelectWidget):
    """A widget featuring links to items by subject.

    The CPS Subject Widget is like the CPS MultiSelect Widget from which it
    derives, except in "view" mode where the listed entries have link on them
    to other documents on the portal which have the same subjects.
    """
    meta_type = 'Subject Widget'

    def getEntriesHtml(self, entries, vocabulary, translated=False):
        entries_html_list = []
        if translated:
            cpsmcat = getToolByName(self, 'translation_service', None)
            encoding = get_final_encoding(cpsmcat)
            if cpsmcat is None:
                translated = False
        for subject_name in entries:
            if translated:
                subject_label = cpsmcat(
                    vocabulary.getMsgid(subject_name, subject_name),
                            subject_name).encode(encoding, 'ignore')
                entries_html_list.append(self.getSubjectSearchLink(
                    subject_name, subject_label))
            else:
                entries_html_list.append(
                    self.getSubjectSearchLink(subject_name,
                                              subject_name))
        return ', '.join(entries_html_list)

    def getSubjectSearchLink(self, subject_name, subject_label):
        """Return an HTML link for the subject name with the given label."""
        subject_name = str(subject_name) # no shame: voc entries must be str
        return ('<a href="%s">%s</a>'
                % (self.getSubjectSearchUrl(escape(subject_name)),
                   escape(subject_label)))

    def getSubjectSearchUrl(self, subject_name):
        """Return the subject search URL.

        The provided links are actually requests to the portal search engine.
        """
        return "%s/search_form?Subject=%s" % (self.portal_url(), subject_name)

InitializeClass(CPSSubjectWidget)

##################################################

class CPSFlashWidget(CPSAttachedFileWidget):
    """Flash Widget.
    """
    meta_type = 'Flash Widget'

    field_types = ('CPS File Field',   # File
                   'CPS String Field', # Caption (optional)
                   'CPS File Field')   # Preview (optional)
    field_inits = ({'is_searchabletext': 0,
                    'suffix_text': '_f1', # _f# are autocomputed field ext
                    'suffix_html': '_f2',},
                   {'is_searchabletext': 1}, {},
                   )

    def _flash_validate(self, datastructure, **kw):
        """Check that this is a Flash animation
        """
        widget_id = self.getWidgetId()
        choice = datastructure[widget_id+'_choice']
        if choice == 'change':
            fileinfo = self.getFileInfo(datastructure)
            if fileinfo is not None:
                cond = fileinfo['mimetype'] == 'application/x-shockwave-flash'
                if not cond:
                    datastructure.setError(self.getWidgetId(),
                                           'cpsschemas_err_file')
                    return False
        return True

    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel.
        """
        return (CPSAttachedFileWidget.validate(self, datastructure, **kw) and
                self._flash_validate(datastructure, **kw))

    def render(self, mode, datastructure, **kw):
        """Render this widget from the datastructure or datamodel.
        """
        render_method = 'widget_flash_render'
        meth = getattr(self, render_method, None)

        if meth is None:
            raise RuntimeError("Unknown Render Method %s for widget type %s"
                               % (render_method, self.getId()))

        file = datastructure[self.getWidgetId()]

        # Get common File props
        file_info = self.getFileInfo(datastructure)

        # Update with speficic swf header props
        if file is not None:
            try:
                file_info.update(analyseContent(
                    str(file.read()), file_info['size']))
            except TypeError:
                pass

        return meth(mode=mode, datastructure=datastructure, **file_info)

InitializeClass(CPSFlashWidget)

##################################################

class CPSLinkWidget(CPSProgrammerCompoundWidget):
    """Widget for an HTTP link.
    """
    meta_type = 'Link Widget'
    render_method = 'widget_link_render'
    prepare_validate_method = ''

    _properties = CPSProgrammerCompoundWidget._properties + (
        dict(id='display_href_if_title', type='boolean', mode='w',
             label="Display the URL in view mode if the title is filled ?"),)

    display_href_if_title = True # BBB, although it's pretty useless imho

InitializeClass(CPSLinkWidget)


class CPSTextImageWidget(CPSProgrammerCompoundWidget):
    """Widget for text+image.

    Also Support two column for backwards compatibility.
    """
    meta_type = 'Text Image Widget'
    render_method = 'widget_textimage_render'
    prepare_validate_method = 'widget_textimage_prepare_validate'

InitializeClass(CPSTextImageWidget)


class CPSTextColumnsWidget(CPSProgrammerCompoundWidget):
    """Widget for two columns of texts.

    Currently supports only two columns, but should evolve to support any of
    them (note that there are CSS3 properties for that).
    """
    meta_type = 'Text Columns Widget'
    render_method = 'widget_textimage_render'
    prepare_validate_method = 'widget_textcolumns_prepare_validate'

InitializeClass(CPSTextColumnsWidget)


class CPSImageLinkWidget(CPSProgrammerCompoundWidget):
    """
    """
    meta_type = 'Image Link Widget'
    render_method = 'widget_imagelink_render'
    prepare_validate_method = 'widget_imagelink_prepare_validate'

InitializeClass(CPSImageLinkWidget)

class CPSAutocompletionStringWidget(CPSStringWidget):
    """Autocompletion String widget."""
    meta_type = 'Autocompletion String Widget'
    server_method = ''

    _properties = CPSStringWidget._properties + (
        {'id': 'server_method', 'type': 'string', 'mode': 'w',
         'label': 'Server method',},)

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        render_method = 'widget_autocompletion_string_render'
        meth = getattr(self, render_method, None)
        if meth is None:
            raise RuntimeError("Unknown Render Method %s for widget type %s"
                               % (render_method, self.getId()))
        if mode not in ('view', 'edit'):
            raise RuntimeError('unknown mode %s' % mode)

        value = datastructure[self.getWidgetId()]
        widget_id = self.getWidgetId()
        html_widget_id = self.getHtmlWidgetId()

        return meth(mode=mode, widget_id=widget_id,value=value,
                    size=self.display_width, server_method=self.server_method,
                    html_widget_id=html_widget_id)

InitializeClass(CPSAutocompletionStringWidget)
