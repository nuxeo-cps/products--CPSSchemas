# (c) 2003 Nuxeo SARL <http://nuxeo.com>
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



