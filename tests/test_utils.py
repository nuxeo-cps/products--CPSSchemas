#!/usr/bin/python
# -*- encoding: iso-8859-15 -*-
# Copyright (C) 2004 Nuxeo SARL <http://nuxeo.com>
# Author: Tarek Ziadé <tz@nuxeo.com>
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

import unittest
from Testing.ZopeTestCase import ZopeTestCase
from Products.CPSSchemas.utils import getHumanReadableSize

class UtilsTestCase(ZopeTestCase):

    def test_getHumanReadableSize(self):
        """ testing human readable size getter
        """
        str_size = getHumanReadableSize(-1)
        self.assertEquals(str_size, (0, 'cpsschemas_unit_mega_bytes'))

        str_size = getHumanReadableSize(0)
        self.assertEquals(str_size, (0, 'cpsschemas_unit_mega_bytes'))

        str_size = getHumanReadableSize(156)
        self.assertEquals(str_size, (156, 'cpsschemas_unit_bytes'))

        str_size = getHumanReadableSize(1526)
        self.assertEquals(str_size, (1.49, 'cpsschemas_unit_kilo_bytes'))

        str_size = getHumanReadableSize(1024)
        self.assertEquals(str_size, (1, 'cpsschemas_unit_kilo_bytes'))

        str_size = getHumanReadableSize(1048576)
        self.assertEquals(str_size, (1, 'cpsschemas_unit_mega_bytes'))

        str_size = getHumanReadableSize(1098776)
        self.assertEquals(str_size, (1.05, 'cpsschemas_unit_mega_bytes'))

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(UtilsTestCase),
        ))
