# Copyright (c) 2003-2004 Nuxeo SARL <http://nuxeo.com>
# Copyright (c) 2003 CEA <http://www.cea.fr>
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

"""
  DiskFile
"""

__version__ = '$Revision$'[11:-2]

import os
import sys
import logging

from Globals import InitializeClass, DTMLFile
from ComputedAttribute import ComputedAttribute
from AccessControl import ClassSecurityInfo
from OFS.Image import File
from TM import VTM

from Products.CMFCore.permissions import View

logger = logging.getLogger('CPSSchemas.DiskFile')

class DiskFile(File, VTM):
    """Stores the data of a file object into a file on the disk
    """
    meta_type = 'Disk File'
    security = ClassSecurityInfo()
    _v_new_file = False
    _v_tmp = False
    content_type = ''

    def __init__(self, id, title, file=None, content_type=None, storage_path='var/files'):
        self.__name__ = id
        self.title = self._filename = title # _filename prone to change
        self._file_store = storage_path
        self.precondition = '' # For Image.File compatibility
        self._v_new_file = True # NB: __init__ is bypassed by ZODB loads
        if file:
            data, size = self._read_data(file)
            content_type = self._get_content_type(file, data, id, content_type)
            self.update_data(data, content_type, size)

    def getFullFilename(self, filename=None):
        """Return the full path name to a file.

        If filename not specified, the current one is used.
        This is the temporary one if applicable or the permanent one
        """
        if filename is None:
            filename = self._v_tmp and self._v_tmp_filename or self._filename
        return os.path.join(INSTANCE_HOME, self._file_store, filename)

    def getNewFilename(self, suggested_id, tmp=False):
        """Return a free file name in the file store, based on suggested id.

        If new, an additional marker is also inserted."""

        dot = suggested_id.find('.')
        if dot != -1:
            ext = suggested_id[dot:]
            suggested_id = suggested_id[:dot]
        else:
            ext = ''

        path = os.path.join(INSTANCE_HOME, self._file_store)
        existing_files = os.listdir(path)
        newid = tmp and (suggested_id + '_tmp' + ext) or (suggested_id + ext)
        theint = 0
        # Q: Won't this be horribly slow when there are hundreds of documents ?
        # A: Probably.
        # GR: why not let the FS cope and use os.path.exists() ?
        while newid in existing_files:
            theint += 1
            baseid = suggested_id + str(theint)
            newid = tmp and (baseid + '_tmp' + ext) or (baseid + ext)
        return newid


    #
    # Transaction support
    #
    def _finish(self):
        # This is called after ZODB write
        if not self._v_tmp:
            return
        tmp_path = self.getFullFilename(self._v_tmp_filename)
        target = self.getFullFilename(self._filename)

        if sys.platform == 'win32' and not self._v_new_file:
            # Crappy win32 cannot do an atomic rename
            try:
                os.remove(target)
            except OSError:
                logger.warn('Error during transaction commit',
                    'Removing file %s failed. \nStray files may linger.\n',
                    target)
        os.rename(tmp_path, target)
        self._v_tmp = self._v_new_file = False

    def _abort(self):
        if not self._v_tmp:
            return
        self._v_tmp = self._v_new_file = False
        path = self.getFullFilename(self._v_tmp_filename)
        try:
            os.remove(path)
        except OSError:
            logger.warn('Error during transaction abort',
                'Removing file %s failed. \nStray files may linger.\n', path)

    #
    # API
    #
    def update_data(self, data, content_type=None, size=None):
        self._register()
        if content_type is not None:
            self.content_type = content_type
        elif not self.content_type:
            # Neither new nor old contentype specified.
            # Try to figure it out:
            self.content_type = self._get_content_type('', data,
                                self._filename, None)
        if size is None:
            size = len(data)
        self.size = size
        new_tmp = self.getNewFilename(self._filename, tmp=True)
        fpath = self.getFullFilename(new_tmp)
        file_d = open(fpath, 'wb')
        file_d.write(str(data))
        file_d.close()
        if self._v_tmp:
            # There is a previous temporary file. It is now outdated.
            oldpath = self.getFullFilename(self._v_tmp_filename)
            try:
                os.unlink(oldpath)
            except OSError:
                logger.error("Error attempting to remove the previous "
                             "temporary file %s", oldpath)
        self._v_tmp = True
        self._v_tmp_filename = new_tmp

        self.ZCacheable_invalidate()
        self.ZCacheable_set(None)
        self.http__refreshEtag()

        # must be done before ZODB write
        if self._v_new_file:
            self._filename = self.getNewFilename(self.title)

    security.declareProtected(View, 'getData')
    def getData(self):
        filename = self.getFullFilename()

        file = open(filename, 'rb')
        data = file.read()
        return data

    def __str__(self):
        return str(self.getData())

    security.declareProtected(View, 'data')
    data = ComputedAttribute(getData, 1)

    #
    # cut/copy/paste/delete support
    #
    def loadData(self):
        """Loads the data from the external object to internal attributes

        This is used for cut/copy/paste.
        XXX GR within a folder cut/paste, this can load gigabytes in RAM
               If this is for cut/copy/paste *only*, a simple set of
               flags would be much better.
        """
        self._copy_data = self.getData()

    def storeData(self):
        """Stores internal data into the external storage"""
        # Clear the _storage_id to force the use of a new object
        filename = self.getFullFilename()
        file = open(filename, 'wb')
        file.write(self._copy_data)
        del self._copy_data

    def manage_beforeDelete(self, item, container):
        self.loadData()
        try:
            os.remove(self.getFullFilename())
        except OSError:
            logger.warn('manage_beforeDelete: '
                'Removing file %s failed. \nStray files may linger.\n',
                    self.getFullFilename())

    def manage_afterClone(self, item):
        # This is a copy-paste operation, so duplicate the data!
        data = self.getData()
        self._filename = self.getNewFilename(self._filename)
        filename = self.getFullFilename()
        file = open(filename, 'wb')
        file.write(data)

    def manage_afterAdd(self, item, container):
        if hasattr(self, '_copy_data'):
            # This is a cut-paste operation, so restore the data loaded
            # in manage_beforeDelete!
            self.storeData()

    def get_size(self):
        """Get the size of a file or image.

        Returns the size of the file or image.
        """
        if getattr(self, 'size', None) is not None:
            return self.size
        return 0

    getSize = get_size #getSize is supposed to be deprecated

InitializeClass(DiskFile)

addDiskFileForm = DTMLFile('zmi/addDiskFileForm', globals())

def addDiskFile(self, id, title, file=None, content_type=None,
                storage_path='var/files', REQUEST=None):
    """Add a ZODBStorageItem."""
    ob = DiskFile(id, title, '', content_type, storage_path)
    self._setObject(id, ob)
    # Upload in two steps, as OFS.Image.File does, since this is more efficient
    if file:
        self._getOb(id).manage_upload(file)
    if content_type:
        self._getOb(id).content_type = content_type
    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(self.absolute_url() + '/manage_main')
