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
"""FileUtils

Utilities to deal with files: conversion to HTML, or text.
"""

from zLOG import LOG, DEBUG
from Products.CMFCore.utils import getToolByName


def _convertFileToMimeType(file, mime_type, context=None):
    """Convert a file to a new mime type.

    The file argument may be a Zope File object or None.

    The context argument is used to find placeful tools.

    Returns a string, or None if no conversion is possible.
    """
    if file is None:
        return None
    transformer = getToolByName(context, 'portal_transforms', None)
    if transformer is None:
        LOG('convertFileToText', DEBUG, 'No portal_transforms')
        return None
    raw = str(file)
    if not raw:
        return None
    LOG('convertFileToText', DEBUG, 'File is %s' % repr(file))
    data = transformer.convertTo(mime_type,
                                 raw,
                                 mimetype=file.content_type,
                                 # filename='fooXXX',
                                 # encoding='',
                                 )
    if not data:
        return None
    return data.getData()

def convertFileToText(file, context=None):
    """Convert a file to text.

    Returns a string, or None if no conversion is possible.
    """
    return _convertFileToMimeType(file, 'text/plain', context=context)


def convertFileToHtml(file, context=None):
    """Convert a file to HTML.

    Returns a string, or None if no conversion is possible.
    """
    return _convertFileToMimeType(file, 'text/html', context=context)
