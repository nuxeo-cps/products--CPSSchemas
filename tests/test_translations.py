# (C) Copyright 2005 Nuxeo SARL <http://nuxeo.com>
# Authors:
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
"""Unit tests on the well-formedness and quality of .pot and .po files.
"""
from Products.CPSI18n.tests.translations import TranslationsTestCase
from Testing import ZopeTestCase
import unittest


class Test(TranslationsTestCase):

    def setUp(self):
        self.product_name = 'CPSSchemas'

def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
