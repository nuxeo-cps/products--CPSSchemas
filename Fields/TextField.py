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

from BasicField import BasicField, BasicFieldWidget

class TextFieldWidget(BasicFieldWidget):
    """A field for single or multiple lines of text"""

    _lines = 1 # In edit mode, 1 makes it display a <input> widget, everything
               # over 1 makes it display a <textarea> widget.

    def renderEdit(self, renderer, field, content, error):
        """Renders the content with the renderer"""
        return renderer.editBox(self.id, content, height=1, width=20)

    def renderView(self, renderer, field, content, error):
        """Renders the content with the renderer"""
        return renderer.text(content)


class TextField(BasicField):
    _field_widget = TextFieldWidget

    def _validate(self, data):
        return str(data)

