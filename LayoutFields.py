from FlexibleLayout import FlexibleLayout

class LayoutField:
    """A layout unit

    The smallest part of a Layout. Can be things as a string, a rich text field,
    a date or an image. They can have numerous settings, both to decide details
    about presentation, as well as details about validation. There will be
    several classes subclassing the basic/abstract LayoutField class for
    different types of data, such as TextLayoutField, DateLayoutField, ...
    """

    title = ""

    def __init__(self, id):
        self._id = id

    def id(self):
        return self._id

    def render(self, data, edit=0):
        """Renders the field as HTML

        Uses skins in one way or another. Setting edit to 1 renders the
        field to accept data input.
        """
        return None

    def validate(self, data):
        """Makes sure the data to be set is acceptable for the field

        Data is a dictionary of all the data for the document, so that
        validation can take place over multiple fields.
        """
        return None

    def setValidationMethod(self, method):
        return None

    def getValidationMethod(self):
        return None


class TextLayoutField(LayoutField):
    """A field for single or multiple lines of text"""

    _lines = 1 # In edit mode, 1 makes it display a <input> widget, everything
               # over 1 makes it display a <textarea> widget.



class SelectionLayoutField(LayoutField):
    """For selections from lists."""

    _selector_type = 'listbox' #one of 'radiobutton', 'checkbox', 'multiplecheckboxes', 'dropdown', 'listbox', 'multiplelistbox', ...

    _options = [] #The different options.

    _rendering_type = 'bullet_list' # or numbered_list, comma_separated, ...




class MultipleLayoutField(LayoutField, FlexibleLayout):
    """A layoutfield that is made up of other layoutfields"""

    _rendering_type = 'vertical' # or horizontal
