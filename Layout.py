# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$

from OrderedDictionary import OrderedDictionary
from Renderer import BasicRenderer, HtmlRenderer

class BasicLayout(OrderedDictionary):
    """Defines a document layout

    """

    _renderer = BasicRenderer

    def __init__(self, id, title):
        OrderedDictionary.__init__(self)
        self.id = id
        self.title = title

    def render(self, model, data):
        """Renders the defined layout with data"""
        renderer = self._renderer
        rendering = ""

        for key, widget in self.items():
            field = model[key]
            content = data.data[key]
            error = data.errors[key]
            rendering = rendering + widget.render(renderer, field, content, error)

        return rendering


class HtmlLayout(BasicLayout):
    """A layout for HTML

    TODO: Ponder about how styles gets into this.
    """
    _renderer = HtmlRenderer
