##Script Python "CPSDocumentLayouts"
##parameters=
#$Id$

"""
List of layouts to be registered
"""

layouts = {
        'faq': {
            'widgets': {
                'title': {
                    'type': 'String Widget',
                    'data': {
                        'fields': ['title'],
                        'title': 'FAQ short question',
                        'title_msgid': 'FAQ short question',
                        'description': 'FAQ short question for section display',
                        'css_class': 'title',
                        'display_width': 20,
                        'display_maxwidth': 0,
                        },
                    },
                'description': {
                    'type': 'TextArea Widget',
                    'data': {
                        'fields': ['description'],
                        'title': 'FAQ answer resume',
                        'title_msgid': 'FAQ answer resume',
                        'description': 'FAQ answer resume for section display',
                        'css_class': 'description',
                        'width': 40,
                        'height': 5,
                        'render_mode': 'stx',
                        },
                    },
                'question': {
                    'type': 'TextArea Widget',
                    'data': {
                        'fields': ['question'],
                        'title': 'FAQ question',
                        'title_msgid': 'FAQ question',
                        'description': 'FAQ full question',
                        'css_class': 'title',
                        'width': 40,
                        'height': 5,
                        'render_mode': 'stx',
                        },
                    },
                'answer': {
                    'type': 'TextArea Widget',
                    'data': {
                        'fields': ['answer'],
                        'title': 'FAQ answer',
                        'title_msgid': 'FAQ answer',
                        'description': 'FAQ full answer',
                        'css_class': 'stx',
                        'width': 40,
                        'height': 5,
                        'render_mode': 'stx',
                        },
                    },
                },
            'layout': {
                'ncols': 1,
                'rows': [
                   [{'ncols': 1, 'widget_id': 'title'},
                    ],
                   [{'ncols': 1, 'widget_id': 'description'},
                    ],
                   [{'ncols': 1, 'widget_id': 'question'},
                    ],
                   [{'ncols': 1, 'widget_id': 'answer'},
                    ],
                   ],
                },
            },
        'dummy_form': {
            'widgets': {
                'title': {
                    'type': 'String Widget',
                    'data': {
                        'fields': ['title'],
                        'title': 'Dummy Form title field',
                        'title_msgid': 'dummy_form_title_field',
                        'description': 'Title for a dummy form',
                        'css_class': 'title',
                        'display_width': 20,
                        'display_maxwidth': 0,
                        },
                    },
                'description': {
                    'type': 'TextArea Widget',
                    'data': {
                        'fields': ['description'],
                        'title': 'Dummy Form Description field',
                        'title_msgid': 'dummy_form_description_field',
                        'description': 'Description field for a dummy form',
                        'css_class': 'description',
                        'width': 40,
                        'height': 5,
                        'render_mode': 'stx',
                        },
                    },
                },
            'layout': {
                'ncols': 1,
                'rows': [
                   [{'ncols': 1, 'widget_id': 'title'},
                    ],
                   [{'ncols': 1, 'widget_id': 'description'},
                    ],
                   ],
                },
            },
        'news': {
            'widgets': {
                'newsdate': {
                    'type': 'Date Widget',
                    'data': {
                        'fields': ['newsdate'],
                        'title': 'News date',
                        'title_msgid': 'News date',
                        'description': 'News date',
                        'css_class': 'title',
                        'allow_none': 1,
                        'view_format': '%d/%m/%Y',
                        'view_format_none': '-',
                        },
                    },
                'title': {
                    'type': 'String Widget',
                    'data': {
                        'fields': ['title'],
                        'title': 'News short title',
                        'title_msgid': 'News short title',
                        'description': 'News short title for section display',
                        'css_class': 'title',
                        'display_width': 20,
                        'display_maxwidth': 0,
                        },
                    },
                'longTitle': {
                    'type': 'String Widget',
                    'data': {
                        'fields': ['longTitle'],
                        'title': 'News title',
                        'title_msgid': 'News title',
                        'description': 'News title',
                        'css_class': 'title',
                        'display_width': 20,
                        'display_maxwidth': 0,
                        },
                    },
                'description': {
                    'type': 'TextArea Widget',
                    'data': {
                        'fields': ['description'],
                        'title': 'News content resume',
                        'title_msgid': 'News content resume',
                        'description': 'News content resume for section display',
                        'css_class': 'description',
                        'width': 40,
                        'height': 5,
                        'render_mode': 'stx',
                        },
                    },
                'content': {
                    'type': 'TextArea Widget',
                    'data': {
                        'fields': ['content'],
                        'title': 'News content',
                        'title_msgid': 'News content',
                        'description': 'News content',
                        'css_class': 'stx',
                        'width': 40,
                        'height': 25,
                        'render_mode': 'stx',
                        },
                    },
                'sticker': {
                    'type': 'Image Widget',
                    'data': {
                        'fields': ['sticker'],
                        'title': 'News sticker',
                        'title_msgid': 'News sticker',
                        'description': 'News sticker for section diplay',
                        'css_class': '',
                        'deletable': 1,
                        },
                    },
                'image': {
                    'type': 'Image Widget',
                    'data': {
                        'fields': ['image'],
                        'title': 'News image',
                        'title_msgid': 'News image',
                        'description': 'News image',
                        'css_class': '',
                        'deletable': 1,
                        },
                    },
                },
            'layout': {
                'ncols': 2,
                'rows': [
                   [{'ncols': 1, 'widget_id': 'newsdate'},
                    ],
                   [{'ncols': 1, 'widget_id': 'title'},
                    {'ncols': 2, 'widget_id': 'longTitle'},
                    ],
                   [{'ncols': 1, 'widget_id': 'description'},
                    ],
                   [{'ncols': 1, 'widget_id': 'content'},
                    ],
                   [{'ncols': 1, 'widget_id': 'sticker'},
                    {'ncols': 2, 'widget_id': 'image'},
                    ],
                   ],
                },
            },
        }
