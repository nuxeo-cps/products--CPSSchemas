##Script Python "CPSDocumentSchemas"
##parameters=
#$Id$

"""
Return the list of schemas to be registered
"""

schemas = {
        'faq': {
            'title': {
                'type': 'CPS String Field',
                'data': {
                    'default': '',
                    'is_indexed': 1,
                    },
                },
            'description': {
                'type': 'CPS String Field',
                'data': {
                    'default': '',
                    'is_indexed': 1,
                    },
                },
            'question': {
                'type': 'CPS String Field',
                'data': {
                    'default': '',
                    'is_indexed': 0,
                    },
                },
            'answer': {
                'type': 'CPS String Field',
                'data': {
                    'default': '',
                    'is_indexed': 0,
                    },
                },
            },
        'dummy_form': {
            'title': {
                'type': 'CPS String Field',
                'data': {
                    'default': '',
                    'is_indexed': 1,
                    },
                },
            'description': {
                'type': 'CPS String Field',
                'data': {
                    'default': '',
                    'is_indexed': 1,
                    },
                },
            },
        'news': {
            'title': {
                'type': 'CPS String Field',
                'data': {
                    'default': '',
                    'is_indexed': 1,
                    },
                },
            'description': {
                'type': 'CPS String Field',
                'data': {
                    'default': 'resume',
                    'is_indexed': 1,
                    },
                },
            'longTitle': {
                'type': 'CPS String Field',
                'data': {
                    'default': '',
                    'is_indexed': 1,
                    },
                },
            'content': {
                'type': 'CPS String Field',
                'data': {
                    'default': '',
                    'is_indexed': 1,
                    },
                },
            'sticker': {
                'type': 'CPS Image Field',
                'data': {
                    'default': '',
                    'is_indexed': 0,
                    },
                },
            'image': {
                'type': 'CPS Image Field',
                'data': {
                    'default': '',
                    'is_indexed': 0,
                    },
                },
            'newsdate': {
                'type': 'CPS DateTime Field',
                'data': {
                    'default': '',
                    'is_indexed': 0,
                    },
                },
            },
        }
