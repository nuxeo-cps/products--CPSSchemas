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


def convertFileToText(file):
    """Convert a file to text.

    Returns a string, or None if no conversion is possible.
    """
    if file is None:
        return None
    return 'Some text here...'


def convertFileToHtml(file):
    """Convert a file to HTML.

    Returns a string, or None if no conversion is possible.
    """
    if file is None:
        return None
    return '<b>Some html here...</b>'
