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
"""Extended widget types.

Definition of extended widget types.
"""

from cgi import escape
from re import match
from Globals import InitializeClass
from Acquisition import aq_base
from types import ListType, TupleType, StringType
from DateTime.DateTime import DateTime
from ZPublisher.HTTPRequest import FileUpload
from OFS.Image import cookId, File, Image
import os.path
from zLOG import LOG, DEBUG, TRACE
from zipfile import ZipFile, BadZipfile
from Products.PythonScripts.standard import structured_text, newline_to_br
from Products.CMFCore.utils import getToolByName
from Products.CPSSchemas.WidgetTypesTool import WidgetTypeRegistry
from Products.CPSSchemas.Widget import CPSWidget, CPSWidgetType
from Products.CPSSchemas.BasicWidgets import CPSNoneWidget, \
     CPSSelectWidget, CPSMultiSelectWidget, \
     CPSStringWidget, CPSImageWidget, CPSFileWidget, \
     _isinstance, renderHtmlTag

##################################################
# previously named CPSTextAreaWidget in BasicWidget r1.78
class CPSTextWidget(CPSStringWidget):
    """Text widget."""
    meta_type = "CPS Text Widget"

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
        {'id': 'file_uploader', 'type': 'boolean', 'mode': 'w',
         'label': 'Add a file uploader to the widget UI'},
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
    all_configurable = ['nothing', 'position', 'format', 'position and format']
    all_render_positions = ['normal', 'col_left', 'col_right']
    all_render_formats = ['text', 'stx', 'html'] # remove 'pre' as we do the
                                                 # same using text

    width = 40
    height = 5
    size_max = 2*1024*1024
    file_uploader = 0
    render_position = all_render_positions[0]
    render_format = all_render_formats[0]
    configurable = 'nothing'

    def prepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel."""
        datamodel = datastructure.getDataModel()
        widget_id = self.getWidgetId()
        datastructure[widget_id] = str(datamodel[self.fields[0]])
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
            file_upload_valid = True
            file_upload.seek(0)
            value = file_upload.read()
        if not file_upload_valid:
            value = datastructure[widget_id]
        err, v = self._extractValue(value)
        if err:
            datastructure.setError(widget_id, err)
            datastructure[widget_id] = v
        else:
            datamodel = datastructure.getDataModel()
            datamodel[self.fields[0]] = v
            if self.configurable != 'nothing':
                if len(self.fields) > 1:
                    rposition = datastructure[widget_id + '_rposition']
                    if rposition and rposition in self.all_render_positions:
                        datamodel[self.fields[1]] = rposition
                if len(self.fields) > 2:
                    rformat = datastructure[widget_id + '_rformat']
                    if rformat and rformat in self.all_render_formats:
                        datamodel[self.fields[2]] = rformat
            if file_upload_valid:
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
        rposition = datastructure[widget_id + '_rposition']
        rformat = datastructure[widget_id + '_rformat']
        if mode == 'view':
            if rformat == 'pre':
                value = '<pre>' + escape(value) + '</pre>'
            elif rformat == 'stx':
                value = structured_text(value)
            elif rformat == 'text':
                value = newline_to_br(escape(value))
            elif rformat == 'html':
                pass
            else:
                RuntimeError("unknown render_format '%s' for '%s'" %
                             (rformat, self.getId()))
        return meth(mode=mode, datastructure=datastructure, value=value,
                    file_uploader=self.file_uploader,
                    render_position=rposition, render_format=rformat,
                    configurable=str(self.configurable))

InitializeClass(CPSTextWidget)


class CPSTextWidgetType(CPSWidgetType):
    """Text widget type."""
    meta_type = "CPS Text Widget Type"
    cls = CPSTextWidget

InitializeClass(CPSTextWidgetType)



##################################################
# previously named CPSDateWidget in BasicWidget r1.78
class CPSDateTimeWidget(CPSWidget):
    """DateTime widget.

    A widget that displays and makes it possible to edit a DateTime object.
    View and edit mode can be done in the ISO 8601 date format (YYYY-mm-dd)
    or in a localized format (mm/dd/YYYY for English and dd/mm/YYYY for the rest
    of the world) cf. http://www.w3.org/TR/NOTE-datetime
    """
    meta_type = "CPS DateTime Widget"

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
        )
    # When will CPS default to the more sensible ISO 8601 date format?
    #view_format = 'iso8601_medium_easy'
    view_format = 'medium'
    time_setting = 1
    time_hour_default = '12'
    time_minutes_default = '00'

    def prepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel."""
        datamodel = datastructure.getDataModel()
        v = datamodel[self.fields[0]]
        if not v and self.is_required:
            v = DateTime()
        widget_id = self.getWidgetId()
        date = ''
        hour = minute = ''

        if v == 'None':
            v = None
        if v:
            # Backward compatibility test, this logic is not used by the
            # current code.
            if type(v) is StringType:
                v = DateTime(v)
            d = str(v.day())
            m = str(v.month())
            y = str(v.year())
            if self.view_format.startswith('iso8601'):
                date = '%s-%s-%s' % (y, m, d)
            else:
                locale = self.Localizer.get_selected_language()
                if locale in ('en', 'hu'):
                    date = '%s/%s/%s' % (m, d, y)
                else:
                    date = '%s/%s/%s' % (d, m, y)
            hour = str(v.h_24())
            minute = str(v.minute())

        datastructure[widget_id] = v
        datastructure[widget_id + '_date'] = date
        datastructure[widget_id + '_hour'] = hour or self.time_hour_default
        datastructure[widget_id + '_minute'] = minute or self.time_minutes_default

    def validate(self, datastructure, **kw):
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
            if self.is_required:
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
                locale = self.Localizer.get_selected_language()
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
        else:
            datastructure[widget_id] = v
            datamodel[field_id] = v
            return 1

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        render_method = 'widget_datetime_render'
        meth = getattr(self, render_method, None)
        if meth is None:
            raise RuntimeError("Unknown Render Method %s for widget type %s"
                               % (render_method, self.getId()))
        return meth(mode=mode, datastructure=datastructure)


