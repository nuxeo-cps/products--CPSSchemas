# (C) Copyright 2010 CPS-CMS Community <http://cps-cms.org/>
# Authors:
#     G. Racinet <georges@racinet.fr>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging

from Globals import InitializeClass
from OFS.Image import Image

from Products.CPSUtil.html import renderHtmlTag
from Products.CPSUtil.mail import make_cid
from Products.CPSSchemas.Widget import EMAIL_LAYOUT_MODE
from Products.CPSSchemas.BasicWidgets import CPSFileWidget
from Products.CPSSchemas.BasicWidgets import CPSProgrammerCompoundWidget
from Products.CPSSchemas.Widget import CIDPARTS_KEY

logger = logging.getLogger(__name__)

class CPSImageWidget(CPSFileWidget, CPSProgrammerCompoundWidget):
    """Image widget.

    Stores an image in document and display it according to a size spec
    either fixed in property or managed by another widget.
    It is assumed that this latter widget uses its id as datastructure key
    for the main value it handles (as most widget do).
    Typically, a Select widget is being used
    """

    meta_type = 'Image Widget'

    field_types = ('CPS Image Field',
                   'CPS String Field',  # Title
                   'CPS String Field',  # Alternate text for accessibility
                   )

    _properties = CPSFileWidget._properties + (
        dict(id='size_spec', type='string', mode='w',
         label='Size specification (e.g. 320x200, w430, h200, l320, full)'),
        dict(id='widget_ids', type='tokens', mode='w',
             label='Auxiliary widgets for size specifications '
             '(e.g. 320x200, w430, h200, l320, full)'),
        )

    size_spec = ''
    widget_ids = ()
    allow_resize = True

    def updateImageInfoForEmail(self, info, datastructure, dump=False):
        """Use the cid: URL scheme (RFC 2392) and dump parts in datastructure.
        """

        info['mime_content_id'] = cid = make_cid(self.getHtmlWidgetId())
        info['content_url'] = 'cid:' + cid
        if not dump:
            return

        # TODO now we need resizing here also!
        fupload = datastructure[self.getWidgetId()]
        if fupload is not None:
            fupload.seek(0)
            parts = datastructure.setdefault(CIDPARTS_KEY, {})
            parts[cid] = {'content': fupload.read(),
                          'filename': info['current_filename'],
                          'content-type': info['mimetype'],
                          }
            fupload.seek(0)

    def readImageGeometry(self, ds):
        """Return width, height for image in datastructure.
        """
        image = ds[self.getWidgetId()]
        # TODO getImageInfo has problems with some jpg images
        # use PIL instead if available
        from OFS.Image import getImageInfo
        image.seek(0)
        width, height = getImageInfo(image.read(24))[1:]
        image.seek(0)

        if width < 0:
            width = None
        if height < 0:
            height = None

        return width, height

    def getImageInfo(self, ds, dump_cid_parts=False, **kw):
        """Get the image info from the datastructure.

        This is what's called file_info in File Widget, enhanced with image
        specific data.

        if 'dump_cid_parts' is True, the image is dumped in the datastructure.
        This is a side-effect, but it's been made such to avoid code duplication
        in subclasses' render methods. To update these latter, just
        set this kwarg to True in the call of getImageInfo and pass **kw.
        """
        info = self.getFileInfo(ds)

        layout_mode = kw.get('layout_mode')
        if layout_mode == EMAIL_LAYOUT_MODE:
            self.updateImageInfoForEmail(info, ds, dump=dump_cid_parts)

        if info['empty_file']:
            info['height'] = info['width'] = 0
            info['image_tag'] = info['alt'] = ''
            return info

        info['height'], info['width'] = self.readImageGeometry(ds)

        title = info['title']

        # alt (defaults to title)
        wid = self.getWidgetId()
        alt = ds.get(wid + '_alt', title)
        info['alt'] = alt

        if layout_mode == EMAIL_LAYOUT_MODE:
            uri = info['content_url']
        else: # generate resizing URI
            # TODO -> CPSUtil
            from Products.CPSCore.ProxyBase import ImageDownloader
            size_spec = ds[wid + '_size']
            parsed_spec = ImageDownloader._parseSizeSpecAsDict(size_spec)
            dm = ds.getDataModel()
            uri = dm.imageUri(self.fields[0], **parsed_spec)
        info['image_tag'] = renderHtmlTag('img', src=uri, title=title, alt=alt)

        return info

    def sizeKey(self):
        if self.widget_ids:
            # GR: this in almost always equivalent to widget_ids[0]
            # thank you ZODB cache
            return self._getSubWidgets()[0].getWidgetId()
        return self.getWidgetId() + '_size'

    def getSizeWidget(self):
        if self.widget_ids:
            return self._getSubWidgets()[0]
        return self

    def prepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel."""

        CPSFileWidget.prepare(self, datastructure, **kw)
        datamodel = datastructure.getDataModel()
        widget_id = self.getWidgetId()

        if self.widget_ids:
            for widget in subw:
                widget.prepare(datastructure, **kw)
        else:
            datastructure[widget_id + '_size'] = self.size_spec

        title = ''
        if len(self.fields) > 2:
            title = datamodel[self.fields[2]]
        datastructure[widget_id + '_title'] = title

        alt = ''
        if len(self.fields) > 2:
            alt = datamodel[self.fields[2]]
            # Defaulting to the file name if there is an image file and if no
            # alt has been given yet. This is the case when the document is
            # created.
            if not alt:
                alt = datastructure[widget_id + '_filename']
        datastructure[widget_id + '_alt'] = alt

    def otherProcessing(self, choice, ds):
        """Override FileWidget's method."""
        if self.widget_ids:
            for subw in self._getSubWidgets():
                if not subw.validate(ds):
                    return False

        dm = ds.getDataModel()
        widget_id = self.getWidgetId()

        # Title
        if len(self.fields) > 2:
            dm[self.fields[2]] = ds[widget_id + '_title']

        # Alt
        if len(self.fields) > 3:
            dm[self.fields[3]] = ds[widget_id + '_alt']


