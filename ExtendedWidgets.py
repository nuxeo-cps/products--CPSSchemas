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

from zLOG import LOG, DEBUG, TRACE
from cgi import escape
from re import match
from Globals import InitializeClass
from Acquisition import aq_base
from types import ListType, TupleType, StringType
from DateTime.DateTime import DateTime
from ZPublisher.HTTPRequest import FileUpload
from OFS.Image import cookId, File

from Products.PythonScripts.standard import structured_text, newline_to_br
from Products.CMFCore.utils import getToolByName
from Products.CPSSchemas.WidgetTypesTool import WidgetTypeRegistry
from Products.CPSSchemas.Widget import CPSWidget, CPSWidgetType
from Products.CPSSchemas.BasicWidgets import CPSSelectWidget, \
     _isinstance, CPSStringWidget, CPSImageWidget, CPSNoneWidget, CPSFileWidget,\
     renderHtmlTag

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
        {'id': 'render_position', 'type': 'selection', 'mode': 'w',
         'select_variable': 'all_render_positions',
         'label': 'Render position'},
        {'id': 'render_format', 'type': 'selection', 'mode': 'w',
         'select_variable': 'all_render_formats',
         'label': 'Render format'},
        {'id': 'configurable', 'type': 'selection', 'mode': 'w',
         'select_variable': 'all_configurable',
         'label': 'What is user configurable, require extra fields'},
        )
    all_configurable = ['nothing', 'position', 'format', 'position and format']
    all_render_positions = ['normal', 'col_left', 'col_right']
    all_render_formats = ['text', 'stx', 'html'] # remove 'pre' as we do the
                                                 # same using text

    width = 40
    height = 5
    size_max = 0
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
        datastructure[widget_id + '_rposition'] = rposition
        datastructure[widget_id + '_rformat'] = rformat

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
            if self.configurable != 'nothing':
                if len(self.fields) > 1:
                    rposition = datastructure[widget_id + '_rposition']
                    if rposition and rposition in self.all_render_positions:
                        datamodel[self.fields[1]] = rposition
                if len(self.fields) > 2:
                    rformat = datastructure[widget_id + '_rformat']
                    if rformat and rformat in self.all_render_formats:
                        datamodel[self.fields[2]] = rformat
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
    """DateTime widget."""
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
            if type(v) is StringType:
                v = DateTime(v)
            d = str(v.day())
            m = str(v.month())
            y = str(v.year())
            locale = self.Localizer.get_selected_language()
            if locale in ('en', 'hu', ):
                date = m+'/'+d+'/'+y
            else:
                date = d+'/'+m+'/'+y
            hour = str(v.h_24())
            minute = str(v.minute())

        datastructure[widget_id] = v
        datastructure[widget_id+'_date'] = date
        datastructure[widget_id+'_hour'] = hour or self.time_hour_default
        datastructure[widget_id+'_minute'] = minute or \
                                             self.time_minutes_default

    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel."""
        datamodel = datastructure.getDataModel()
        field_id = self.fields[0]
        widget_id = self.getWidgetId()

        date = datastructure[widget_id+'_date'].strip()
        hour = datastructure[widget_id+'_hour'].strip() or \
               self.time_hour_default
        minute = datastructure[widget_id+'_minute'].strip() or \
                 self.time_minutes_default

        if not (date):
            if self.is_required:
                datastructure[widget_id] = ''
                datastructure.setError(widget_id, "cpsschemas_err_required")
                return 0
            else:
                datamodel[field_id] = None
                return 1

        if not match(r'^[0-9]?[0-9]/[0-9]?[0-9]/[0-9]{2,4}$', date):
            datastructure.setError(widget_id, 'cpsschemas_err_date')
            return 0

        locale = self.Localizer.get_selected_language()
        if locale in ('en', 'hu', ):
            m, d, y = date.split('/')
        else:
            d, m, y = date.split('/')

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
        # Compute preview info for widget.
        if len(self.fields) > 2 and datamodel.get(self.fields[2]) is not None:
            preview_id = self.fields[2]
        else:
            preview_id = None
        datastructure[widget_id + '_preview'] = preview_id
        # make update from request work
        datastructure[widget_id + '_choice'] = ''
        datastructure[widget_id + '_title'] = ''
        datastructure[widget_id + '_filename'] = ''


    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel."""
        datamodel = datastructure.getDataModel()
        field_id = self.fields[0]
        widget_id = self.getWidgetId()
        choice = datastructure[widget_id+'_choice']
        filetitle = datastructure[widget_id + '_title']
        file = None
        err = 0
        if choice == 'keep':
            file = datamodel[field_id]
            if file is not None:
                # do not allow empty title: it is used as link text
                if not filetitle:
                    filetitle = datastructure[widget_id + '_filename']
                file.manage_changeProperties(title=filetitle)
                datamodel[field_id] = file
        if choice == 'delete':
            datamodel[field_id] = None
        elif choice == 'change' and datastructure.get(widget_id):
            fileUpload = datastructure[widget_id]
            if not _isinstance(fileUpload, FileUpload):
                err = 'cpsschemas_err_file'
            else:
                ms = self.size_max
                if fileUpload.read(1) == '':
                    err = 'cpsschemas_err_file_empty'
                else:
                    fileUpload.seek(0)
                    fileReadLength = len(fileUpload.read(ms + 1))
                if ms and fileReadLength > ms:
                    err = 'cpsschemas_err_file_too_big'
                else:
                    fileUpload.seek(0)
                    # ignore title value from form;
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
        if err:
            datastructure.setError(widget_id, err)
            LOG('CPSAttachedFileWidget', DEBUG,
                'error %s on %s' % (err, `file`))
        else:
            self.prepare(datastructure)

        return not err

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        render_method = 'widget_attachedfile_render'
        meth = getattr(self, render_method, None)
        if meth is None:
            raise RuntimeError("Unknown Render Method %s for widget type %s"
                               % (render_method, self.getId()))

        if mode == 'create':
            file_info = {'empty_file': 1,
                         'content_url': '',
                         'current_name': '-',
                         'current_title': '',
                         'mimetype': '',
                         'last_modified': '',
                        }
        else:
            file_info = self.getFileInfo(datastructure)

        return meth(mode=mode, datastructure=datastructure,
                    **file_info)