InitializeClass(CPSDateTimeWidget)


class CPSDateTimeWidgetType(CPSWidgetType):
    """DateTime widget type."""
    meta_type = "CPS DateTime Widget Type"
    cls = CPSDateTimeWidget

InitializeClass(CPSDateTimeWidgetType)



##################################################
class CPSAttachedFileWidget(CPSFileWidget):
    """AttachedFile widget."""
    meta_type = "CPS AttachedFile Widget"

    # XXX The second and third fields are actually optional...
    field_types = ('CPS File Field', 'CPS String Field', 'CPS File Field')
    field_inits = ({'is_searchabletext': 0,
                    'suffix_text': '_f1', # _f# are autocomputed field ext
                    'suffix_html': '_f2',
                    },
                   {'is_searchabletext': 1,
                    },
                   {'is_searchabletext': 0,
                    },
                   )

    _properties = CPSFileWidget._properties + (
        {'id': 'allowed_suffixes', 'type': 'tokens', 'mode': 'w',
         'label': 'Allowed file suffixes (for example: .html .sxw)'},
        )
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

    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel."""
        datamodel = datastructure.getDataModel()
        field_id = self.fields[0]
        widget_id = self.getWidgetId()
        choice = datastructure[widget_id+'_choice']
        filetitle = datastructure[widget_id + '_title']
        file = None
        err = 0
        err_mapping = None
        if choice == 'delete':
            if self.is_required:
                return self.doesNotValidate('cpsschemas_err_required',
                                            None, file, datastructure)
            datamodel[field_id] = None
        elif choice == 'keep':
            if datastructure.has_key('restored_items') and \
                   widget_id in datastructure['restored_items']:
                # the file is restored from the session after an invalid layout
                datamodel[field_id] = datastructure[widget_id]
                if not datastructure.has_key('backup_items'):
                    # we may have again an invalid layout
                    datastructure['backup_items'] = {}
                datastructure['backup_items'][widget_id] = field_id
            file = datamodel[field_id]
            if file is None:
                if self.is_required:
                    return self.doesNotValidate('cpsschemas_err_required',
                                                None, file, datastructure)
            else:
                # do not allow empty title: it is used as link text
                if not filetitle:
                    filetitle = datastructure[widget_id + '_filename']
                if filetitle != file.title:
                    file.manage_changeProperties(title=filetitle)
                    datamodel[field_id] = file
        elif choice == 'change' and datastructure.get(widget_id):
            fileUpload = datastructure[widget_id]
            if not _isinstance(fileUpload, FileUpload):
                return self.doesNotValidate('cpsschemas_err_file',
                                            None, file, datastructure)
            file_base, file_suffix = os.path.splitext(fileUpload.filename)
            if (self.allowed_suffixes
                and file_suffix not in self.allowed_suffixes):
                err = 'cpsschemas_err_file_bad_suffix ${allowed_suffixes}'
                err_mapping = {'allowed_suffixes':
                               ' '.join(self.allowed_suffixes)}
                return self.doesNotValidate(err, err_mapping,
                                            file, datastructure)
            ms = self.size_max
            if fileUpload.read(1) == '':
                return self.doesNotValidate('cpsschemas_err_file_empty',
                                            None, file, datastructure)
            fileUpload.seek(0)
            read_size = len(fileUpload.read(ms + 1))
            if ms and read_size > ms:
                # Size is expressed in human readable value
                max_size_str = self.getHumanReadableSize(ms)
                err = 'cpsschemas_err_file_too_big ${max_size}'
                err_mapping = {'max_size': max_size_str}
                return self.doesNotValidate(err, err_mapping,
                                            file, datastructure)
            fileUpload.seek(0)
            # Ignore title value from form;
            # re-initialize title with fileid value
            fileid = cookId('', '', fileUpload)[0]
            file = File(fileid, fileid, fileUpload)
            registry = getToolByName(self, 'mimetypes_registry')
            mimetype = registry.lookupExtension(fileid.lower())
            if mimetype and file.content_type != mimetype.normalized():
                LOG('CPSAttachedFileWidget', DEBUG,
                    'Fixing mimetype from %s to %s' % (
                    file.content_type, mimetype.normalized()))
                file.manage_changeProperties(
                    content_type=mimetype.normalized())
                LOG('CPSAttachedFileWidget', DEBUG,
                    'validate change set %s' % `file`)
            datamodel[field_id] = file
            # here we ask to backup our file
            # in case of invalid layout
            if not datastructure.has_key('backup_items'):
                datastructure['backup_items'] = {}
            datastructure['backup_items'][widget_id] = field_id
        self.prepare(datastructure)
        return 1

    def doesNotValidate(self, err, err_mapping, file, datastructure):
        LOG('CPSAttachedFileWidget', DEBUG, 'error %s on %s' % (err, `file`))
        widget_id = self.getWidgetId ()
        field_id = self.fields[0]
        # do not keep rejected file; set error after change
        datastructure[widget_id] = datastructure.getDataModel()[field_id]
        datastructure.setError(widget_id, err, err_mapping)
        return 0

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


class CPSAttachedFileWidgetType(CPSWidgetType):
    """AttachedFile widget type."""
    meta_type = "CPS AttachedFile Widget Type"
    cls = CPSAttachedFileWidget

InitializeClass(CPSAttachedFileWidgetType)


##################################################
class CPSZippedHtmlWidget(CPSAttachedFileWidget):
    """ZippedHtml widget.

    A zip file that contains html which can be viewed online.
    Use index.html or any html file from the zip as preview page.
    """
    meta_type = "CPS ZippedHtml Widget"
    size_max = 1024*1024

    # XXX don't knwo why this does not work ?
    # allowed_suffixes = ['zip']

    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel."""
        widget_id = self.getWidgetId()
        choice = datastructure[widget_id+'_choice']
        if choice == 'change':
            # looking for an html index
            file_upload = datastructure.get(widget_id)
            if _isinstance(file_upload, FileUpload):
                try:
                    zf = ZipFile(file_upload, 'r')
                except BadZipfile:
                    return self.doesNotValidate(
                        'cpsschemas_err_zippedhtml_invalid_zip',
                        None, file_upload, datastructure)
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
                if not index_path:
                    return self.doesNotValidate(
                        'cpsschemas_err_zippedhtml_html_not_found',
                        None, file_upload, datastructure)
        # std attached file validation
        ret = CPSAttachedFileWidget.validate(self, datastructure, **kw)
        if ret and choice == 'change':
            field_id = self.fields[0]
            datamodel = datastructure.getDataModel()
            # adding attribute to file ofs
            file = datamodel[field_id]
            file._zip_index_path = index_path
            datamodel[field_id] = file
        return ret

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        render_method = 'widget_zippedhtml_render'
        meth = getattr(self, render_method, None)
        if meth is None:
            raise RuntimeError("Unknown Render Method %s for widget type %s"
                               % (render_method, self.getId()))
        file_info = self.getFileInfo(datastructure)
        file_info['index_path'] = getattr(datastructure[self.getWidgetId()],
                                          '_zip_index_path', '')
        return meth(mode=mode, datastructure=datastructure, **file_info)