#        from Products.CPSCore.ProxyBase import ImageDownloader
#        try:
#            ImageDownloader._parseSizeSpec(size_spec)
#        except BadRequest:
#            ds.setError(self.getSizeWidget().getWidgetId(),
#                        'cpsschemas_invalid_size_spec')
#            return False
#        dm[self.fields[1]] = size_spec
#        return True

    def makeFile(self, filename, fileupload, datastructure):
        return Image(self.fields[0], filename, fileupload)

    def checkFileName(self, filename, mimetype):
        if mimetype and mimetype.startswith('image'):
            return '', {}
        return 'cpsschemas_err_image', {}

    render_method = 'fullEditRender'

    def render(self, mode, datastructure, **kw):
        img_info = self.getImageInfo(datastructure, dump_cid_parts=True, **kw)
        if mode == 'view':
            if img_info['empty_file']:
                return ''
            return img_info['image_tag']

        return CPSProgrammerCompoundWidget.render(self, mode, datastructure,
                                                  img_info=img_info, **kw)


    def fullEditRender(self, mode='edit', datastructure=None,
                       cells=(), img_info=None, **kw):
        """Final rendering method for the compound case."""

        if datastructure is None or img_info is None:
            # should really not happen
            raise ValueError('datastructure or img_info is None')

        render_method = 'widget_image_render'
        if cells:
            size_widget = cells[0]
        else:
            size_widget = None
        meth = getattr(self, render_method, None)
        if meth is None:
            raise RuntimeError("Unknown Render Method %s for widget type %s"
                               % (render_method, self.getId()))
        return meth(mode=mode, size_widget=cells and cells[0] or None,
                    datastructure=datastructure, **img_info)

InitializeClass(CPSImageWidget)

