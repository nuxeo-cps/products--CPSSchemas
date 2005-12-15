# (C) Copyright 2003-2005 Nuxeo SARL <http://nuxeo.com>
# Authors:
# M.-A. Darche <madarche@nuxeo.com>
# Tarek Ziade <tziade@nuxeo.com>
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
"""Miscellaneous utility functions.
"""

import warnings
from zLOG import LOG, INFO, DEBUG
from cStringIO import StringIO
from OFS.Image import File, Image, cookId
from ZPublisher.HTTPRequest import FileUpload

# BBB goes away in 3.5.0
def copyFile(file_src):
    """Return a copy of a file object."""
    warnings.warn("copyFile is deprecated, use untieFromDatabase",
                  DeprecationWarning, 2)
    if not isinstance(file_src, File):
        LOG('CPSSchemas.utils:copyFile', DEBUG,
            'file_src %s is not a File object' % str(file_src))
        return
    # we use a StringIO for performance
    data = StringIO(str(file_src.data))
    file_dest = File(file_src.id(), file_src.title, data)
    file_dest.manage_changeProperties(content_type=file_src.content_type)
    return file_dest

# BBB goes away in 3.5.0
def copyImage(file_src):
    """Return a copy of an image object."""
    warnings.warn("copyImage is deprecated, use untieFromDatabase",
                  DeprecationWarning, 2)
    if not isinstance(file_src, Image):
        LOG('CPSSchemas.utils:copyImage', DEBUG,
            'file_src %s is not an Image object' % str(file_src))
        return
    # we use a StringIO for performance
    data = StringIO(str(file_src.data))
    file_dest = Image(file_src.id(), file_src.title, data)
    file_dest.manage_changeProperties(content_type=file_src.content_type)
    return file_dest

def untieFromDatabase(ob):
    """Untie an object from the database.

    Used to copy objects from/to a session.

    A FileUpload objects is turned into a File (or None).
    """
    if isinstance(ob, FileUpload):
        # A FileUpload is a braindead object holding references
        # to bound functions and thus not picklable... <sigh>
        # We'll replace it with a File, or None if it's empty.
        if not ob:
            return None
        id, title = cookId('', '', ob)
        id = id or 'file' # Don't keep an empty id
        f = File(id, title, ob)
        return f
    if getattr(ob, '_p_jar', None) is None:
        return ob
    if isinstance(ob, File): # including Image
        klass = ob.__class__
        f = klass(ob.id(), ob.title, str(ob.data),
                  content_type=ob.content_type,
                  precondition=ob.precondition)
        return f
    raise ValueError("untieFromDatabase can't untie %r" % (ob,))

def getHumanReadableSize(octet_size):
    """ returns a human readable file size
    """
    mega = 1024*1024
    kilo = 1024

    if octet_size is None or octet_size <= 0:
        return (0, 'cpsschemas_unit_mega_bytes')
    elif octet_size >= mega:
        if octet_size == mega:
            return (1, 'cpsschemas_unit_mega_bytes')
        else:
            msize = float(octet_size/float(mega))
            msize = float('%.02f' % msize)
            return (msize, 'cpsschemas_unit_mega_bytes')
    elif octet_size >= kilo:

        if octet_size == kilo:
            return (1, 'cpsschemas_unit_kilo_bytes')
        else:
            msize = float(octet_size/float(kilo))
            msize = float('%.02f' % msize)
            return (msize, 'cpsschemas_unit_kilo_bytes')
    else:
        if octet_size == 1:
            return (1, 'cpsschemas_unit_bytes')
        else:
            return (octet_size ,'cpsschemas_unit_bytes')
