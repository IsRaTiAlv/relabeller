from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QSlider, QLabel
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QPushButton
import sys


class Slider(QMainWindow):
    change = QtCore.pyqtSignal(list)

    def __init__(self, id, label):
        super().__init__()
        title = "Paint Application"
        self.setWindowTitle(title)

        # def create(self, name, label):
        self.label = label
        self.id = id
        self.hbox = QHBoxLayout()
        self.vbox = QVBoxLayout()
        self.text_label = QLabel(self.label)
        self.reset_button = QPushButton('Reset', self)
        self.slider = QSlider(self)
        self.slider.setOrientation(QtCore.Qt.Horizontal)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickPosition(QSlider.NoTicks)
        self.slider.setTickInterval(10)
        # self.slider.setSingleStep(10)
        if id == 'imgs':
            self.slider.setMaximum(500)
            self.slider.setMinimum(0)

        if id == 'imgb':
            self.slider.setMaximum(100)
            self.slider.setMinimum(-100)

        if id == 'cursor':
            self.slider.setMaximum(50)
            self.slider.setMinimum(5)
            self.slider.setValue(15)
        if id == 'labelb':
            self.slider.setMaximum(100)
            self.slider.setMinimum(-100)

        if id == 'segments':
            self.slider.setSingleStep(20)
            self.slider.setMaximum(500)
            self.slider.setMinimum(20)
            self.slider.setValue(200)

        if id == 'compactness':
            self.slider.setMaximum(100)
            self.slider.setMinimum(1)
            self.slider.setSingleStep(10)
            self.slider.setValue(20)

        self.changeLabel(self.slider.value())
        self.slider.valueChanged[int].connect(self.changeValue)
        # self.hbox.addWidget(self.text_label)
        # self.hbox.addWidget(self.reset_button)
        # self.vbox.addLayout(self.hbox)
        self.vbox.addWidget(self.text_label)
        self.vbox.addWidget(self.slider)
        self.vbox.setContentsMargins(5, 0, 5, 0)
        self.widget = QWidget(self)
        self.widget.setFixedWidth(200)
        # widget.resize(10, 2)
        self.widget.setLayout(self.vbox)
        # return self.widget

    def changeValue(self, value):
        self.changeLabel(value)
        self.change.emit([self.id, value])
        # print((f'{self.label}: {str(value)} %'))

    def setValue(self, value):
        self.changeLabel(value)
        self.slider.setValue(value)

    def changeLabel(self, value):
        if self.id == 'segments' or self.id == 'compactness':
            self.text_label.setText(f'{self.label}: {str(value)}')
        elif self.id == ' cursor':
            self.text_label.setText(f'{self.label}: {str(value)} px')
        else:
            self.text_label.setText(f'{self.label}: {str(value)} %')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Slider()
    window.show()
    sys.exit(app.exec_())
