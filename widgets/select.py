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

"""
Select and MultiSelect widgets allow the user to choose value(s) from a vocabularay.
"""

import logging
from cgi import escape

from Globals import InitializeClass
from Products.CMFCore.utils import getToolByName

from Products.CPSUtil.text import uni_lower
from Products.CPSUtil.html import XhtmlSanitizer
from Products.CPSUtil.html import renderHtmlTag
from Products.CPSSchemas.Widget import CPSWidget
from Products.CPSSchemas.MethodVocabulary import MethodVocabularyWithContext
from Products.CPSSchemas.Vocabulary import EmptyKeyVocabularyWrapper

logger = logging.getLogger(__name__)

class CPSSelectWidget(CPSWidget):
    """Select widget."""
    meta_type = 'Select Widget'

    field_types = ('CPS String Field',)
    field_inits = ({'is_searchabletext': 1,},)

    _properties = CPSWidget._properties + (
        {'id': 'vocabulary', 'type': 'string', 'mode': 'w',
         'label': 'Vocabulary', 'is_required' : 1},
        {'id': 'translated', 'type': 'boolean', 'mode': 'w',
         'label': 'Vocabulary is i18n'},
        {'id': 'sorted', 'type': 'boolean', 'mode': 'w',
         'label': 'Are vocabulary values rendered sorted'},
        {'id': 'add_empty_key', 'type': 'boolean', 'mode': 'w',
         'label':'Add an empty key'},
        {'id': 'empty_key_pos', 'type': 'selection', 'mode': 'w',
         'select_variable': 'empty_key_pos_select',
         'label':'Empty key position'},
        {'id': 'empty_key_value', 'type': 'string', 'mode': 'w',
         'label':'Empty key value'},
        {'id': 'empty_key_value_i18n', 'type': 'string', 'mode': 'w',
         'label':'Empty key i18n value'},
        )

    # XXX make a menu for the vocabulary.
    vocabulary = ''
    translated = False
    sorted = False
    add_empty_key = False
    empty_key_pos_select = ('first', 'last')
    empty_key_pos = empty_key_pos_select[0]
    empty_key_value = ''
    empty_key_value_i18n = ''

    # Associating the widget label with an input area to improve the widget
    # accessibility.
    has_input_area = True

    def _getVocabulary(self, datastructure=None):
        """Get the vocabulary object for this widget."""
        context = datastructure.getDataModel().getContext()
        if not isinstance(self.vocabulary, str):
            # this is in case vocabulary directly holds
            # a vocabulary object
            vocabulary = self.vocabulary
        else:
            vtool = getToolByName(self, 'portal_vocabularies')
            vocabulary = vtool.getVocabularyFor(context, self.vocabulary)
        if vocabulary.meta_type == 'CPS Method Vocabulary':
            vocabulary = MethodVocabularyWithContext(vocabulary, context)
        if self.add_empty_key:
            vocabulary = EmptyKeyVocabularyWrapper(
                vocabulary, self.empty_key_value,
                msgid=self.empty_key_value_i18n,
                position=self.empty_key_pos,)
        return vocabulary

    def _getTranslatedVocabularyKey(self, translation_service, vocabulary,
                                    key):
        """Get vocabulary key translated."""
        msgid = vocabulary.getMsgid(key, key)
        if not isinstance(msgid, basestring):
            msgid = str(msgid)
        value = translation_service(msgid, default=msgid)
        return value

    def _getTranslatedMsgid(self, translation_service, msgid):
        """Get translated Msgid for selections presentation
        """
        value = translation_service(msgid, default=msgid)
        return value

    def prepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel."""
        datamodel = datastructure.getDataModel()
        datastructure[self.getWidgetId()] = datamodel[self.fields[0]]

    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel."""
        widget_id = self.getWidgetId()
        value = datastructure[widget_id]
        try:
            v = str(value)
        except ValueError:
            datastructure.setError(widget_id, "cpsschemas_err_select")
            return 0
        vocabulary = self._getVocabulary(datastructure)
        if not vocabulary.has_key(value):
            datastructure.setError(widget_id, "cpsschemas_err_select")
            return 0
        if self.is_required and not len(v):
            datastructure.setError(widget_id, "cpsschemas_err_required")
            return 0

        datamodel = datastructure.getDataModel()
        datamodel[self.fields[0]] = v
        return 1

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        value = datastructure[self.getWidgetId()]
        vocabulary = self._getVocabulary(datastructure)
        portal = getToolByName(self, 'portal_url').getPortalObject()
        cpsmcat = portal.translation_service
        if mode == 'view':
            if self.translated:
                return escape(cpsmcat(vocabulary.getMsgid(value, value)))
            else:
                ret = vocabulary.get(value, value)
                if ret is not None:
                    return escape(ret)
                else:
                    return ""
        elif mode == 'edit':
            html_widget_id = self.getHtmlWidgetId()
            res = renderHtmlTag('select',
                                name=html_widget_id, id=html_widget_id)
            in_selection = False
            vocabulary_items = vocabulary.items()
            if self.translated:
                vocabulary_items_translated = []
                for k, v in vocabulary_items:
                    label = cpsmcat(vocabulary.getMsgid(k, k), default=k)
                    vocabulary_items_translated.append((k, label))
                vocabulary_items = vocabulary_items_translated
            if self.sorted:
                vocabulary_items.sort(key=lambda obj: obj[1].lower())
            for k, v in vocabulary_items:
                kw = {'value': k, 'contents': v}
                if value == k:
                    kw['selected'] = 'selected'
                    in_selection = True
                res += renderHtmlTag('option', **kw)
            if value and not in_selection:
                kw = {'value': value, 'contents': 'invalid: ' + value,
                      'selected': 'selected'}
                res += renderHtmlTag('option', **kw)
            res += '</select>'
            return res
        raise RuntimeError('unknown mode %s' % mode)

