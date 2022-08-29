from PySide2.QtWidgets import QGridLayout, QApplication, QWidget, QScrollArea, QAction, QLabel
from PySide2.QtCore import QEvent, Signal, Slot, Qt
from PySide2.QtGui import QImage, QPixmap, QFont
import sys


class ImageViewer(QWidget):

    def __init__(self):
        super().__init__()
        self.scrollArea = QScrollArea(self)
        self.view = QLabel(self)
        self.view.setScaledContents(True)

        self.scrollArea.setWidget(self.view)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.scrollArea.viewport().installEventFilter(self)

        self.layout = QGridLayout(self)
        self.layout.addWidget(self.scrollArea)
        self.setLayout(self.layout)

    def setImage(self, path):
        image = QImage(path)
        self.view.setPixmap(QPixmap.fromImage(image))

    def eventFilter(self, source, event):
        if event.type() == QEvent.MouseMove and source is self.scrollArea.viewport():
            moveEvent = event
            if moveEvent.buttons() == Qt.MiddleButton:
                self.scrollArea.horizontalScrollBar().setValue(self.scrollArea.horizontalScrollBar().value() + (self.panReferenceClick.x() - moveEvent.pos().x()))
                self.scrollArea.verticalScrollBar().setValue(self.scrollArea.verticalScrollBar().value() + (self.panReferenceClick.y() - moveEvent.pos().y()))
                self.panReferenceClick = moveEvent.pos();
        if event.type() == QEvent.MouseButtonPress and source is self.scrollArea.viewport():
            mouseEvent = event
            if mouseEvent.buttons() == Qt.MiddleButton:
                QApplication.setOverrideCursor(Qt.ClosedHandCursor)
                self.panReferenceClick = mouseEvent.pos()
        if event.type() == QEvent.MouseButtonRelease:
            QApplication.restoreOverrideCursor();
        if event.type() == QEvent.Wheel and source is self.scrollArea.viewport():
            wheelEvent = event
            if wheelEvent.angleDelta().y() > 0:
                factor = 1.25
                self.view.setFixedSize(factor*self.view.size())
                self.scrollArea.horizontalScrollBar().setValue(factor*self.scrollArea.horizontalScrollBar().value() + ((factor-1)*self.scrollArea.horizontalScrollBar().pageStep()/2))
                self.scrollArea.verticalScrollBar().setValue(factor*self.scrollArea.verticalScrollBar().value() + ((factor-1)*self.scrollArea.verticalScrollBar().pageStep()/2))
            else:
                factor = 0.8
                self.view.setFixedSize(factor*self.view.size())
                self.scrollArea.horizontalScrollBar().setValue(factor*self.scrollArea.horizontalScrollBar().value() + ((factor-1)*self.scrollArea.horizontalScrollBar().pageStep()/2))
                self.scrollArea.verticalScrollBar().setValue(factor*self.scrollArea.verticalScrollBar().value() + ((factor-1)*self.scrollArea.verticalScrollBar().pageStep()/2))
        return True



def main():
    app = QApplication([])
    widget = ImageViewer()
    widget.setImage("test.jpg")
    widget.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
