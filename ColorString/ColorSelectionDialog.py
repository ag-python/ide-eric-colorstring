# -*- coding: utf-8 -*-

# Copyright (c) 2014 - 2015 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to select a color by name.
"""

from PyQt5.QtGui import QColor, QPixmap, QIcon
from PyQt5.QtWidgets import QDialog

from .Ui_ColorSelectionDialog import Ui_ColorSelectionDialog


class ColorSelectionDialog(QDialog, Ui_ColorSelectionDialog):
    """
    Class implementing a dialog to select a color by name.
    """
    def __init__(self, selectedName="", parent=None):
        """
        Constructor
        
        @param selectedName name of the color to be selected initially
            (string)
        @param parent reference to the parent widget (QWidget)
        """
        super().__init__(parent)
        self.setupUi(self)
        
        for colorName in QColor.colorNames():
            px = QPixmap(22, 22)    # icon size 22x22 pixels
            px.fill(QColor(colorName))
            self.colorComboBox.addItem(QIcon(px), colorName)
        if selectedName:
            self.colorComboBox.setCurrentIndex(
                self.colorComboBox.findText(selectedName))
        
        msh = self.minimumSizeHint()
        self.resize(max(self.size().width(), msh.width()), msh.height())
    
    def getColor(self):
        """
        Public method to retrieve the selected color name.
        
        @return color name (string)
        """
        return self.colorComboBox.currentText()
