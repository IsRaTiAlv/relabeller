from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QListWidget, QScrollArea, QComboBox, QRadioButton, QVBoxLayout, QGroupBox, QPushButton, QWidget, QGridLayout, QLabel, QTabWidget, QApplication, QFormLayout, QLineEdit
import sys
import logging


class confTab(QTabWidget):
    updatedConf = pyqtSignal(dict)

    def __init__(self, confInfo=None):
        super().__init__()
        self.setWindowModality(Qt.ApplicationModal)

        self.lname = QLabel()
        self.linput = QLabel()
        self.loutput = QLabel()
        self.lclasses = QListWidget()
        self.lthreshold = QLineEdit()
        self.ldescription = QLineEdit()

        self.logger = logging.getLogger(__name__)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        # self.gridLayout = QLayou()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.configuration = confInfo

        if self.configuration is None:
            ph1 = {
                'name': 'test1',
                'input': 'test2',
                'output': 'test3',
                'classes': [1, 2, 3],
                'threshold': 'test4',
                'description': ''
            }
            ph2 = {
                'name': 'name',
                'input': 'input',
                'output': 'output',
                'classes': [4, 5, 6],
                'threshold': '0.5',
                'description': 'None'
            }
            self.models = {
                'Custom': {
                    'name': 'Custom',
                    'model': '',
                    'config': ph1,
                    'default': False
                },
                'MaskRCNN': {
                    'name': 'MaskRCNN',
                    'model': '',
                    'config': ph2,
                    'default': True
                },
            }

            self.menuActions = {
                'File': ['OpenFile', 'OpenDir', 'NextImg', 'PrevImg', 'Save', 'SaveAs', 'Clear'],
                'Edit': [
                    'NewMask', 'NewBBox', 'Draw', 'Erase', 'Fill', 'Unfill', 'Done', 'Undo',
                    'Correct'
                ],
                'View': ['Original', 'ZoomIn', 'ZoomOut', 'Fit', 'Drag'],
                'Label': ['AutoMask', 'AutoBbox', 'Seg_Custom', 'Seg_MaskRCNN', 'BBox_MaskRCNN'],
                'Correct': ['SLIC_KMeans']
            }
            self.shortCuts = {
                'OpenFile': {
                    'icon': 'openf.png',
                    'key': 'Ctrl+O',
                    'tip': 'Open image .png .jpg .jpeg'
                },
                'OpenDir': {
                    'icon': 'opend.png',
                    'key': 'Ctrl+D',
                    'tip': 'Open a directory and load all the images in .png .jpg and .jpeg format'
                },
                'Next': {
                    'icon': 'next.png',
                    'key': 'Right',
                    'tip': 'Move to the following image in the file list if any'
                },
                'Prev': {
                    'icon': 'prev.png',
                    'key': 'Left',
                    'tip': 'Move to the previous image in the file list if any'
                },
                'Save': {
                    'icon': 'save.png',
                    'key': 'Ctrl+S',
                    'tip': 'Save the annotations in a JSON file'
                },
                'SaveAs': {
                    'icon': 'save-as.png',
                    'key': 'Shift+S',
                    'tip': 'Save the annotations in a different formats'
                },
                'Clear': {
                    'icon': 'clear.png',
                    'key': 'Ctrl+C',
                    'tip': ''
                },
                'NewMask': {
                    'icon': 'mask.png',
                    'key': 'Shift+M',
                    'tip': ''
                },
                'NewBBox': {
                    'icon': 'boxes.png',
                    'key': 'Shift+B',
                    'tip': ''
                },
                'Draw': {
                    'icon': 'pen.png',
                    'key': 'Shift+D',
                    'tip': ''
                },
                'Erase': {
                    'icon': 'eraser.png',
                    'key': 'Shift+E',
                    'tip': ''
                },
                'Fill': {
                    'icon': 'fill.png',
                    'key': '',
                    'tip': ''
                },
                'Unfill': {
                    'icon': 'clear.png',
                    'key': '',
                    'tip': ''
                },
                'Done': {
                    'icon': 'done.png',
                    'key': 'Shift+Enter',
                    'tip': ''
                },
                'Undo': {
                    'icon': 'undo.png',
                    'key': 'Ctrl+Z',
                    'tip': ''
                },
                'Correct': {
                    'icon': 'correct.png',
                    'key': 'Shift+C',
                    'tip': ''
                },
                'MaxBlob': {
                    'icon':
                        'correct.png',
                    'key':
                        '',
                    'tip':
                        'Based on the current segmentation it deletes all blobs and keeps the biggest'
                },
                'Original': {
                    'icon': 'zoom_original.png',
                    'key': '',
                    'tip': ''
                },
                'ZoomIn': {
                    'icon': 'zoom_in.png',
                    'key': 'Ctrl++',
                    'tip': ''
                },
                'ZoomOut': {
                    'icon': 'zoom_out.png',
                    'key': 'Ctrl--',
                    'tip': ''
                },
                'Fit': {
                    'icon': 'zoom_fit.png',
                    'key': 'Shift+F',
                    'tip': ''
                },
                'Drag': {
                    'icon': 'drag.png',
                    'key': '',
                    'tip': ''
                },
                'AutoMask': {
                    'icon':
                        'mask.png',
                    'key':
                        '',
                    'tip':
                        'Segmentation using the default model_name. Set the default model in the configuration pannel'
                },
                'AutoBbox': {
                    'icon':
                        'boxes.png',
                    'key':
                        '',
                    'tip':
                        'Bounding box detection using the default model_name. Set the default model in the configuration pannel'
                },
                'Seg_Custom': {
                    'icon': 'mask.png',
                    'key': 'Ctrl+1',
                    'tip': ''
                },
                'Seg_MaskRCNN': {
                    'icon': 'mask.png',
                    'key': 'Ctrl+2',
                    'tip': ''
                },
                'BBox_MaskRCNN': {
                    'icon': 'boxes.png',
                    'key': 'Shift+1',
                    'tip': ''
                },
                'SLIC_KMeans': {
                    'icon': 'superpixel.png',
                    'key': '',
                    'tip': ''
                },
                'Configuration': {
                    'icon': 'config.png',
                    'key': '',
                    'tip': ''
                },
                'Help': {
                    'icon': 'help.png',
                    'key': 'Ctrl+H',
                    'tip': ''
                },
            }

        else:
            self.models = self.configuration['models']['segmentation']

            self.menuActions = self.configuration['shortcuts']['menu']
            self.shortCuts = self.configuration['shortcuts']['actions']

        self.addTab(self.tab1, "Auto Labeling")
        self.addTab(self.tab2, "List of shortcuts")

        self.lineEdit_sc = []
        self.lineEdit_name = []
        self.lineEdit = {}

        self.windo_top = 400
        self.windo_left = 500
        self.windo_width = 1000
        self.windo_height = 400
        # self.setGeometry(self.windo_top, self.windo_left, self.windo_width, self.windo_height)
        self.setWindowTitle('Configuration Pannel')

        self.fillTab1()
        self.fillTab2()

    def fillTab1(self):
        ''' Fill the tab 1 (model default and parameters) in the configuration window '''
        gridLayout = QGridLayout()
        segGroupBox = self.createGroupBox()
        # bboxGroupBox = self.createGroupBox()
        parameters = self.createInference()

        # self.t1editBt = QPushButton('Edit')
        # self.t1editBt.clicked.connect(lambda: self.enableShotCutEditing(True))

        self.t1saveBt = QPushButton('Save changes')
        self.t1saveBt.setEnabled(False)
        self.t1saveBt.clicked.connect(self.saveChanges)

        self.t1cancelBt = QPushButton('Cancel')
        self.t1cancelBt.clicked.connect(self.close)

        gridLayout.addWidget(segGroupBox, 0, 0, 1, 2)
        gridLayout.addWidget(QWidget(), 1, 0, 1, 2)
        gridLayout.addLayout(parameters, 0, 2, 1, 3)
        # gridLayout.addWidt1editBtget(self.t1editBt, 2, 2, 1, 1)
        gridLayout.addWidget(self.t1saveBt, 2, 3, 1, 1)
        gridLayout.addWidget(self.t1cancelBt, 2, 4, 1, 1)
        self.tab1.setLayout(gridLayout)

    def saveChanges(self):
        for name, data in self.models.items():
            if name != self.new_default:
                self.models[name]["default"] = False
            else:
                self.logger.info("Defaul model for segmentation: " + self.new_default)
                self.models[name]["default"] = True
        self.t1saveBt.setEnabled(False)
        self.updatedConf.emit(self.configuration)
        # print(self.models)

    def createGroupBox(self):
        self.groupbox = QGroupBox("Select default segmentation model:")
        vbox = QVBoxLayout()

        for name, data in self.models.items():
            default = data['default']
            rbutton = self.radiobtn(name, default)
            vbox.addWidget(rbutton)
        self.groupbox.setLayout(vbox)
        return self.groupbox

    def radiobtn(self, text, checked):
        radiobtn1 = QRadioButton(text)
        radiobtn1.setChecked(checked)
        radiobtn1.toggled.connect(self.OnRadioBtn)
        return radiobtn1

    def OnRadioBtn(self):
        radioBtn = self.sender()
        self.t1saveBt.setEnabled(True)
        if radioBtn.isChecked():
            self.new_default = radioBtn.text()

    def closeEvent(self, event):
        # pass
        none = {}
        self.updatedConf.emit(none)
        # print(self.models)
        # self.updatedConf.emit(self.configuration)
        # self.settings.setValue('window size', self.size())
        # self.settings.setValue('window position', self.pos())

    def createInference(self):
        grid = QGridLayout()
        parameters = QFormLayout()

        # Fill the first part of the right secction
        title = QLabel('Inference parameters')
        models = QLabel('Available models')
        cb = QComboBox()
        cb.currentTextChanged.connect(self.on_combobox_changed)
        for index, (name, data) in enumerate(self.models.items()):
            if data['default']:
                defIndex = index
                defModel = name
            cb.addItem(name)
        parameters.addRow(title)
        parameters.addRow(models, cb)
        cb.setCurrentIndex(defIndex)

        # Fill the second part
        model_parameters = ['name', 'input', 'output', 'classes', 'threshold', 'description']
        # conf = self.models[defModel]['config'][parameter]
        qname = QLabel(model_parameters[0])
        qinput = QLabel(model_parameters[1])
        qoutput = QLabel(model_parameters[2])
        qclasses = QLabel(model_parameters[3])
        qthreshold = QLabel(model_parameters[4])
        qdescription = QLabel(model_parameters[5])

        self.lname.setText(self.models[defModel]['config'][model_parameters[0]])
        self.linput.setText(self.models[defModel]['config'][model_parameters[1]])
        self.loutput.setText(self.models[defModel]['config'][model_parameters[2]])
        self.lclasses = QListWidget()
        for classname in self.models[defModel]['config'][model_parameters[3]]:
            self.lclasses.addItem(str(classname))
        # self.lclasses.setText(self.models[defModel]['config'][model_parameters[3]])
        self.lthreshold.setText(self.models[defModel]['config'][model_parameters[4]])
        self.ldescription.setText(self.models[defModel]['config'][model_parameters[5]])

        parameters.addRow(qname, self.lname)
        parameters.addRow(qinput, self.linput)
        parameters.addRow(qoutput, self.loutput)
        parameters.addRow(qclasses, self.lclasses)
        parameters.addRow(qthreshold, self.lthreshold)
        parameters.addRow(qdescription, self.ldescription)
        # parameters.addRow(qthreshold, lthreshold)
        grid.addLayout(parameters, 0, 0, 1, 1)
        return grid

    def on_combobox_changed(self, value):
        defModel = value
        model_parameters = ['name', 'input', 'output', 'classes', 'threshold', 'description']
        self.lclasses.clear()

        self.lname.setText(self.models[defModel]['config'][model_parameters[0]])
        self.linput.setText(self.models[defModel]['config'][model_parameters[1]])
        self.loutput.setText(self.models[defModel]['config'][model_parameters[2]])
        for classname in self.models[defModel]['config'][model_parameters[3]]:
            self.lclasses.addItem(str(classname))
        # self.lclasses.setText(self.models[defModel]['config'][model_parameters[3]])
        self.lthreshold.setText(self.models[defModel]['config'][model_parameters[4]])
        self.ldescription.setText(self.models[defModel]['config'][model_parameters[5]])

        # self.lthreshold = QLineEdit(self.models[defModel]['config'][model_parameters[4]])
        # self.ldescription = QLineEdit(self.models[defModel]['config'][model_parameters[5]])

    def createLabelEdit(self, label, line, enable):
        pass

    def fillTab2(self, edit=False):
        ''' Function defined to fill the SHORTCUT tab'''
        gridLayout = QGridLayout()

        for col, menu in enumerate(self.menuActions):
            column = QFormLayout()
            group_name = QLabel(menu + ' shortcuts:')
            column.addRow(group_name)
            for name in self.menuActions[menu]:
                shortcut = self.shortCuts[name]['key']
                sc_line = QLineEdit(shortcut)
                sc_line.setEnabled(edit)
                column.addRow(name, sc_line)
                self.lineEdit[name] = sc_line
                self.lineEdit_sc.append(sc_line)

            gridLayout.addLayout(column, 1, col, 1, 1)

        self.editBt = QPushButton('Edit')
        self.editBt.clicked.connect(lambda: self.enableShotCutEditing(True))
        gridLayout.addWidget(self.editBt, 2, 0, 1, 1)

        self.saveBt = QPushButton('Save changes')
        self.saveBt.setEnabled(False)
        self.saveBt.clicked.connect(lambda: self.enableShotCutEditing(False))
        gridLayout.addWidget(self.saveBt, 2, len(self.menuActions) - 2, 1, 1)

        self.cancelBt = QPushButton('Cancel')
        self.cancelBt.clicked.connect(self.printCurrent)
        gridLayout.addWidget(self.cancelBt, 2, len(self.menuActions) - 1, 1, 1)

        # self.setTabText(0, "Contact Details")
        self.tab2.setLayout(gridLayout)

    # def enableShotCutEditing(self, enable):
    #     self.saveBt.setEnabled(enable)
    #     self.editBt.setEnabled(not enable)
    #     for lineEdit in self.lineEdit_sc:
    #         lineEdit.setEnabled(enable)

    def enableShotCutEditing(self, enable):
        self.saveBt.setEnabled(enable)
        self.editBt.setEnabled(not enable)
        for name, lineEdit in self.lineEdit.items():
            lineEdit.setEnabled(enable)
            if not enable:
                self.shortCuts[name]['key'] = lineEdit.text()

    def printCurrent(self):
        pass
        # print(self.shortCuts)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    screen = confTab()
    screen.showNormal()
    sys.exit(app.exec_())
