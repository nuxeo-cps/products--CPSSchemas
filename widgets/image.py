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
import urllib

from Globals import InitializeClass
from OFS.Image import Image
from zExceptions import BadRequest

from Products.CPSUtil.html import renderHtmlTag
from Products.CPSUtil.mail import make_cid
from Products.CPSUtil.file import ofsFileHandler
from Products.CPSUtil.image import resized_geometry
from Products.CPSUtil.image import parse_size_spec_as_dict
from Products.CPSUtil.image import parse_size_spec
from Products.CPSUtil.image import resize as image_resize
from Products.CPSUtil.image import SizeSpecError
from Products.CPSUtil.image import geometry as image_geometry
from Products.CPSSchemas.Widget import EMAIL_LAYOUT_MODE
from Products.CPSSchemas.BasicWidgets import CPSFileWidget, CPSIntWidget
from Products.CPSSchemas.BasicWidgets import CPSProgrammerCompoundWidget
from Products.CPSSchemas.Widget import CIDPARTS_KEY

logger = logging.getLogger(__name__)

class MissingSizeWidget(IndexError):
    """Exception raised if a size widget does not exist (not always an error).
    """

class CPSImageWidget(CPSFileWidget, CPSProgrammerCompoundWidget):
    """Image widget.

    Stores an image in document and display it according to a size spec
    either fixed in property or managed by another widget. In that case,
    the Image widget acts in edit mode like the compound widget.
    Actually, all sub widgets are rendered in edit mode.
    Subclasses using several of them to manipulate several renderings
    (popup, mouse-over etc) therefore don't have to override the edit rendering.

    These size widgets can manipulate either:
    - string fields: in that case, the value is expected to be a valid
    size spec as for the live resizing system hooked in traversal
    (e.g., 320x200, w640)
    - integer fields: in that case, the value is applied as a "largest
    dimension" (i.e. the size spec is 'l320'), and the size widget must
    subclass CPSIntWidget.

    There is a simple assumptions on auxiliary widgets, which is a largely
    observed convention:
    - the field used to store the value must be its first.
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
             label='Auxiliary widgets for user-managed size specifications '),
        )

    size_spec = ''
    widget_ids = ()
    allow_resize = True

    size_widgets = (0,) # sub widgets that handle size specs, if defined

    render_method = 'renderAsCompound' # called by CPSCompoundWidget.render
    final_render_method = 'widget_image_render' # called by renderAsCompound

    def updateImageInfoForEmail(self, info, datastructure, dump=False):
        """Use the cid: URL scheme (RFC 2392) and dump parts in datastructure.
        """

        info['mime_content_id'] = cid = make_cid(self.getHtmlWidgetId())
        info['content_url'] = 'cid:' + cid
        if not dump:
            return

        # we must avoid the FileUpload object that's in datastructure,
        # because we may have a TramlineImage here and in that case the
        # FileUpload is just the id.
        # note that using this method between prepare and validate is
        # a really strange idea
        dm = datastructure.getDataModel()
        fobj = dm[self.fields[0]]
        if fobj is not None:
            parts = datastructure.setdefault(CIDPARTS_KEY, {})
            filename = info['current_filename']
            try:
                spec = self.getSizeSpec(dm, w_index=0)
            except MissingSizeWidget:
                spec = self.size_spec

            if spec == 'full':
                resized = ofsFileHandler(fobj).read() # Youps, RAM
            else:
                w, h = resized_geometry(fobj, spec)
                resized = image_resize(fobj, w, h,
                                       fobj.getId(), raw=True)

            parts[cid] = {'content': resized,
                          'filename': filename,
                          'content-type': info['mimetype'],
                          }

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
        if info['empty_file']:
            return info

        info['height'], info['width'] = image_geometry(ds[self.getWidgetId()])

        layout_mode = kw.get('layout_mode')
        if layout_mode == EMAIL_LAYOUT_MODE:
            self.updateImageInfoForEmail(info, ds, dump=dump_cid_parts)

        if info['empty_file']:
            info['height'] = info['width'] = 0
            info['image_tag'] = info['alt'] = ''
            return info

        title = info['title']

        # alt (defaults to title)
        wid = self.getWidgetId()
        alt = ds.get(wid + '_alt', title)
        info['alt'] = alt

        # image URI
        if layout_mode == EMAIL_LAYOUT_MODE:
            uri = info['content_url']
        else:
            uri = self.imageUri(ds.getDataModel())
        info['image_tag'] = renderHtmlTag('img', src=uri, title=title, alt=alt)

        return info

    def imageUri(self, dm, w_index=0, if_w_missing='prop'):
        """Return a sized URI for the image.
        w_index can be used to select the size widget responsible for the spec.
        if_w_missing controls what to do if the size widget is missing.
        values : 'prop' (default to widget prop)
                 'full' (default to full size)
        """
        try:
            spec = self.getSizeSpec(dm, w_index=w_index)
        except MissingSizeWidget:
            if if_w_missing == 'prop':
                spec = self.size_spec
            elif if_w_missing == 'full':
                spec = 'full'
            else:
                raise

        parsed_spec = parse_size_spec_as_dict(spec)
        return dm.imageUri(self.fields[0], **parsed_spec)

    def getSizeSpec(self, dm, w_index=0, with_widget=False):
        """Return a usable size spec from what's in datamodel.

        If the dm value evaluates to False, the widget property is used.
        The optional w_index allows to choose among subwidgets
        if with_widget is True, the widget is also returned, or None
        """
        try:
            swidget = self._getSubWidgets()[w_index]
        except IndexError:
            raise MissingSizeWidget(w_index)

        v = dm[swidget.fields[0]]
        if not v:
            res = self.size_spec
        elif isinstance(v, int):
            res = 'l%d' % v
        else:
            res = v
        return with_widget and (res, swidget) or res

    def mainPrepare(self, ds, **kw):
        """Part of preparation that does not depend on optional fields."""
        CPSFileWidget.prepare(self, ds, **kw)
        if self.widget_ids:
            for widget in self._getSubWidgets():
                widget.prepare(ds, **kw)

    def optPrepare(self, ds, **kw):
        """Prepare datastructure from datamodel using optional fields"""
        dm = ds.getDataModel()
        widget_id = self.getWidgetId()

        title = ''
        if len(self.fields) > 2:
            title = dm[self.fields[2]]
        ds[widget_id + '_title'] = title

        alt = ''
        if len(self.fields) > 2:
            alt = dm[self.fields[2]]
            # Defaulting to the file name if there is an image file and if no
            # alt has been given yet. This is the case when the document is
            # created.
            if not alt:
                alt = ds[widget_id + '_filename']
        ds[widget_id + '_alt'] = alt

    def prepare(self, ds, **kw):
        self.mainPrepare(ds, **kw)
        self.optPrepare(ds, **kw)

    def imageValidate(self, ds, **kw):
        """Validation for image and size_spec widgets only."""
        if not CPSFileWidget.validate(self, ds, **kw):
            return False

        if self.widget_ids:
            for subw in self._getSubWidgets():
                if not subw.validate(ds):
                    return False
        return True

    def validate(self, ds, **kw):
        """Override FileWidget's method."""
        if not self.imageValidate(ds, **kw):
            return False

        dm = ds.getDataModel()
        widget_id = self.getWidgetId()

        # Title
        if len(self.fields) > 2:
            dm[self.fields[2]] = ds[widget_id + '_title']

        # Alt
        if len(self.fields) > 3:
            dm[self.fields[3]] = ds[widget_id + '_alt']

        for i in self.size_widgets:
            if not self.validateSizeSpec(ds, i):
                return False

        return True

    def validateSizeSpec(self, ds, widget_index):
        """Validate the size specification handled by sub widget #widget_index.

        Note that we need the typed value, so it's read from datamodel.
        This means that this method must be called *after* validation of
        the subwidgets has validated the datamodel.
        """
        dm = ds.getDataModel()
        try:
            spec, swidget = self.getSizeSpec(dm, w_index=widget_index,
                                             with_widget=True)
        except MissingSizeWidget:
            return True

        try:
            parse_size_spec(spec)
        except SizeSpecError:
            if swidget is None:
                raise
            ds.setError(swidget.getWidgetId(),
                        'cpsschemas_invalid_size_spec')
            return False

        return True

    def makeFile(self, filename, fileupload, datastructure):
        return Image(self.fields[0], filename, fileupload)

    def checkFileName(self, filename, mimetype):
        if mimetype and mimetype.startswith('image'):
            return '', {}
        return 'cpsschemas_err_image', {}

    def render(self, mode, datastructure, **kw):
        img_info = self.getImageInfo(datastructure, dump_cid_parts=True, **kw)
        if mode == 'view':
            if img_info['empty_file']:
                return ''
            return img_info['image_tag']

        return CPSProgrammerCompoundWidget.render(self, mode, datastructure,
                                                  img_info=img_info, **kw)

    def renderAsCompound(self, mode='edit', datastructure=None, cells=(),
                         img_info=None, **kw):
        """Final rendering method for the compound case.
        """

        if datastructure is None or img_info is None:
            # should really not happen
            raise ValueError('datastructure or img_info is None')

        render_method = self.final_render_method
        if cells:
            size_widget = cells[0]
        else:
            size_widget = None

        kw.update(img_info)
        meth = getattr(self, render_method, None)
        if meth is None:
            raise RuntimeError("Unknown Render Method %s for widget type %s"
                               % (render_method, self.getId()))
        return meth(size_widget=cells and cells[0] or None, mode=mode,
                    datastructure=datastructure, **kw)

