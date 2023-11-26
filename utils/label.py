import sys

from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QLineEdit, QPushButton, QWidget, QListWidget
from PyQt5.QtCore import Qt, pyqtSignal


class labelDialog(QtWidgets.QDialog):
    label = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.title = "Edit Label"
        self.top = 100
        self.left = 100
        self.width = 800
        self.height = 800
        self.initWindow()

    def initWindow(self):
        self.setWindowTitle(self.title)
        vbox = QVBoxLayout()
        # self.label = QLabel(self)
        self.lineedit = QLineEdit(self)
        # self.lineedit.returnPressed.connect(self.onPressed)
        self.lineedit.setFont(QtGui.QFont("Sanserif", 12))
        vbox.addWidget(self.lineedit)

        # Labels
        self.lableList = QListWidget(self)
        self.lableList.itemClicked.connect(self.clickList)
        # self.lableList.addItems([str(i) for i in range(20)])
        vbox.addWidget(self.lableList)
        # Buttons
        buttonswidget = QWidget(self)
        hbox = QHBoxLayout(self)
        self.okButton = QPushButton('OK')
        self.okButton.clicked.connect(self.saveLabel)
        self.cancelButton = QPushButton('Cancel')
        self.cancelButton.clicked.connect(self.closeDialog)
        hbox.addWidget(self.okButton)
        hbox.addWidget(self.cancelButton)
        buttonswidget.setLayout(hbox)

        vbox.addWidget(buttonswidget)
        self.setLayout(vbox)
        # self.show()

    def saveLabel(self):
        text = self.lineedit.text()
        self.label.emit(text)
        self.close()

    def clickList(self):
        row = self.lableList.currentItem().text()
        self.lineedit.setText(row)

    def closeDialog(self):
        self.label.emit(None)
        self.close()

    def keyPressEvent(self, event):
        super(labelDialog, self).keyPressEvent(event)
        if event.key() == Qt.Key_Escape:
            self.closeDialog()
        if event.key() == Qt.Key_Return:
            self.saveLabel()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = labelDialog()
    window.show()
    sys.exit(app.exec_())
