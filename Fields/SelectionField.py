# (C) Copyright 2003 Nuxeo SARL <http://nuxeo.com>
# Author: Lennart Regebro <fg@nuxeo.com>
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

from types import TupleType, ListType

from BasicField import BasicField, BasicFieldWidget

class SelectionFieldWidget(BasicFieldWidget):
    """For selections from lists."""

    _selector_type = 'listbox' # one of 'radiobutton', 'checkbox', 
                               # 'multiplecheckboxes', 'dropdown', 'listbox', 
                               # 'multiplelistbox', ...
    _rendering_type = 'bullet_list' # or numbered_list, comma_separated, ...

    def renderView(self, renderer, field, content, error):
        """Rendering method"""
        result = ''
        if not (isinstance(content, TupleType) \
                or isinstance(content, ListType)):
            content = [content]
        for each in content:
            result += str(each) + ', '
        result = result[:-2] + '\n'

        return result

    def renderEdit(self, renderer, field, content, error):
        """Rendering method"""
        result = ''
        if not (isinstance(content, TupleType) \
                or isinstance(content, ListType)):
            content = [content]
        for each in field.getOptions():
            if each in content:
                result += '*'
            else:
                result += ' '
            result += str(each) + '\n'

        return result


class SelectionField(BasicField):
    """For selections from lists."""

    _field_widget = SelectionFieldWidget
    _multiple_selection = 1

    _options = [] #The different options.

    def setOptions(self, options):
        self._options = options

    def getOptions(self):
        return self._options

    def _validate(self, data):
        if not data in self._options:
            raise ValueError('Invalid Option')
        return data