InitializeClass(CPSSelectWidget)


class CPSMultiSelectWidget(CPSSelectWidget):
    """MultiSelect widget."""
    meta_type = 'MultiSelect Widget'

    field_types = ('CPS String List Field',)
    field_inits = ({'is_searchabletext': 1,},)

    _properties = CPSSelectWidget._properties + (
        {'id': 'size', 'type': 'int', 'mode': 'w',
         'label': 'Size'},
        {'id': 'format_empty', 'type': 'string', 'mode': 'w',
         'label': 'Format for empty list'},
        )
    size = 0
    format_empty = ''

    # Associating the widget label with an input area to improve the widget
    # accessibility.
    has_input_area = True

    # BBB for [46410]. Remove this once an upgrade step has been written
    sorted = False

    def prepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel."""
        datamodel = datastructure.getDataModel()
        value = datamodel[self.fields[0]]
        if value == '':
            # Buggy Zope :lines prop may give us '' instead of [] for default
            value = []
        # XXX make a copy of the list ?
        datastructure[self.getWidgetId()] = value

    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel."""
        widget_id = self.getWidgetId()
        value = datastructure[widget_id]
        if not isinstance(value, (list, tuple)):
            datastructure.setError(widget_id, "cpsschemas_err_multiselect")
            return 0
        vocabulary = self._getVocabulary(datastructure)
        v = []
        for i in value:
            try:
                i = str(i)
            except ValueError:
                datastructure.setError(widget_id, "cpsschemas_err_multiselect")
                return 0
            if not vocabulary.has_key(i):
                datastructure.setError(widget_id, "cpsschemas_err_multiselect")
                return 0
            v.append(i)
        if self.is_required and not len(v):
            datastructure.setError(widget_id, "cpsschemas_err_required")
            return 0
        datamodel = datastructure.getDataModel()
        datamodel[self.fields[0]] = v
        return 1

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        value = datastructure[self.getWidgetId()]
        vocabulary = self._getVocabulary(datastructure)
        portal = getToolByName(self, 'portal_url').getPortalObject()
        cpsmcat = portal.translation_service
        if mode == 'view':
            if not value:
                # XXX L10N empty format may be subject to i18n
                return self.format_empty
            # XXX customize view mode, lots of displays are possible
            else:
                return self.getEntriesHtml(value, vocabulary, self.translated)
        elif mode == 'edit':
            html_widget_id = self.getHtmlWidgetId()
            kw = {'name': html_widget_id + ':utf8:ulist',
                  'multiple': 'multiple',
                  'id': html_widget_id,
                  }
            if self.size:
                kw['size'] = self.size
            res = renderHtmlTag('select', **kw)

            vocabulary_items = vocabulary.items()
            if self.translated:
                vocabulary_items_translated = []
                for k, v in vocabulary_items:
                    label = cpsmcat(vocabulary.getMsgid(k, k), default=k)
                    vocabulary_items_translated.append((k, label))
                vocabulary_items = vocabulary_items_translated
            if self.sorted:
                vocabulary_items.sort(key=lambda obj: obj[1].lower())
            for k, v in vocabulary_items:
                kw = {'value': k, 'contents': v}
                if k in value:
                    kw['selected'] = 'selected'
                res += renderHtmlTag('option', **kw)
            res += '</select>'
            default_tag = renderHtmlTag('input',
                                        type='hidden',
                                        name=html_widget_id+':utf8:utokens:default',
                                        value='')
            return default_tag+res
        raise RuntimeError('unknown mode %s' % mode)

    def getEntriesHtml(self, entries, vocabulary, translated=False):
        if translated:
            cpsmcat = getToolByName(self, 'translation_service', None)
            if cpsmcat is None:
                translated = False
        values = []
        for entry in entries:
            if translated:
                value = vocabulary.getMsgid(entry, entry)
                value = cpsmcat(value, default=value)
            else:
                value = vocabulary.get(entry, entry)
            values.append(value)
            if self.sorted:
                values.sort(key=uni_lower)
        return escape(', '.join(values))