InitializeClass(CPSZippedHtmlWidget)


class CPSZippedHtmlWidgetType(CPSWidgetType):
    """ZippedHtml widget type."""
    meta_type = "CPS ZippedHtml Widget Type"
    cls = CPSZippedHtmlWidget

InitializeClass(CPSZippedHtmlWidgetType)



#################################################

class CPSRichTextEditorWidget(CPSWidget):
    """Rich Text Editor widget.

    This widget should not be used. Use the Text Widget which provides both HTML
    and text formats.
    """
    meta_type = "CPS Rich Text Editor Widget"

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
        # XXXX
        # Not finished !! Just for tests
        value = datastructure[self.getWidgetId()]
        if mode == 'view':
            # To change
            return structured_text(value)
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

class CPSRichTextEditorWidgetType(CPSWidgetType):
    """RTE widget type"""
    meta_type = "CPS Rich Text Editor Widget Type"
    cls = CPSRichTextEditorWidget

InitializeClass(CPSRichTextEditorWidgetType)


##########################################

class CPSExtendedSelectWidget(CPSSelectWidget):
    """Extended Select widget."""
    meta_type = "CPS ExtendedSelect Widget"

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""

        if mode == 'view':
            return CPSSelectWidget.render(self, mode, datastructure)

        elif mode == 'edit':
            render_method = 'widget_extendedselect_render'

            meth = getattr(self, render_method, None)
            if meth is None:
                raise RuntimeError("Unknown Render Method %s for widget type %s"
                                   % (render_method, self.getId()))
            return meth(mode=mode, datastructure=datastructure,
                        vocabulary=self._getVocabulary(datastructure))

        else:
            raise RuntimeError('unknown mode %s' % mode)

InitializeClass(CPSExtendedSelectWidget)

class CPSExtendedSelectWidgetType(CPSWidgetType):
    """Extended Select widget type."""
    meta_type = "CPS ExtendedSelect Widget Type"
    cls = CPSExtendedSelectWidget

InitializeClass(CPSExtendedSelectWidgetType)

##########################################

