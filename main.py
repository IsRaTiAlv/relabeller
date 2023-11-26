from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QColor, QIcon, QImage, QPixmap, QCursor
from PyQt5.QtCore import Qt, QSize, QEvent, QSettings
from PyQt5.QtWidgets import QMessageBox, QListWidgetItem, QGraphicsView, QMainWindow, QApplication
from PyQt5.QtWidgets import QMenu, QFileDialog, QDockWidget, QListWidget, QWidget

import imageio
import json
import logging
import numpy as np
import os
import sys
import time
from collections import OrderedDict

from logging import config as logging_config
from models.predict_torch import torch_model
from models.predict_custom import custom_model
from models.predict_silhouette import person_model
from models.predict_superpixel import superpixel_model
from utils.change import map_image
from utils.menu import menu
from utils.zoom import PhotoViewer
from utils.label import labelDialog
from utils.conf import confTab
# from utils.save import save_annotations
from utils.slider import Slider
from utils.list_preview_images import listImages
import utils.misc as utils


class Window(QMainWindow):

    def __init__(self):
        super().__init__()
        self.settings = QSettings('relabeller', 'app1')

        # Logging
        current_path = os.path.abspath(os.path.dirname(__file__))
        logging_config.fileConfig(os.path.abspath(os.path.join(current_path, 'config.ini')))

        self.logger = logging.getLogger(__name__)
        self.logger.info('Starting Relabeller.')

        # Define the title and the windows geometry
        self.windo_title = "Relabeller"
        self.iconName = "icons/icon.png"
        self.statusBar().showMessage("Relabeller launched")
        self.setAcceptDrops(True)

        self.windo_top = 400
        self.windo_left = 400
        self.windo_width = 1200
        self.windo_height = 800
        self.setWindowTitle(self.windo_title)
        self.setWindowIcon(QIcon(self.iconName))

        self.menuActions = {
            'File': ['OpenFile', 'OpenDir', 'NextImg', 'PrevImg', 'Save', 'SaveAs', 'Clear'],
            'Edit': [
                'NewMask', 'NewBBox', 'Draw', 'Erase', 'Fill', 'Unfill', 'Done', 'Undo', 'Correct'
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
            'NextImg': {
                'icon': 'next.png',
                'key': 'Right',
                'tip': 'Move to the following image in the file list if any'
            },
            'PrevImg': {
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
                'key': 'D',
                'tip': ''
            },
            'Erase': {
                'icon': 'eraser.png',
                'key': 'E',
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
            'Hide': {
                'icon': 'visible.png',
                'key': 'Shift+1',
                'tip': 'Hides all the masks if any'
            },
            'Correct': {
                'icon':
                    'correct.png',
                'key':
                    'Shift+2',
                'tip':
                    'Grabs an image region and clusters it in two clusters accoring to their color'
            },
            'MaxBlob': {
                'icon':
                    'holes.png',
                'key':
                    'Shift+3',
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
                    None,
                'tip':
                    'Segmentation using the default model_name. Set the default model in the configuration pannel'
            },
            'AutoBbox': {
                'icon':
                    'boxes.png',
                'key':
                    None,
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
                'key': 'Ctrl+3',
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

        self.image = None
        self.image_path = ''
        self.image_size = None
        self.image_brigtness = None
        self.labels_brigtness = None
        self.images_path = []
        self.images_folder = ''
        self.image_chages = []
        self.current_cursor = QCursor(Qt.ArrowCursor)
        self.cursor_size = 15
        self.cursor_factor = None
        self.color_draw = None
        self.mask_items = []
        self.label_items = []
        self.mode = None
        self.view_segments = None
        self.hideInstances = True
        self.all_checked_items = []
        self.model = custom_model('models/fscnn640_320YCbCr_e49196bc-409e-11ec-871d-0c9d92c51afe.onnx')
        self.torch_model = torch_model()
        self.sil_seg_model = person_model()
        self.superpixel_model = superpixel_model()
        ''' Define de models object and configuration '''
        self.objModels = {
            'Custom': {
                'name': 'custom',
                'model': self.model
            },
            'MaskRCNN': {
                'name': 'maskrcnn',
                'model': self.torch_model
            }
        }

        self.seg_models = {
            'Custom': {
                'name': 'custom',
                'model': '',
                'config': self.model.getInfo(),
                'default': False
            },
            'MaskRCNN': {
                'name': 'maskrcnn',
                'model': '',
                'config': self.torch_model.getInfo(),
                'default': True
            },
            'test1': {
                'name': 'T1',
                'model': '',
                'config': None,
                'default': False
            },
            'test2': {
                'name': 'T2',
                'model': '',
                'config': None,
                'default': False
            },
            'test3': {
                'name': 'T3',
                'model': '',
                'config': None,
                'default': False
            }
        }

        self.bbox_models = {}

        self.Info = {
            'models': {
                'segmentation': self.seg_models,
                'Bbox': self.bbox_models
            },
            'shortcuts': {
                'menu': self.menuActions,
                'actions': self.shortCuts
            }
        }
        self.confInfo = OrderedDict(self.Info)

        if len(sys.argv) == 0:
            try:
                self.confInfo = self.settings.value('configuration')
                self.logger.info('Configuration restored correctly')
            except Exception:
                print("An exception occurred")
        else:
            self.logger.info('Default configuration')
            # self.confInfo = OrderedDict()

        # self.save_ann = save_annotations()
        self.map_image = None
        self.slices, self.marked = None, None  # SuperPixel flags
        # self.slider_class = Slider()

        self.menu = menu(self.confInfo['shortcuts']['actions'])
        self.image = QImage(self.size(), QImage.Format_RGB32)

        self.dialog = labelDialog()
        self.dialog.label.connect(self.modifyLabel)
        self.labellistImages = listImages(self.objModels)
        self.labellistImages.list_images.connect(self.openListImages)
        self.configuration = confTab(self.confInfo)
        self.configuration.updatedConf.connect(self.updateConfiguration)
        # self.listImages.connect(self.openlistImages)

        self.viewer = PhotoViewer(self, self.statusBar)
        self.viewer.photoClicked.connect(self.imageModification)
        self.viewer.zoom_action.connect(self.draw_mode)
        self.viewer.zoom_ratio.connect(self.update_zoom)
        self.viewer.tool_val.connect(self.tool_wheel)
        self.viewer.factor_rate.connect(self.setSizeLabel)
        self.viewer.mask_selected.connect(self.maskList)
        self.viewer.bbox_selected.connect(self.bboxList)
        self.viewer.bbox_created.connect(self.instanceListEdit)
        self.viewer.bbox_modified.connect(self.bboxModification)

        self.setCentralWidget(self.viewer)

        self.mainMenu = self.menuBar()
        self.mainMenu.installEventFilter(self)
        fileMenu = self.mainMenu.addMenu("File")
        editMenu = self.mainMenu.addMenu("Edit")
        viewMenu = self.mainMenu.addMenu("View")
        toolsMenu = self.mainMenu.addMenu("Tools")
        autolabelMenu = self.mainMenu.addMenu("AutoLabel")

        helpMenu = self.mainMenu.addMenu('Help')
        '''Filling actions the FILE MENU'''
        fileMenu.addAction(self.menu.openAction)
        self.menu.openAction.triggered.connect(lambda: self.open_file('file'))
        fileMenu.addAction(self.menu.openDirAction)
        self.menu.openDirAction.triggered.connect(lambda: self.open_file('dir'))
        fileMenu.addAction(self.menu.nextImgAction)
        self.menu.nextImgAction.triggered.connect(lambda: self.orderImage('next'))
        fileMenu.addAction(self.menu.preImgAction)
        self.menu.preImgAction.triggered.connect(lambda: self.orderImage('prev'))

        fileMenu.addAction(self.menu.saveAction)
        # self.menu.saveMenuAction.triggered.connect(lambda: self.saveButtonAction('save'))
        self.menu.saveAction.triggered.connect(lambda: self.saveButtonAction('save'))
        fileMenu.addAction(self.menu.saveasAction)
        self.menu.saveasAction.triggered.connect(lambda: self.saveButtonAction('save_as'))
        ''' Filling actions the EDIT MENU'''
        editMenu.addAction(self.menu.CreateMaskAction)
        self.menu.CreateMaskAction.triggered.connect(self.newMask)
        editMenu.addAction(self.menu.CreateBboxAction)
        self.menu.CreateBboxAction.triggered.connect(self.newbbox)

        self.menu.drawMenuAction.triggered.connect(lambda: self.draw_mode(mode='pen'))
        editMenu.addAction(self.menu.drawAction)
        self.menu.drawAction.triggered.connect(lambda: self.draw_mode(mode='pen'))
        editMenu.addAction(self.menu.eraseAction)
        self.menu.eraseAction.triggered.connect(lambda: self.draw_mode(mode='erase'))
        editMenu.addAction(self.menu.fillAction)
        self.menu.fillAction.triggered.connect(lambda: self.draw_mode(mode='fill'))
        editMenu.addAction(self.menu.unfillAction)
        self.menu.unfillAction.triggered.connect(lambda: self.draw_mode(mode='unfill'))
        editMenu.addAction(self.menu.doneAction)
        self.menu.doneAction.triggered.connect(lambda: self.draw_mode(mode='done'))
        editMenu.addAction(self.menu.undoAction)
        self.menu.undoAction.triggered.connect(lambda: self.draw_mode(mode='undo'))
        fileMenu.addAction(self.menu.clearAction)
        self.menu.clearAction.triggered.connect(self.clear)
        ''' Filling actions the VIEW MENU'''
        viewMenu.addAction(self.menu.zoomOrgAction)
        self.menu.zoomOrgAction.triggered.connect(lambda: self.draw_mode(mode='drag'))
        viewMenu.addAction(self.menu.zoomInAction)
        self.menu.zoomInAction.triggered.connect(lambda: self.viewer.zoom('in'))
        viewMenu.addAction(self.menu.zoomOutAction)
        self.menu.zoomOutAction.triggered.connect(lambda: self.viewer.zoom('out'))
        viewMenu.addAction(self.menu.zoomFitAction)
        self.menu.zoomFitAction.triggered.connect(lambda: self.viewer.zoom('fit'))
        viewMenu.addAction(self.menu.zoomDragAction)
        self.menu.zoomDragAction.triggered.connect(self.viewer.toggleDragMode)
        ''' Filling actions the CORRECTION MENU'''
        # toolsMenu.addWidget(self.menu.hideAction)
        self.menu.hideAction.toggled.connect(self.uncheckInstanceList)
        toolsMenu.addAction(self.menu.correctAction)
        self.menu.correctAction.triggered.connect(lambda: self.draw_mode(mode='rect'))
        toolsMenu.addAction(self.menu.maxBlobAction)
        self.menu.maxBlobAction.triggered.connect(lambda: self.draw_mode(mode='close'))
        toolsMenu.addSeparator()
        toolsMenu.addAction(self.menu.slicSegmentatinoAction)
        self.menu.slicSegmentatinoAction.triggered.connect(lambda: self.auto_SPixel('network'))
        ''' Filling actions the LABELING MENU'''
        autolabelMenu.addAction(self.menu.autoSegAction)
        autolabelMenu.addAction(self.menu.autoBboxAction)
        autolabelMenu.addSeparator()
        autolabelMenu.addAction(self.menu.segCustomAction)
        autolabelMenu.addAction(self.menu.segMaskRCNNAction)
        autolabelMenu.addSeparator()
        autolabelMenu.addAction(self.menu.bboxMaskRCNNAction)

        self.menu.autoSegAction.triggered.connect(lambda: self.auto_seg('default'))
        self.menu.segCustomAction.triggered.connect(lambda: self.auto_seg('custom'))
        self.menu.segMaskRCNNAction.triggered.connect(lambda: self.auto_seg('maskrcnn'))
        self.menu.bboxMaskRCNNAction.triggered.connect(lambda: self.auto_bbox('maskrcnn'))
        # autolabel.addAction(self.menu.silSegmentatinoAction)
        # self.menu.silSegmentatinoAction.triggered.connect(lambda: self.auto_seg('unet'))
        ''' Filling actions the HELP MENU'''
        helpMenu.addAction(self.menu.configAction)
        self.menu.configAction.triggered.connect(self.configTab)
        helpMenu.addAction(self.menu.helpAction)
        # self.menu.helpAction.triggered.connect(self.help)

        self.toolbar = self.addToolBar("FileToolbar")
        self.toolbar.setIconSize(QtCore.QSize(20, 20))
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.toolbar.installEventFilter(self)
        self.toolbar.addAction(self.menu.openAction)
        self.toolbar.addAction(self.menu.openDirAction)
        self.toolbar.addAction(self.menu.nextImgAction)
        self.toolbar.addAction(self.menu.preImgAction)
        self.toolbar.addAction(self.menu.saveAction)
        self.toolbar.addAction(self.menu.saveasAction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.menu.CreateAction)
        self.toolbar.addAction(self.menu.drawMenuAction)
        self.toolbar.addAction(self.menu.fillMenuAction)
        self.toolbar.addAction(self.menu.doneAction)
        self.toolbar.addAction(self.menu.undoAction)
        self.toolbar.addAction(self.menu.clearAction)
        self.toolbar.addWidget(self.menu.sizeLabel)
        self.toolbar.addAction(self.menu.zoomFitAction)
        self.addToolBar(Qt.LeftToolBarArea, self.toolbar)

        self.toolbar2 = self.addToolBar("Toolsbar")
        self.toolbar2.setIconSize(QtCore.QSize(20, 20))
        self.toolbar2.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.toolbar2.installEventFilter(self)

        self.toolbar2.addAction(self.menu.autoSegAction)
        self.toolbar2.addAction(self.menu.autoBboxAction)
        self.toolbar2.addAction(self.menu.hideAction)
        self.toolbar2.addAction(self.menu.correctAction)
        self.toolbar2.addAction(self.menu.maxBlobAction)
        self.addToolBar(Qt.BottomToolBarArea, self.toolbar2)

        # self.image_size_widget = Slider('imgs', 'Image size')
        # self.image_size_widget.change.connect(self.changeValue)
        self.image_brigtness_widget = Slider('imgb', 'Image brigtness')
        self.image_brigtness_widget.change.connect(self.changeValue)
        self.labels_brigtness_widget = Slider('labelb', 'Label brigtness')
        self.labels_brigtness_widget.change.connect(self.changeValue)
        self.cursor_size_widget = Slider('cursor', 'Cursor size')
        self.cursor_size_widget.change.connect(self.changeValue)
        self.segments_size_widget = Slider('segments', '# Segments')
        self.segments_size_widget.change.connect(self.changeValue)
        self.ncompactsness_widget = Slider('compactness', 'Compactness')
        self.ncompactsness_widget.change.connect(self.changeValue)

        self.uppertoolbar = QtWidgets.QToolBar("uppertoolbar")
        self.uppertoolbar.setIconSize(QtCore.QSize(30, 30))
        self.uppertoolbar.installEventFilter(self)
        # self.adding_isize_slider = self.uppertoolbar.addWidget(self.image_size_widget.widget)
        self.adding_ibrig_slider = self.uppertoolbar.addWidget(self.image_brigtness_widget.widget)
        # self.addImagesliders(add=False)
        self.adding_label_slider = self.uppertoolbar.addWidget(self.labels_brigtness_widget.widget)
        self.adding_label_cursor = self.uppertoolbar.addWidget(self.cursor_size_widget.widget)
        self.addLabelsliders(add=False)
        self.addCursorsliders(add=False)
        self.adding_segment_slider = self.uppertoolbar.addWidget(self.segments_size_widget.widget)
        self.adding_compactness = self.uppertoolbar.addWidget(self.ncompactsness_widget.widget)
        self.addPixmapsliders(add=False)
        # self.uppertoolbar.addAction(self.menu.openDirAction)
        self.addToolBar(Qt.TopToolBarArea, self.uppertoolbar)

        self.filesDock = QDockWidget('Files List', self)
        self.filesDock.installEventFilter(self)
        self.filesList = QListWidget(self)
        # self.filesList.addItems(self.images_path)
        self.filesList.itemClicked.connect(self.itemList)
        self.filesDock.setWidget(self.filesList)
        self.addDockWidget(Qt.RightDockWidgetArea, self.filesDock)

        self.masksDock = QDockWidget('Masks List', self)
        self.masksDock.installEventFilter(self)
        self.instancesList = QListWidget(self)
        # self.instancesList.addItems(['1','2','3','4','5'])
        self.instancesList.setContextMenuPolicy(Qt.CustomContextMenu)
        self.instancesList.customContextMenuRequested.connect(self.rightMenuShow)
        self.instancesList.itemClicked.connect(self.instanceList)
        # self.instancesList.itemDoubleClicked.connect(self.rightMenuShow)
        self.masksDock.setWidget(self.instancesList)
        self.addDockWidget(Qt.RightDockWidgetArea, self.masksDock)

        self.labelDock = QDockWidget('Labels List', self)
        self.labelDock.installEventFilter(self)
        self.labelList = QListWidget(self)
        # self.labelList.addItems(['1','2','3','4','5'])
        # self.filesList.addItems(self.images_path)
        # self.labelList.itemClicked.connect(self.itemList)
        self.labelDock.setWidget(self.labelList)
        self.addDockWidget(Qt.RightDockWidgetArea, self.labelDock)

        self.disableActions()

        self.rightMenu = QMenu(self.instancesList)
        self.rightMenu.addAction(self.menu.addInstanceAction)
        self.rightMenu.addAction(self.menu.editAction)
        self.rightMenu.addAction(self.menu.deleteAction)
        self.menu.editAction.triggered.connect(lambda: self.instanceListEdit(None))
        self.menu.deleteAction.triggered.connect(self.instanceListDelete)

        try:
            self.resize(self.settings.value('window size'))
            self.move(self.settings.value('window position'))
            self.show()
        except Exception:
            self.setGeometry(self.windo_top, self.windo_left, self.windo_width, self.windo_height)
            self.showMaximized()

    def updateConfiguration(self, newConf):
        if len(newConf) == 0:
            del self.configuration
        else:
            self.logger.info('Configuration updated correctly')
            self.confInfo = newConf

    def configTab(self):
        self.configuration = confTab(self.confInfo)
        self.configuration.updatedConf.connect(self.updateConfiguration)
        self.configuration.show()

    def addImagesliders(self, add):
        if add:
            # self.uppertoolbar.addAction(self.adding_isize_slider)
            self.uppertoolbar.addAction(self.adding_ibrig_slider)
        else:
            # self.uppertoolbar.removeAction(self.adding_isize_slider)
            self.uppertoolbar.removeAction(self.adding_ibrig_slider)

    def addLabelsliders(self, add):
        if add:
            self.uppertoolbar.addAction(self.adding_label_slider)
        else:
            self.uppertoolbar.removeAction(self.adding_label_slider)

    def addCursorsliders(self, add):
        if add:
            self.uppertoolbar.addAction(self.adding_label_cursor)
        else:
            self.uppertoolbar.removeAction(self.adding_label_cursor)

    def addPixmapsliders(self, add):
        if add:
            self.uppertoolbar.addAction(self.adding_segment_slider)
            self.uppertoolbar.addAction(self.adding_compactness)
        else:
            self.uppertoolbar.removeAction(self.adding_segment_slider)
            self.uppertoolbar.removeAction(self.adding_compactness)

    def loadImage(self):
        self.viewer.setPhoto(self.pixmap_image, self.image_path, self.pil_image, self.map_image)

    def eventFilter(self, object, event):
        if event.type() == QEvent.Enter:
            self.setCursor(QCursor(Qt.ArrowCursor))
            return True
        elif event.type() == QEvent.Leave:
            self.setCursor(self.current_cursor)
        return False

    def rightMenuShow(self, item):
        self.rightMenu.exec_(QCursor.pos())

    def showDialog(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText("Maintain current masks?")
        msgBox.setWindowTitle("New inference")
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        # msgBox.buttonClicked.connect(msgButtonClick)

        returnValue = msgBox.exec()
        if returnValue == QMessageBox.Yes:
            return True
        elif returnValue == QMessageBox.No:
            return False

    def newMaskDialog(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText("Do you want to create a new mask?")
        msgBox.setWindowTitle("New mask")
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        # msgBox.buttonClicked.connect(msgButtonClick)

        returnValue = msgBox.exec()
        if returnValue == QMessageBox.Yes:
            return True
        elif returnValue == QMessageBox.No:
            self.labelDialogResponse = True
            return False

    def saveLabelDialog(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText("Do you want to save the annotations before closing?")
        msgBox.setWindowTitle("Save annotations")
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        # msgBox.buttonClicked.connect(msgButtonClick)

        returnValue = msgBox.exec()
        if returnValue == QMessageBox.Yes:
            return True
        elif returnValue == QMessageBox.No:
            self.labelDialogResponse = True
            return False

    def auto_seg(self, mode, json_data=None):
        self.addLabelsliders(add=True)
        self.addCursorsliders(add=True)
        if json_data is None:
            self.map_image.do_action()

        self.setCursor(QCursor(Qt.WaitCursor))
        self.mode = 'seg'
        self.updateModeButtons()
        self.menu.correctAction.setEnabled(True)
        self.imageModification(True)
        # self.image_chages.append(self.map_image.img)
        if mode == 'default':
            for name, data in self.confInfo['models']['segmentation'].items():
                if data['default']:
                    mode = data['name']

        if mode == 'maskrcnn':
            masks, _, class_names = self.torch_model.image_prediction(self.image_path, 0.7)
        elif mode == 'custom':
            masks, _, class_names = self.model.image_prediction(self.image_path)
        elif mode == 'unet':
            masks, _, class_names = self.sil_seg_model.image_prediction(self.image_path)
        elif mode == 'json':
            masks, _, class_names = json_data

        if type(self.map_image.masks) == list:  # Check if the image is mask empty
            self.map_image.masks = masks
            self.map_image.class_names = class_names
        elif not self.showDialog():  # If clear option is selected in dialog
            self.instancesList.clear()
            self.map_image.masks = masks
            self.map_image.class_names = class_names
        else:
            self.map_image.masks = np.concatenate((self.map_image.masks, masks), axis=0)
            self.map_image.class_names = self.map_image.class_names + class_names
            self.instancesList.clear()

        masked_image = self.map_image.generate_mask()
        # self.map_image.img = self.img_mask
        self.viewer.setPixmapImage(masked_image)
        # past_labels = len(self.map_image.class_names) - len(class_names)
        for i, class_name in enumerate(self.map_image.class_names):
            r, g, b = self.map_image.colors[i]
            item = QListWidgetItem(class_name)
            '''
            widget = QtWidgets.QWidget()
            widgetText = QtWidgets.QLabel(class_name)
            widgetButton = QtWidgets.QPushButton()
            img = QIcon('icons/invisible.png')
            widgetButton.setIcon(img)
            # widgetButton.setIconSize(QtCore.QSize(5, 5))

            trashButton = QtWidgets.QPushButton()
            img = QIcon('icons/remove.png')
            trashButton.setIcon(img)
            # widgetButton.setIconSize(QtCore.QSize(3, 3))

            widgetButton.clicked.connect(self.pressed)
            widgetLayout = QtWidgets.QHBoxLayout()
            widgetLayout.addWidget(widgetText)
            widgetLayout.addWidget(widgetButton,  10, Qt.AlignRight)
            widgetLayout.addWidget(trashButton)
            widgetLayout.addStretch()

            # widgetLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
            widgetLayout.setContentsMargins(0, 0, 0, 0)

            widget.setLayout(widgetLayout)
            item.setSizeHint(widget.sizeHint())
            '''
            item.setCheckState(Qt.Checked)
            pixmap = QPixmap(15, 15)
            pixmap.fill(QColor(int(255 * r), int(255 * g), int(255 * b)))
            item.setIcon(QIcon(pixmap))
            self.instancesList.addItem(item)
            # self.instancesList.setItemWidget(item, widget)
        self.map_image.mask_items = list(range(len(class_names)))
        # self.instancesList.setCurrentRow(0)

        self.update_items(class_names)
        self.setCursor(QCursor(Qt.ArrowCursor))

    def auto_bbox(self, mode, json_data=None):
        # self.menu.CreateMaskAction.setEnabled(False)
        self.addLabelsliders(add=True)
        ids = []
        self.setCursor(QCursor(Qt.WaitCursor))
        self.bboxModification(True)
        self.mode = 'bbox'
        self.updateModeButtons()
        if mode == "maskrcnn":
            _, bbox, self.map_image.class_names = self.torch_model.image_prediction(
                self.image_path, 0.8)
        elif mode == 'json':
            _, bbox, self.map_image.class_names = json_data

        self.colors = self.map_image.random_colors(8) * 2
        for i, class_name in enumerate(self.map_image.class_names):
            id = int(time.time() * 1000) + i
            ids.append(id)
            r, g, b = self.colors[i]
            item = QListWidgetItem(class_name)
            item.setData(100, 'id-' + str(id))
            item.setCheckState(Qt.Checked)
            pixmap = QPixmap(15, 15)
            pixmap.fill(QColor(int(255 * r), int(255 * g), int(255 * b)))
            item.setIcon(QIcon(pixmap))
            self.instancesList.addItem(item)

        self.viewer.addbbox(bbox, self.map_image.class_names, self.colors, ids)
        self.update_items(self.map_image.class_names)
        self.setSizeLabel('0')
        self.setCursor(QCursor(Qt.ArrowCursor))

    def auto_SPixel(self, mode):
        if mode == 'slic':
            if type(self.map_image.masks) is list:
                self.newMask()
            elif self.newMaskDialog():
                self.newMask()
            if self.labelDialogResponse:
                self.statusBar().showMessage("Press Space Key to switch views")
                self.fillModification(True)
                self.hasMask(False)
                self.draw_mode('fill')
                self.slices, self.marked = self.superpixel_model.slic_prediction(self.image_path)
                self.map_image.segments = self.slices
                self.map_image.array_image = self.marked

                self.maskList(self.map_image.masks.shape[0] - 1)
                # self.map_image.colors = self.map_image.random_colors(self.map_image.masks.shape[0])
                masked_image = self.map_image.apply_masks_to_image()
                self.viewer.setPixmapImage(masked_image)
                self.view_segments = True  # True View segments in the scene
                self.addPixmapsliders(True)
                self.cursor_size = 15
                self.update_cursor()

    def changeValue(self, values):
        id, value = values
        label_br = value / 350
        br_value = round(value / 100 + 1, 2)  # Map value to [0, 2] range
        # print(value)
        if id == 'imgs':
            self.image_size = value
        if id == 'imgb':
            self.pil_image = utils.brightness(self.image_path, br_value)
            self.map_image.pil_image = self.pil_image
            self.map_image.array_image = np.array(self.pil_image)
            # Uncomment if you want to change the label intensity as well.
            # self.map_image.alpha = self.map_image.base_alpha + label_br
            # self.map_image.alpha_ = self.map_image.base_alpha_ + label_br
            masked = self.map_image.apply_masks_to_image()
            self.pixmap_image = utils.ndarray2Pixmap(masked)
            self.viewer._photo.setPixmap(self.pixmap_image)
            self.image_brigtness = value
            # self.image_size_label.setText(f'Image size: {str(value)}%')

        if id == 'cursor':
            # print(self.cursor_size)
            self.cursor_size = self.viewer.brushSize = value
            self.update_cursor()
            masked_image = self.map_image.apply_masks_to_image()
            self.viewer.setPixmapImage(masked_image)

        if id == 'labelb':
            if self.mode == 'seg':
                self.map_image.alpha = self.map_image.base_alpha + label_br
                self.map_image.alpha_ = self.map_image.base_alpha_ + label_br
                masked = self.map_image.apply_masks_to_image()
                self.pixmap_image = utils.ndarray2Pixmap(masked)
                self.viewer._photo.setPixmap(self.pixmap_image)
                self.label_brigtness = value

            if self.mode == 'bbox':
                self.viewer.updatebboxColor(value // 2)

            self.labels_brigtness = value

        if id == 'segments' or id == 'compactness':
            seg = self.segments_size_widget.slider.value()
            com = self.ncompactsness_widget.slider.value()
            self.slices, self.marked = self.superpixel_model.slic_prediction(self.image_path,
                                                                             segments=seg,
                                                                             compact=com)
            self.map_image.segments = self.slices
            self.map_image.array_image = self.marked
            # self.newMask()
            # width, height = self.pil_image.size
            # self.map_image.masks = np.zeros((1, height, width))
            # self.map_image.channel = 0
            # self.map_image.colors = self.map_image.random_colors(self.map_image.masks.shape[0])
            masked_image = self.map_image.apply_masks_to_image()
            self.viewer.setPixmapImage(masked_image)
            self.view_segments = True

        # else:
    def tool_wheel(self, value):
        new_val = 0
        if value:
            new_val = self.cursor_size +1
        else:
            new_val = self.cursor_size -1

        if new_val >= 3 and new_val <= 50:
            self.cursor_size = new_val
            self.cursor_size_widget.setValue(self.cursor_size)
            self.changeValue(('cursor', self.cursor_size))
        else:
            self.statusBar().showMessage("Max and min value [3,50]")
        time.sleep(0.05)

    def newMask(self):
        self.mode = 'seg'
        self.instanceListEdit(id=[0, 0, 0, 0], title='New label')
        if self.labelDialogResponse:
            self.statusBar().showMessage("New mask created")
            self.addLabelsliders(add=True)
            # self.addCursorsliders(add=True)

            # self.menu.CreateBboxAction.setEnabled(False)
            self.updateModeButtons()
            class_names = [self.new_seg_class]
            width, height = self.pil_image.size
            new_mask = np.zeros((1, height, width)).astype('bool')
            if type(self.map_image.masks) == list:  # Check if the image is mask empty
                self.map_image.masks = new_mask
                self.map_image.class_names = class_names
            else:
                self.map_image.masks = np.concatenate((self.map_image.masks, new_mask), axis=0)
                self.map_image.class_names = self.map_image.class_names + class_names
                self.instancesList.clear()

            masked_image = self.map_image.generate_mask()
            self.viewer.setPixmapImage(masked_image)
            # past_labels = len(self.map_image.class_names) - len(class_names)
            # print(self.map_image.class_names)
            # print(self.map_image.colors)
            for i, class_name in enumerate(self.map_image.class_names):
                r, g, b = self.map_image.colors[i]
                item = QListWidgetItem(class_name)
                item.setCheckState(Qt.Checked)
                pixmap = QPixmap(15, 15)
                pixmap.fill(QColor(int(255 * r), int(255 * g), int(255 * b)))
                item.setIcon(QIcon(pixmap))
                self.instancesList.addItem(item)
                # self.instancesList.setItemWidget(item, widget)
            self.map_image.mask_items = list(range(len(class_names)))
            # self.instancesList.setCurrentRow(0)
            self.maskList(self.map_image.masks.shape[0] - 1)
            self.update_items(class_names)
            self.menu.correctAction.setEnabled(True)
            self.imageModification(True)
            self.update_cursor()
        else:
            self.statusBar().showMessage("The new name can't be empty")

    def newbbox(self):
        # self.menu.CreateMaskAction.setEnabled(False)
        # dialog.setMo
        # self.dialog.exec()
        self.mode = 'bbox'
        self.updateModeButtons()
        self.current_cursor = QCursor(Qt.CrossCursor)
        self.setCursor(self.current_cursor)
        self.viewer.bbox = True

    def clear(self):
        self.imageModification(False)
        self.instancesList.clear()
        self.map_image.clear()
        self.viewer.clear()
        self.mode = None
        self.menu.CreateAction.setEnabled(True)
        self.menu.CreateMaskAction.setEnabled(True)
        self.menu.CreateBboxAction.setEnabled(True)
        self.addLabelsliders(False)
        self.addCursorsliders(False)
        self.menu.undoAction.setEnabled(False)
        self.loadImage()
        self.statusBar().showMessage("Cleaned")

    def contextMenuEvent(self, event):
        contextMenu = QMenu(self)
        contextMenu.addAction(self.menu.drawAction)
        contextMenu.addAction(self.menu.eraseAction)
        contextMenu.addAction(self.menu.doneAction)
        contextMenu.addAction(self.menu.correctAction)
        contextMenu.addAction(self.menu.clearAction)
        contextMenu.exec_(self.mapToGlobal(event.pos()))

    def set_draw_parameters(self, draw=False, rect=False, drawing=False, pixel=False):
        self.viewer.draw = draw
        self.viewer.rect = rect
        self.viewer.drawing_mode = drawing
        self.viewer.pixel_annotation = pixel

    def draw_mode(self, mode):
        # print(self.map_image.channel)
        self.viewer.brushSize = self.cursor_size
        if self.map_image.channel == -1 and self.instancesList.count() > 0 and self.mode == 'seg':
            self.maskList(0)
        if (mode == 'pen'):
            self.addCursorsliders(add=True)
            self.statusBar().showMessage("Press Space key to switch to eraser")
            self.set_draw_parameters(draw=True, drawing=True)
            self.update_cursor()
            self.viewer.setDragMode(QGraphicsView.NoDrag)

        elif mode == 'erase':
            self.addCursorsliders(add=True)
            self.statusBar().showMessage("Press Space key to switch to pen")
            self.set_draw_parameters(draw=True)
            self.update_cursor()
            self.viewer.setDragMode(QGraphicsView.NoDrag)

        elif mode == 'fill':
            self.statusBar().showMessage('''Press Space key to switch to unfill
             Press Shift key to switch views''')
            # self.current_cursor = QCursor(Qt.PointingHandCursor)
            self.set_draw_parameters(pixel=True, drawing=True)
            self.update_cursor()
            # self.setCursor(self.current_cursor)

        elif mode == 'unfill':
            self.statusBar().showMessage('''Press Space key to switch to fill
            Press Shift key to switch views''')
            # self.current_cursor = QCursor(Qt.PointingHandCursor)
            self.set_draw_parameters(pixel=True)
            self.update_cursor()
            # self.viewer.pixel_annotation = True
            # self.setCursor(self.current_cursor)

        elif mode == 'drag':
            self.menu.doneAction.setEnabled(False)
            self.setCursor(self.current_cursor)
            self.set_draw_parameters()

        elif mode == 'done':
            # print('done')
            self.statusBar().showMessage("Done")
            # Update the buttons and sliders
            self.menu.doneAction.setEnabled(False)
            self.hasMask()
            self.fillModification(False)
            self.addPixmapsliders(add=False)
            self.addLabelsliders(add=False)
            self.addCursorsliders(add=False)

            # Update the cursor
            self.current_cursor = QCursor(Qt.ArrowCursor)
            self.setCursor(self.current_cursor)
            self.set_draw_parameters()
            # self.view_segments = True
            self.toggleView(original=True)

        elif mode == 'undo':
            # print(self.mode, self.viewer.pixel_annotation)
            if self.mode == 'seg':
                self.map_image.undo_action()
                if self.map_image.colors is None:
                    self.clear()
                    return 0
                self.instancesList.clear()
                for i, class_name in enumerate(self.map_image.class_names):
                    r, g, b = self.map_image.colors[i]
                    item = QListWidgetItem(class_name)
                    item.setCheckState(Qt.Checked)
                    pixmap = QPixmap(15, 15)
                    pixmap.fill(QColor(int(255 * r), int(255 * g), int(255 * b)))
                    item.setIcon(QIcon(pixmap))
                    self.instancesList.addItem(item)
                    # self.instancesList.setItemWidget(item, widget)
                self.map_image.mask_items = list(range(len(self.map_image.class_names)))
                masked_image = self.map_image.apply_masks_to_image()
                self.viewer.setPixmapImage(masked_image)
                if len(self.map_image.masks_record) == 0:
                    self.menu.undoAction.setEnabled(False)
            elif self.mode == 'bbox':
                self.viewer.undo_action()
                self.uptade_instances()
                if len(self.viewer.bbox_record) == 1:
                    self.menu.undoAction.setEnabled(False)

        elif mode == 'rect':
            self.menu.doneAction.setEnabled(True)
            self.current_cursor = QCursor(Qt.CrossCursor)
            self.setCursor(self.current_cursor)
            # self.viewer.rect = True
            self.set_draw_parameters(rect=True)
            self.viewer.setDragMode(QGraphicsView.NoDrag)

        elif mode == 'close':
            self.viewer.closeMask()

    def itemList(self, item):
        if self.filesList.count() > 1:
            self.autosave(self.last_image_path)
            if (self.filesList.item(self.filesList.currentRow()).text() == item.text()):
                self.image_path = item.data(100)
                if item.checkState() == Qt.Checked:
                    self.json_path = item.data(101)
                    if self.json_path is None:
                        self.json_path = ""
                        item.setCheckState(Qt.Unchecked)
                else:
                    self.json_path = ""
                self.update_arrows()
                self.open_file('next')
            else:
                item.setCheckState(Qt.Unchecked)

    def instanceListEdit(self, id=None, title=None):
        if id is None:  # If an item is selected from the list
            self.row = self.instancesList.currentRow()
            self.dialog.lineedit.setText(self.instancesList.item(self.row).text())
        else:  # If a new item is being created
            self.row = -1
            self.new_color = id
            self.dialog.lineedit.setText("")
            self.dialog.title = title
            self.dialog.update()
        self.dialog.lableList.clear()
        self.dialog.lableList.addItems(self.label_items)
        self.dialog.exec()

    def instanceListDelete(self):
        row = self.instancesList.currentRow()
        if self.mode == 'seg':
            self.map_image.do_action()
            self.map_image.colors.pop(row)
            self.map_image.class_names.pop(row)
            self.map_image.masks = np.delete(self.map_image.masks, row, axis=0)
            # self.map_image.masks_record.append(self.map_image.masks.copy())

        elif self.mode == 'bbox':
            id = self.instancesList.item(row).data(100)
            self.viewer.deleteBbox('selected', id)

        self.instancesList.takeItem(row)
        self.instanceList()
        self.menu.undoAction.setEnabled(True)

    def instanceList(self):
        row = self.instancesList.currentRow()
        # print(row)
        if self.mode == 'seg':
            if row >= 0:
                self.mask_items = []
                for index in range(self.instancesList.count()):
                    if self.instancesList.item(index).checkState() == Qt.Checked:
                        self.mask_items.append(index)
                self.map_image.channel = row
                self.color_draw = self.map_image.colors[row]
                masked_image = self.map_image.generate_mask(self.mask_items)
                self.viewer.setPixmapImage(masked_image)
                self.update_cursor(onList=True)
            else:
                self.clear()

        elif self.mode == 'bbox':
            self.bbox_items = {}
            for index in range(self.instancesList.count()):
                state = self.instancesList.item(index).checkState() == Qt.Checked
                self.bbox_items[self.instancesList.item(index).data(100)] = state
            # show_bbox = []
            # for index in self.mask_items:
            # show_bbox.append(self.instancesList.item(index).data(100))
            # print(self.instancesList.item(index))
            # print(index)
            # print(self.instancesList.item(index).data(100))
            # print(self.bbox_items)
            if row >= 0:
                row_id = self.instancesList.item(row).data(100)
                self.viewer.modificationBbox(self.bbox_items, row_id)
            else:
                self.viewer.modificationBbox(self.bbox_items, row)

    def uncheckInstanceList(self):
        if self.hideInstances:
            for index in range(self.instancesList.count()):
                if self.instancesList.item(index).checkState() == Qt.Checked:
                    self.all_checked_items.append(index)
                    self.instancesList.item(index).setCheckState(Qt.Unchecked)

            masked_image = self.map_image.generate_mask([])
            self.viewer.setPixmapImage(masked_image)
            self.hideInstances = False
        else:
            for index in self.all_checked_items:
                self.instancesList.item(index).setCheckState(Qt.Checked)

            masked_image = self.map_image.generate_mask(self.all_checked_items)
            self.viewer.setPixmapImage(masked_image)
            self.hideInstances = True
            self.all_checked_items = []

    def maskList(self, channel):
        # print(channel)
        self.instancesList.setCurrentRow(channel)
        self.mask_items = []
        for index in range(self.instancesList.count()):
            if self.instancesList.item(index).checkState() == Qt.Checked:
                self.mask_items.append(index)

        self.map_image.channel = channel
        masked_image = self.map_image.generate_mask(self.mask_items)
        self.viewer.setPixmapImage(masked_image)
        self.color_draw = self.map_image.colors[channel]

    def bboxList(self, id):
        for index in range(self.instancesList.count()):
            if self.instancesList.item(index).data(100) == id:
                self.instancesList.setCurrentRow(index)

    def closeEvent(self, event):
        self.settings.setValue('window size', self.size())
        self.settings.setValue('window position', self.pos())
        self.settings.setValue('configuration', self.confInfo)
        self.logger.info("Configuration correctly saved")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

        if event.key() == Qt.Key_F11:
            if self.isMaximized():
                self.showNormal()
            else:
                self.showMaximized()

        if event.key() == Qt.Key_Space:
            if self.viewer.draw or self.viewer.pixel_annotation:
                self.update_cursor_toggle()

            # if self.viewer.pixel_annotation:
            #     self.update_cursor_toggle()

            if self.map_image is not None:
                if self.map_image.mask_roi is not None:
                    self.map_image.flip_roi_mask()
                    masked_image = self.map_image.apply_masks_to_image()
                    self.viewer.setPixmapImage(masked_image)

        if event.key() == Qt.Key_Delete:
            self.instanceListDelete()
            # self.viewer.deleteBbox(type='selected')
            # self.close()
        if event.key() == Qt.Key_Shift:
            if self.view_segments is not None:
                self.toggleView()

        if event.key() == Qt.Key_Up:
            print('up')
            # if self.viewer.draw:
            #     self.cursor_size +=2
            #     self.update_cursor()
        if event.key() == Qt.Key_Down:
            print('down')
            # if self.viewer.draw:
            #     self.cursor_size -=2
            #     self.update_cursor()
        # print(self.cursor_size)

    def openListImages(self, imageList):
        self.open_file('labeled_dir', imageList)

    def modifyLabel(self, newLabel):
        if newLabel:
            if self.row != -1:
                self.instancesList.item(self.row).setText(newLabel)
                if self.mode == 'bbox':
                    self.viewer.updatebbox(self.instancesList.item(self.row).data(100), newLabel)
                if self.mode == 'seg':
                    self.map_image.class_names[self.row] = self.instancesList.item(self.row).text()

                # elif self.mode == 'seg':
                #     self.new_seg_class = newLabel

            # if a new item is being created
            else:
                if self.mode == 'bbox':
                    r, g, b, id = self.new_color
                    item = QListWidgetItem(newLabel)
                    item.setData(100, id)
                    item.setCheckState(Qt.Checked)
                    pixmap = QPixmap(15, 15)
                    pixmap.fill(QColor(r, g, b))
                    item.setIcon(QIcon(pixmap))
                    self.instancesList.addItem(item)
                    self.viewer.updatebbox(id, newLabel)

                elif self.mode == 'seg':
                    self.new_seg_class = newLabel
                # elif self.mode == 'spixel':
                #     r, g, b = self.new_color
                #     item = QListWidgetItem(newLabel)
                #     item.setCheckState(Qt.Checked)
                #     pixmap = QPixmap(15, 15)
                #     pixmap.fill(QColor(r, g, b))
                #     item.setIcon(QIcon(pixmap))
                #     self.instancesList.addItem(item)

            self.update_items([newLabel])
            self.labelDialogResponse = True
        else:
            self.labelDialogResponse = False

    # def mouseReleaseEvent(self, event):
    #     undo_mode = self.viewer.save_current_bbox(has_changed=False)
    #     print(undo_mode)
    #     self.menu.undoAction.setEnabled(undo_mode)
    def open_label(self, jsonname):
        # jsonname = (filename.split('/')[-1]).split('.')[0] + '.json'
        # print(jsonname)
        with open(jsonname) as json_file:
            data = json.load(json_file)
        annotations = data['annotations']
        self.mode = data['type']
        if self.mode == 'seg':
            classes = list()
            masks = list()
            for instance in annotations:
                classes.append(instance['category'])
                masks.append(utils.rle2mask(instance['segmentation']))
            self.auto_seg(mode='json', json_data=(np.array(masks), None, classes))
        elif self.mode == 'bbox':
            classes = list()
            bboxes = list()
            for instance in annotations:
                classes.append(instance['category'])
                bboxes.append(instance['bbox'])
            self.auto_bbox(mode='json', json_data=(None, bboxes, classes))
        self.menu.doneAction.setEnabled(False)
        self.menu.undoAction.setEnabled(False)

    def open_file(self, type, files=None):
        self.instancesList.clear()
        self.viewer.deleteBbox('all')
        self.viewer.bbox_record = []
        self.undo_bbox_record = []
        if type == 'file':
            self.image_path, _ = QFileDialog.getOpenFileName(
                self, "Open Image", "", "PNG or JPEG(*.png *.jpg *.jpeg );;;;All Files(*.*) ")
            if self.image_path != '':
                # print(self.image_path)
                # self.filesList.clear()
                self.instancesList.clear()
                # self.viewer.deleteBbox('all')
                self.images_path.append(self.image_path)
                item = QListWidgetItem(self.image_path.split('/')[-1])
                item.setData(100, self.image_path)
                self.json_path = utils.pathpng2json(self.image_path)
                if os.path.isfile(self.json_path):
                    # print(self.json_path, 'exists ...')
                    item.setCheckState(Qt.Checked)
                    item.setData(101, self.json_path)
                else:
                    item.setCheckState(Qt.Unchecked)

                self.filesList.addItem(item)
                self.filesList.setCurrentRow(self.filesList.count() - 1)

        elif type == 'dir':
            dir_ = QFileDialog.getExistingDirectory(self, 'Select a folder:', '',
                                                    QFileDialog.ShowDirsOnly)
            if dir_ != '':
                empty_dir = True
                self.statusBar().showMessage("Directory empty")
                files = os.listdir(dir_)
                for file in files:
                    if file.split('.')[-1] == 'png' or file.split('.')[-1] == 'jpg' or file.split(
                            '.')[-1] == 'jpeg':
                        empty_dir = False
                        self.statusBar().showMessage("Directory opened")
                        break

                if not empty_dir:
                    self.images_folder = dir_
                    self.labellistImages.init(dir_ + '/')
                    self.labellistImages.exec()
                # self.image_path = ''

        elif type == 'labeled_dir':
            len_prev_images = self.filesList.count()
            self.instancesList.clear()
            # self.viewer.deleteBbox('all')
            files = sorted(files)
            for file in files:
                if file.split('.')[-1] == 'png' or file.split('.')[-1] == 'jpg' or file.split(
                        '.')[-1] == 'jpeg':
                    self.image_path = file
                    self.images_path.append(self.image_path)
                    item = QListWidgetItem(file.split('/')[-1])
                    item.setData(100, self.image_path)
                    # Chech if there is a label file
                    self.json_path = utils.pathpng2json(self.image_path)
                    if os.path.isfile(self.json_path):
                        item.setCheckState(Qt.Checked)
                        item.setData(101, self.json_path)
                    else:
                        item.setCheckState(Qt.Unchecked)
                    self.filesList.addItem(item)

            self.image_path = self.images_path[len_prev_images]
            self.filesList.setCurrentRow(len_prev_images)
            self.json_path = utils.pathpng2json(self.image_path)

        if self.image_path != '' and type != 'dir':
            self.last_image_path = self.image_path
            self.addImagesliders(add=True)
            self.enableActions()
            self.map_image = map_image(self.image_path, self.viewer.size())
            self.pil_image = self.map_image.pil_image
            self.pixmap_image = QPixmap(self.image_path)

            if self.image_brigtness is not None:
                self.changeValue(('imgb', self.image_brigtness))
            if self.labels_brigtness is not None:
                self.changeValue(('labelb', self.label_brigtness))

            self.loadImage()
            self.setWindowTitle(self.image_path)

            self.menu.CreateAction.setEnabled(True)
            self.menu.CreateMaskAction.setEnabled(True)
            self.menu.CreateBboxAction.setEnabled(True)
            self.update_arrows()
            self.viewer.zoom('fit')
            # path_list = self.image_path.split('/')
            # path_list[-1] = path_list[-1].split('.')[0] + '.json'
            # self.json_path = "/" + os.path.join(*path_list)
            # # print(self.json_path)
            if os.path.isfile(self.json_path):
                # print(self.json_path, 'exists ...')
                self.open_label(self.json_path)

    def orderImage(self, mode):
        self.autosave(self.image_path)
        if mode == 'next':
            index = self.images_path.index(self.image_path) + 1
        elif mode == 'prev':
            index = self.images_path.index(self.image_path) - 1
        self.filesList.setCurrentRow(index)
        self.image_path = self.images_path[index]
        if self.filesList.item(index).checkState() == Qt.Checked:
            self.json_path = self.filesList.item(index).data(101)
        else:
            self.json_path = ""
        self.update_arrows()
        self.open_file('next')

    def autosave(self, last_image_path):
        save = False
        # if self.instancesList.count() > 0:
        if self.mode == 'bbox':
            # print(len(self.viewer.bbox_record))
            if len(self.viewer.bbox_record) > 1:
                save = True
                self.viewer.bbox_record = list()
        if self.mode == 'seg':
            if len(self.map_image.masks_record) > 0:
                save = True
                self.map_image.masks_record = list()
        if save:
            if self.saveLabelDialog():
                self.save(mode='auto', image_path=last_image_path)

    def saveButtonAction(self, mode):
        self.save(mode=mode, image_path=self.image_path)

    def save(self, mode, image_path=None):
        self.menu.undoAction.setEnabled(False)
        if self.mode == 'bbox':
            self.viewer.bbox_record = list()
        elif self.mode == 'seg':
            self.map_image.masks_record = list()

        if image_path is None:
            image_path = self.images_path

        file_name = image_path.split('/')[-1]

        label_json = {
            'version': '1.0.0',
            "image": file_name,
            "annotations": None,
            "type": self.mode
        }
        instances = list()
        instance_json = {
            "category": None,
            "iscrowd": 0,
            "segmentation": [],
            "area": None,
            "bbox": None
        }
        filePath = '.'
        # print(self.map_image.class_names)
        # print(self.map_image.masks.shape)
        if mode == 'save_as':
            filePath, _ = QFileDialog.getSaveFileName(self, "Save Image",
                                                      utils.pathpng2json(image_path),
                                                      "JSON(*.json)")
        if filePath != '':
            if self.mode == 'seg':
                for index, classname in enumerate(self.map_image.class_names):
                    instance = instance_json.copy()
                    instance["category"] = classname
                    instance["segmentation"] = utils.mask2rle(self.map_image.masks[index])
                    instances.append(instance)
            elif self.mode == 'bbox':
                bboxes = self.viewer.save_all()
                for coordinates, classname, area in bboxes:
                    instance = instance_json.copy()
                    instance["category"] = classname
                    instance["bbox"] = coordinates
                    instance["area"] = area
                    instances.append(instance)
            # label_json['shapes'] = self.save_ann.masks_to_json(self.map_image.masks, labels)
            # _, label_json['imageHeight'], label_json['imageWidth'] = self.map_image.masks.shape
            label_json["annotations"] = instances
            with open(image_path.split('.')[0] + '.json', 'w') as f:
                json.dump(label_json, f)

            # row = self.filesList.currentRow()
            for index in range(self.filesList.count()):
                if self.filesList.item(index).text() == file_name:
                    row = index
            item = self.filesList.item(row)
            item.setCheckState(Qt.Checked)
            self.json_path = utils.pathpng2json(image_path)
            item.setData(101, self.json_path)

    def save1(self, mode):
        filePath = self.sil_seg_model.mask_path
        path = filePath.split('/')
        path[-2] = 'corrected'
        filePath = ('/').join(path)
        if mode == 'save_as':
            filePath, _ = QFileDialog.getSaveFileName(
                self, "Save Image", filePath, "PNG(*.png);;JPEG(*.jpg *.jpeg);;All Files(*.*) ")
        if filePath != '':
            # if not filePath.split('.')[-1] == "png" or not filePath.split('.')[-1] == "jpg":
            #     filePath +='.png'
            mask = self.map_image.masks[0].astype('uint8') * 255
            imageio.imwrite(filePath, mask)
            self.menu.saveAction.setEnabled(False)

    def setSizeLabel(self, factor):
        self.menu.sizeLabel.setText(factor + "%")
        '''
        if self.cursor_factor is None:
            self.cursor_factor = int(factor)
        else:
            self.cursor_size = int((int(factor)/ self.cursor_factor)* self.cursor_size)
        '''
        # self.image_size_widget.setValue(int(factor))
        # self.image_brigtness_widget.setValue(0)
        # self.labels_brigtness_widget.setValue(0)
        # self.ncompactsness_widget.setValue(20)
        # self.segments_size_widget.setValue(200)
        # self.cursor_size_widget.setValue(self.cursor_size)

    def toggleView(self, original=False):
        if self.view_segments:
            self.map_image.array_image = np.array(self.pil_image)
            self.view_segments = False
        else:
            self.map_image.array_image = self.marked
            self.view_segments = True
        if original:
            self.map_image.array_image = np.array(self.pil_image)
            self.view_segments = None

        masked_image = self.map_image.apply_masks_to_image()
        self.viewer.setPixmapImage(masked_image)

    def updateModeButtons(self):
        if self.mode == 'seg':
            self.menu.bboxMaskRCNNAction.setEnabled(False)
            self.menu.CreateBboxAction.setEnabled(False)
        elif self.mode == 'bbox':
            self.menu.CreateMaskAction.setEnabled(False)
            self.menu.segCustomAction.setEnabled(False)
            self.menu.segMaskRCNNAction.setEnabled(False)
            # self.menu.silSegmentatinoAction.setEnabled(False)
            self.menu.slicSegmentatinoAction.setEnabled(False)

    def update_cursor(self, onList=False):
        if self.viewer.draw:
            if self.viewer.drawing_mode:
                self.current_cursor = utils.cursor('pen', self.cursor_size, self.color_draw)
            else:
                self.current_cursor = utils.cursor('eraser', self.cursor_size, self.color_draw)
        elif self.viewer.pixel_annotation:
            if self.viewer.drawing_mode:
                self.current_cursor = utils.cursor('fill', self.cursor_size, self.color_draw)
            else:
                self.current_cursor = utils.cursor('unfill', self.cursor_size, self.color_draw)
        if onList:
            self.setCursor(QCursor(Qt.ArrowCursor))
        else:
            self.setCursor(self.current_cursor)

    def update_cursor_toggle(self):
        if self.viewer.draw:
            if self.viewer.drawing_mode:
                self.viewer.drawing_mode = False
                self.current_cursor = utils.cursor('eraser', self.cursor_size, self.color_draw)
                self.statusBar().showMessage("Press Space key to switch to pen")
            else:
                self.viewer.drawing_mode = True
                self.current_cursor = utils.cursor('pen', self.cursor_size, self.color_draw)
                self.statusBar().showMessage("Press Space key to switch to eraser")

        elif self.viewer.pixel_annotation:
            if self.viewer.drawing_mode:
                self.viewer.drawing_mode = False
                self.current_cursor = utils.cursor('unfill', self.cursor_size, self.color_draw)
                self.statusBar().showMessage('''Press Space key to switch to fill
                Press Shift key to switch views''')

            else:
                self.viewer.drawing_mode = True
                self.current_cursor = utils.cursor('fill', self.cursor_size, self.color_draw)
                self.statusBar().showMessage('''Press Space key to switch to unfill
                Press Shift key to switch views''')

        self.setCursor(self.current_cursor)

    def uptade_instances(self):
        self.instancesList.clear()
        instances = self.viewer.instances
        instances = dict(sorted(instances.items(), key=lambda item: item[0]))
        # print(instances)
        for id, [label, color, isVisible] in instances.items():
            r, g, b = color
            item = QListWidgetItem(label)
            item.setData(100, id)
            if isVisible:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
            pixmap = QPixmap(15, 15)
            pixmap.fill(QColor(int(r), int(g), int(b)))
            item.setIcon(QIcon(pixmap))
            self.instancesList.addItem(item)

    def update_arrows(self):
        self.imageModification(False)
        self.draw_mode(mode='done')
        # print('update', self.map_image.channel)
        index = self.images_path.index(self.image_path)
        if len(self.images_path) > 1:
            self.menu.nextImgAction.setEnabled(True)
        if index > 0:
            self.menu.preImgAction.setEnabled(True)

        if index == len(self.images_path) - 1:
            self.menu.nextImgAction.setEnabled(False)
        if index == 0:
            self.menu.preImgAction.setEnabled(False)

    def update_items(self, add_classes=[]):
        self.labelList.clear()
        self.label_items = sorted(list(set(list(self.label_items) + add_classes)))
        self.labelList.addItems(self.label_items)

    def update_zoom(self, ratio):
        # if ratio>1:
        #     self.cursor_size *=1.5
        # else:
        #     self.cursor_size *=0.8
        # print(self.cursor_size)
        # self.update_cursor()
        pass

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()

            links = []
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    links.append(str(url.toLocalFile()))
                else:
                    links.append(str(url.toString()))
            # self.addItems(links)
            self.logger.debug(links)
        else:
            event.ignore()

    def enableActions(self):
        self.menu.zoomOrgAction.setEnabled(True)
        self.menu.zoomInAction.setEnabled(True)
        self.menu.zoomOutAction.setEnabled(True)
        self.menu.zoomFitAction.setEnabled(True)
        self.menu.zoomDragAction.setEnabled(True)

        self.menu.autoSegAction.setEnabled(True)
        self.menu.autoBboxAction.setEnabled(True)
        self.menu.segCustomAction.setEnabled(True)
        self.menu.segMaskRCNNAction.setEnabled(True)
        self.menu.bboxMaskRCNNAction.setEnabled(True)
        # self.menu.silSegmentatinoAction.setEnabled(True)
        self.menu.slicSegmentatinoAction.setEnabled(True)

        # self.image_size_widget.slider.setEnabled(True)
        self.image_brigtness_widget.slider.setEnabled(True)

    def hasMask(self, state=None):
        if state is None:
            if type(self.map_image.masks) is list:
                state = False
            else:
                state = True
        self.menu.drawMenuAction.setEnabled(state)
        self.menu.drawAction.setEnabled(state)
        self.menu.eraseAction.setEnabled(state)
        if state:
            self.addLabelsliders(add=True)

    def fillModification(self, state):
        self.menu.fillMenuAction.setEnabled(state)
        self.menu.fillAction.setEnabled(state)
        self.menu.unfillAction.setEnabled(state)

    def imageModification(self, state):
        if not self.viewer.pixel_annotation:
            self.menu.correctAction.setEnabled(state)
            self.menu.drawMenuAction.setEnabled(state)
            self.menu.hideAction.setEnabled(state)
            self.menu.maxBlobAction.setEnabled(state)

        self.menu.doneAction.setEnabled(state)
        self.menu.drawAction.setEnabled(state)
        self.menu.eraseAction.setEnabled(state)
        # self.menu.saveMenuAction.setEnabled(state)
        self.menu.saveAction.setEnabled(state)
        self.menu.saveasAction.setEnabled(state)
        self.menu.clearAction.setEnabled(state)
        self.menu.undoAction.setEnabled(state)
        self.labels_brigtness_widget.slider.setEnabled(state)
        self.cursor_size_widget.slider.setEnabled(state)
        self.segments_size_widget.slider.setEnabled(state)
        self.ncompactsness_widget.slider.setEnabled(state)

    def bboxModification(self, state):
        # self.menu.saveMenuAction.setEnabled(state)
        self.menu.saveAction.setEnabled(state)
        self.menu.saveasAction.setEnabled(state)
        self.menu.clearAction.setEnabled(state)
        self.menu.undoAction.setEnabled(state)
        self.labels_brigtness_widget.slider.setEnabled(state)
        self.cursor_size_widget.slider.setEnabled(state)
        self.segments_size_widget.slider.setEnabled(state)
        self.ncompactsness_widget.slider.setEnabled(state)

    def disableActions(self):
        self.menu.correctAction.setEnabled(False)
        self.menu.hideAction.setEnabled(False)
        self.menu.maxBlobAction.setEnabled(False)

        self.menu.drawMenuAction.setEnabled(False)
        self.menu.drawAction.setEnabled(False)
        self.menu.eraseAction.setEnabled(False)
        self.menu.fillMenuAction.setEnabled(False)
        self.menu.fillAction.setEnabled(False)
        self.menu.unfillAction.setEnabled(False)
        self.menu.nextImgAction.setEnabled(False)
        self.menu.preImgAction.setEnabled(False)

        self.menu.saveAction.setEnabled(False)
        self.menu.saveasAction.setEnabled(False)
        self.menu.CreateAction.setEnabled(False)
        self.menu.CreateMaskAction.setEnabled(False)
        self.menu.CreateBboxAction.setEnabled(False)
        self.menu.doneAction.setEnabled(False)
        self.menu.undoAction.setEnabled(False)

        self.menu.clearAction.setEnabled(False)
        self.menu.zoomOrgAction.setEnabled(False)
        self.menu.zoomInAction.setEnabled(False)
        self.menu.zoomOutAction.setEnabled(False)
        self.menu.zoomFitAction.setEnabled(False)
        self.menu.zoomDragAction.setEnabled(False)

        self.menu.autoSegAction.setEnabled(False)
        self.menu.autoBboxAction.setEnabled(False)
        self.menu.segCustomAction.setEnabled(False)
        self.menu.segMaskRCNNAction.setEnabled(False)
        self.menu.bboxMaskRCNNAction.setEnabled(False)
        # self.menu.silSegmentatinoAction.setEnabled(False)
        self.menu.slicSegmentatinoAction.setEnabled(False)

        # self.image_size_widget.slider.setEnabled(False)
        self.image_brigtness_widget.slider.setEnabled(False)
        self.labels_brigtness_widget.slider.setEnabled(False)
        self.cursor_size_widget.slider.setEnabled(False)
        self.segments_size_widget.slider.setEnabled(False)
        self.ncompactsness_widget.slider.setEnabled(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec_())
