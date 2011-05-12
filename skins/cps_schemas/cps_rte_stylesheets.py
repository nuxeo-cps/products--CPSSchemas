##parameters=climb=0
sheets = ['default.css', 'custom.css', 'document.css', 'schemas.css']
theme_sheets = ['moi.css']
from Products.CPSDesignerThemes.negociator import adapt
engine = adapt(context, context.REQUEST)
theme_sheets = engine.getStyleSheetUris()

if climb:
    prefix = '/'.join(('..',) * climb)
    theme_sheets = [prefix + sheet for sheet in theme_sheets]
sheets.extend(theme_sheets)

return "'%s'" % ','.join(sheets)
