/*
 * FCKeditor - The text editor for internet
 * Copyright (C) 2003-2005 Frederico Caldeira Knabben
 *
 * Licensed under the terms of the GNU Lesser General Public License:
 *		http://www.opensource.org/licenses/lgpl-license.php
 *
 * For further information visit:
 *		http://www.fckeditor.net/
 *
 * "Support Open Source software. What about a donation today?"
 *
 * File Name: fckconfig.js
 *	Editor configuration settings.
 *	See the documentation for more info.
 *
 * File Authors:
 *		Frederico Caldeira Knabben (fredck@fckeditor.net)
 *
 * Zope + Plone2 adaptation : Jean-mat Grimaldi - jean-mat@macadames.com
 *
 * $Id$
 */

FCKConfig.Debug = false;

// basepath example for other Zope Implementation
// FCKConfig.BasePath = document.location.protocol + '//' + document.location.host + document.location.pathname.substring(0,document.location.pathname.lastIndexOf('/')+1) ;

FCKConfig.CustomConfigurationsPath = '' ;

// Style File to be used in the editable area for Plone (plone.css or ploneCustom.css ...)
// FCKConfig.EditorAreaCSS = FCKConfig.BasePath + 'css/fck_editorarea.css' ;
FCKConfig.EditorAreaCSS = FCKConfig.BasePath + 'fckeditor_wysiwyg.css' ;

FCKConfig.DocType = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">';

FCKConfig.BaseHref = '' ;

// don't use true with plone
FCKConfig.FullPage = false ;

// Set the path for the skin files to use.
// Change for Zope CMF because 'skins'is a folder name reserved
FCKConfig.SkinPath = FCKConfig.BasePath + 'fck_skins/default/' ;

FCKConfig.PluginsPath = FCKConfig.BasePath + 'plugins/' ;

//FCKConfig.Plugins.Add('placeholder', 'en,it');
FCKConfig.Plugins.Add('semantic', 'en,fr');

// You can protect specific tags in source like script tags
// using a reg exp
FCKConfig.ProtectedSource.Add( /<script[\s\S]*?\/script>/gi ) ;	// <SCRIPT> tags.
// FCKConfig.ProtectedSource.Add( /<\?[\s\S]*?\?>/g ) ;	// PHP style server side code <?...?>

FCKConfig.AutoDetectLanguage	= true ;
FCKConfig.DefaultLanguage		= 'en' ;
FCKConfig.ContentLangDirection	= 'ltr' ;

FCKConfig.EnableXHTML		= true ;	// Unsupported: Do not change.
FCKConfig.EnableSourceXHTML	= true ;	// Unsupported: Do not change.

FCKConfig.ProcessHTMLEntities	= true ;
FCKConfig.IncludeLatinEntities	= false ;
FCKConfig.IncludeGreekEntities	= true ;

FCKConfig.FillEmptyBlocks	= true ;

FCKConfig.FormatSource		= true ;
FCKConfig.FormatOutput		= true ;
FCKConfig.FormatIndentator	= '    ' ;

FCKConfig.ForceStrongEm = true ;
FCKConfig.GeckoUseSPAN	= false ;
FCKConfig.StartupFocus	= false ;
FCKConfig.ForcePasteAsPlainText	= false ;
FCKConfig.AutoDetectPasteFromWord = true ;	// IE only.
FCKConfig.ForceSimpleAmpersand	= false ;
FCKConfig.TabSpaces		= 0 ;
FCKConfig.ShowBorders	= true ;
FCKConfig.UseBROnCarriageReturn	= false ;
FCKConfig.ToolbarStartExpanded	= true ;
FCKConfig.ToolbarCanCollapse	= true ;
FCKConfig.IEForceVScroll = false ;
FCKConfig.IgnoreEmptyParagraphValue = true ;

FCKConfig.ToolbarSets["Default"] = [
	['Source','DocProps','-','Save','NewPage','Preview','-','Templates'],
	['Cut','Copy','Paste','PasteText','PasteWord','-','Print','SpellCheck'],
	['Undo','Redo','-','Find','Replace','-','SelectAll','RemoveFormat'],
	['Bold','Italic','Underline','StrikeThrough','-','Subscript','Superscript'],
	['OrderedList','UnorderedList','-','Outdent','Indent'],
	['JustifyLeft','JustifyCenter','JustifyRight','JustifyFull'],
	['Link','Unlink','Anchor'],
	['Image','Flash','Table','Rule','Smiley','SpecialChar','PageBreak','UniversalKey'],
	['Form','Checkbox','Radio','TextField','Textarea','Select','Button','ImageButton','HiddenField'],
	'/',
	['Style','FontFormat','FontName','FontSize'],
	['TextColor','BGColor'],
	['About']
] ;


// toolbars for plone
// use SmallZopeCmf for small textarea form input (example : a rich description)