class CPSInternalLinksWidget(CPSWidget):
    """Internal Links widget."""
    meta_type = "CPS InternalLinks Widget"

    field_types = ('CPS String List Field',)
    field_inits = ({'is_searchabletext': 1,},)

    _properties = CPSWidget._properties + (
        {'id': 'new_window', 'type': 'boolean', 'mode': 'w',
         'label': 'Display in a new window'},
        {'id': 'size', 'type': 'int', 'mode': 'w',
         'label': 'Links displayed'},
        )
    new_window = 0
    size = 0

    def prepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel."""
        datamodel = datastructure.getDataModel()
        datastructure[self.getWidgetId()] = datamodel[self.fields[0]]

    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel."""
        widget_id = self.getWidgetId()
        value = datastructure[widget_id]
        err = 0
        if self.is_required and (value == [] or value == ['']):
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

class CPSInternalLinksWidgetType(CPSWidgetType):
    """Internal links widget type."""
    meta_type = "CPS InternalLinks Widget Type"
    cls = CPSInternalLinksWidget

InitializeClass(CPSInternalLinksWidgetType)

##################################################

class CPSPhotoWidget(CPSImageWidget):
    """Photo widget."""
    meta_type = "CPS Photo Widget"

    field_types = ('CPS Image Field',   # Image
                   'CPS String Field',  # Sub title
                   'CPS String Field',  # render_position if configurable
		   'CPS Image Field',)  # original photo
    field_inits = ({}, {'is_searchabletext': 1,}, {}, {})

    _properties = CPSImageWidget._properties + (
        {'id': 'render_position', 'type': 'selection', 'mode': 'w',
         'select_variable': 'all_render_positions',
         'label': 'Render position'},
        {'id': 'configurable', 'type': 'selection', 'mode': 'w',
         'select_variable': 'all_configurable',
         'label': 'What is user configurable, require extra fields'},
        {'id': 'keep_original', 'type': 'boolean', 'mode': 'w',
         'label': 'Enable to keep original image'},
        )
    all_configurable = ['nothing', 'position']
    all_render_positions = ['left', 'center', 'right']

    allow_resize = 1
    configurable = all_configurable[0]
    render_position = all_render_positions[0]
    keep_original = 1

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

    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel."""
        datamodel = datastructure.getDataModel()
        field_id = self.fields[0]
        widget_id = self.getWidgetId()
        subtitle = datastructure[widget_id + '_subtitle']
        rposition = datastructure[widget_id + '_rposition']
        # validate items specific to photo widget
        if len(self.fields) > 1:
            datamodel[self.fields[1]] = subtitle
        if self.configurable != 'nothing':
            if len(self.fields) > 2:
                if rposition and rposition in self.all_render_positions:
                    datamodel[self.fields[2]] = rposition
        choice = datastructure[widget_id+'_choice']
        if choice not in ['resize', 'change']:
            # CPSImage validation resets datastructure
            ret = CPSImageWidget.validate(self, datastructure, **kw)
        else:
            filetitle = datastructure[widget_id + '_title']
            err = None
            if choice == 'resize':
                # figure out if the original size image can be kept
                can_keep_original = self.keep_original and \
                                    self.allow_resize and \
                                    len(self.fields) > 3
                if can_keep_original:
                    original_image = datamodel[self.fields[3]]
                    file = datamodel[field_id]
                    if original_image is None and file is None:
                        if self.is_required:
                            err = 'cpsschemas_err_required'
                        # else ignore, this should not happen anyway
                    else:
                        # file or original_image is not None.
                        # if original file is not set (upgrade for instance),
                        # actual file becomes original file
                        if original_image is None:
                            original_image = file
                            datamodel[self.fields[3]] = original_image
                        # do not allow empty title: it is used as link text
                        if not filetitle:
                            filetitle = datastructure[widget_id + '_filename']
                        # get resized image
                        fileid = original_image.getId()
                        resize_op = datastructure[widget_id + '_resize_kept']
                        file = self.getResizedImage(original_image, fileid,
                                                    filetitle, resize_op)
                        datamodel[field_id] = file
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
                            # figure out if the original size image can be kept
                            can_keep_original = self.keep_original and \
                                                self.allow_resize and \
                                                len(self.fields) > 3
                            original_image = Image(fileid, filetitle, file)
                            if not self.allow_resize:
                                file = original_image
                            else:
                                if can_keep_original:
                                    # set original image
                                    datamodel[self.fields[3]] = original_image
                                # get resized image
                                resize_op = datastructure[widget_id + '_resize']
                                file = self.getResizedImage(original_image, fileid,
                                                            filetitle, resize_op)
                            LOG('CPSImageWidget', DEBUG,
                                'validate change set %s' % `file`)
                            datamodel[field_id] = file
                            # here we ask to backup our file
                            # in case of invalid layout
                            if not datastructure.has_key('backup_items'):
                                datastructure['backup_items'] = {}
                            datastructure['backup_items'][widget_id] = field_id

            if err:
                LOG('CPSImageWidget', DEBUG,
                    'error %s on %s' % (err, `file`))
                # do not keep rejected file; set error after change
                datastructure[widget_id] = datamodel[field_id]
                datastructure.setError(widget_id, err)
            else:
                # reset datastructure
                self.prepare(datastructure)

            ret = not err

        return ret


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

        img_info = self.getImageInfo(datastructure)

        return meth(mode=mode, datastructure=datastructure,
                    subtitle=subtitle,
                    render_position=rposition,
                    configurable=str(self.configurable),
                    **img_info)


InitializeClass(CPSPhotoWidget)


class CPSPhotoWidgetType(CPSWidgetType):
    """Photo widget type."""
    meta_type = "CPS Photo Widget Type"
    cls = CPSPhotoWidget

    # XXX: TBD

InitializeClass(CPSPhotoWidgetType)

##################################################
class CPSLinkWidget(CPSNoneWidget):
    """Deprecated Link Widget now using compound widget."""
    meta_type = "CPS Link Widget"

InitializeClass(CPSLinkWidget)

##################################################

class CPSGenericSelectWidget(CPSWidget):
    """Generic Select widget."""
    meta_type = "CPS Generic Select Widget"

    field_types = ('CPS String Field',)
    field_inits = ({'is_searchabletext': 1,},)

    _properties = CPSWidget._properties + (
        {'id': 'vocabulary', 'type': 'string', 'mode': 'w',
         'label': 'Vocabulary', 'is_required' : 1},
        {'id': 'translated', 'type': 'boolean', 'mode': 'w',
         'label': 'Is vocabulary translated on display'},
        {'id': 'render_format', 'type': 'selection', 'mode': 'w',
         'select_variable': 'render_formats',
         'label': 'Render format'},
        # Provide an 'other' option where free input is accepted
        # (ignored if render format is 'select')
        {'id': 'other_option', 'type': 'boolean', 'mode':'w',
         'label': "Provide an 'other' option"},
        {'id': 'other_option_display_width', 'type': 'int', 'mode': 'w',
         'label': "'other' option display width"},
        {'id': 'other_option_size_max', 'type': 'int', 'mode': 'w',
         'label': "'other' option maximum input width"},
        # Enables the possibility to add blank values to vocabulary just to
        # change the way the list is presented (using items like 'choose a
        # category' or '------------' to separate items) and not affect the way
        # the value will be validated if the widget is required.
        # Before this, if the widget was required, default behavior was to
        # accept blank values if they were in the vocabulary (e.g
        # blank_value_ok_if_required = 1)
        {'id': 'blank_value_ok_if_required', 'type': 'boolean', 'mode':'w',
         'label': "Accept blank values when validating"},
        )
    render_formats = ['select', 'radio']

    # XXX make a menu for the vocabulary.
    vocabulary = ''
    translated = 0
    render_format = render_formats[0]
    other_option = 0
    other_option_display_width = 20
    other_option_size_max = 0
    blank_value_ok_if_required = 1

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
        if (_isinstance(value, ListType) or
            _isinstance(value, TupleType)):
            LOG('CPSGenericSelectWidget.prepare', TRACE,
                'expected String got Typle %s use first element' % value)
            if len(value):
                value = value[0]
            else:
                value = ''
        datastructure[self.getWidgetId()] = value

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
        if len(value)>0:
            if not vocabulary.has_key(value):
                if self.render_format == 'select' or not self.other_option:
                    datastructure.setError(widget_id, "cpsschemas_err_select")
                    return 0
        else:
            if self.is_required:
                # set error unless vocabulary holds blank values and
                # blank_value_ok_if_required is set to 1
                if vocabulary.has_key(value):
                    if not self.blank_value_ok_if_required:
                        datastructure.setError(widget_id, "cpsschemas_err_required")
                        return 0
                else:
                    datastructure.setError(widget_id, "cpsschemas_err_required")
                    return 0
        datamodel = datastructure.getDataModel()
        datamodel[self.fields[0]] = v
        return 1

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        widget_id = self.getWidgetId()
        value = datastructure[widget_id]
        vocabulary = self._getVocabulary(datastructure)
        portal = getToolByName(self, 'portal_url').getPortalObject()
        cpsmcat = portal.Localizer.default
        if mode == 'view':
            if not vocabulary.has_key(value):
                # for free input
                if value is not None:
                    return escape(value)
                else:
                    return ''
            else:
                if getattr(self, 'translated', None):
                    return escape(cpsmcat(vocabulary.getMsgid(value, value)).encode('ISO-8859-15', 'ignore'))
                else:
                    return escape(vocabulary.get(value, value))
        elif mode == 'edit':
            in_selection = 0
            in_other_selection = 0
            res = ''
            html_widget_id = self.getHtmlWidgetId()
            render_format = self.render_format
            if render_format not in self.render_formats:
                raise RuntimeError('unknown render format %s' % render_format)
            if render_format == 'select':
                res = renderHtmlTag('select', name=html_widget_id)
            # vocabulary options
            for k, v in vocabulary.items():
                if getattr(self, 'translated', None):
                    v = cpsmcat(vocabulary.getMsgid(k, k)).encode('ISO-8859-15', 'ignore')
                if render_format == 'select':
                    kw = {'value': k, 'contents': v}
                    # do not add a selected option if it is already set
                    if value == k and not in_selection:
                        kw['selected'] = 'selected'
                        in_selection = 1
                    res += renderHtmlTag('option', **kw)
                    res += '\n'
                else:
                    kw = {'id': html_widget_id+'_'+k,
                          'type': render_format,
                          'name': html_widget_id,
                          'value': k,
                          }
                    # do not add a selected option if it is already set
                    if value == k and not in_selection:
                        kw['checked'] = 'checked'
                        in_selection = 1
                    res += renderHtmlTag('input', **kw)
                    kw = {'for': html_widget_id+'_'+k,
                          'contents': v,
                          }
                    res += renderHtmlTag('label', **kw)
                    res += '<br/>\n'
            # invalid or free selections
            if value and not in_selection:
                if render_format == 'select':
                    in_selection = 1
                    kw = {'value': value,
                          'contents': 'invalid: '+value,
                          'selected': 'selected',
                          }
                    res += renderHtmlTag('option', **kw)
                    res += '\n'
                else:
                    if self.other_option:
                        in_selection = 1
                        in_other_selection = 1
                        kw = {'id': html_widget_id+'_other_selection',
                              'type': render_format,
                              'name': html_widget_id,
                              'value':  value,
                              'checked': 'checked',
                              }
                        res += renderHtmlTag('input', **kw)
                        kw = {'for': html_widget_id+'_other_selection',
                              'contents': cpsmcat('label_other_selection').encode('ISO-8859-15', 'ignore'),
                              }
                        res += renderHtmlTag('label', **kw)
                        kw = {'type': 'text',
                              'name': html_widget_id+'_other',
                              'value': value,
                              'onchange': "document.getElementById('"+html_widget_id+"_other_selection').value = this.value",
                              'onclick': "document.getElementById('"+html_widget_id+"_other_selection').checked='checked'",
                              'size': self.other_option_display_width,
                              }
                        if self.other_option_size_max:
                            kw['maxlength'] = self.other_option_size_max
                        res += renderHtmlTag('input', **kw)
                        res += '<br/>\n'
                    else:
                        kw = {'id': html_widget_id+'_'+value,
                              'type': render_format,
                              'name': html_widget_id,
                              'value': value,
                              'disabled': 'disabled',
                              }
                        res += renderHtmlTag('input', **kw)
                        kw = {'for': html_widget_id+'_'+value,
                              'contents': 'invalid: '+value,
                              }
                        res += renderHtmlTag('label', **kw)
                        res += '<br/>\n'
            # 'other' option
            if self.other_option and not in_other_selection:
                if render_format != 'select':
                    kw = {'id': html_widget_id+'_other_selection',
                          'type': render_format,
                          'name': html_widget_id,
                          'value': '',
                          }
                    res += renderHtmlTag('input', **kw)
                    kw = {'for': html_widget_id+'_other_selection',
                          'contents': cpsmcat('label_other_selection').encode('ISO-8859-15', 'ignore'),
                          }
                    res += renderHtmlTag('label', **kw)
                    kw = {'type': 'text',
                          'name': html_widget_id+'_other',
                          'value': "",
                          'onchange': "document.getElementById('"+html_widget_id+"_other_selection').value = this.value",
                          'onclick': "document.getElementById('"+html_widget_id+"_other_selection').checked='checked'",
                          'size': self.other_option_display_width,
                          }
                    if self.other_option_size_max:
                        kw['maxlength'] = self.other_option_size_max
                    res += renderHtmlTag('input', **kw)
                    res += '<br/>\n'
            # default option
            if not self.is_required and not vocabulary.has_key(''):
                if render_format == 'select':
                    kw = {'value': '',
                          'contents': cpsmcat('label_none_selection').encode('ISO-8859-15', 'ignore'),
                          }
                    if not in_selection:
                        kw['selected'] = 'selected'
                    res += renderHtmlTag('option', **kw)
                    res += '\n'
                else:
                    kw = {'id': html_widget_id+'_empty',
                          'type': render_format,
                          'name': html_widget_id,
                          'value': '',
                          }
                    if not in_selection:
                        kw['checked'] = 'checked'
                    res += renderHtmlTag('input', **kw)
                    kw = {'for': html_widget_id+'_empty',
                          'contents': cpsmcat('label_none_selection').encode('ISO-8859-15', 'ignore'),
                          }
                    res += renderHtmlTag('label', **kw)
                    res += '<br/>\n'
            if render_format == 'select':
                res += '</select>'
            return res
        raise RuntimeError('unknown mode %s' % mode)

InitializeClass(CPSGenericSelectWidget)


class CPSGenericSelectWidgetType(CPSWidgetType):
    """Generic Select widget type."""
    meta_type = "CPS Generic Select Widget Type"
    cls = CPSGenericSelectWidget

InitializeClass(CPSGenericSelectWidgetType)


##################################################

class CPSGenericMultiSelectWidget(CPSWidget):
    """Generic MultiSelect widget."""
    meta_type = "CPS Generic MultiSelect Widget"

    field_types = ('CPS String List Field',)
    field_inits = ({'is_searchabletext': 1,},)

    _properties = CPSWidget._properties + (
        {'id': 'vocabulary', 'type': 'string', 'mode': 'w',
         'label': 'Vocabulary', 'is_required' : 1},
        {'id': 'translated', 'type': 'boolean', 'mode': 'w',
         'label': 'Is vocabulary translated on display'},
        {'id': 'size', 'type': 'int', 'mode': 'w',
         'label': 'Size'},
        {'id': 'format_empty', 'type': 'string', 'mode': 'w',
         'label': 'Format for empty list'},
        {'id': 'render_format', 'type': 'selection', 'mode': 'w',
         'select_variable': 'render_formats',
         'label': 'Render format'},
        # Enables the possibility to add blank values to vocabulary just to
        # change the way the list is presented (using items like 'choose a
        # category' or '------------' to separate items) and not affect the way
        # the value will be validated if the widget is required.
        # Before this, if the widget was required, default behavior was to
        # accept blank values if they were in the vocabulary (e.g
        # blank_value_ok_if_required = 1)
        {'id': 'blank_value_ok_if_required', 'type': 'boolean', 'mode':'w',
         'label': "Accept blank values when validating"},
        )
    render_formats = ['select', 'radio', 'checkbox']
    # XXX make a menu for the vocabulary.

    vocabulary = ''
    translated = 0
    size = 0
    format_empty = ''
    render_format = render_formats[0]
    blank_value_ok_if_required = 1

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
        if _isinstance(value, StringType):
            LOG('CPSGenericMultiSelectWidget.prepare', TRACE,
                'expected List got String %s converting into list' % value)
            if value:
                value = [value,]
            else:
                value = []
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
            if i != '':
                try:
                    i = str(i)
                except ValueError:
                    datastructure.setError(widget_id, "cpsschemas_err_multiselect")
                    return 0
                if not vocabulary.has_key(i):
                    datastructure.setError(widget_id, "cpsschemas_err_multiselect")
                    return 0
            else:
                if not vocabulary.has_key(i):
                    datastructure.setError(widget_id, "cpsschemas_err_multiselect")
                    return 0
                else:
                    if self.is_required and not self.blank_value_ok_if_required:
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
        widget_id = self.getWidgetId()
        value = datastructure[widget_id]
        vocabulary = self._getVocabulary(datastructure)
        portal = getToolByName(self, 'portal_url').getPortalObject()
        cpsmcat = portal.Localizer.default
        if mode == 'view':
            if not value:
                # XXX L10N empty format may be subject to i18n.
                return self.format_empty
            # XXX customize view mode, lots of displays are possible
            elif getattr(self, 'translated', None):
                return ', '.join([escape(cpsmcat(vocabulary.getMsgid(i, i))) for i in value])
            else:
                return ', '.join([escape(vocabulary.get(i, i)) for i in value])
        elif mode == 'edit':
            in_selection = 0
            res = ''
            html_widget_id = self.getHtmlWidgetId()
            render_format = self.render_format
            if render_format not in self.render_formats:
                raise RuntimeError('unknown render format %s' % render_format)
            if render_format == 'select':
                kw = {'name': html_widget_id+':list',
                      'multiple': 'multiple',
                      }
                if self.size:
                    kw['size'] = self.size
                res = renderHtmlTag('select', **kw)
            # vocabulary options
            for k, v in vocabulary.items():
                if getattr(self, 'translated', None):
                    v = cpsmcat(vocabulary.getMsgid(k, k)).encode('ISO-8859-15', 'ignore')
                if render_format == 'select':
                    kw = {'value': k, 'contents': v}
                    if k in value:
                        kw['selected'] = 'selected'
                        in_selection = 1
                    res += renderHtmlTag('option', **kw)
                    res += '\n'
                else:
                    kw = {'id': html_widget_id+'_'+k,
                          'type': render_format,
                          'name': html_widget_id+':list',
                          'value': k,
                          }
                    if k in value:
                        kw['checked'] = 'checked'
                        in_selection = 1
                    res += renderHtmlTag('input', **kw)
                    kw = {'for': html_widget_id+'_'+k,
                          'contents': v,
                          }
                    res += renderHtmlTag('label', **kw)
                    res += '<br/>\n'
            # invalid selections
            for value_item in value:
                if value_item and value_item not in vocabulary.keys():
                    if render_format == 'select':
                        kw = {'value': value_item,
                              # XXX missing i18n for invalid
                              'contents': 'invalid: ' + value_item,
                              'selected': 'selected',
                              }
                        res += renderHtmlTag('option', **kw)
                        res += '\n'
                    else:
                        kw = {'id': html_widget_id+'_'+value_item,
                              'type': render_format,
                              'name': html_widget_id+':list',
                              'value': value_item,
                              'disabled': 'disabled',
                              }
                        res += renderHtmlTag('input', **kw)
                        kw = {'for': html_widget_id+'_'+value_item,
                              'contents': 'invalid: '+value_item,
                              }
                        res += renderHtmlTag('label', **kw)
                        res += '<br/>\n'
            # default option
            if not self.is_required and not vocabulary.has_key(''):
                if render_format == 'select':
                    kw = {'value': '',
                          'contents': cpsmcat('label_none_selection').encode('ISO-8859-15', 'ignore'),
                          }
                    if not in_selection:
                        kw['selected'] = 'selected'
                    res += renderHtmlTag('option', **kw)
                    res += '\n'
                # not interesting to have a default choice for checkboxes
                elif render_format == 'radio':
                    kw = {'id': html_widget_id+'_empty',
                          'type': render_format,
                          'name': html_widget_id+':list',
                          'value': '',
                          }
                    if not in_selection:
                        kw['checked'] = 'checked'
                    res += renderHtmlTag('input', **kw)
                    kw = {'for': html_widget_id+'_empty',
                          'contents': cpsmcat('label_none_selection').encode('ISO-8859-15', 'ignore'),
                          }
                    res += renderHtmlTag('label', **kw)
                    res += '<br/>\n'
            if render_format == 'select':
                res += '</select>'
            default_tag = renderHtmlTag('input',
                                        type='hidden',
                                        name=html_widget_id+':tokens:default',
                                        value='')
            return default_tag+res
        raise RuntimeError('unknown mode %s' % mode)

InitializeClass(CPSGenericMultiSelectWidget)


class CPSGenericMultiSelectWidgetType(CPSWidgetType):
    """Generic MultiSelect widget type."""
    meta_type = "CPS Generic MultiSelect Widget Type"
    cls = CPSGenericMultiSelectWidget

InitializeClass(CPSGenericMultiSelectWidgetType)


##################################################

class CPSRangeListWidget(CPSWidget):
    """Range List widget."""
    meta_type = "CPS Range List Widget"

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


    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel."""
        widget_id = self.getWidgetId()
        value = datastructure[widget_id]
        if not _isinstance(value, ListType):
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
        if self.is_required and not len(v):
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
            if isinstance(i, StringType):
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