InitializeClass(CPSMultiSelectWidget)

class CPSGenericSelectWidget(CPSSelectWidget):
    """The Generic Select widget is more flexible and powerful."""

    meta_type = 'Generic Select Widget'

    _properties = CPSSelectWidget._properties + (
        {'id': 'render_format', 'type': 'selection', 'mode': 'w',
         'select_variable': 'render_formats',
         'label': 'Render format'},
        # Provide an 'other' option where free input is accepted
        # (ignored if render format is 'select')
        {'id': 'other_option', 'type': 'boolean', 'mode':'w',
         'label': "Provide an 'other' option"},
        {'id': 'other_option_display_width', 'type': 'int', 'mode': 'w',
         'label': "'other' option display width"},
        {'id': 'other_option_size_max', 'type': 'int', 'mode': 'w',
         'label': "'other' option maximum input width"},
        # Enables the possibility to add blank values to vocabulary just to
        # change the way the list is presented (using items like 'choose a
        # category' or '------------' to separate items) and not affect the way
        # the value will be validated if the widget is required.
        # Before this, if the widget was required, default behavior was to
        # accept blank values if they were in the vocabulary (e.g
        # blank_value_ok_if_required = 1)
        {'id': 'blank_value_ok_if_required', 'type': 'boolean', 'mode':'w',
         'label': "Accept blank values when validating"},
        {'id': 'onchange', 'type': 'string', 'mode':'w',
         'label': "onchange attribute (edit mode only)"}
        )
    render_formats = ['select', 'radio']

    render_format = render_formats[0]
    other_option = 0
    other_option_display_width = 20
    other_option_size_max = 0
    blank_value_ok_if_required = 1
    onchange = ''

    # BBB for [46171]. Remove this once an upgrade step has been written
    sorted = False

    def prepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel."""
        datamodel = datastructure.getDataModel()
        value = datamodel[self.fields[0]]
        if isinstance(value, (list, tuple)):
            if len(value):
                value = value[0]
            else:
                value = ''
        datastructure[self.getWidgetId()] = value

    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel."""
        widget_id = self.getWidgetId()
        value = datastructure[widget_id]
        vocabulary = self._getVocabulary(datastructure)
        if value != '':
            if not vocabulary.has_key(value):
                if self.render_format == 'select' or not self.other_option:
                    datastructure.setError(widget_id, "cpsschemas_err_select")
                    return 0
        else:
            if self.is_required:
                # set error unless vocabulary holds blank values and
                # blank_value_ok_if_required is set to 1
                if vocabulary.has_key(value):
                    if not self.blank_value_ok_if_required:
                        datastructure.setError(widget_id, "cpsschemas_err_required")
                        return 0
                else:
                    datastructure.setError(widget_id, "cpsschemas_err_required")
                    return 0
        datamodel = datastructure.getDataModel()
        datamodel[self.fields[0]] = value
        return 1


    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        widget_id = self.getWidgetId()
        value = datastructure[widget_id]
        # allow int values to work
        if value is not None:
            value = str(value)
        vocabulary = self._getVocabulary(datastructure)
        cpsmcat = getToolByName(self, 'translation_service')
        if mode == 'view':
            if not vocabulary.has_key(value):
                # for free input
                if value is not None:
                    return escape(value)
                else:
                    return ''
            else:
                if getattr(self, 'translated', None):
                    return escape(self._getTranslatedVocabularyKey(cpsmcat,
                                                                   vocabulary,
                                                                   value))
                else:
                    return escape(vocabulary.get(value, value))
        elif mode == 'edit':
            in_selection = 0
            in_other_selection = 0
            res = ''
            html_widget_id = self.getHtmlWidgetId()
            render_format = self.render_format
            if render_format not in self.render_formats:
                raise RuntimeError('unknown render format %s' % render_format)
            if render_format == 'select':
                res = renderHtmlTag('select',
                                    name=html_widget_id, id=html_widget_id,
                                    onchange=self.onchange or None)
            # vocabulary options
            vocabulary_items = vocabulary.items()
            if self.sorted:
                vocabulary_items.sort(key=lambda obj: obj[1].lower())
            for k, v in vocabulary_items:
                # this enable to work with vocabulary that have integer keys
                k = str(k)
                if getattr(self, 'translated', None):
                    v = self._getTranslatedVocabularyKey(cpsmcat,
                                                         vocabulary,
                                                         k)
                if render_format == 'select':
                    kw = {'value': k, 'contents': v}
                    # do not add a selected option if it is already set
                    if value == k and not in_selection:
                        kw['selected'] = 'selected'
                        in_selection = 1
                    res += renderHtmlTag('option', **kw)
                    res += '\n'
                else:
                    kw = {'id': html_widget_id+'_'+k,
                          'type': render_format,
                          'name': html_widget_id,
                          'value': k,
                          }
                    # do not add a selected option if it is already set
                    if value == k and not in_selection:
                        kw['checked'] = 'checked'
                        in_selection = 1
                    res += renderHtmlTag('input', **kw)
                    kw = {'for': html_widget_id+'_'+k,
                          'contents': v,
                          }
                    res += renderHtmlTag('label', **kw)
                    res += '<br/>\n'
            # invalid or free selections
            if value and not in_selection:
                invalid_contents = '%s %s' % (self._getTranslatedMsgid(
                    cpsmcat, 'label_invalid_selection'), value)
                if render_format == 'select':
                    in_selection = 1
                    kw = {'value': value,
                          'contents': invalid_contents,
                          'selected': 'selected',
                          }
                    res += renderHtmlTag('option', **kw)
                    res += '\n'
                else:
                    if self.other_option:
                        in_selection = 1
                        in_other_selection = 1
                        kw = {'id': html_widget_id+'_other_selection',
                              'type': render_format,
                              'name': html_widget_id,
                              'value':  value,
                              'checked': 'checked',
                              }
                        res += renderHtmlTag('input', **kw)
                        kw = {'for': html_widget_id+'_other_selection',
                              'contents': self._getTranslatedMsgid(
                            cpsmcat, 'label_other_selection'),
                              }
                        res += renderHtmlTag('label', **kw)
                        kw = {'type': 'text',
                              'name': html_widget_id+'_other',
                              'value': value,
                              'onchange': "document.getElementById('"+html_widget_id+"_other_selection').value = this.value",
                              'onclick': "document.getElementById('"+html_widget_id+"_other_selection').checked='checked'",
                              'size': self.other_option_display_width,
                              }
                        if self.other_option_size_max:
                            kw['maxlength'] = self.other_option_size_max
                        res += renderHtmlTag('input', **kw)
                        res += '<br/>\n'
                    else:
                        kw = {'id': html_widget_id+'_'+value,
                              'type': render_format,
                              'name': html_widget_id,
                              'value': value,
                              'disabled': 'disabled',
                              }
                        res += renderHtmlTag('input', **kw)
                        kw = {'for': html_widget_id+'_'+value,
                              'contents': invalid_contents,
                              }
                        res += renderHtmlTag('label', **kw)
                        res += '<br/>\n'
            # 'other' option
            if self.other_option and not in_other_selection:
                if render_format != 'select':
                    kw = {'id': html_widget_id+'_other_selection',
                          'type': render_format,
                          'name': html_widget_id,
                          'value': '',
                          }
                    res += renderHtmlTag('input', **kw)
                    kw = {'for': html_widget_id+'_other_selection',
                          'contents': self._getTranslatedMsgid(
                        cpsmcat, 'label_other_selection'),
                          }
                    res += renderHtmlTag('label', **kw)
                    kw = {'type': 'text',
                          'name': html_widget_id+'_other',
                          'value': "",
                          'onchange': "document.getElementById('"+html_widget_id+"_other_selection').value = this.value",
                          'onclick': "document.getElementById('"+html_widget_id+"_other_selection').checked='checked'",
                          'size': self.other_option_display_width,
                          }
                    if self.other_option_size_max:
                        kw['maxlength'] = self.other_option_size_max
                    res += renderHtmlTag('input', **kw)
                    res += '<br/>\n'
            # default option
            if not self.is_required and not vocabulary.has_key(''):
                if render_format == 'select':
                    kw = {'value': '',
                          'contents': self._getTranslatedMsgid(
                        cpsmcat, 'label_none_selection'),
                          }
                    if not in_selection:
                        kw['selected'] = 'selected'
                    res += renderHtmlTag('option', **kw)
                    res += '\n'
                else:
                    kw = {'id': html_widget_id+'_empty',
                          'type': render_format,
                          'name': html_widget_id,
                          'value': '',
                          }
                    if not in_selection:
                        kw['checked'] = 'checked'
                    res += renderHtmlTag('input', **kw)
                    kw = {'for': html_widget_id+'_empty',
                          'contents': self._getTranslatedMsgid(
                        cpsmcat, 'label_none_selection'),
                          }
                    res += renderHtmlTag('label', **kw)
                    res += '<br/>\n'
            if render_format == 'select':
                res += '</select>'
            return res
        raise RuntimeError('unknown mode %s' % mode)