InitializeClass(CPSImageWidget)


class CPSPhotoWidget(CPSImageWidget):
    """Photo widget.

    has more content-dependent options than plain Image Widget:
      - caption (aka subtitle)
      - user-configurable position (or not)
      - popup for separate image viewing (typically bigger)

    Overall, has potentially more rendering options than Image Widget.
    New rendering options should be added to this widget rather than to Image
    Widget
    """
    meta_type = 'Photo Widget'

    field_types = ('CPS Image Field',   # Original image
                   'CPS String Field',  # Caption
                   'CPS String Field',  # render_position if configurable
                   'CPS String Field',  # Title
                   'CPS String Field',  # Alternate text for accessibility
                   )

    field_inits = ({}, {'is_searchabletext': 1,}, {}, {}, {})

    _properties = CPSImageWidget._properties + (
        {'id': 'render_position', 'type': 'selection', 'mode': 'w',
         'select_variable': 'all_render_positions',
         'label': 'Render position'},
        {'id': 'configurable', 'type': 'selection', 'mode': 'w',
         'select_variable': 'all_configurable',
         'label': 'What is user configurable, require extra fields'},
        {'id': 'zoom_size_spec', 'type': 'string', 'mode': 'w',
         'label': 'Size specification for the zoomed display'},
        )
    all_configurable = ['nothing', 'position']
    all_render_positions = ['left', 'center', 'right']

    render_position = all_render_positions[0]
    configurable = all_configurable[0]
    zoom_size_spec = 'full'

    final_render_method = 'widget_photo_render' # called by fullEditRender

    def optPrepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel using optional fields"""
        datamodel = datastructure.getDataModel()
        widget_id = self.getWidgetId()

        if len(self.fields) > 1:
            datastructure[widget_id + '_subtitle'] = datamodel[self.fields[1]]
        else:
            datastructure[widget_id + '_subtitle'] = ''

        rposition = self.render_position
        if self.configurable != 'nothing':
            if len(self.fields) > 2:
                v = datamodel[self.fields[2]]
                if v in self.all_render_positions:
                    rposition = v
        datastructure[widget_id + '_rposition'] = rposition

        title = ''
        if len(self.fields) > 4:
            title = datamodel[self.fields[4]]
        datastructure[widget_id + '_title'] = title

        alt = ''
        if len(self.fields) > 5:
            alt = datamodel[self.fields[5]] # Same as in Image Widget
            if not alt:
                alt = datastructure[widget_id + '_filename']
        datastructure[widget_id + '_alt'] = alt

    def validate(self, ds, **kw):
        """Override FileWidget's method."""
        if not self.imageValidate(ds, **kw):
            return False

        dm = ds.getDataModel()
        widget_id = self.getWidgetId()

        # Caption
        if len(self.fields) > 1:
            subtitle = ds[widget_id + '_subtitle']
            dm[self.fields[1]] = subtitle

        # Position
        if self.configurable != 'nothing' and len(self.fields) > 2:
            rposition = ds[widget_id + '_rposition']
            if rposition and rposition in self.all_render_positions:
                dm[self.fields[2]] = rposition

        # Title
        if len(self.fields) > 3:
            dm[self.fields[3]] = ds[widget_id + '_title']

        # Alt
        if len(self.fields) > 4:
            dm[self.fields[4]] = ds[widget_id + '_alt']

        return True

    def getZoomInfo(self, ds):
        """Extract info about zoomed image from datastructure."""
        dm = ds.getDataModel()
        try:
            spec = self.getSizeSpec(dm, w_index=1)
        except MissingSizeWidget:
            spec = self.zoom_size_spec
        wid = self.getWidgetId()
        uri = dm.imageUri(self.fields[0], **parse_size_spec_as_dict(spec))
        if uri is None:
            return
        w, h = resized_geometry(ds[wid], spec)
        return dict(uri=uri, width=w, height=h,
                    escaped_uri=urllib.quote_plus(uri))

    def render(self, mode, ds, **kw):
        """Render in mode from datastructure."""
        img_info = self.getImageInfo(ds, dump_cid_parts=True, **kw)
        if mode == 'view':
            if img_info['empty_file']:
                return ''

        widget_id = self.getWidgetId()
        rposition = ds[widget_id + '_rposition']
        subtitle = ds[widget_id + '_subtitle']

        return CPSProgrammerCompoundWidget.render(
            self, mode, ds,
            subtitle=subtitle,
            render_position=rposition,
            configurable=str(self.configurable),
            zoom=self.getZoomInfo(ds),
            img_info=self.getImageInfo(ds, dump_cid_parts=True, **kw),
            **kw)


InitializeClass(CPSPhotoWidget)

