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

    def render(self, document):
        """Renders the defined layout with data

        Data should have a subscriptable interface, such as a dictionary"""
        rendering = ""

        for key, widget in self.items():
            rendering = rendering + widget.render(self._renderer, document)

        return rendering


class HtmlLayout(BasicLayout):
    """A layout for HTML

    TODO: Ponder about how styles gets into this.
    """
    _renderer = HtmlRenderer
