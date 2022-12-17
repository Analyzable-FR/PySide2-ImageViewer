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


from PySide2.QtWidgets import QOpenGLWidget, QUndoStack, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QApplication, QWidget, QScrollArea, QAction, QLabel
from PySide2.QtCore import QEvent, Signal, Slot, Qt, QPoint
from PySide2.QtGui import QImage, QPixmap, QFont, QPainter, QPen, QCursor, QKeySequence
import rc_resources


class ImageViewer(QGraphicsView):

    def __init__(self):
        super().__init__()

        self.setMouseTracking(False)
        self.setViewport(QOpenGLWidget())
        self.setAcceptDrops(True)

        self.undoAction = QAction(self, self.tr("Undo"))
        self.undoAction.setShortcut(QKeySequence(QKeySequence.Undo))
        self.undoAction.triggered.connect(self.undo)
        self.addAction(self.undoAction)
        self.painterStack = []

        self.scene = QGraphicsScene(self)
        self.image = QGraphicsPixmapItem()
        self.image.setAcceptDrops(True)
        self.scene.addItem(self.image)
        self.setScene(self.scene)
        self.setTransformationAnchor(QGraphicsView.AnchorViewCenter)
        self.setDragMode(QGraphicsView.NoDrag)

        self.currentZoom = 1

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
        self.drawingCursor = QCursor(
            self.brushPixmap.scaledToHeight(self.brushSize*factor))

    def setImage(self, path):
        '''
        Open an image from a file.
        '''
        self.clear()
        self.image.setPixmap(QPixmap(path))

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
        event.accept()
        super().wheelEvent(event)

    def mousePressEvent(self, event):
        '''
        Pan with middle click, draw with left, change brush size with CTRL + left click + horizontal drag.
        '''
        if event.buttons() == Qt.MiddleButton:  # Get pan coordinates reference with middle click
            QApplication.setOverrideCursor(Qt.ClosedHandCursor)
            self.panReferenceClick = event.pos()
        # Get coordinates reference for brush size
        elif event.buttons() == Qt.LeftButton and event.modifiers() == Qt.ControlModifier:
            # Cursor will be drawed below. TO DO need refactoring.
            self.brushReference = event.pos()
        if event.buttons() == Qt.LeftButton:  # Get drawing coordinates reference with left click
            QApplication.setOverrideCursor(self.drawingCursor)
            self.drawReference = self.mapToScene(event.pos())
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        QApplication.restoreOverrideCursor()
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        '''
        Pan with middle click, draw with left, change brush size with CTRL + left click + horizontal drag.
        '''
        if event.buttons() == Qt.MiddleButton:  # pan with middle click pressed
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() +
                                                (self.panReferenceClick.x() - event.pos().x()))
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() +
                                              (self.panReferenceClick.y() - event.pos().y()))
            self.panReferenceClick = event.pos()
        elif event.buttons() == Qt.LeftButton and event.modifiers() == Qt.ControlModifier:
            if event.pos().x() - self.brushReference.x() > 25:
                self.brushSize += 5
                self.setBrush(size=self.brushSize, factor=self.currentZoom)
                self.cursor().setPos(self.mapToGlobal(self.brushReference))
                QApplication.restoreOverrideCursor()
                QApplication.setOverrideCursor(self.drawingCursor)
            elif event.pos().x() - self.brushReference.x() < -25:
                self.brushSize -= 5
                self.setBrush(size=max(self.brushSize, 5),
                              factor=self.currentZoom)
                self.cursor().setPos(self.mapToGlobal(self.brushReference))
                QApplication.restoreOverrideCursor()
                QApplication.setOverrideCursor(self.drawingCursor)

        if event.buttons() == Qt.LeftButton and self.isDrawable and event.modifiers() == Qt.NoModifier:  # Draw with left click pressed
            pixmap = self.image.pixmap()
            self.painter.begin(pixmap)
            self.painter.setPen(
                QPen(self.brushColor, self.brushSize, Qt.SolidLine, Qt.RoundCap))
            self.painter.drawLine(self.drawReference,
                                  self.mapToScene(event.pos()))
            self.drawReference = self.mapToScene(event.pos())
            self.addToUndoStack()
            self.painter.end()
            self.image.setPixmap(pixmap)
        super().mouseMoveEvent(event)

    def addToUndoStack(self):
        if len(self.painterStack) > 40:  # Avoid high memory usage
            self.painterStack = [j for i, j in enumerate(
                self.painterStack) if i % 2 == 0]
        self.painterStack.append(self.image.pixmap())

    def undo(self):
        '''
        Undo drawing.
        '''
        if self.painterStack:
            self.image.setPixmap(self.painterStack.pop())

    def clear(self):
        self.image.setPixmap(QPixmap())
        self.painterStack.clear()

    def dropEvent(self, event):
        mimeData = event.mimeData()
        if mimeData.hasUrls():
            self.setImage(mimeData.urls()[0].toLocalFile())

    def dragEnterEvent(self, event):
        event.acceptProposedAction()
