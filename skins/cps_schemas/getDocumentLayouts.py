## Script (Python) "getDocumentLayouts"
##parameters=
# $Id$
"""
Here are defined the list of layouts to be registred
Please, follow the same pattern to add new layouts
"""

#########################################################
# FAQ LAYOUT
#########################################################

faq_layout = {
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
               }
#########################################################
# DUMMY FORM LAYOUT
#########################################################

dummy_form_layout = {
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
            }

#########################################################
# NEWS LAYOUT
#########################################################

news_layout = {
            'widgets': {
                'title': {
                    'type': 'String Widget',
                    'data': {
                        'fields': ['title'],
                        'is_i18n': 1,
                        'title': 'cpsdoc_News_title_title',
                        'description': 'cpsdoc_News_title_description',
                        'css_class': 'dtitle',
                        'display_width': 20,
                        'display_maxwidth': 0,
                        },
                    },
                'longTitle': {
                    'type': 'String Widget',
                    'data': {
                        'fields': ['longTitle'],
                        'is_i18n': 1,
                        'title': 'cpsdoc_News_longTitle_title',
                        'description': 'cpsdoc_News_longTitle_description',
                        'css_class': 'dtitle2',
                        'display_width': 50,
                        'display_maxwidth': 0,
                        'allow_empty': 0,
                        },
                    },
                'description': {
                    'type': 'TextArea Widget',
                    'data': {
                        'fields': ['description'],
                        'is_i18n': 1,
                        'title': 'cpsdoc_News_description_title',
                        'description': 'cpsdoc_News_description_description',
                        'css_class': 'ddescription',
                        'width': 40,
                        'height': 5,
                        'render_mode': 'stx',
                        },
                    },
                'newsdate': {
                    'type': 'Date Widget',
                    'data': {
                        'fields': ['newsdate'],
                        'is_i18n': 1,
                        'title': 'cpsdoc_News_newsdate_title',
                        'title_view': 'cpsdoc_News_newsdate_title_view',
                        'description': 'cpsdoc_News_newsdate_description',
                        'css_class': 'dtitle5 dright',
                        'allow_none': 1,
                        'view_format': '%d/%m/%Y',
                        'view_format_none': '-',

                        },
                    },
                'content': {
                    'type': 'TextArea Widget',
                    'data': {
                        'fields': ['content'],
                        'is_i18n': 1,
                        'title': 'cpsdoc_News_content_title',
                        'description': 'cpsdoc_News_content_description',
                        'css_class': 'dcontent',
                        'width': 40,
                        'height': 25,
                        'render_mode': 'stx',
                        },
                    },
                'photo': {
                    'type': 'Image Widget',
                    'data': {
                        'fields': ['photo'],
                        'is_i18n': 1,
                        'title': 'cpsdoc_News_photo_title',
                        'description': 'cpsdoc_News_photo_description',
                        'css_class': 'dleft',
                        'deletable': 1,
                        'display_width': 250,
                        'display_height': 150,
                        'maxsize': 1024*1024,
                        },
                    },
                'preview': {
                    'type': 'Image Widget',
                    'data': {
                        'fields': ['preview'],
                        'is_i18n': 1,
                        'title': 'cpsdoc_News_preview_title',
                        'description': 'cpsdoc_News_preview_description',
                        'css_class': '',
                        'deletable': 1,
                        'display_width': 200,
                        'display_height': 150,
                        'maxsize': 1024*1024,
                        'hidden_view': 1,
                        },
                    },
                'attachedFile': {
                    'type': 'File Widget',
                    'data': {
                        'fields': ['attachedFile'],
                        'is_i18n': 1,
                        'title': 'cpsdoc_News_attachedFile_title',
                        'title_view': 'cpsdoc_News_attachedFile_title_view',
                        'description': 'cpsdoc_News_attachedFile_description',
                        'css_class': '',
                        'deletable': 1,
                        'display_width': 200,
                        'display_height': 150,
                        'maxsize': 1024*1024,
                        },
                    },
                },
            'layout': {
                'ncols': 2,
                'rows': [[{'ncols': 1, 'widget_id': 'title'},
                          {'ncols': 1, 'widget_id': 'newsdate'},],
                         [{'ncols': 1, 'widget_id': 'longTitle'},],
                         [{'ncols': 1, 'widget_id': 'description'},],
                         [{'ncols': 1, 'widget_id': 'photo'},
                          {'ncols': 1, 'widget_id': 'preview'},],
                         [{'ncols': 1, 'widget_id': 'content'},],
                         [{'ncols': 1, 'widget_id': 'attachedFile'},],
                         ]
                },
            }

###########################################################
# END OF LAYOUTS DEFINITIONS
###########################################################

layouts = {}

#
# Building the dictionnary of layouts for the installer
#

layouts['faq'] = faq_layout
layouts['dummy_form'] = dummy_form_layout
layouts['news'] = news_layout

clayouts = context.getCustomDocumentLayouts()

layouts.update(clayouts)

return layouts
