# Renders a CSS file with the styles of the main slot, useable mainly for
# FCKEditor.
pt = context.portal_themes
theme, page = pt.getEffectiveThemeAndPageName()

theme = pt[theme]
page = theme.getPageContainer(page)

for templet in page.getTemplets():
    if hasattr(templet, 'getSlot') and templet.getSlot() == 'content_well':
        break

styles_dir = theme.getStylesFolder()
all_styles = {}
for s in styles_dir.objectValues():
    all_styles[s.getTitle()] = s

res = ''
fontshape = all_styles[getattr(templet, 'fontshape')]
res += context.cpsskins_fontshape_fckeditor(fontshape)
fontcolor = all_styles[getattr(templet, 'fontcolor')]
res += context.cpsskins_fontcolor_fckeditor(fontcolor)
        
return res

