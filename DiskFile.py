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

from zLOG import LOG, DEBUG, ERROR, WARNING
from Globals import InitializeClass, DTMLFile
from ComputedAttribute import ComputedAttribute
from AccessControl import ClassSecurityInfo
from OFS.Image import File
from TM import VTM

from Products.CMFCore.CMFCorePermissions import View

class DiskFile(File, VTM):
    """Stores the data of a file object into a file on the disk
    """
    meta_type = 'Disk File'
    security = ClassSecurityInfo()
    is_new_file = 0
    content_type = ''

    def __init__(self, id, title, file=None, content_type=None, storage_path='var/files'):
        self.__name__ = id
        self.title = title
        self._file_store = storage_path
        self._filename = self.getNewFilename(id)
        self._is_new_file = 1
        self.precondition = '' # For Image.File compatibility
        if file:
            data, size = self._read_data(file)
            content_type = self._get_content_type(file, data, id, content_type)
            self.update_data(data, content_type, size)

    def getFullFilename(self, filename=None):
        """Returns the full path name to a file"""
        if filename == None:
            filename = self._filename
        return os.path.join(INSTANCE_HOME, self._file_store, filename)

    def getNewFilename(self, suggested_id):
        path = os.path.join(INSTANCE_HOME, self._file_store)
        existing_files = os.listdir(path)
        newid = suggested_id
        theint = 0
        # Q: Won't this be horribly slow when there are hundreds of documents ?
        # A: Probably.
        while newid in existing_files:
            theint += 1
            newid = suggested_id + str(theint)
        return newid
      
    #
    # Transaction support
    #
    def _finish(self):
        if not self._is_new_file:
            try:
                os.remove(self.getFullFilename())
            except OSError:
                LOG('DiskFile', WARNING, 'Error during transaction commit',
                    'Removing file %s failed. \nStray files may linger.\n' %
                        self.getFullFilename())        
        self._is_new_file = 0
        os.rename(self.getFullFilename(self._new_filename),
                  self.getFullFilename())

    def _abort(self):
        try:
            os.remove(self.getFullFilename(self._new_filename))
        except OSError:
            LOG('DiskFile', WARNING, 'Error during transaction abort',
                'Removing file %s failed. \nStray files may linger.\n' %
                    self.getFullFilename(self._new_filename))        
   
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
        self._new_filename = self.getNewFilename(self._filename + '.new')
        filename = self.getFullFilename(self._new_filename)
        file = open(filename, 'wb')
        file.write(str(data))
    
    security.declareProtected(View, 'getData')
    def getData(self):
        filename = self.getFullFilename()
        file = open(filename, 'rb')
        data = file.read()
        return data

    security.declareProtected(View, 'data')
    data = ComputedAttribute(getData, 1)
        
    #
    # cut/copy/paste/delete support
    #
    def loadData(self):
        """Loads the data from the external object to internal attributes

        This is used for cut/copy/paste.
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
            LOG('DiskFile', WARNING, 'manage_beforeDelete',
                'Removing file %s failed. \nStray files may linger.\n' %
                    self.getFullFilename())        
        
    def manage_afterClone(self, item):
        filename = self.getFullFilename()
        # This is a copy-paste operation, so duplicate the data!
        data = self.getData()
        del self._filename
        filename = self.getFullFilename() # XXX Doesn't this fail?
        file = open(filename, 'wb')
        file.write(data)

    def manage_afterAdd(self, item, container):
        if hasattr(self, '_copy_data'):
            # This is a cut-paste operation, so restore the data loaded
            # in manage_beforeDelete!
            self.storeData()


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
