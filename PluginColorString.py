# -*- coding: utf-8 -*-

# Copyright (c) 2014 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the 'Color String' tool plug-in.
"""

from __future__ import unicode_literals

import os

from PyQt4.QtCore import QObject, QTranslator
from PyQt4.QtGui import QColor, QColorDialog, QMenu, QDialog

from E5Gui.E5Application import e5App
from E5Gui import E5MessageBox

# Start-Of-Header
name = "Color String Plug-in"
author = "Detlev Offenbach <detlev@die-offenbachs.de>"
autoactivate = True
deactivateable = True
version = "0.2.0"
className = "ColorStringPlugin"
packageName = "ColorString"
shortDescription = "Insert color as string"
longDescription = \
    """This plug-in implements a tool to select a color via a""" \
    """ color selection dialog and insert it as a hex string at the""" \
    """ current cursor position. Selected text is used to initialize""" \
    """ the dialog and is replaced with the new color."""
needsRestart = False
pyqtApi = 2
# End-Of-Header

error = ""


class ColorStringPlugin(QObject):
    """
    Class implementing the 'Color String' tool plug-in.
    """
    def __init__(self, ui):
        """
        Constructor
        
        @param ui reference to the user interface object (UI.UserInterface)
        """
        QObject.__init__(self, ui)
        self.__ui = ui
        
        self.__translator = None
        self.__loadTranslator()
        
        self.__initMenu()
        
        self.__editors = {}
    
    def activate(self):
        """
        Public method to activate this plugin.
        
        @return tuple of None and activation status (boolean)
        """
        global error
        error = ""     # clear previous error
        
        self.__ui.showMenu.connect(self.__populateMenu)
        
        e5App().getObject("ViewManager").editorOpenedEd.connect(
            self.__editorOpened)
        e5App().getObject("ViewManager").editorClosedEd.connect(
            self.__editorClosed)
        
        for editor in e5App().getObject("ViewManager").getOpenEditors():
            self.__editorOpened(editor)
        
        return None, True
    
    def deactivate(self):
        """
        Public method to deactivate this plugin.
        """
        self.__ui.showMenu.disconnect(self.__populateMenu)
        
        e5App().getObject("ViewManager").editorOpenedEd.disconnect(
            self.__editorOpened)
        e5App().getObject("ViewManager").editorClosedEd.disconnect(
            self.__editorClosed)
        
        for editor, acts in self.__editors.items():
            menu = editor.getMenu("Tools")
            if menu is not None:
                for act in acts:
                    menu.removeAction(act)
        self.__editors = {}
    
    def __loadTranslator(self):
        """
        Private method to load the translation file.
        """
        if self.__ui is not None:
            loc = self.__ui.getLocale()
            if loc and loc != "C":
                locale_dir = os.path.join(
                    os.path.dirname(__file__), "ColorString", "i18n")
                translation = "colorstring_{0}".format(loc)
                translator = QTranslator(None)
                loaded = translator.load(translation, locale_dir)
                if loaded:
                    self.__translator = translator
                    e5App().installTranslator(self.__translator)
                else:
                    print("Warning: translation file '{0}' could not be"
                          " loaded.".format(translation))
                    print("Using default.")
    
    def __initMenu(self):
        """
        Private method to initialize the menu.
        """
        self.__menu = QMenu("Color String")
        self.__menu.addAction("Hex Color", self.__selectHexColor)
        self.__menu.addAction("Color Name", self.__selectColorName)
        self.__menu.setEnabled(False)
    
    def __populateMenu(self, name, menu):
        """
        Private slot to populate the tools menu with our entry.
        
        @param name name of the menu (string)
        @param menu reference to the menu to be populated (QMenu)
        """
        if name != "Tools":
            return
        
        if not menu.isEmpty():
            menu.addSeparator()
        menu.addMenu(self.__menu)
    
    def __editorOpened(self, editor):
        """
        Private slot called, when a new editor was opened.
        
        @param editor reference to the new editor (QScintilla.Editor)
        """
        menu = editor.getMenu("Tools")
        if menu is not None:
            self.__editors[editor] = []
            if not menu.isEmpty():
                act = menu.addSeparator()
                self.__editors[editor].append(act)
            act = menu.addMenu(self.__menu)
            self.__menu.setEnabled(True)
            self.__editors[editor].append(act)
    
    def __editorClosed(self, editor):
        """
        Private slot called, when an editor was closed.
        
        @param editor reference to the editor (QScintilla.Editor)
        """
        try:
            del self.__editors[editor]
            if not self.__editors:
                self.__menu.setEnabled(False)
        except KeyError:
            pass
    
    def __isHexString(self, text):
        """
        Private method to check, if a given text is a hex string.
        
        @param text text to check (string)
        @return flag indicating a hex string (boolean)
        """
        isHex = True
        for c in text:
            isHex = isHex and c in "0123456789abcdefABCDEF" 
        return isHex
    
    def __isValidColor(self, name):
        """
        Private method to check for a valid color name.
        
        @param name color name to check (string)
        @return flag indicating a valid color name (boolean)
        """
        try:
            if self.__isHexString(name) and len(name) in [3, 6, 9, 12]:
                return True
            return QColor.isValidColor(name)
        except AttributeError:
            if name.startswith("#"):
                if len(name) not in [4, 7, 10, 13]:
                    return False
                hexCheckStr = name[1:]
                return self.__isHexString(hexCheckStr)
            else:
                if self.__isHexString(name) and len(name) in [3, 6, 9, 12]:
                    return True
                return name in QColor.colorNames()
    
    def __selectHexColor(self):
        """
        Private slot implementing the hex color string selection.
        """
        editor = e5App().getObject("ViewManager").activeWindow()
        if editor is None:
            return
        
        if editor.hasSelectedText():
            currColor = editor.selectedText()
            if not self.__isValidColor(currColor):
                E5MessageBox.critical(
                    self.__ui,
                    self.trUtf8("Color String"),
                    self.trUtf8(
                        """<p>The selected string <b>{0}</b> is not a""" \
                        """ valid color string. Aborting!</p>""")
                    .format(currColor))
                return
            
            if currColor.startswith("#"):
                withHash = True
            elif self.__isHexString(currColor):
                withHash = False
                currColor = "#" + currColor
            else:
                withHash = True
            initColor = QColor(currColor)
        else:
            withHash = True
            currColor = ""
            initColor = QColor()
        
        color = QColorDialog.getColor(
            initColor, self.__ui, self.tr("Color String"))
        if color.isValid():
            colorStr = color.name()
            if not withHash:
                colorStr = colorStr[1:]
            editor.beginUndoAction()
            if editor.hasSelectedText():
                editor.replaceSelectedText(colorStr)
            else:
                line, index = editor.getCursorPosition()
                editor.insert(colorStr)
                editor.setCursorPosition(line, index + len(colorStr))
            editor.endUndoAction()
    
    def __selectColorName(self):
        """
        Private slot implementing the named color string selection.
        """
        editor = e5App().getObject("ViewManager").activeWindow()
        if editor is None:
            return
        
        if editor.hasSelectedText():
            currColor = editor.selectedText()
            if currColor not in QColor.colorNames():
                E5MessageBox.critical(
                    self.__ui,
                    self.trUtf8("Color String"),
                    self.trUtf8(
                        """<p>The selected string <b>{0}</b> is not a""" \
                        """ valid color name. Aborting!</p>""")
                    .format(currColor))
                return
        else:
            currColor = ""
        
        from ColorString.ColorSelectionDialog import ColorSelectionDialog
        dlg = ColorSelectionDialog(currColor, self.__ui)
        if dlg.exec_() == QDialog.Accepted:
            colorStr = dlg.getColor()
            editor.beginUndoAction()
            if editor.hasSelectedText():
                editor.replaceSelectedText(colorStr)
            else:
                line, index = editor.getCursorPosition()
                editor.insert(colorStr)
                editor.setCursorPosition(line, index + len(colorStr))
            editor.endUndoAction()
