
import os
from App.Extensions import getPath
from re import match
from zLOG import LOG, INFO, DEBUG
from Products.CMFCore.CMFCorePermissions import View, ModifyPortalContent
from Products.ExternalMethod.ExternalMethod import ExternalMethod



def install(self):

    _log = []
    def pr(bla, zlog=1, _log=_log):
        if bla == 'flush':
            return '<html><head><title>SIT UPDATE</title></head><body><pre>'+ \
                   '\n'.join(_log) + \
                   '</pre></body></html>'

        _log.append(bla)
        if (bla and zlog):
            LOG('CPSDocument install:', INFO, bla)

    def prok(pr=pr):
        pr(" Already correctly installed")

    pr("Starting CPSDocument install")

    portal = self.portal_url.getPortalObject()

    def portalhas(id, portal=portal):
        return id in portal.objectIds()

# widgets
    pr("Verifiying widgets")
    widgets = {
        'Int Widget': {
            'type': 'CPS Int Widget Type',
            'data': {},
            },
        'String Widget': {
            'type': 'CPS String Widget Type',
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
        'Dummy Widget': {
            'type': 'CPS Customizable Widget Type',
            'data': {
                'prepare_validate_method': 'widget_dummy_prepare_validate',
                'render_method': 'widget_dummy_render',
                },
            },
        }
    wtool = portal.portal_widgets
    for id, info in widgets.items():
        pr(" Widget %s" % id)
        if id in wtool.objectIds():
            pr("  Deleting.")
            wtool.manage_delObjects([id])
        pr("  Installing.")
        widget = wtool.manage_addCPSWidgetType(id, info['type'])
        widget.manage_changeProperties(**info['data'])


    # setup portal_type: CPS Proxy Document, CPS Proxy Folder
    # CPS Folder
    pr("Verifying portal types")
    newptypes = ('FAQ', 'News')
    ttool = portal.portal_types
    if 'Workspace' in ttool.objectIds():
        workspaceACT = list(ttool['Workspace'].allowed_content_types)
    else:
        raise DependanceError, 'Workspace'
    for ptype in newptypes:
        if ptype not in  workspaceACT:
            workspaceACT.append(ptype)
    
    ptypes = {
        }
    flextypes = {
        'FAQ': {
            'title': 'portal_type_FAQ_title',
            'description': 'portal_type_FAQ_description',
            'icon': 'faq_icon.gif',
            'immediate_view': 'cpsdocument_edit_form',
            'schemas': ['faq'],
            'default_layout': 'faq',
            'layout_style_prefix': 'layout_faq_',
            },
        'News': {
            'title': 'portal_type_News_title',
            'description': 'portal_type_News_description',
            'icon': 'news_icon.gif',
            'immediate_view': 'cpsdocument_edit_form',
            'schemas': ['news'],
            'default_layout': 'news',
            'layout_style_prefix': 'layout_news_',
            }
        }
    allowed_content_type = {
                            'Workspace' : workspaceACT,
                            }
    
    ptypes_installed = ttool.objectIds()
    
    for prod in ptypes.keys():
        for ptype in ptypes[prod]:
            pr("  Type '%s'" % ptype)
            if ptype in ptypes_installed:
                ttool.manage_delObjects([ptype])
                pr("   Deleted")

            ttool.manage_addTypeInformation(
                id=ptype,
                add_meta_type='Factory-based Type Information',
                typeinfo_name=prod+': '+ptype,
                )
            pr("   Installation")

    for ptype, data in flextypes.items():
        pr("  Type '%s'" % ptype)
        if ptype in ptypes_installed:
            ttool.manage_delObjects([ptype])
            pr("   Deleted")
        ti = ttool.addFlexibleTypeInformation(id=ptype)
        ti.manage_changeProperties(**data)
        pr("   Installation")
    

    # check site and workspaces proxies
    sections_id = 'sections'
    workspaces_id = 'workspaces'
    
    # check workflow association
    pr("Verifying local workflow association")
    if not '.cps_workflow_configuration' in portal[workspaces_id].objectIds():
        raise DependanceError, 'no .cps_workflow_configuration in Workspace'
    else:
        wfc = getattr(portal[workspaces_id], '.cps_workflow_configuration')
    
    for ptype in newptypes:
        pr("  Add %s chain to portal type %s in %s of %s" %('workspace_content_wf',
             ptype, '.cps_workflow_configuration', workspaces_id)) 
        wfc.manage_addChain(portal_type=ptype,
                            chain='workspace_content_wf')
    
    if not '.cps_workflow_configuration' in portal[sections_id].objectIds():
        raise DependanceError, 'no .cps_workflow_configuration in Section'
    else:
        wfc = getattr(portal[sections_id], '.cps_workflow_configuration')
    
    for ptype in newptypes:    
        pr("  Add %s chain to portal type %s in %s of %s" %('section_content_wf',
             ptype, '.cps_workflow_configuration', sections_id))
        wfc.manage_addChain(portal_type=ptype,
                            chain='section_content_wf')
        
    # skins
    skins = ('cps_document',)
    paths = {
        'cps_document': 'Products/CPSDocument/skins/cps_document',
    }

    for skin in skins:
        path = paths[skin]
        path = path.replace('/', os.sep)
        pr(" FS Directory View '%s'" % skin)
        if skin in portal.portal_skins.objectIds():
            dv = portal.portal_skins[skin]
            oldpath = dv.getDirPath()
            if oldpath == path:
                prok()
            else:
                pr("  Correctly installed, correcting path")
                dv.manage_properties(dirpath=path)
        else:
            portal.portal_skins.manage_addProduct['CMFCore'].manage_addDirectoryView(filepath=path, id=skin)
            pr("  Creating skin")
    allskins = portal.portal_skins.getSkinPaths()
    for skin_name, skin_path in allskins:
        if skin_name != 'Basic':
            continue
        path = [x.strip() for x in skin_path.split(',')]
        path = [x for x in path if x not in skins] # strip all
        if path and path[0] == 'custom':
            path = path[:1] + list(skins) + path[1:]
        else:
            path = list(skins) + path
        npath = ', '.join(path)
        portal.portal_skins.addSkinSelection(skin_name, npath)
        pr(" Fixup of skin %s" % skin_name)

    # schemas
    pr("Verifiying schemas")
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
            },
        }
    stool = portal.portal_schemas
    for id, info in schemas.items():
        pr(" Schema %s" % id)
        if id in stool.objectIds():
            pr("  Deleting.")
            stool.manage_delObjects([id])
        pr("  Installing.")
        schema = stool.manage_addCPSSchema(id)
        for field_id, fieldinfo in info.items():
            pr("   Field %s." % field_id)
            schema.manage_addField(field_id, fieldinfo['type'])
            # TODO for fieldinfo['data']
            #schema[field_id].manage_editProperties()

    # layouts
    pr("Verifiying layouts")
    layouts = {
        'faq': {
            'widgets': {
                'title': {
                    'type': 'String Widget',
                    'data': {
                        'fields': ['title'],
                        'title': 'FAQ short question',
                        'title_msgid': 'FAQ short question',
                        'descrition': 'FAQ short question for section display',
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
                        'descrition': 'FAQ answer resume for section display',
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
                        'descrition': 'FAQ full question',
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
                        'descrition': 'FAQ full answer',
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
        'news': {
            'widgets': {
                'newsdate': {
                    'type': 'Date Widget',
                    'data': {
                        'fields': ['newsdate'],
                        'title': 'News date',
                        'title_msgid': 'News date',
                        'descrition': 'News date',
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
                        'descrition': 'News short title for section display',
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
                        'descrition': 'News title',
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
                        'descrition': 'News content resume for section display',
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
                        'descrition': 'News content',
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
                        'descrition': 'News sticker for section diplay',
                        'css_class': '',
                        'deletable': 1,
                        },
                    },
                'image': {
                    'type': 'Image Widget',
                    'data': {
                        'fields': ['sticker'],
                        'title': 'News image',
                        'title_msgid': 'News image',
                        'descrition': 'News image',
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
    
    ltool = portal.portal_layouts
    for id, info in layouts.items():
        pr(" Layout %s" % id)
        if id in ltool.objectIds():
            pr("  Deleting.")
            ltool.manage_delObjects([id])
        pr("  Installing.")
        layout = ltool.manage_addCPSLayout(id)
        for widget_id, widgetinfo in info['widgets'].items():
            pr("   Widget %s" % widget_id)
            widget = layout.manage_addCPSWidget(widget_id, widgetinfo['type'])
            widget.manage_changeProperties(**widgetinfo['data'])
        layout.setLayoutDefinition(info['layout'])


    pr("End of specific CPSDocument intall")
    return pr('flush')
