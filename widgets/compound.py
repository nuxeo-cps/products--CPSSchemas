# (C) Copyright 2003-2009 Nuxeo SA <http://nuxeo.com>
# Authors:
# Florent Guillaume <fg@nuxeo.com>
# M.-A. Darche <madarche@nuxeo.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.

"""Compound widgets are made of subwidgets with a bit of glue.
"""

import logging
from Globals import InitializeClass
from Acquisition import aq_parent, aq_inner, aq_base
from Products.CPSSchemas.Widget import CPSWidget

logger = logging.getLogger(__name__)

class CPSCompoundWidget(CPSWidget):
    """Widget with customizable logic and presentation.

    Allows the use of other widgets to do the rendering.
    """
    meta_type = 'Compound Widget'

    _properties = (
        CPSWidget._properties[:2] + (
        {'id': 'widget_ids', 'type': 'tokens', 'mode': 'w',
         'label': 'Widget ids'},
        {'id': 'render_method', 'type': 'string', 'mode': 'w',
         'label': 'Render Method'},
        {'id': 'prepare_validate_method', 'type': 'string', 'mode': 'w',
         'label': 'Prepare & Validate Method'},
        ) + CPSWidget._properties[2:]
        )
    widget_ids = []
    widget_type = None # Compat with old instances
    render_method = 'widget_compound_default_render'
    prepare_validate_method = ''
    fieldset = True # making <fieldset> <legend> likely to be useful

    _old_render_methods = {
        'Link Widget': 'widget_link_render',
        'Text Image Widget': 'widget_textimage_render',
        'Search Widget': 'widget_search_render',
        'Image Link Widget': 'widget_imagelink_render',
        'Search Location Widget': 'widget_searchlocation_render',
        }

    logger = logger # available from subclasses

    def _getRenderMethod(self):
        """Get the render method."""
        name = self._old_render_methods.get(self.widget_type,
                                            self.render_method)
        meth = getattr(self, name, None)
        if meth is None:
            raise RuntimeError("Unknown render method %r for widget %s" %
                               (name, self.getWidgetId()))
        return meth

    _old_prepare_validate_methods = {
        'Link Widget': '',
        'Text Image Widget': 'widget_textimage_prepare_validate',
        'Search Widget': '',
        'Image Link Widget': 'widget_imagelink_prepare_validate',
        'Search Location Widget': 'widget_searchlocation_prepare_validate',
        }

    def _getSubWidgets(self, with_ids=False):
        """Return the subwidgets, or None if one is missing."""
        layout = aq_parent(aq_inner(self))
        wids = self.widget_ids
        try:
            widgets = tuple(layout[wid] for wid in wids)
        except KeyError, e:
            self._v_hidden = True
            self.logger.error("Missing subwidget %s in compound widget %r. "
                              "Hiding", e, self)
            return () # don't break downstream code

        if with_ids:
            return zip(wids, widgets)
        return widgets

    def _getPrepareValidateMethod(self):
        """Get the prepare/validate method."""
        # Compatibility for old instances
        name = self._old_prepare_validate_methods.get(self.widget_type,
                                               self.prepare_validate_method)
        if not name:
            meth = lambda *args, **kw: True
        else:
            meth = getattr(self, name, None)
        if meth is None:
            raise RuntimeError("Unknown prepare/validate method '%s' "
                               "for widget %s" % (name, self.getWidgetId()))
        return meth

    def getFieldTypes(self):
        """Get field types from the underlying widgets."""
        return [] #X XXX

    def getFieldInits(self):
        """Get field inits from the underlying widgets."""
        return [] # XXX

    def isHidden(self):
        if getattr(aq_base(self), '_v_hidden', False):
            return True
        return CPSWidget.isHidden(self)

    def prepare(self, datastructure, **kw):
        """Prepare the underlying widgets."""

        # Prepare each widget
        for widget in self._getSubWidgets():
            widget.prepare(datastructure, **kw)
        # Now prepare compound
        prepare = self._getPrepareValidateMethod()
        return prepare('prepare', datastructure)

    def validate(self, datastructure, **kw):
        """Validate the underlying widgets."""
        validate = self._getPrepareValidateMethod()
        # Pre-validate compound (may fixup the datastructure)
        ret = validate('prevalidate', datastructure)
        if not ret and ret is not None:
            # None is allowed to mean "ok"
            return False
        # Now validate each widget
        layout = aq_parent(aq_inner(self))
        ret = True
        for widget in self._getSubWidgets():
            ret = widget.validate(datastructure, **kw) and ret
        # Post-validate
        return ret and validate('validate', datastructure)

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        widget_infos = kw['widget_infos']
        cells = []
        for widget_id, widget in self._getSubWidgets(with_ids=True):
            cell = {}
            # widget, widget_mode, css_class
            cell.update(widget_infos[widget_id])
            widget_mode = cell['widget_mode']
            if widget_mode == 'hidden':
                continue
            rendered = widget.render(widget_mode, datastructure, **kw)
            rendered = rendered.strip()
            cell['widget_rendered'] = rendered
            if not widget.hidden_empty or rendered:
                # do not add widgets to be hidden when empty
                cells.append(cell)

        render = self._getRenderMethod()
        return render(mode=mode, datastructure=datastructure,
                      cells=cells, **kw)

InitializeClass(CPSCompoundWidget)

class CPSProgrammerCompoundWidget(CPSCompoundWidget):
    """Base class for compound widgets defined in code.

    They don't need to have the "method" fields customizable,
    because these are defined by their class.
    """
    meta_type = 'Code Compound Widget'
    _properties = (
        CPSCompoundWidget._properties[:3] +
        # skip render_method
        # skip prepare_validate_method
        CPSCompoundWidget._properties[5:]
        )
    field_types = ()

InitializeClass(CPSProgrammerCompoundWidget)
