# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$
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

"""
A Renderer defines the basic widgets used when rendering. A widget is the
smallest graphical element like text, editboxes and so on. This is all
highly experimental, and will be adapted for HTML for now. If it proves
useful other renderers will be created and this interface will most likely
change accordingly.

Since a renderer (at least so far) has no instance data, only one instance
of each renderer is needed. Therefore each class will be named XxxRendererClass
and each instance will be called XxxRenderer. It will then be used from the
Layouts by importing XxxRenderer
"""

class BasicRendererClass:
    """Renders documents to plain text

    Primarily done for testing rendering.
    """

    def text(self, content):
        return str(content) + '\n'

    def editBox(self, name, content, height, width):
        return '[%s]\n' % str(content)

    def radioButton(self, name, label, value, selected):
        if selected:
            string = '(*) '
        else:
            string = '( ) '
        return string + content + '\n'

    def checkBox(self, name, label, value, selected):
        if selected:
            string = '[x] '
        else:
            string = '[ ] '
        return string + content + '\n'

    def selectionList(self, name, label, values, value_list):
        string = ''
        for each in value_list:
            if each in values:
                string = string + '|#'
            else:
                string = string + '| '
            string = string + each + '\n'

        return string

    def dropDownList(self, name, label, value, value_list):
        return value + '[V]\n'

BasicRenderer = BasicRendererClass()


class HtmlRendererClass:
    """The renderer for HTML

    TODO: Ponder about how styles gets into this.
    """

    def text(self, content):
        return content #TODO: Should this maybe return a whole paragraph?

    def editBox(self, name, content, height, width):
        if height > 1: # Render as a text area
            return '<textarea name="%s" height=%s width=%s>%s</textarea>' % \
                   (name, str(height), str(width), content)
        else: #Render as an input
            return '<input type=text name="%s" width=%s value="%s>' % \
                   (name, str(width), content)

    def radioButton(self, name, label, value, selected):
        return ""

    def checkBox(self, name, label, value, selected):
        return ""

    def selectionList(self, name, label, value, value_list):
        return ""

    def dropDownList(self, name, label, value, value_list):
        return ""

HtmlRenderer = HtmlRendererClass()
