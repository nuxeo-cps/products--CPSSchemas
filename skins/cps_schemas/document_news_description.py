##parameters=

# this archetype can be split in three files: schema, layout, type
# workflow information have to be set independantly
# News document archetype description

{
  'type_properties': {
    'id': 'News',
    'title': 'portal_type_News_title',
    'description': 'portal_type_News_description',
    'icon': '',
    'initial_view': '',
    'implicity_addable': 1,
    'filter': 1,
    'allowed_content_types': [],
    'discussion': 0,
    'schemas': ['news'],
    'default_layout': 'news',
    'style_layout_prefix': 'layout_news_',
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
    'id': 'news',
    'schema': {
      'title': {
        'type': 'CPS String Field',
        'default': 'News short title',
        'indexed': 1,
        },
      'description': {
        'type': 'CPS String Field',
        'default': 'News resume',
        'indexed': 1,
        },
      'newsdate': {
        'type': 'CPS String Field',
        'default': '01/01/2001',
        'indexed': 1,
        },
      'longTitle': {
        'type': 'CPS String Field',
        'default': 'News title',
        'indexed': 0,
        },
      'content': {
        'type': 'CPS String Field',
        'default': 'News',
        'indexed': 0,
        },
      },
    },
  'layouts': {
    'id': 'news',
    'widgets': {
      'title': {
        'type': 'CPS String Widget',
        'fields': ['title'],
        'title': 'News short title',
        'title_msgid': 'News short title',
        'description': '',
        'css_class': 'title',
        'witdh': '40',
        'max_width': '0',
        },
      'description': {
        'type': 'CPS TextArea Widget',
        'fields': ['description'],
        'title': 'News resume',
        'title_msgid': 'News resume',
        'description': '',
        'css_class': 'description',
        'witdh': '40',
        'heigth': '5',
        'render_mode': 'stx',
        },
      'newsdate': {
        'type': 'CPS Date Widget',
        'fields': ['newsdate'],
        'title': 'News date',
        'title_msgid': 'News date',
        'description': '',
        'css_class': 'title',
        },
      'longTitle': {
        'type': 'CPS String Widget',
        'fields': ['longTitle'],
        'title': 'News title',
        'title_msgid': 'News title',
        'description': '',
        'css_class': 'title',
        'witdh': '40',
        'max_width': '0',
        },
      'content': {
        'type': 'CPS TextArea Widget',
        'fields': ['content'],
        'title': 'News content',
        'title_msgid': 'News content',
        'description': '',
        'css_class': 'stx',
        'witdh': '40',
        'heigth': '25',
        'render_mode': 'stx',
        },
      },
    'layout': {
      'cols': 2,
      'rows': 4,
      'data': ('newsdate',
               ('title','longTitle'),
               'description',
               'content'
               ),
      },
    },
  }
