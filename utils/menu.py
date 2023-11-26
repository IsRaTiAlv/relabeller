from PyQt5.QtCore import Qt, QSize, QRect
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QApplication, QAction, QLineEdit, QMenu, QWidget, QHBoxLayout, QPushButton, QToolButton
import logging
import sys


class Action(QAction):

    def __init__(self, name, info):
        ''' Creates an action with the properties stated in info variable '''
        super().__init__(name)
        if info['icon'] is not None:
            self.icon = QIcon('icons/' + info['icon'])
            self.setIcon(self.icon)
        if info['key'] is not None:
            key = info['key']

            if key == 'Right':
                key = Qt.Key_Down
                # key = Qt.Key_Right
            if key == 'Left':
                key = Qt.Key_Up
                # key = Qt.Key_Left
            self.setShortcut(key)
            self.setToolTip(f'{name} -> {key}')
        if info['tip'] is not None:
            self.setStatusTip(info['tip'])


class TAction(QAction):

    def __init__(self, name, info):
        ''' Creates an action with the properties stated in info variable '''
        super().__init__(name)
        self.setCheckable(True)
        if info['icon'] is not None:
            self.icon = QIcon('icons/' + info['icon'])
            self.setIcon(self.icon)
        if info['key'] is not None:
            key = info['key']
            self.setToolTip(f'{name} -> {key}')
            if key == 'Right':
                key = Qt.Key_Down
                # key = Qt.Key_Right
            if key == 'Left':
                key = Qt.Key_Up
                # key = Qt.Key_Left
            self.setShortcut(key)
        if info['tip'] is not None:
            self.setStatusTip(info['tip'])