FCKConfig.ToolbarSets["ZopeCmf"] = [
	['Source','DocProps','-','Preview','-','Templates'],
	['Cut','Copy','Paste','PasteText','PasteWord','-','Print','SpellCheck'],
	['Undo','Redo','-','Find','Replace','-','SelectAll','RemoveFormat'],
	['Bold','Italic','Underline','StrikeThrough','-','Subscript','Superscript'],
	['OrderedList','UnorderedList','-','Outdent','Indent'],
	['JustifyLeft','JustifyCenter','JustifyRight','JustifyFull'],
	['Link','Unlink','Anchor'],
	['Image','Flash','Table','Rule','SpecialChar','PageBreak','Smiley','UniversalKey'],
	['Form','Checkbox','Radio','TextField','Textarea','Select','Button','ImageButton','HiddenField'],
	'/',
	['Style','FontFormat','FontName','FontSize'],
	['TextColor','BGColor'],
	['About']
] ;

FCKConfig.ToolbarSets["SmallZopeCmf"] = [
	['Source','-','Preview'],
	['Cut','Copy','Paste','PasteText','PasteWord'],
	['Undo','Redo','SelectAll','RemoveFormat'],
	['Bold','Italic','Underline','StrikeThrough','-','Subscript','Superscript'],
	['OrderedList','UnorderedList','-','Outdent','Indent'],
	['JustifyLeft','JustifyCenter','JustifyRight','JustifyFull'],
	['Link','Unlink'],
	['Image','Flash','Table','Rule','SpecialChar','Smiley','UniversalKey'],
	['Style','FontFormat','FontName','FontSize'],
	['TextColor','BGColor'],
	['About']
] ;

// The semantic toolbar using the "semantic" plugin
FCKConfig.ToolbarSets['Semantic'] = [
    ['Italic','Bold','Lang','Abbr','Acronym','Cite','Q','Style'],
    ['-','OrderedList','UnorderedList','-','Link','Unlink'],
    '/',
    ['RemoveFormat','Undo','Redo','Source']
] ;

// The semantic toolbar without the "semantic" plugin
// FCKConfig.ToolbarSets['Semantic'] = [
//     ['Italic','Bold','Style','-','OrderedList','UnorderedList','-','Link','Unlink','-','Style'],
//     ['RemoveFormat','Undo','Redo','Source']
// ] ;

FCKConfig.ToolbarSets["Basic"] = [
	['Bold','Italic','-','OrderedList','UnorderedList','-','Link','Unlink','-','About']
] ;

FCKConfig.ContextMenu = ['Generic','Link','Anchor','Image','Flash','Select','Textarea','Checkbox','Radio','TextField','HiddenField','ImageButton','Button','BulletedList','NumberedList','TableCell','Table','Form'] ;

FCKConfig.FontColors = '000000,993300,333300,003300,003366,000080,333399,333333,800000,FF6600,808000,808080,008080,0000FF,666699,808080,FF0000,FF9900,99CC00,339966,33CCCC,3366FF,800080,999999,FF00FF,FFCC00,FFFF00,00FF00,00FFFF,00CCFF,993366,C0C0C0,FF99CC,FFCC99,FFFF99,CCFFCC,CCFFFF,99CCFF,CC99FF,FFFFFF' ;

FCKConfig.FontNames		= 'Arial, Geneva, Helvetica, Helv, sans-serif;Verdana, Arial, Helvetica, sans-serif;Tahoma, Arial, Helvetica, sans-serif;Trebuchet MS, Arial, Helvetica, sans-serif;Comic Sans MS, Arial, Helvetica, sans-serif;Garamond, Times New Roman, Times, Serif;Times New Roman, Times, Roman, Serif;Courier New, Courier;Letter Gothic, LetterGothic, Courier New, Courier;Lucida Console, Courier New, Courier' ;
FCKConfig.FontSizes		= '1/xx-small;2/x-small;3/small;4/medium;5/large;6/x-large;7/xx-large' ;
FCKConfig.FontFormats	= 'p;div;pre;address;h1;h2;h3;h4;h5;h6' ;

//FCKConfig.StylesXmlPath		= FCKConfig.EditorPath + 'fckstyles.xml' ;
FCKConfig.StylesXmlPath		= FCKConfig.EditorPath + 'fckstyles-cps.xml' ;
FCKConfig.TemplatesXmlPath	= FCKConfig.EditorPath + 'fcktemplates.xml' ;

FCKConfig.SpellChecker			= 'SpellerPages' ;	// 'ieSpell' | 'SpellerPages'
FCKConfig.IeSpellDownloadUrl	= 'http://www.iespell.com/rel/ieSpellSetup211325.exe' ;

FCKConfig.MaxUndoLevels = 15 ;

FCKConfig.DisableImageHandles = false ;
FCKConfig.DisableTableHandles = false ;

FCKConfig.LinkDlgHideTarget		= false ;
FCKConfig.LinkDlgHideAdvanced	= false ;