class CPSRangeListWidgetType(CPSWidgetType):
    """Range List widget type."""
    meta_type = "CPS Range List Widget Type"
    cls = CPSRangeListWidget

InitializeClass(CPSRangeListWidgetType)

##################################################

class CPSDocumentLanguageSelectWidget(CPSWidget):
    """Document Language Selection widget."""
    meta_type = "CPS Document Language Select Widget"

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
        Localizer = getToolByName(self, 'Localizer')
        if Localizer is not None:
            mcat = Localizer.default
        else:
            def mcat(msgid):
                return msgid

        for language in languages:
            language_title = mcat('label_language_%s'% language).encode(
                'ISO-8859-15', 'ignore')
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


class CPSDocumentLanguageSelectWidgetType(CPSWidgetType):
    """Document Language Select widget type."""
    meta_type = "CPS Document Language Select Widget Type"
    cls = CPSDocumentLanguageSelectWidget

InitializeClass(CPSDocumentLanguageSelectWidgetType)


##################################################

class CPSSubjectWidget(CPSMultiSelectWidget):
    """A widget featuring links to items by subject.

    The CPS Subject Widget is like the CPS MultiSelect Widget from which it
    derives, except in "view" mode where the listed entries have link on them
    to other documents on the portal which have the same subjects.
    """
    meta_type = "CPS Subject Widget"

    def getEntriesHtml(self, entries, vocabulary, translated=False):
        entries_html_list = []
        if translated:
            cpsmcat = getToolByName(self, 'translation_service', None)
            if cpsmcat is None:
                translated = False
        for subject_name in entries:
            if translated:
                subject_label = cpsmcat(
                    vocabulary.getMsgid(subject_name, subject_name),
                    subject_name)
                entries_html_list.append(self.getSubjectSearchLink(
                    subject_name, subject_label))
            else:
                entries_html_list.append(
                    self.getSubjectSearchLink(subject_name,
                                              subject_name))
        return ', '.join(entries_html_list)

    def getSubjectSearchLink(self, subject_name, subject_label):
        """Return an HTML link for the subject name with the given label."""
        return ('<a href="%s">%s</a>'
                % (self.getSubjectSearchUrl(escape(subject_name)),
                   escape(subject_label)))

    def getSubjectSearchUrl(self, subject_name):
        """Return the subject search URL.

        The provided links are actually requests to the portal search engine.
        """
        return "%s/search_form?Subject=%s" % (self.portal_url(), subject_name)


