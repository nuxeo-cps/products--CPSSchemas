# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$

from Products.CPSDocument.OrderedDictionary import OrderedDictionary
from Products.CPSDocument.Renderer import BasicRenderer, HtmlRenderer

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

        for fieldid, widget in self.items():

            # TODO:
            # Fields that aren't reqired may have no data in the document, and
            # they will then have no data in the DataStructure.
            # The question is then, what to do with these fields?
            # Currently they are rendered with None, which may not be
            # the correct behaviour. Skip them completely?
            content = data.data.get(fieldid)
            error = data.errors.get(fieldid) # Both '' or None are acceptable as meaning no error
            field = model.getField(fieldid)
            rendering = rendering + widget.render(renderer, field, content, error)

        return rendering


class HtmlLayout(BasicLayout):
    """A layout for HTML

    TODO: Ponder about how styles gets into this.
    """
    _renderer = HtmlRenderer
