##parameters=

# this archetype can be split in three files: schema, layout, type
# workflow information have to be set independantly
# FAQ document archetype description

{
  'type_properties': {
    'id': 'FAQ',
    'title': 'portal type Faq title',
    'description': 'portal type Faq description',
    'icon': '',
    'initial_view': '',
    'implicity_addable': 1,
    'filter': 1,
    'allowed_content_types': [],
    'discussion': 0,
    'schemas': ['faq'],
    'default_layout': 'faq',
    'style_layout_prefix': 'layout_faq_',
    'actions': {
      'replace_actions': 0,
      'isproxytype': {
        'name': 'isproxytype',
        'id': 'isproxytype',
        'action': 'document',
        'permission': None,
        'category': 'object',
        'visible': 0,
        },
      'issearchabledocument': {
        'name': 'issearchabledocument',
        'id': 'issearchabledocument',
        'action': 'document',
        'permission': None,
        'category': 'object',
        'visible': 0,
        },
      },
    },
  'schemas': {
    'id': 'faq',
    'schema': {
      'title': {
        'type': 'CPS String Field',
        'default': 'Faq short title',
        'indexed': 1,
        },
      'description': {
        'type': 'CPS String Field',
        'default': 'Faq short answer',
        'indexed': 1,
        },
      'question': {
        'type': 'CPS String Field',
        'default': 'Faq question',
        'indexed': 0,
        },
      'content': {
        'type': 'CPS String Field',
        'default': 'Faq answer',
        'indexed': 0,
        },
      'rating': {
        'type': 'CPS Int Field',
        'default': '0',
        'indexed': 1,
        },
      },
    },
  'layouts': {
    'id': 'faq',
    'widgets': {
      'title': {
        'type': 'CPS String Widget',
        'fields': ['title'],
        'title': 'FAQ short question',
        'title_msgid': 'FAQ short question',
        'description': '',
        'css_class': 'title',
        'witdh': '40',
        'max_width': '0',
        },
      'description': {
        'type': 'CPS TextArea Widget',
        'fields': ['description'],
        'title': 'FAQ short answer',
        'title_msgid': 'FAQ short answer',
        'description': '',
        'css_class': 'description',
        'witdh': '40',
        'heigth': '5',
        'render_mode': 'stx',
        },
      'question': {
        'type': 'CPS TextArea Widget',
        'fields': ['question'],
        'title': 'FAQ question',
        'title_msgid': 'FAQ question',
        'description': '',
        'css_class': 'stx',
        'witdh': '40',
        'heigth': '5',
        'render_mode': 'stx',
        },
      'content': {
        'type': 'CPS TextArea Widget',
        'fields': ['content'],
        'title': 'FAQ answer',
        'title_msgid': 'FAQ answer',
        'description': '',
        'css_class': 'stx',
        'witdh': '40',
        'heigth': '25',
        'render_mode': 'stx',
        },
      'rating': {
        'type': 'CPS Int Widget',
        'fields': ['rating'],
        'title': 'FAQ rating',
        'title_msgid': 'FAQ rating',
        'description': '',
        'css_class': 'description',
        },
      },
    'layout': {
      'cols': 1,
      'rows': 5,
      'data': ('title',
               'question',
               'description',
               'content',
               'rating',
               ),
      },
    },
  }
