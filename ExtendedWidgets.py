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

from zLOG import LOG, DEBUG
from Globals import InitializeClass
from Acquisition import aq_base
from AccessControl import ClassSecurityInfo
from Products.PythonScripts.standard import structured_text, newline_to_br

from Products.CPSSchemas.WidgetTypesTool import WidgetTypeRegistry
from Products.CPSSchemas.Widget import CPSWidget, CPSWidgetType
from Products.CPSSchemas.BasicWidgets import renderHtmlTag, CPSSelectWidget

##################################################
# previously named CPSTextAreaWidget in BasicWidget r1.78
class CPSTextWidget(CPSWidget):
    """Text widget."""
    meta_type = "CPS Text Widget"

    # Warning if configurable the widget require field[1] and field[2]
    field_types = ('CPS String Field',  # text value
                   'CPS String Field',  # render_format if configurable
                   'CPS String Field')  # render_position if configurable
    field_inits = ({'is_indexed': 1,}, {}, {})

    _properties = CPSWidget._properties + (
        {'id': 'width', 'type': 'int', 'mode': 'w',
         'label': 'Width'},
        {'id': 'height', 'type': 'int', 'mode': 'w',
         'label': 'Height'},
        {'id': 'render_format', 'type': 'selection', 'mode': 'w',
         'select_variable': 'all_render_formats',
         'label': 'Render format'},
        {'id': 'render_position', 'type': 'selection', 'mode': 'w',
         'select_variable': 'all_render_positions',
         'label': 'Render position'},
        {'id': 'configurable', 'type': 'boolean', 'mode': 'w',
         'label': 'Render format and position are editable, REQUIRES 3 FIELDS'},

        )
    all_render_formats = ['text', 'pre', 'stx', 'html']
    all_render_positions = ['normal', 'col_left', 'col_right']

    width = 40
    height = 5
    render_format = all_render_formats[0]
    render_position = all_render_positions[0]
    configurable = 0

    def prepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel."""
        datamodel = datastructure.getDataModel()
        widget_id = self.getWidgetId()
        datastructure[widget_id] = str(datamodel[self.fields[0]])
        if self.configurable and len(self.fields) != 3:
            raise ValueError("Invalid text widget '%s' " % widget_id +
                             "configurable text requires 3 fields.")
        if self.configurable:
            datastructure[widget_id + '_rformat'] = datamodel[self.fields[1]]
            datastructure[widget_id + '_rposition'] = datamodel[self.fields[2]]
        else:
            datastructure[widget_id + '_rformat'] = self.render_format
            datastructure[widget_id + '_rposition'] = self.render_position

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
        if self.configurable:
            rformat = datastructure[widget_id + '_rformat']
            rposition = datastructure[widget_id + '_rposition']
            if rformat and rformat in self.all_render_formats:
                datamodel[self.fields[1]] = rformat
                LOG('text', DEBUG, 'saving rformat = %s' % rformat)
            if rposition and rposition in self.all_render_positions:
                datamodel[self.fields[2]] = rposition
                LOG('text', DEBUG, 'saving rposition = %s' % rposition)
        return 1

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        render_method = 'widget_text_render'
        meth = getattr(self, render_method, None)
        if meth is None:
            raise RuntimeError("Unknown Render Method %s for widget type %s"
                               % (render_method, self.getId()))
        widget_id = self.getWidgetId()
        value = datastructure[widget_id]
        rformat = datastructure[widget_id + '_rformat']
        rposition = datastructure[widget_id + '_rposition']
        if mode == 'view':
            if rformat == 'pre':
                value = '<pre>'+escape(value)+'</pre>'
            elif rformat == 'stx':
                value = structured_text(value)
            elif rformat == 'text':
                value = newline_to_br(value)
            elif rformat == 'html':
                pass
            else:
                RuntimeError("unknown render_format '%s' for '%s'" %
                             (rformat, self.getId()))
        return meth(mode=mode, datastructure=datastructure,
                    value=value, render_format=rformat,
                    render_position=rposition)

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
         'label': 'enable time setting'},
        )
    view_format = 'medium'
    time_setting = 1

    def prepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel."""
        datamodel = datastructure.getDataModel()
        v = datamodel[self.fields[0]]
        if not v and self.is_required:
            v = DateTime()
        widget_id = self.getWidgetId()
        date = ''
        hour = minute = ''
        if v is not None:
            d = str(v.day())
            m = str(v.month())
            y = str(v.year())
            locale = self.Localizer.default.get_selected_language()
            if locale in ('en', 'hu', ):
                date = m+'/'+d+'/'+y
            else:
                date = d+'/'+m+'/'+y
            hour = str(v.h_24())
            minute = str(v.minute())

        datastructure[widget_id] = v
        datastructure[widget_id+'_date'] = date
        datastructure[widget_id+'_hour'] = hour or '12'
        datastructure[widget_id+'_minute'] = minute or '00'

    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel."""
        datamodel = datastructure.getDataModel()
        field_id = self.fields[0]
        widget_id = self.getWidgetId()

        date = datastructure[widget_id+'_date'].strip()
        hour = datastructure[widget_id+'_hour'].strip() or '12'
        minute = datastructure[widget_id+'_minute'].strip() or '00'

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

        locale = self.Localizer.default.get_selected_language()
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
        value = datastructure[self.getWidgetId()]
        return meth(mode=mode, datastructure=datastructure)


InitializeClass(CPSDateTimeWidget)


class CPSDateTimeWidgetType(CPSWidgetType):
    """DateTime widget type."""
    meta_type = "CPS DateTime Widget Type"
    cls = CPSDateTimeWidget

InitializeClass(CPSDateTimeWidgetType)



##################################################
class CPSAttachedFileWidget(CPSWidget):
    """AttachedFile widget."""
    meta_type = "CPS AttachedFile Widget"

    # XXX The second and third fields are actually optional...
    field_types = ('CPS File Field', 'CPS String Field', 'CPS File Field')
    field_inits = ({'is_indexed': 0,
                    'suffix_text': '_f1', # _f# are autocomputed field ext
                    'suffix_html': '_f2',
                    },
                   {'is_indexed': 1,
                    },
                   {'is_indexed': 0,
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
                    file = File(fileid, filetitle, file)
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

InitializeClass(CPSAttachedFileWidget)


class CPSAttachedFileWidgetType(CPSWidgetType):
    """AttachedFile widget type."""
    meta_type = "CPS AttachedFile Widget Type"
    cls = CPSAttachedFileWidget

InitializeClass(CPSAttachedFileWidgetType)

#################################################

class CPSRichTextEditorWidget(CPSWidget):
    """Rich Text Editor widget."""
    meta_type = "CPS Rich Text EditorWidget"

    field_types = ('CPS String Field',)
    field_inits = ({'is_indexed': 1,},)

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
                        current_name=current_name)

InitializeClass(CPSRichTextEditorWidget)

class CPSRichTextEditorWidgetType(CPSWidgetType):
    """ RTE widget type """
    meta_type = "CPS Rich Text Editor Widget Type "
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

##################################################

class CPSLinkWidget(CPSWidget):
    """Link widget."""
    meta_type = "CPS Link Widget"

    field_types = ('CPS String Field', 'CPS String Field', 'CPS String Field')
    field_inits = ({'is_indexed': 1,},
                   {'is_indexed': 1,},
                   {'is_indexed': 1,},)

    def prepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel."""
        datamodel = datastructure.getDataModel()
        widget_id = self.getWidgetId()
        datastructure[widget_id] = datamodel[self.fields[0]]
        datastructure[widget_id + '_content'] = datamodel[self.fields[1]]
        datastructure[widget_id + '_title'] = datamodel[self.fields[2]]

    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel."""
        widget_id = self.getWidgetId()
        href = datastructure[widget_id]
        content = datastructure[widget_id + '_content']
        title = datastructure[widget_id + '_title']
        err = 0
        try:
            href = str(href).strip()
            content = str(content).strip()
            title = str(title).strip()
        except ValueError:
            err = 'cpsschemas_err_string'
        else:
            if not href and self.is_required:
                datastructure[widget_id] = ''
                err = 'cpsschemas_err_required'
            elif href and not match(
                r'^((http://)|/)?([\w\~](\:|\.|\-|\/|\?|\=)?){2,}$', href):
                err = 'cpsschemas_err_url'
        if err:
            datastructure.setError(widget_id, err)
        else:
            datamodel = datastructure.getDataModel()
            datamodel[self.fields[0]] = href
            datamodel[self.fields[1]] = content
            datamodel[self.fields[2]] = title

        return not err

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        href = datastructure[self.getWidgetId()]
        content = datastructure[self.getWidgetId() + '_content']
        title = datastructure[self.getWidgetId() + '_title']
        render_method = 'widget_link_render'
        meth = getattr(self, render_method, None)
        if meth is None:
            raise RuntimeError("Unknown Render Method %s for widget type %s"
                               % (render_method, self.getId()))
        if mode in ('view', 'edit'):
            return meth(mode=mode, datastructure=datastructure,
                        href=href, content=content, title=title)

        raise RuntimeError('unknown mode %s' % mode)

InitializeClass(CPSLinkWidget)


class CPSLinkWidgetType(CPSWidgetType):
    """Link widget type."""
    meta_type = "CPS Link Widget Type"
    cls = CPSLinkWidget

InitializeClass(CPSLinkWidgetType)


##########################################

class CPSInternalLinksWidget(CPSWidget):
    """Internal Links widget."""
    meta_type = "CPS InternalLinks Widget"

    field_types = ('CPS String List Field',)
    field_inits = ({'is_indexed': 1,},)

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

#
# Register widget types.
#

WidgetTypeRegistry.register(CPSTextWidgetType, CPSTextWidget)
WidgetTypeRegistry.register(CPSDateTimeWidgetType, CPSDateTimeWidget)
WidgetTypeRegistry.register(CPSAttachedFileWidgetType, CPSAttachedFileWidget)
WidgetTypeRegistry.register(CPSRichTextEditorWidgetType,
                            CPSRichTextEditorWidget)
WidgetTypeRegistry.register(CPSExtendedSelectWidgetType,
                            CPSExtendedSelectWidget)
WidgetTypeRegistry.register(CPSLinkWidgetType, CPSLinkWidget)
WidgetTypeRegistry.register(CPSInternalLinksWidgetType,
                            CPSInternalLinksWidget)