FCKConfig.ImageDlgHideLink		= false ;
FCKConfig.ImageDlgHideAdvanced	= false ;

FCKConfig.FlashDlgHideAdvanced	= false ;

FCKConfig.LinkBrowser = false;
// simple dtml-tree browser compatible with all zope cms
// you can set advanced browser capabilities in wysiwyg templates support (fckeditor_wysiwyg_support for Plone, popup_rte_form for CPS)
// or you can change it here (uncomment 2nd next line)
FCKConfig.LinkBrowserURL = FCKConfig.BasePath + "fck_browse_files.html" ;
//FCKConfig.LinkBrowserURL = "/editor/filemanager/browser/zope/browser.html?Connector=connectors/connectorPlone&ServerPath=/&CurrentPath=" + FCKConfig.BasePath ;
//FCKConfig.LinkBrowserURL = "/editor/filemanager/browser/zope/browser.html?Connector=connectors/connectorCPS&ServerPath=/&CurrentPath=" + FCKConfig.BasePath ;
FCKConfig.LinkBrowserWindowWidth	= FCKConfig.ScreenWidth * 0.7 ;	// 70%
FCKConfig.LinkBrowserWindowHeight	= FCKConfig.ScreenHeight * 0.7 ;// 70%

FCKConfig.ImageBrowser = false ;
FCKConfig.ImageBrowserURL = FCKConfig.BasePath + "fck_browse_images.html" ;
//FCKConfig.ImageBrowserURL = "/editor/filemanager/browser/zope/browser.html?Type=Image&Connector=connectors/connectorPlone&ServerPath=/&CurrentPath=" + FCKConfig.BasePath ;
//FCKConfig.ImageBrowserURL = "/editor/filemanager/browser/zope/browser.html?Type=Image&Connector=connectors/connectorCPS&ServerPath=/&CurrentPath=" + FCKConfig.BasePath ;
FCKConfig.ImageBrowserWindowWidth  = FCKConfig.ScreenWidth * 0.7 ;	// 70% ;
FCKConfig.ImageBrowserWindowHeight = FCKConfig.ScreenHeight * 0.7 ;	// 70% ;

FCKConfig.FlashBrowser = true ;
FCKConfig.FlashBrowserURL = FCKConfig.BasePath + "fck_browse_files.html" ;
// FCKConfig.FlashBrowserURL = "/editor/filemanager/browser/zope/browser.html?Type=Flash&Connector=connectors/connectorPlone&ServerPath=/&CurrentPath=" + FCKConfig.BasePath ;
// FCKConfig.FlashBrowserURL = "/editor/filemanager/browser/zope/browser.html?Type=Flash&Connector=connectors/connectorCPS&ServerPath=/&CurrentPath=" + FCKConfig.BasePath ;
FCKConfig.FlashBrowserWindowWidth  = FCKConfig.ScreenWidth * 0.7 ;	//70% ;
FCKConfig.FlashBrowserWindowHeight = FCKConfig.ScreenHeight * 0.7 ;	//70% ;

// rapid upload activation
// called by fckeditor_wysiwyg_support for Plone

FCKConfig.LinkUpload = false ;
FCKConfig.LinkUploadAllowedExtensions	= "" ;			// empty for all
FCKConfig.LinkUploadDeniedExtensions	= ".(php|php3|php5|phtml|asp|aspx|ascx|jsp|cfm|cfc|pl|bat|exe|dll|reg|cgi)$" ;	// empty for no one

FCKConfig.ImageUpload = false ;
FCKConfig.ImageUploadAllowedExtensions	= ".(jpg|gif|jpeg|png)$" ;		// empty for all
FCKConfig.ImageUploadDeniedExtensions	= "" ;							// empty for no one

FCKConfig.FlashUpload = false ;
FCKConfig.FlashUploadAllowedExtensions	= ".(swf|fla)$" ;		// empty for all
FCKConfig.FlashUploadDeniedExtensions	= "" ;					// empty for no one

FCKConfig.SmileyPath	= FCKConfig.BasePath + 'images/smiley/msn/' ;
FCKConfig.SmileyImages	= ['regular_smile.gif','sad_smile.gif','wink_smile.gif','teeth_smile.gif','confused_smile.gif','tounge_smile.gif','embaressed_smile.gif','omg_smile.gif','whatchutalkingabout_smile.gif','angry_smile.gif','angel_smile.gif','shades_smile.gif','devil_smile.gif','cry_smile.gif','lightbulb.gif','thumbs_down.gif','thumbs_up.gif','heart.gif','broken_heart.gif','kiss.gif','envelope.gif'] ;
FCKConfig.SmileyColumns = 8 ;
FCKConfig.SmileyWindowWidth		= 320 ;
FCKConfig.SmileyWindowHeight	= 240 ;

if( window.console ) window.console.log( 'Config is loaded!' ) ;	// @Packager.Compactor.RemoveLine
