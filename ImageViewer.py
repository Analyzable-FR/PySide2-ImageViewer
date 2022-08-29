'''
MIT License

Copyright (c) 2022 Analyzable

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''


from PySide2.QtWidgets import QGridLayout, QApplication, QWidget, QScrollArea, QAction, QLabel
from PySide2.QtCore import QEvent, Signal, Slot, Qt, QPoint
from PySide2.QtGui import QImage, QPixmap, QFont, QPainter, QPen, QCursor
import rc_resources


class ImageViewer(QWidget):

    def __init__(self):
        super().__init__()

        self.setMouseTracking(True);

        self.view = QLabel(self)
        self.view.installEventFilter(self)
        self.view.setScaledContents(True)

        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidget(self.view)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.scrollArea.viewport().installEventFilter(self)
        self.currentZoom = 1

        self.layout = QGridLayout(self)
        self.layout.addWidget(self.scrollArea)
        self.setLayout(self.layout)

        self.pixmap = None
        self.isDrawable = True
        self.setBrush()

    def setBrush(self, color=Qt.white, size=25, factor=1):
        '''
        Set the brush color and size. The cursor is scalled with the current zoom.
        '''
        self.brushColor = color
        self.brushSize = size
        self.drawingCursor = QCursor(QPixmap(":/assets/cursor.png").scaledToHeight(self.brushSize*factor))

    def setImage(self, path):
        '''
        Open an image from a file.
        '''
        self.pixmap = QPixmap(path)
        self.view.setPixmap(self.pixmap)

    def eventFilter(self, source, event):
        if event.type() == QEvent.MouseButtonPress:
            mouseEvent = event
            if source is self.scrollArea.viewport():
                if mouseEvent.buttons() == Qt.MiddleButton: # Get pan coordinates reference with middle click
                    QApplication.setOverrideCursor(Qt.ClosedHandCursor)
                    self.panReferenceClick = mouseEvent.pos()
            if source is self.view:
                if mouseEvent.buttons() == Qt.LeftButton: # Get drawing coordinates reference with left click
                    QApplication.setOverrideCursor(self.drawingCursor)
                    self.drawReference = QPoint((event.pos().x()*self.view.pixmap().size().width())/self.view.size().width(), (event.pos().y()*self.view.pixmap().size().height())/self.view.size().height())
            return False

        if event.type() == QEvent.MouseMove:
            moveEvent = event
            if source is self.scrollArea.viewport():
                if moveEvent.buttons() == Qt.MiddleButton: # pan with middle click pressed
                    self.scrollArea.horizontalScrollBar().setValue(self.scrollArea.horizontalScrollBar().value() + (self.panReferenceClick.x() - moveEvent.pos().x()))
                    self.scrollArea.verticalScrollBar().setValue(self.scrollArea.verticalScrollBar().value() + (self.panReferenceClick.y() - moveEvent.pos().y()))
                    self.panReferenceClick = moveEvent.pos();
            elif source is self.view:
                if moveEvent.buttons() == Qt.LeftButton and self.isDrawable: # Draw with left click pressed
                    painter = QPainter(self.pixmap)
                    painter.setPen(QPen(self.brushColor, self.brushSize, Qt.SolidLine, Qt.RoundCap))
                    painter.drawLine(self.drawReference, QPoint((event.pos().x()*self.view.pixmap().size().width())/self.view.size().width(), (event.pos().y()*self.view.pixmap().size().height())/self.view.size().height()))
                    self.drawReference = QPoint((event.pos().x()*self.view.pixmap().size().width())/self.view.size().width(), (event.pos().y()*self.view.pixmap().size().height())/self.view.size().height())
                    self.view.setPixmap(self.pixmap)
            return False

        if event.type() == QEvent.MouseButtonRelease: # Reset default cursor
            QApplication.restoreOverrideCursor();
            return True

        if event.type() == QEvent.Wheel and source is self.scrollArea.viewport(): # Zoom with mouse wheel
            wheelEvent = event
            if wheelEvent.angleDelta().y() > 0:
                factor = 1.25
                self.currentZoom *= factor
                self.setBrush(factor=self.currentZoom)
                self.view.setFixedSize(factor*self.view.size())
                self.scrollArea.horizontalScrollBar().setValue(factor*self.scrollArea.horizontalScrollBar().value() + ((factor-1)*self.scrollArea.horizontalScrollBar().pageStep()/2))
                self.scrollArea.verticalScrollBar().setValue(factor*self.scrollArea.verticalScrollBar().value() + ((factor-1)*self.scrollArea.verticalScrollBar().pageStep()/2))
            else:
                factor = 0.8
                self.currentZoom *= factor
                self.setBrush(factor=self.currentZoom)
                self.view.setFixedSize(factor*self.view.size())
                self.scrollArea.horizontalScrollBar().setValue(factor*self.scrollArea.horizontalScrollBar().value() + ((factor-1)*self.scrollArea.horizontalScrollBar().pageStep()/2))
                self.scrollArea.verticalScrollBar().setValue(factor*self.scrollArea.verticalScrollBar().value() + ((factor-1)*self.scrollArea.verticalScrollBar().pageStep()/2))
            return True
        return super(ImageViewer, self).eventFilter(source, event)
