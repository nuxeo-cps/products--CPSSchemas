# (C) Copyright 2003 Nuxeo SARL <http://nuxeo.com>
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

from AccessControl import allow_type, allow_class
from AccessControl import ModuleSecurityInfo
from zLOG import LOG, INFO, DEBUG


# Allowing the methods of this file to be imported in restricted code
ModuleSecurityInfo('Products.CPSSchemas.utils').declarePublic('isProductPresent')


def isProductPresent(product_name):
    """Return whether the product corresponding to the given product name is
    present and ready (not broken) in the current Zope instance.

    Examples:
      * in Python code utils.isProductPresent('Products.ExternalEditor')
      * in ZEXPR modules["Products.CPSSchemas.utils"].isProductPresent("Products.ExternalEditor")

    """
    log_key = 'isProductPresent'
    LOG(log_key, DEBUG, "...")
    try:
        __import__(product_name)
        present = 1
    except ImportError:
        present = 0
    LOG(log_key, DEBUG, "present = %s" % present)
    return present
