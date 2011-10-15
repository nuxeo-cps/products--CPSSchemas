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
"""BasicWidgets

Definition of standard widget types.
"""

import logging

from Globals import InitializeClass
from ZPublisher.HTTPRequest import FileUpload
from OFS.Image import cookId, File

from Products.CMFCore.utils import getToolByName

from Products.CPSUtil.id import generateFileName
from Products.CPSUtil.html import renderHtmlTag
from Products.CPSUtil.file import PersistableFileUpload
from Products.CPSUtil.file import makeFileUploadFromOFSFile
from Products.CPSSchemas.utils import getHumanReadableSize
from Products.CPSSchemas.Widget import CPSWidget

logger = logging.getLogger(__name__)


class CPSFileWidget(CPSWidget):
    """File widget.

    The DataStructure stores either a FileUpload or None.

    A FileUpload itself has a filename.

    When stored in the DataModel, the filename is stored as the File
    title. The File id is fixed to the id under which its parent
    container knows it.
    """

    meta_type = 'File Widget'

    field_types = ('CPS File Field',    # File content
                   'CPS String Field',  # Title
                   )

    _properties = CPSWidget._properties + (
        {'id': 'size_max', 'type': 'int', 'mode': 'w',
         'label': 'Maximum file size'},
        {'id': 'display_external_editor', 'type': 'boolean', 'mode': 'w',
         'label': 'Display link to external editor in edit mode'},
        {'id': 'ascii_filename', 'type': 'boolean', 'mode': 'w',
         'label': 'Convert file name to ascii'},
        )
    size_max = 4*1024*1024
    display_external_editor = True

    logger = logger # available for subclasses

    def getHumanReadableSize(self, size):
        """ get human readable size
        """
        hr = getHumanReadableSize(size)
        cpsmcat = getToolByName(self, 'translation_service')
        return str(hr[0]) + ' ' + cpsmcat(hr[1])

    def getFileSize(self, fileupload):
        """Find size of given fileupload.

        fileupload is assumed not to be None."""

        current = fileupload.tell()
        fileupload.seek(0, 2) # end of file
        size = fileupload.tell()
        fileupload.seek(current)
        return size

    def getFileSize(self, fileupload):
        """Find size of given fileupload.

        fileupload is assumed not to be None."""

        current = fileupload.tell()
        fileupload.seek(0, 2) # end of file
        size = fileupload.tell()
        fileupload.seek(current)
        return size

    def cleanFileName(self, name):
        return generateFileName(name, ascii=self.ascii_filename)

    def getFileInfo(self, datastructure):
        """Get the file info from the datastructure."""
        widget_id = self.getWidgetId()
        fileupload = datastructure[widget_id]
        dm = datastructure.getDataModel()
        field_id = self.fields[0]
        if fileupload:
            empty_file = False
            session_file = isinstance(fileupload, PersistableFileUpload)
            current_filename = self.cleanFileName(fileupload.filename)
            size = self.getFileSize(fileupload)
            file = dm[field_id] # last stored file
            if file is not None:
                last_modified = str(file._p_mtime or '')
            else:
                last_modified = ''
        else:
            empty_file = True
            session_file = False
            current_filename = ''
            size = 0
            last_modified = ''

        content_url = dm.fileUri(field_id) # can be None

        # get the mimetype
        registry = getToolByName(self, 'mimetypes_registry')
        mimetype = (registry.lookupExtension(current_filename.lower()) or
                    registry.lookupExtension('file.bin'))
        # Using a title if there is one present in the datastructure
        # otherwise defaulting to the file name.
        title = datastructure.get(widget_id + '_title', current_filename)

        file_info = {
            'empty_file': empty_file,
            'session_file': session_file,
            'current_filename': current_filename,
            'title': title,
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
            filename = file.title
        else:
            filename = ''
        datastructure[widget_id + '_filename'] = filename

        if len(self.fields) > 1:
            datastructure[widget_id + '_title'] = datamodel[self.fields[1]]
        else:
            datastructure[widget_id + '_title'] = ''

    def unprepare(self, datastructure):
        # Remove costly things already stored from the datastructure
        try:
            del datastructure[self.getWidgetId()]
        except KeyError:
            # unprepare may be called several times
            pass

    def getFileName(self, fileupload, datastructure, choice, old_filename=''):
        filename = datastructure[self.getWidgetId()+'_filename'].strip()
        if choice == 'change' and filename == old_filename:
            # if upload with input field unchanged, use fileupload filename
            filename = cookId('', '', fileupload)[0].strip()
        filename = self.cleanFileName(filename or 'file.bin')
        return filename

    def checkFileName(self, filename, mimetype):
        return '', {}

    def makeFile(self, filename, fileupload, datastructure):
        return File(self.fields[0], filename, fileupload)

    def otherProcessing(self, choice, datastructure):
        return

    def validate(self, datastructure, **kw):
        """Update datamodel from user data in datastructure.
        """
        datamodel = datastructure.getDataModel()
        field_id = self.fields[0]
        widget_id = self.getWidgetId()
        choice = datastructure[widget_id + '_choice']
        store = False
        fileupload = None
        mimetype = None
        old_file = datamodel[field_id]
        if old_file is not None:
            old_filename = old_file.title
        else:
            old_filename = ''

        if choice == 'delete':
            if self.is_required:
                return self.validateError('cpsschemas_err_required', {},
                                          datastructure)
            datamodel[field_id] = None
        elif choice == 'keep':
            fileupload = datastructure[widget_id]
            if fileupload is None and self.is_required:
                return self.validateError('cpsschemas_err_required', {},
                                          datastructure)

            if isinstance(fileupload, PersistableFileUpload):
                # Keeping something from the session means we
                # actually want to store it.
                store = True
            else:
                # Nothing to change, don't pollute datastructure
                # with something costly already stored, which therefore
                # doesn't need to be kept in the session.
                self.unprepare(datastructure)
        elif choice == 'change':
            fileupload = datastructure[widget_id]
            if not fileupload:
                return self.validateError('cpsschemas_err_file_empty', {},
                                          datastructure)
            if not isinstance(fileupload, FileUpload):
                return self.validateError('cpsschemas_err_file', {},
                                          datastructure)
            size = self.getFileSize(fileupload)
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

        # Find filename
        if fileupload is not None:
            filename = self.getFileName(fileupload, datastructure, choice,
                                        old_filename)
            if filename != old_filename:
                registry = getToolByName(self, 'mimetypes_registry')
                mimetype = registry.lookupExtension(filename.lower())
                if mimetype is not None:
                    mimetype = str(mimetype) # normalize
                err, err_mapping = self.checkFileName(filename, mimetype)
                if err:
                    return self.validateError(err, err_mapping, datastructure)
        elif datamodel[field_id] is not None:
            # FIXME: not correct in the case of change=='resize' (CPSPhotoWidget)
            filename = datamodel[field_id].title

        # Set/update data
        if store:
            # Create file
            file = self.makeFile(filename, fileupload, datastructure)
            # Fixup mimetype
            if mimetype and file.content_type != mimetype:
                file.content_type = mimetype
            # Store
            datamodel[field_id] = file
        elif datamodel[field_id] is not None:
            # Change filename
            if datamodel[field_id].title != filename:
                datamodel[field_id].title = filename

        return True

    def validateError(self, err, err_mapping, datastructure):
        self.logger.debug("Validation error %s", err)
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