InitializeClass(CPSGenericSelectWidget)


class CPSGenericMultiSelectWidget(CPSMultiSelectWidget):
    """The Generic MultiSelect widget is more flexible than the regular"""

    meta_type = 'Generic MultiSelect Widget'

    _properties = CPSMultiSelectWidget._properties + (
        {'id': 'render_format', 'type': 'selection', 'mode': 'w',
         'select_variable': 'render_formats',
         'label': 'Render format'},
        # Enables the possibility to add blank values to vocabulary just to
        # change the way the list is presented (using items like 'choose a
        # category' or '------------' to separate items) and not affect the way
        # the value will be validated if the widget is required.
        # Before this, if the widget was required, default behavior was to
        # accept blank values if they were in the vocabulary (e.g
        # blank_value_ok_if_required = 1)
        {'id': 'blank_value_ok_if_required', 'type': 'boolean', 'mode':'w',
         'label': "Accept blank values when validating"},
        )
    render_formats = ['select', 'radio', 'checkbox']

    render_format = render_formats[0]
    blank_value_ok_if_required = 1

    # BBB for [46171]. Remove this once an upgrade step has been written
    sorted = False

    def prepare(self, datastructure, **kw):
        """Prepare datastructure from datamodel."""
        datamodel = datastructure.getDataModel()
        value = datamodel[self.fields[0]]
        if isinstance(value, str):
            if value:
                value = [value,]
            else:
                value = []
        datastructure[self.getWidgetId()] = value


    def validate(self, datastructure, **kw):
        """Validate datastructure and update datamodel."""
        widget_id = self.getWidgetId()
        value = datastructure[widget_id]
        if not isinstance(value, (list, tuple)):
            datastructure.setError(widget_id, "cpsschemas_err_multiselect")
            return 0
        vocabulary = self._getVocabulary(datastructure)
        v = []
        for i in value:
            if i != '':
                try:
                    i = str(i)
                except ValueError:
                    datastructure.setError(widget_id, "cpsschemas_err_multiselect")
                    return 0
                if not vocabulary.has_key(i):
                    datastructure.setError(widget_id, "cpsschemas_err_multiselect")
                    return 0
            else:
                if self.is_required:
                    # set error unless vocabulary holds blank values and
                    # blank_value_ok_if_required is set to 1
                    if vocabulary.has_key(i):
                        if not self.blank_value_ok_if_required:
                            datastructure.setError(widget_id, "cpsschemas_err_required")
                            return 0
                    else:
                        datastructure.setError(widget_id, "cpsschemas_err_required")
                        return 0
            v.append(i)
        if self.is_required and not len(v):
            datastructure.setError(widget_id, "cpsschemas_err_required")
            return 0
        datamodel = datastructure.getDataModel()
        datamodel[self.fields[0]] = v
        return 1

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""
        widget_id = self.getWidgetId()
        value = datastructure[widget_id]
        vocabulary = self._getVocabulary(datastructure)
        cpsmcat = getToolByName(self, 'translation_service')
        if mode == 'view':
            if not value:
                # XXX L10N empty format may be subject to i18n.
                return self.format_empty
            # XXX customize view mode, lots of displays are possible
            else:
                return self.getEntriesHtml(value, vocabulary, self.translated)
        elif mode == 'edit':
            in_selection = 0
            res = ''
            html_widget_id = self.getHtmlWidgetId()
            render_format = self.render_format
            if render_format not in self.render_formats:
                raise RuntimeError('unknown render format %s' % render_format)
            if render_format == 'select':
                kw = {'name': html_widget_id + ':utf8:ulist',
                      'id': html_widget_id,
                      'multiple': 'multiple',
                      }
                if self.size:
                    kw['size'] = self.size
                res = renderHtmlTag('select', **kw)
            # vocabulary options
            vocabulary_items = vocabulary.items()
            if self.sorted:
                vocabulary_items.sort(key=lambda obj: obj[1].lower())
            for k, v in vocabulary_items:
                if getattr(self, 'translated', None):
                    v = cpsmcat(vocabulary.getMsgid(k, k))
                if render_format == 'select':
                    kw = {'value': k, 'contents': v}
                    if k in value:
                        kw['selected'] = 'selected'
                        in_selection = 1
                    res += renderHtmlTag('option', **kw)
                    res += '\n'
                else:
                    kw = {'id': html_widget_id+'_'+k,
                          'type': render_format,
                          'name': html_widget_id+':list',
                          'value': k,
                          }
                    if k in value:
                        kw['checked'] = 'checked'
                        in_selection = 1
                    res += '<div class="labelledCheckbox">'
		    res += renderHtmlTag('input', **kw)
                    kw = {'for': html_widget_id+'_'+k,
                          'contents': v,
                          }
                    res += renderHtmlTag('label', **kw)
                    res += '</div>\n'
            # invalid selections
            for value_item in value:
                if value_item and value_item not in vocabulary.keys():
                    invalid_contents = '%s %s' % (self._getTranslatedMsgid(
                        cpsmcat, 'label_invalid_selection'), value_item)
                    if render_format == 'select':
                        kw = {'value': value_item,
                              'contents': invalid_contents,
                              'selected': 'selected',
                              }
                        res += renderHtmlTag('option', **kw)
                        res += '\n'
                    else:
                        kw = {'id': html_widget_id+'_'+value_item,
                              'type': render_format,
                              'name': html_widget_id+':list',
                              'value': value_item,
                              'disabled': 'disabled',
                              }
                        res += renderHtmlTag('input', **kw)
                        kw = {'for': html_widget_id+'_'+value_item,
                              'contents': invalid_contents,
                              }
                        res += renderHtmlTag('label', **kw)
                        res += '<br/>\n'
            # default option
            if not self.is_required and not vocabulary.has_key(''):
                if render_format == 'select':
                    kw = {'value': '',
                          'contents': self._getTranslatedMsgid(
                        cpsmcat, 'label_none_selection'),
                          }
                    if not in_selection:
                        kw['selected'] = 'selected'
                    res += renderHtmlTag('option', **kw)
                    res += '\n'
                # not interesting to have a default choice for checkboxes
                elif render_format == 'radio':
                    kw = {'id': html_widget_id+'_empty',
                          'type': render_format,
                          'name': html_widget_id+':list',
                          'value': '',
                          }
                    if not in_selection:
                        kw['checked'] = 'checked'
                    res += renderHtmlTag('input', **kw)
                    kw = {'for': html_widget_id+'_empty',
                          'contents': self._getTranslatedMsgid(
                        cpsmcat, 'label_none_selection'),
                          }
                    res += renderHtmlTag('label', **kw)
                    res += '<br/>\n'
            if render_format == 'select':
                res += '</select>'
            default_tag = renderHtmlTag('input',
                                        type='hidden',
                                        name=html_widget_id+':tokens:default',
                                        value='')
            return default_tag+res
        raise RuntimeError('unknown mode %s' % mode)

InitializeClass(CPSGenericMultiSelectWidget)

class CPSExtendedSelectWidget(CPSSelectWidget):
    """The extended Select widget fires a popup for user selection
    """
    meta_type = 'ExtendedSelect Widget'

    def render(self, mode, datastructure, **kw):
        """Render in mode from datastructure."""

        if mode == 'view':
            return CPSSelectWidget.render(self, mode, datastructure)

        elif mode == 'edit':
            render_method = 'widget_extendedselect_render'

            meth = getattr(self, render_method, None)
            if meth is None:
                raise RuntimeError("Unknown Render Method %s for widget type %s"
                                   % (render_method, self.getId()))
            return meth(mode=mode, datastructure=datastructure,
                        vocabulary=self._getVocabulary(datastructure))

        else:
            raise RuntimeError('unknown mode %s' % mode)

InitializeClass(CPSExtendedSelectWidget)