InitializeClass(CPSSubjectWidget)


class CPSSubjectWidgetType(CPSWidgetType):
    """Subject widget type."""
    meta_type = "CPS Subject Widget Type"
    cls = CPSSubjectWidget

InitializeClass(CPSSubjectWidgetType)


##################################################
#
# Register widget types.
#
WidgetTypeRegistry.register(CPSTextWidgetType)
WidgetTypeRegistry.register(CPSDateTimeWidgetType)
WidgetTypeRegistry.register(CPSAttachedFileWidgetType)
WidgetTypeRegistry.register(CPSZippedHtmlWidgetType)
WidgetTypeRegistry.register(CPSRichTextEditorWidgetType)
WidgetTypeRegistry.register(CPSExtendedSelectWidgetType)
WidgetTypeRegistry.register(CPSInternalLinksWidgetType)
WidgetTypeRegistry.register(CPSPhotoWidgetType)
WidgetTypeRegistry.register(CPSGenericSelectWidgetType)
WidgetTypeRegistry.register(CPSGenericMultiSelectWidgetType)
WidgetTypeRegistry.register(CPSRangeListWidgetType)
WidgetTypeRegistry.register(CPSDocumentLanguageSelectWidgetType)
WidgetTypeRegistry.register(CPSSubjectWidgetType)