class menu(QMainWindow):

    def __init__(self, shortCuts):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        # self.logger.info("initializing menu")
        # self.logger.info(shortCuts)

        self.openAction = Action('OpenFile', shortCuts['OpenFile'])
        self.openDirAction = Action('OpenDir', shortCuts['OpenDir'])
        self.nextImgAction = Action('Next', shortCuts['NextImg'])
        self.preImgAction = Action('Prev', shortCuts['PrevImg'])
        self.saveAction = Action('Save', shortCuts['Save'])
        self.saveasAction = Action('SaveAs', shortCuts['SaveAs'])

        self.clearAction = Action('Clear', shortCuts['Clear'])
        self.CreateMaskAction = Action('NewMask', shortCuts['NewMask'])
        self.CreateBboxAction = Action('NewBBox', shortCuts['NewBBox'])
        self.drawAction = Action('Draw', shortCuts['Draw'])
        self.eraseAction = Action('Erase', shortCuts['Erase'])
        self.fillAction = Action('Fill', shortCuts['Fill'])
        self.unfillAction = Action('Unfill', shortCuts['Unfill'])
        self.doneAction = Action('Done', shortCuts['Done'])
        self.undoAction = Action('Undo', shortCuts['Undo'])
        self.zoomOrgAction = Action('Original', shortCuts['Original'])
        self.zoomInAction = Action('ZoomIn', shortCuts['ZoomIn'])
        self.zoomOutAction = Action('ZoomOut', shortCuts['ZoomOut'])
        self.zoomFitAction = Action('Fit', shortCuts['Fit'])
        self.zoomDragAction = Action('Drag', shortCuts['Drag'])
        self.autoSegAction = Action('AutoMask', shortCuts['AutoMask'])
        self.autoBboxAction = Action('AutoBbox', shortCuts['AutoBbox'])

        # self.hideAction = QToolButton(self)
        # self.hideAction.setIcon(QIcon('icons/visible.png'))
        # self.hideAction.setCheckable(True)

        self.hideAction = TAction('Hide', shortCuts['Hide'])
        self.correctAction = Action('Correct', shortCuts['Correct'])
        self.maxBlobAction = Action('MaxBlob', shortCuts['MaxBlob'])

        self.segCustomAction = Action('Seg_Custom', shortCuts['Seg_Custom'])
        self.segMaskRCNNAction = Action('Seg_MaskRCNN', shortCuts['Seg_MaskRCNN'])
        self.bboxMaskRCNNAction = Action('BBox_MaskRCNN', shortCuts['BBox_MaskRCNN'])
        self.slicSegmentatinoAction = Action('SLIC_KMeans', shortCuts['SLIC_KMeans'])
        self.configAction = Action('Configuration', shortCuts['Configuration'])
        self.helpAction = Action('Help', shortCuts['Help'])

        # self.openAction = QAction(QIcon('icons/openf.png'), "Open file", self)
        # self.openAction.setShortcut("Ctrl+O")
        # self.openAction.setStatusTip("Open image .png .jpg .jpeg")

        # self.openDirAction = QAction(QIcon('icons/opend.png'), "Open Dir", self)
        # self.openDirAction.setShortcut("Ctrl+D")
        # self.openDirAction.setStatusTip("Open a directory and load all the images in .png .jpg and .jpeg format")
        #
        # self.nextImgAction = QAction(QIcon('icons/next.png'), "Next img", self)
        # self.nextImgAction.setShortcut(QtCore.Qt.Key_Right)
        # self.nextImgAction.setStatusTip("Move to the following image in the file list if any")
        #
        # self.preImgAction = QAction(QIcon('icons/prev.png'), "Prev img", self)
        # self.preImgAction.setShortcut(QtCore.Qt.Key_Left)
        # self.preImgAction.setStatusTip("Move to the previous image in the file list if any")

        # self.saveAction = QAction(QIcon("icons/save.png"), "Save", self)
        # self.saveAction.setShortcut("Ctrl+S")
        # self.saveAction.setStatusTip('Save the annotations in a JSON file')

        # self.saveasAction = QAction(QIcon("icons/save-as.png"), "Save as", self)
        # self.saveasAction.setShortcut("Shift+S")
        # self.saveasAction.setStatusTip('Save the annotations in a different formats')

        # self.save_menu = QMenu()
        # self.save_menu.addAction(self.saveAction)
        # self.save_menu.addAction(self.saveasAction)
        # self.saveMenuAction = QAction(QIcon("icons/save.png"), "Save", self)
        # self.saveMenuAction.setStatusTip('Save the image and the annotations with the current file name')
        # self.saveMenuAction.setMenu(self.save_menu)

        # self.clearAction = QAction(QIcon("icons/clear.png"), "Clear", self)
        # self.clearAction.setShortcut("Ctrl+C")
        #
        # self.CreateMaskAction = QAction(QIcon('icons/mask.png'), "New Mask", self)
        # self.CreateMaskAction.setShortcut("Shift+M")
        #
        # self.CreateBboxAction = QAction(QIcon('icons/boxes.png'), "New BBox", self)
        # self.CreateBboxAction.setShortcut("Shift+B")

        self.create_menu = QMenu()
        self.create_menu.addAction(self.CreateMaskAction)
        self.create_menu.addAction(self.CreateBboxAction)
        self.CreateAction = QAction(QIcon('icons/draw.png'), "New", self)
        self.CreateAction.setShortcut("Ctrl+N")
        self.CreateAction.setMenu(self.create_menu)

        # self.drawAction = QAction(QIcon('icons/pen.png'), "Draw", self)
        # self.drawAction.setShortcut("Shift+D")

        # self.eraseAction = QAction(QIcon('icons/eraser.png'), "Erase", self)
        # self.eraseAction.setShortcut("Shift+E")

        self.paint_menu = QMenu()
        self.paint_menu.addAction(self.drawAction)
        self.paint_menu.addAction(self.eraseAction)
        self.drawMenuAction = QAction(QIcon('icons/pen.png'), "Draw", self)
        self.drawMenuAction.setShortcut("Shift+D")
        self.drawMenuAction.setMenu(self.paint_menu)

        # self.fillAction = QAction(QIcon('icons/fill.png'), "Fill", self)
        # self.unfillAction = QAction(QIcon('icons/clear.png'), "Unfill", self)
        self.fill_menu = QMenu()
        self.fill_menu.addAction(self.fillAction)
        self.fill_menu.addAction(self.unfillAction)
        self.fillMenuAction = QAction(QIcon('icons/fill.png'), "Fill", self)
        self.fillMenuAction.setMenu(self.fill_menu)

        # self.doneAction = QAction(QIcon('icons/done.png'), "Done", self)
        # self.doneAction.setShortcut("Shift+Enter")
        #
        # self.undoAction = QAction(QIcon('icons/undo.png'), "Undo", self)
        # self.undoAction.setShortcut("Ctrl+Z")
        #
        # self.correctAction = QAction(QIcon('icons/correct.png'), "Correct", self)
        # self.correctAction.setShortcut("Shift+C")
        #
        # self.zoomOrgAction = QAction(QIcon('icons/zoom_original.png'), "Original\nsize", self)
        # # self.zoomOrgAction.setShortcut("Shift+C")
        #
        # self.zoomInAction = QAction(QIcon('icons/zoom_in.png'), "Zoom\nin", self)
        # self.zoomInAction.setShortcut("Ctrl++")
        #
        # self.zoomOutAction = QAction(QIcon('icons/zoom_out.png'), "Zoom\nout", self)
        # self.zoomOutAction.setShortcut("Ctrl+-")
        #
        # self.zoomFitAction = QAction(QIcon('icons/zoom_fit.png'), "Fit", self)
        # self.zoomFitAction.setShortcut("Shift+F")
        #
        # self.zoomDragAction = QAction(QIcon('icons/drag.png'), "Drag", self)
        # self.zoomDragAction.setShortcut("Shift+F")

        # self.autoSegAction = QAction("AutoMask", self)
        # self.autoSegAction.setIcon(QIcon("icons/mask.png"))
        # self.autoSegAction.setStatusTip('MaskRCC model as default. Set the default model in the configuration pannel')
        #
        # self.autoBboxAction = QAction("AutoBbox", self)
        # self.autoBboxAction.setIcon(QIcon("icons/boxes.png"))
        # self.autoBboxAction.setStatusTip('MaskRCC model as default. Set the default model in the configuration pannel')
        #
        # self.segCustomAction = QAction("Segmentation - Custom", self)
        # self.segCustomAction.setIcon(QIcon("icons/mask.png"))
        # self.segCustomAction.setShortcut("Ctrl+1")
        #
        # self.segMaskRCNNAction = QAction("Segmentation - MaskRCNN", self)
        # self.segMaskRCNNAction.setIcon(QIcon("icons/mask.png"))
        # self.segMaskRCNNAction.setShortcut("Ctrl+2")
        #
        # self.bboxMaskRCNNAction = QAction("BBox - MaskRCNN", self)
        # self.bboxMaskRCNNAction.setIcon(QIcon("icons/boxes.png"))
        # self.bboxMaskRCNNAction.setShortcut("Shift+1")
        #
        # self.slicSegmentatinoAction = QAction("SLIC - K-Means", self)
        # self.slicSegmentatinoAction.setIcon(QIcon("icons/superpixel.png"))
        # self.slicSegmentatinoAction.setShortcut("Tab+1")

        self.sizeLabel = QLineEdit(self)
        self.sizeLabel.setAlignment(Qt.AlignCenter)
        self.sizeLabel.setFixedWidth(80)

        # self.sizeImage = QLineEdit('100%')
        # self.sizeImage.setFixedWidth(100)
        # Labels menu
        self.addInstanceAction = QAction(QIcon("icons/add2.png"), "Add", self)
        self.deleteAction = QAction(QIcon("icons/remove.png"), "Delete", self)
        self.editAction = QAction(QIcon("icons/edit.png"), "Edit", self)

        # self.helpAction = QAction(QIcon('icons/help.png'), "Help", self)
        # self.helpAction.setShortcut("Ctrl+H")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = menu()
    window.show()
    sys.exit(app.exec_())
