# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$

#from HTMLRenderer import HTMLRenderer

class BasicFieldWidget:
    """The base class for all FieldWidgets

    A FieldWidget is the class that knows how to render a field.
    Each Field class must have a corresponding FieldWidget.
    The FieldWidget
    """

    _render_mode = 'view'

    def __init__(self, field):
        self.id = field.id
        self.title = field.title
        self._field = field

    def render(self, renderer, field, content, error):
        if callable(self._render_mode):
            return self._render_mode(field, content, error)
        elif self._render_mode == 'edit':
            return self.renderEdit(renderer, field, content, error)
        return self.renderView(renderer, field, content, error)

    def renderEdit(self, renderer, field, content, error):
        """Rendering method

        This method must be overridden in all sub classes.
        """
        return '[%s] %s' % (content, str(error))

    def renderView(self, renderer, field, content, error):
        """Rendering method

        This method must be overridden in all sub classes.
        """
        return '%s %s' % (content, str(error))

    def setRenderMode(self, render_mode):
        self._render_mode = render_mode


class BasicField:
    """The base class for all data structure field definitions

    Each Field definition has a corresponding FieldWidget definition.
    """

    _field_widget = BasicFieldWidget # The corresponding FieldWidget class
    _default = None
    _required = 1
    _allow_none = 1
    requiredmessage = 'This field is required'

    def __init__(self, id, title):
        self.id = id
        self.title = title
        self.setStorageId(id)

    def validate(self, data):
        """Convert and validate data"""
        if data is None and self._required:
            if self._default == None:
                raise ValueError('This field is required')
            # Use the default. Instead of just returning it, validate it.
            # The requirements may have changed since the default was set.
            data = self._default
        return self._validate(data)

    def _validate(self, data):
        """This does the type-specific validation

        It should be overridden in subclasses"""
        return data # No validation

    def setValidationMethod(self, method):
        raise NotImplementedError

    def getValidationMethod(self):
        raise NotImplementedError

    def getFieldWidget(self):
        return self._field_widget(self)

    def getDefaultValue(self):
        return self._default

    def setDefaultValue(self, default):
        self._default = self._validate(default) # Make sure the default is an acceptable value.

    def getStorageId(self):
        """Gets the id used for storing data

        This is the attribute name or SQL record name, and such"""
        return self._storage_id

    def setStorageId(self, id):
        self._storage_id = id