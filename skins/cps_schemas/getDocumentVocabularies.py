##parameters=
#$Id$
"""
Here are defined the vocabularies.
Please, follow the same pattern to add new ones.
"""

vocabularies = {
    'dummy_voc': {
        'data': {
            'dict': {
                'foo': "Foo",
                'bar': "Bar",
                'baz123': "Baz123",
                },
            'list': [
                'foo',
                'bar',
                'baz123',
                ],
            },
        },
    }

cvocabularies = context.getCustomDocumentVocabularies()

vocabularies.update(cvocabularies)

return vocabularies
