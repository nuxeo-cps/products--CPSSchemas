# Copy/pasted from CPSDocument/skins/cps_document/getDocumentSchemas.py
# copy/pasting is bad, but this is supposed to be a unit test.

metadata_schema = {
    'Title': {'type': 'CPS String Field',
              'data': {'is_searchabletext': 1,}},
    'Description': {'type': 'CPS String Field',
                    'data': {'is_searchabletext': 1}},
    'Subject': {'type': 'CPS String List Field',
                'data': {'is_searchabletext': 1}},
    'Contributors': {'type': 'CPS String List Field',
                     'data': {'is_searchabletext': 1}},
    'CreationDate': {'type': 'CPS DateTime Field',
                     'data': {'write_ignore_storage': 1,}},
    'ModificationDate': {'type': 'CPS DateTime Field',
                         'data': {'write_ignore_storage': 1,}},
    'EffectiveDate': {'type': 'CPS DateTime Field', 'data': {}},
    'ExpirationDate': {'type': 'CPS DateTime Field', 'data': {}},
    'Format': {'type': 'CPS String Field',
               'data': {'write_ignore_storage': 1,}},
    'Language': {'type': 'CPS String Field',
                 'data': {'write_ignore_storage': 1,}},
    'Rights': {'type': 'CPS String Field', 
               'data': {'is_searchabletext': 1}},
    'Creator': {'type': 'CPS String Field',
                'data': {'is_searchabletext': 1, 'write_ignore_storage': 1,}},
    }
