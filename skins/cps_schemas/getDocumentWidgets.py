## Script (Python) "getDocumentWidgets"
##parameters=
#$Id$

"""
Here are defined the list of widgets to be registred
Please, follow the same pattern to add new ones
"""

widgets = {
        'Int Widget': {
            'type': 'CPS Int Widget Type',
            'data': {},
            },
        'String Widget': {
            'type': 'CPS String Widget Type',
            'data': {},
            },
        'Password Widget': {
            'type': 'CPS Password Widget Type',
            'data': {},
            },
        'TextArea Widget': {
            'type': 'CPS TextArea Widget Type',
            'data': {},
            },
        'Date Widget': {
            'type': 'CPS Date Widget Type',
            'data': {},
            },
        'File Widget': {
            'type': 'CPS File Widget Type',
            'data': {},
            },
        'Image Widget': {
            'type': 'CPS Image Widget Type',
            'data': {},
            },
        'Html Widget': {
            'type': 'CPS Html Widget Type',
            'data': {},
            },
        'Dummy Widget': {
            'type': 'CPS Customizable Widget Type',
            'data': {
                'field_types': ['CPS String Field'],
                'prepare_validate_method': 'widget_dummy_prepare_validate',
                'render_method': 'widget_dummy_render',
                },
            },
        }

cwidgets = context.getCustomDocumentWidgets()

widgets.update(cwidgets)

return widgets
