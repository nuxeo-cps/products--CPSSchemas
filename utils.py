# (C) Copyright 2003-2007 Nuxeo SAS <http://nuxeo.com>
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
from zLOG import LOG, DEBUG
from cStringIO import StringIO
from OFS.Image import File, Image

# BBB goes away in 3.5.0
def copyFile(file_src):
    """Return a copy of a file object."""
    warnings.warn("copyFile is deprecated", DeprecationWarning, 2)
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
    warnings.warn("copyImage is deprecated", DeprecationWarning, 2)
    if not isinstance(file_src, Image):
        LOG('CPSSchemas.utils:copyImage', DEBUG,
            'file_src %s is not an Image object' % str(file_src))
        return
    # we use a StringIO for performance
    data = StringIO(str(file_src.data))
    file_dest = Image(file_src.id(), file_src.title, data)
    file_dest.manage_changeProperties(content_type=file_src.content_type)
    return file_dest

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
            ksize = float(octet_size/float(kilo))
            ksize = float('%.02f' % ksize)
            return (ksize, 'cpsschemas_unit_kilo_bytes')
    else:
        if octet_size == 1:
            return (1, 'cpsschemas_unit_bytes')
        else:
            return (octet_size ,'cpsschemas_unit_bytes')
