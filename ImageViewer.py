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


from PySide2.QtWidgets import QOpenGLWidget, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QApplication, QWidget, QScrollArea, QAction, QLabel
from PySide2.QtCore import QEvent, Signal, Slot, Qt, QPoint
from PySide2.QtGui import QImage, QPixmap, QFont, QPainter, QPen, QCursor
import rc_resources



class ImageViewer(QGraphicsView):

    def __init__(self):
        super().__init__()

        self.setMouseTracking(True);
        self.setViewport(QOpenGLWidget())

        self.scene = QGraphicsScene(self)
        self.image = QGraphicsPixmapItem()
        self.scene.addItem(self.image)
        self.setScene(self.scene)
        self.setTransformationAnchor(QGraphicsView.AnchorViewCenter)
        self.setDragMode(QGraphicsView.NoDrag)

        self.currentZoom = 1

        self.pixmap = None
        self.isDrawable = True
        self.brushPixmap = QPixmap(":/assets/cursor.png")
        self.setBrush()

        self.painter = QPainter()

    def setBrush(self, color=Qt.white, size=25, factor=1):
        '''
        Set the brush color and size. The cursor is scalled with the current zoom.
        '''
        self.brushColor = color
        self.brushSize = size
        self.drawingCursor = QCursor(self.brushPixmap.scaledToHeight(self.brushSize*factor))

    def setImage(self, path):
        '''
        Open an image from a file.
        '''
        self.pixmap = QPixmap(path)
        self.painter = QPainter(self.pixmap)
        self.image.setPixmap(self.pixmap)

    def wheelEvent(self, event):
        '''
        Zoom with wheel.
        '''
        if event.angleDelta().y() > 0:
            factor = 1.25
            self.currentZoom *= factor
            self.setBrush(size=self.brushSize, factor=self.currentZoom)
        else:
            factor = 0.8
            self.currentZoom *= factor
            self.setBrush(size=self.brushSize, factor=self.currentZoom)
        self.scale(factor, factor)

    def mousePressEvent(self, event):
        '''
        Pan with middle click, draw with left, change brush size with CTRL + left click + horizontal drag.
        '''
        if event.buttons() == Qt.MiddleButton: # Get pan coordinates reference with middle click
            QApplication.setOverrideCursor(Qt.ClosedHandCursor)
            self.panReferenceClick = event.pos()
        elif event.buttons() == Qt.LeftButton and event.modifiers() == Qt.ControlModifier: # Get coordinates reference for brush size
            self.brushReference = event.pos() # Cursor will be drawed below. TO DO need refactoring.
        if event.buttons() == Qt.LeftButton: # Get drawing coordinates reference with left click
            QApplication.setOverrideCursor(self.drawingCursor)
            self.drawReference = self.mapToScene(event.pos())

    def mouseReleaseEvent(self, event):
        QApplication.restoreOverrideCursor();

    def mouseMoveEvent(self, event):
        '''
        Pan with middle click, draw with left, change brush size with CTRL + left click + horizontal drag.
        '''
        if event.buttons() == Qt.MiddleButton: # pan with middle click pressed
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + (self.panReferenceClick.x() - event.pos().x()))
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() + (self.panReferenceClick.y() - event.pos().y()))
            self.panReferenceClick = event.pos();
        elif event.buttons() == Qt.LeftButton and event.modifiers() == Qt.ControlModifier:
            if event.pos().x() - self.brushReference.x() > 25:
                self.brushSize += 5
                self.setBrush(size=self.brushSize, factor=self.currentZoom)
                self.cursor().setPos(self.mapToGlobal(self.brushReference))
                QApplication.restoreOverrideCursor();
                QApplication.setOverrideCursor(self.drawingCursor)
            elif event.pos().x() - self.brushReference.x() <  -25:
                self.brushSize -= 5
                self.setBrush(size=max(self.brushSize, 5), factor=self.currentZoom)
                self.cursor().setPos(self.mapToGlobal(self.brushReference))
                QApplication.restoreOverrideCursor();
                QApplication.setOverrideCursor(self.drawingCursor)

        if event.buttons() == Qt.LeftButton and self.isDrawable and event.modifiers() == Qt.NoModifier: # Draw with left click pressed
            self.painter.setPen(QPen(self.brushColor, self.brushSize, Qt.SolidLine, Qt.RoundCap))
            self.painter.drawLine(self.drawReference, self.mapToScene(event.pos()))
            self.drawReference = self.mapToScene(event.pos())
            self.image.setPixmap(self.pixmap)
