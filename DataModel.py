# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$

from OrderedDictionary import OrderedDictionary

class DataModel(OrderedDictionary):
    """Defines fields used in a document"""

    # It doesn't really have to be ordered, I think a pure
    # PersistentMapping would work. But then again, it can't hurt...
    pass



