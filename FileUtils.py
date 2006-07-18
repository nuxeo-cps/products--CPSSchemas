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

from Products.CMFCore.utils import getToolByName
from logging import getLogger

logger = getLogger('CPSSchemas.FileUtils._convertFileToMimeType')

def _convertFileToMimeType(file, mime_type, context=None, **kwargs):
    """Convert a file to a new mime type.

    The file argument may be a Zope File object or None.

    The context argument is used to find placeful tools.

    Returns a string, or None if no conversion is possible.
    """
    if file is None:
        return None
    transformer = getToolByName(context, 'portal_transforms', None)
    if transformer is None:
        logger.debug('No portal_transforms')
        return None
    raw = str(file)
    if not raw:
        return None
    logger.debug('to %s for file %s', mime_type, repr(file))
    current_mime_type = getattr(file, 'content_type',
                                'application/octet-stream')
    if context is not None:
        default_encoding = context.default_charset
    else:
        default_encoding = 'latin9'

    data = transformer.convertTo(mime_type, raw, mimetype=current_mime_type,
                                 # filename='fooXXX', encoding='',
                                 encoding = default_encoding,
                                 **kwargs
                                 )
    if not data:
        return None
    return data


def convertFileToText(file, context=None, **kwargs):
    """Convert a file to text.

    Returns a string, or None if no conversion is possible.
    """
    result = _convertFileToMimeType(file, 'text/plain',
                                    context=context, **kwargs)
    if result is not None:
        result = result.getData()
    return result


def convertFileToHtml(file, context=None, **kwargs):
    """Convert a file to HTML.

    Returns a data object (string and subobjects),
    or None if no conversion is possible.
    """
    return _convertFileToMimeType(file, 'text/html',
                                  context=context, **kwargs)


def convertFileToDocbook(file, context=None, **kwargs):
    """Convert a file to Docbook XML.

    Returns a data object (string and subobjects),
    or None if no conversion is possible.
    """
    return _convertFileToMimeType(file, 'application/docbook+xml',
                                  context=context, **kwargs)
