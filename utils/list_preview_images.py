import sys
import os
import json
import utils.misc as utils


from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QHBoxLayout, QProgressBar, QCheckBox, QComboBox, QListWidgetItem, QLabel, QGridLayout, QLineEdit, QPushButton, QListWidget
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon, QColor

sys.path.append("..")


class listImages(QtWidgets.QDialog):
    list_images = pyqtSignal(list)

    def __init__(self, models):
        super().__init__()
        self.directory = ''
        self.listselectedmodels = None
        self.models = models
        self.images = {}
        self.labels = []
        self.initWindow()

    def initWindow(self):
        grid_layout = QGridLayout()

        self.everyNselected = QCheckBox('Select every:')
        self.everyNselected.setChecked(False)
        self.everyNselected.stateChanged.connect(self.selectEveryN)
        grid_layout.addWidget(self.everyNselected, 0, 0, 1, 1)

        # Lineedit to search for a especific image
        self.lineedit = QLineEdit(self)
        self.lineedit.setText('2')
        # self.lineedit.returnPressed.connect(self.onPressed)
        self.lineedit.setFont(QtGui.QFont("Sanserif", 8))
        grid_layout.addWidget(self.lineedit, 0, 2, 1, 1)

        # Checkbox
        self.allselected = QCheckBox('Select all')
        self.allselected.setChecked(True)
        self.allselected.stateChanged.connect(self.selectAll)
        grid_layout.addWidget(self.allselected, 1, 2, 1, 1)

        # Labels
        self.selectedImages = QListWidget(self)
        self.selectedImages.itemClicked.connect(self.clickList)
        grid_layout.addWidget(self.selectedImages, 2, 0, 9, 3)

        # label & unlabel dialogs
        self.labeled_label = self.createLabel('Labeled', 'green')
        grid_layout.addLayout(self.labeled_label, 11, 1, 1, 1)

        self.unlabeled_label = self.createLabel('Unlabeled', 'black')
        grid_layout.addLayout(self.unlabeled_label, 11, 2, 1, 1)

        self.showlabels = QCheckBox('Preview image with label')
        self.showlabels.setChecked(True)
        self.showlabels.stateChanged.connect(self.changeShowed)
        grid_layout.addWidget(self.showlabels, 15, 5, 1, 1)

        # Image
        self.label_image = QLabel()
        grid_layout.addWidget(self.label_image, 0, 3, 15, -1)
        # self.setImage(self.directory + self.images[0])

        # Combobox to select the selectedmodel
        self.selectedmodel = QComboBox(self)
        self.listselectedmodels = list(self.models.keys())
        self.selectedmodel.addItems(self.listselectedmodels)
        grid_layout.addWidget(self.selectedmodel, 12, 0, 1, 3)
        # Buttons
        self.okButton = QPushButton('Label')
        self.okButton.clicked.connect(self.label_images)
        grid_layout.addWidget(self.okButton, 13, 2, 1, 1)

        # Progress bar
        self.pbar = QProgressBar()
        self.pbar.setValue(0)
        grid_layout.addWidget(self.pbar, 14, 0, 1, 3)

        self.okButton = QPushButton('Import')
        self.okButton.clicked.connect(self.importSelected)
        grid_layout.addWidget(self.okButton, 15, 1, 1, 1)

        self.cancelButton = QPushButton('Cancel')
        self.cancelButton.clicked.connect(self.closeDialog)
        grid_layout.addWidget(self.cancelButton, 15, 2, 1, 1)

        # grid_layout.addWidget(buttonswidget)

        self.setLayout(grid_layout)
        # self.show()

    def init(self, directory):
        self.directory = directory
        self.getFiles()
        self.fillImages()

    def createLabel(self, text, color):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        if color == 'black':
            color = QColor(10, 10, 10)
        elif color == 'green':
            color = QColor(0, 255, 0)
        pixmap = QPixmap(15, 15)
        pixmap.fill(color)
        icon = QLabel()
        icon.setPixmap(pixmap)
        layout.addWidget(icon)
        layout.addSpacing(0)
        layout.addWidget(QLabel(text))
        return layout

    def changeShowed(self):
        name = self.selectedImages.currentItem().text()
        self.setImage(self.directory + name)

    def fillImages(self):
        ''' Clears and fills the list of images within the directory '''
        self.selectedImages.clear()
        for image, label in self.images.items():
            item = QListWidgetItem(image)
            item.setCheckState(Qt.Checked)
            if label is not None:
                color = QColor(0, 255, 0)
            else:
                color = QColor(50, 50, 50)
            pixmap = QPixmap(15, 15)
            pixmap.fill(color)
            item.setIcon(QIcon(pixmap))
            self.selectedImages.addItem(item)

        # Set the first image in the list to show
        first = self.selectedImages.item(0).text()
        self.setImage(self.directory + first)
        self.selectedImages.setCurrentRow(0)

    def getFiles(self):
        ''' Creates a list of name files that have an image format '''
        self.setWindowTitle(self.directory)
        files = sorted(os.listdir(self.directory))
        image_labels = {}
        for file in files:
            if file.split('.')[-1] == 'png' or file.split('.')[-1] == 'jpg' or file.split(
                    '.')[-1] == 'jpeg':
                image_name = file.split('/')[-1]
                label = utils.pathpng2json(os.path.join(self.directory, file))
                if os.path.isfile(label):
                    image_labels[image_name] = label
                else:
                    image_labels[image_name] = None
        self.images = image_labels

    def setImage(self, path):
        ''' function to set the image in the right of the dialog '''
        label_path = utils.pathpng2json(path)
        if self.showlabels.isChecked() and os.path.isfile(label_path):
            masks, classes = utils.open_label(label_path)
            masked_image = utils.generate_mask(path, masks)
            pixmap = utils.ndarray2Pixmap(masked_image)
        else:
            pixmap = QtGui.QPixmap(path)
        pixmap = pixmap.scaledToWidth(740)
        self.label_image.setPixmap(pixmap)

    def selectAll(self):
        if self.everyNselected.isChecked():
            self.everyNselected.setCheckState(Qt.Unchecked)
        ''' function to check or uncheck all the images '''
        if self.allselected.isChecked():
            for index in range(self.selectedImages.count()):
                self.selectedImages.item(index).setCheckState(Qt.Checked)
        else:
            for index in range(self.selectedImages.count()):
                self.selectedImages.item(index).setCheckState(Qt.Unchecked)

    def selectEveryN(self):
        n = int(self.lineedit.text())
        ''' function to check or uncheck every N images '''
        if self.allselected.isChecked():
            self.allselected.setCheckState(Qt.Unchecked)

        for index in range(self.selectedImages.count()):
            if index % n == 0:
                self.selectedImages.item(index).setCheckState(Qt.Checked)

    def importSelected(self):
        ''' Import to the main list the checked images '''
        selected = []
        for index in range(self.selectedImages.count()):
            if self.selectedImages.item(index).checkState() == Qt.Checked:
                selected.append(self.directory + self.selectedImages.item(index).text())
        self.list_images.emit(selected)
        self.close()

    def label_images(self):
        ''' Label the the checed images with the selected model '''
        selected = []
        for index in range(self.selectedImages.count()):
            if self.selectedImages.item(index).checkState() == Qt.Checked:
                color = QColor(0, 255, 0)
                pixmap = QPixmap(15, 15)
                pixmap.fill(color)
                self.selectedImages.item(index).setIcon(QIcon(pixmap))
                selected.append(self.directory + self.selectedImages.item(index).text())

        total_img = len(selected)
        if self.models is not None:
            model_name = self.selectedmodel.currentText()
            model = self.models[model_name]['model']
            for i, image_path in enumerate(selected):
                self.masks, _, self.class_names = model.image_prediction(image_path)
                self.save('seg', image_path)
                # self.selectedImages.item(i).setTextColor(QtGui.QColor("red"))
                percentage = int(100 * (i + 1) / total_img)
                self.pbar.setValue(percentage)
        # text = self.lineedit.text()
        # self.label.emit(text)

    def save(self, mode='seg', image_path=None):
        file_name = image_path.split('/')[-1]

        label_json = {'version': '1.0.0', "image": file_name, "annotations": None, "type": mode}
        instances = list()
        instance_json = {
            "category": None,
            "iscrowd": 0,
            "segmentation": [],
            "area": None,
            "bbox": None
        }
        filePath = self.directory

        if filePath != '':
            if mode == 'seg':
                for index, classname in enumerate(self.class_names):
                    instance = instance_json.copy()
                    instance["category"] = classname
                    instance["segmentation"] = utils.mask2rle(self.masks[index])
                    instances.append(instance)
            # elif self.mode == 'bbox':
            #     bboxes = self.viewer.save_all()
            #     for coordinates, classname, area in bboxes:
            #         instance = instance_json.copy()
            #         instance["category"] = classname
            #         instance["bbox"] = coordinates
            #         instance["area"] = area
            #         instances.append(instance)

            # label_json['shapes'] = self.save_ann.masks_to_json(self.map_image.masks, labels)
            # _, label_json['imageHeight'], label_json['imageWidth'] = self.map_image.masks.shape
            label_json["annotations"] = instances
            with open(image_path.split('.')[0] + '.json', 'w') as f:
                json.dump(label_json, f)

            # # row = self.filesList.currentRow()
            # for index in range(self.filesList.count()):
            #     if self.filesList.item(index).text() == file_name:
            #         row = index
            # item = self.filesList.item(row)
            # item.setCheckState(Qt.Checked)
            # self.json_path = utils.pathpng2json(image_path)
            # item.setData(101, self.json_path)

    def clickList(self):
        ''' Previews the selected image '''
        image_name = self.selectedImages.currentItem().text()
        path = self.directory + image_name
        self.setImage(path)
        # self.lineedit.setText(row)

    def closeDialog(self):
        # self.label.emit(None)
        self.close()

    def keyPressEvent(self, event):
        # super(labelDialog, self).keyPressEvent(event)
        if event.key() == Qt.Key_Escape:
            self.closeDialog()
        if event.key() == Qt.Key_Return:
            self.label_images()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = listImages()
    window.show()
    sys.exit(app.exec_())