InitializeClass(CPSAttachedFileWidget)


class CPSAttachedFileWidgetType(CPSWidgetType):
    """AttachedFile widget type."""
    meta_type = "CPS AttachedFile Widget Type"
    cls = CPSAttachedFileWidget

InitializeClass(CPSAttachedFileWidgetType)

#################################################

class CPSRichTextEditorWidget(CPSWidget):
    """Rich Text Editor widget."""
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
            if line.strip() != '':
                v.append(line)

        if err:
            datastructure.setError(widget_id, err)
        else:
            datamodel = datastructure.getDataModel()
            datamodel[self.fields[0]] = v

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
                   'CPS String Field',) # render_position if configurable
    field_inits = ({}, {'is_searchabletext': 1,}, {})

    _properties = CPSImageWidget._properties + (
        {'id': 'render_position', 'type': 'selection', 'mode': 'w',
         'select_variable': 'all_render_positions',
         'label': 'Render position'},
        {'id': 'configurable', 'type': 'selection', 'mode': 'w',
         'select_variable': 'all_configurable',
         'label': 'What is user configurable, require extra fields'},
        )
    all_configurable = ['nothing', 'position']
    all_render_positions = ['left', 'center', 'right']

    allow_resize = 1
    configurable = all_configurable[0]
    render_position = all_render_positions[0]

    def prepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel."""
        datamodel = datastructure.getDataModel()
        widget_id = self.getWidgetId()
        datastructure[widget_id] = datamodel[self.fields[0]]
        datastructure[widget_id + '_subtitle'] = datamodel[self.fields[1]]
        rposition = self.render_position
        if self.configurable != 'nothing':
            if len(self.fields) > 2:
                v = datamodel[self.fields[2]]
                if v in self.all_render_positions:
                    rposition = v
        datastructure[widget_id + '_rposition'] = rposition
        # make update from request work
        datastructure[widget_id + '_choice'] = ''
        datastructure[widget_id + '_title'] = ''
        if self.allow_resize:
            datastructure[widget_id + '_resize'] = ''

    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel."""
        datamodel = datastructure.getDataModel()
        field_id = self.fields[0]
        widget_id = self.getWidgetId()
        ret = CPSImageWidget.validate(self, datastructure, **kw)
        if ret and datamodel[field_id]:
            datamodel[self.fields[1]] = datastructure[widget_id + '_subtitle']
            if self.configurable != 'nothing':
                if len(self.fields) > 2:
                    rposition = datastructure[widget_id + '_rposition']
                    if rposition and rposition in self.all_render_positions:
                        datamodel[self.fields[2]] = rposition

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

        if kw['layout_mode'] == 'create':
            img_info = {'empty_file': 1,
                        'content_url': '',
                        'image_tag': '',
                        'current_name': '-',
                        'current_title': '',
                        'mimetype': '',
                        'last_modified': '',
                       }
        else:
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
         'label': 'Vocabulary'},
        {'id': 'render_format', 'type': 'selection', 'mode': 'w',
         'select_variable': 'render_types',
         'label': 'Render format : select menu (default) or radio buttons'},
        )
    render_formats = ['select', 'radio']

    # XXX make a menu for the vocabulary.
    vocabulary = ''
    render_format = render_formats[0]

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
                datastructure.setError(widget_id, "cpsschemas_err_select")
                return 0
        else:
            if self.is_required and not vocabulary.has_key(value):
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
            return escape(vocabulary.get(value, value))
        elif mode == 'edit':
            in_selection = 0
            res = ''
            html_widget_id = self.getHtmlWidgetId()
            render_format = self.render_format
            if render_format not in self.render_formats:
                raise RuntimeError('unknown render format %s' % render_format)
            if render_format == 'select':
                res = renderHtmlTag('select', name=html_widget_id)
            # vocabulary options
            for k, v in vocabulary.items():
                if render_format == 'select':
                    kw = {'value': k, 'contents': v}
                    if value == k:
                        kw['selected'] = None
                        in_selection = 1
                    res += renderHtmlTag('option', **kw)
                    res += '\n'
                else:
                    kw = {'id': html_widget_id+'_'+k,
                          'type': render_format,
                          'name': html_widget_id,
                          'value': k,
                          }
                    if value == k:
                        kw['checked'] = None
                        in_selection = 1
                    res += renderHtmlTag('input', **kw)
                    kw = {'for': html_widget_id+'_'+k,
                          'contents': v,
                          }
                    res += renderHtmlTag('label', **kw)
                    res += '<br/>\n'
            # invalid selections
            if value and not in_selection:
                if render_format == 'select':
                    kw = {'value': value, 'contents': 'invalid: '+value,
                          'selected': None}
                    res += renderHtmlTag('option', **kw)
                    res += '\n'
                else:
                    kw = {'id': html_widget_id+'_'+value,
                          'type': render_format,
                          'name': html_widget_id,
                          'value': k,
                          'disabled': None,
                          }
                    res += renderHtmlTag('input', **kw)
                    kw = {'for': html_widget_id+'_'+value,
                          'contents': 'invalid: '+value,
                          }
                    res += renderHtmlTag('label', **kw)
                    res += '<br/>\n'
            # default option
            if not self.is_required and not vocabulary.has_key(''):
                if render_format == 'select':
                    kw = {'value': '', 'contents': 'None'}
                    if not in_selection:
                        kw['selected'] = None
                    res += renderHtmlTag('option', **kw)
                    res += '\n'
                else:
                    kw = {'id': html_widget_id+'_empty',
                          'type': render_format,
                          'name': html_widget_id,
                          'value': '',
                          }
                    if not in_selection:
                        kw['checked'] = None
                    res += renderHtmlTag('input', **kw)
                    kw = {'for': html_widget_id+'_empty',
                          'contents': 'None',
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
         'label': 'Vocabulary'},
        {'id': 'size', 'type': 'int', 'mode': 'w',
         'label': 'Size'},
        {'id': 'format_empty', 'type': 'string', 'mode': 'w',
         'label': 'Format for empty list'},
        {'id': 'render_format', 'type': 'selection', 'mode': 'w',
         'select_variable': 'render_types',
         'label': 'Render format : select menu (default), radio buttons or checkboxes'},
        )
    render_formats = ['select', 'radio', 'checkbox']
    # XXX make a menu for the vocabulary.

    vocabulary = ''
    vocabulary = ''
    size = 0
    format_empty = ''
    render_format = render_formats[0]

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
        datamodel = datastructure.getDataModel()
        value = datamodel[self.fields[0]]
        if _isinstance(value, StringType):
            LOG('CPSGenericMultiSelectWidget.prepare', TRACE,
                'expected List got String %s converting into list' % value)
            if value:
                value = ['value',]
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
            in_selection = 0
            res = ''
            html_widget_id = self.getHtmlWidgetId()
            render_format = self.render_format
            if render_format not in self.render_formats:
                raise RuntimeError('unknown render format %s' % render_format)
            if render_format == 'select':
                kw = {'name': html_widget_id+':list',
                      'multiple': None,
                      }
                if self.size:
                    kw['size'] = self.size
                res = renderHtmlTag('select', **kw)
            # vocabulary options
            for k, v in vocabulary.items():
                if render_format == 'select':
                    kw = {'value': k,
                          'contents': v}
                    if k in value:
                        kw['selected'] = None
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
                        kw['checked'] = None
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
                              'contents': 'invalid: '+value_item,
                              'selected': None}
                        res += renderHtmlTag('option', **kw)
                        res += '\n'
                    else:
                        kw = {'id': html_widget_id+'_'+value_item,
                              'type': render_format,
                              'name': html_widget_id+':list',
                              'value': value_item,
                              'disabled': None,
                              }
                        res += renderHtmlTag('input', **kw)
                        kw = {'for': html_widget_id+'_'+value,
                              'contents': 'invalid: '+value,
                              }
                        res += renderHtmlTag('label', **kw)
                        res += '<br/>\n'
            # default option
            if not self.is_required and not vocabulary.has_key(''):
                if render_format == 'select':
                    kw = {'value': '', 'contents': 'None'}
                    if not in_selection:
                        kw['selected'] = None
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
                        kw['checked'] = None
                    res += renderHtmlTag('input', **kw)
                    kw = {'for': html_widget_id+'_empty',
                          'contents': 'None',
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
#
# Register widget types.
#

WidgetTypeRegistry.register(CPSTextWidgetType)
WidgetTypeRegistry.register(CPSDateTimeWidgetType)
WidgetTypeRegistry.register(CPSAttachedFileWidgetType)
WidgetTypeRegistry.register(CPSRichTextEditorWidgetType)
WidgetTypeRegistry.register(CPSExtendedSelectWidgetType)
WidgetTypeRegistry.register(CPSInternalLinksWidgetType)
WidgetTypeRegistry.register(CPSPhotoWidgetType)
WidgetTypeRegistry.register(CPSGenericSelectWidgetType)
WidgetTypeRegistry.register(CPSGenericMultiSelectWidgetType)

