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
            field = model.get(key)
            if field is None:
                continue # This field has been removed from the datamodel, skip rendering.
            # TODO:
            # Fields that aren't reqired may have no data in the document, and
            # they will then have no data in the DataStructure.
            # The question is then, what to do with these fields?
            # Currently they are rendered with None, which may not be
            # the correct behaviour. Skip them completely?
            content = data.data.get(key)
            error = data.errors.get(key) # Both '' or None are acceptable as meaning no error
            rendering = rendering + widget.render(renderer, field, content, error)

        return rendering


class HtmlLayout(BasicLayout):
    """A layout for HTML

    TODO: Ponder about how styles gets into this.
    """
    _renderer = HtmlRenderer
