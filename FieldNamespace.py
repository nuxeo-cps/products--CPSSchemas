# (C) Copyright 2005 Nuxeo SAS <http://nuxeo.com>
# Author: Olivier Grisel <og@nuxeo.com>
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
"""FieldNamespace

Utility to register methods made available in a field's read/write process
expressions namespaces
"""

from AccessControl import ClassSecurityInfo
from Acquisition import Implicit
from Globals import InitializeClass

class FieldStorageNamespace(Implicit):
    """Method registry to be made available in read/write_process_expr
    """
    # the util singleton should be made public to be accessed in TALES
    # expressions
    security = ClassSecurityInfo()
    security.declareObjectPublic()
    security.setDefaultAccess('allow')


    def register(cls, name, method):
        """Add a new method to the registry
        """
        setattr(cls, name, method)

    register = classmethod(register)

InitializeClass(FieldStorageNamespace)

# Singleton object publicly available in fields
fieldStorageNamespace = FieldStorageNamespace()

