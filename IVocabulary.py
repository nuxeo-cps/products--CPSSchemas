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
"""IVocabulary

Vocabulary interfaces.
"""

from Interface import Interface

class IVocabulary(Interface):
    """Interface for a basic Vocabulary."""

    def __delitem__(key):
        """Delete an item from the vocabulary."""

    def set(key, label, msgid=None):
        """Set a label for a key."""

    def __getitem__(key):
        """Get a label for a key."""

    def get(key, default=None):
        """Get a label for a key, default to None."""

    def getMsgid(key, default=None):
        """Get a msgid for a key, default to None."""

    def has_key(key):
        """Test if a key is present."""

    def keys():
        """Get the ordered list of keys."""

    def items():
        """Get the ordered list of (key, value)."""

    def values():
        """Get the ordered list of values."""

