from PyQt5.QtGui import QPixmap, QCursor
from PyQt5.QtCore import Qt, QPoint, QSize, QRect, QRectF, pyqtSignal
from PyQt5.QtWidgets import QFrame, QGraphicsPixmapItem, QGraphicsScene, QGraphicsView, QRubberBand, QApplication
from PyQt5 import QtWidgets
from utils.bbox import GraphicsRectItem
from random import random
import colorsys
import time

# from test3 import MovingObject


class PhotoViewer(QGraphicsView, QtWidgets.QGraphicsPolygonItem):
    photoClicked = pyqtSignal(bool)
    zoom_action = pyqtSignal(str)
    factor_rate = pyqtSignal(str)
    mask_selected = pyqtSignal(int)
    bbox_selected = pyqtSignal(str)
    bbox_created = pyqtSignal(list)
    bbox_modified = pyqtSignal(bool)
    zoom_ratio = pyqtSignal(int)
    tool_val = pyqtSignal(bool)

    def __init__(self, parent, statusBar):
        super(PhotoViewer, self).__init__(parent)
        self.image_path = ''
        self.pil_image = None
        self.map_image = None
        self.draw = False
        self.drawing = False
        self.drawing_mode = 1  # 1: draw 0: erase
        self.pixel_annotation = False
        self.statusBar = statusBar
        self.rect = False
        self.bbox = False
        self.brushSize = None
        self.lastPoint = QPoint()

        self.origin = QPoint(0, 0)
        self._zoom = 0
        self._empty = True
        self._scene = QGraphicsScene(self)
        self._photo = QGraphicsPixmapItem()
        self._scene.addItem(self._photo)
        self.setScene(self._scene)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        # self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.setBackgroundBrush(QBrush(QColor(0, 0, 0)))
        self.setFrameShape(QFrame.NoFrame)
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)
        self.bbox_list = []  # List were the current bboxes are saved
        self.bbox_record = []  # list were the past groups of bboxes are saved
        self.undo_bbox_record = []  # list were the current bboxes are saved due to an undo acc

    def hasPhoto(self):
        return not self._empty

    def fitInView(self, scale=True):
        rect = QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            if self.hasPhoto():
                unity = self.transform().mapRect(QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height())
                self.factor_rate.emit(str(int(factor * 100)))
                self.scale(factor, factor)
            self._zoom = 0

    def setPhoto(self, pixmap=None, image_path='', pil_image=None, map_image=None):
        if image_path != '':
            self.image_path = image_path
            self.pil_image = pil_image
            self.map_image = map_image
        self._zoom = 0
        if pixmap and not pixmap.isNull():
            self._empty = False
            self._photo.setPixmap(pixmap)

        else:
            self._empty = True
            self.setDragMode(QGraphicsView.NoDrag)
            self._photo.setPixmap(QPixmap())
        self.fitInView()

    def wheelEvent(self, event):
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ControlModifier:
            if event.angleDelta().y() > 0:
                self.tool_val.emit(True)
            else:
                self.tool_val.emit(False)

        else:
        # rect = QRectF(self._photo.pixmap().rect())
        # viewrect = self.viewport().rect()
        # scenerect = self.transform().mapRect(rect)
        # factor = min(viewrect.width() / scenerect.width(),
        #              viewrect.height() / scenerect.height())
        # self.factor_rate.emit(str(int(factor * 100)))
            if self.hasPhoto() and not self.pixel_annotation:
                self.zoom_action.emit('drag')
                if event.angleDelta().y() > 0:
                    factor = 1.03
                    self.zoom_ratio.emit(factor)
                    self._zoom += 1
                else:
                    factor = 0.97
                    self.zoom_ratio.emit(factor)
                    self._zoom -= 1
                if self._zoom > 0:
                    self.setDragMode(QGraphicsView.ScrollHandDrag)
                    self.scale(factor, factor)
                elif self._zoom == 0:
                    self.fitInView()
                    self.setDragMode(QGraphicsView.NoDrag)
                    self.zoom_action.emit('done')
                else:
                    self._zoom = 0

    def zoom(self, value):
        if self.hasPhoto():
            self.zoom_action.emit('drag')
            if value == 'in':
                factor = 1.25
                self._zoom += 1
            if value == 'out':
                factor = 0.8
                self._zoom -= 1
            if value == 'fit':
                # self.scale(1, 1)
                self.fitInView()
                self.setDragMode(QGraphicsView.NoDrag)
                return True

            if self._zoom > 0:
                self.setDragMode(QGraphicsView.ScrollHandDrag)
                self.scale(factor, factor)
            elif self._zoom == 0:
                self.fitInView()
                self.setDragMode(QGraphicsView.NoDrag)
            else:
                self._zoom = 0

    def toggleDragMode(self):
        if self.dragMode() == QGraphicsView.ScrollHandDrag:
            self.setDragMode(QGraphicsView.NoDrag)

        elif not self._photo.pixmap().isNull():
            self.setDragMode(QGraphicsView.ScrollHandDrag)

    def mouseDoubleClickEvent(self, event):
        # print(self.size())
        self.zoom_action.emit('done')
        self.zoom('fit')
        # self.save_all()

    def hoverMoveEvent(self, moveEvent):
        super().hoverMoveEvent(moveEvent)

    def mousePressEvent(self, event):
        super(PhotoViewer, self).mousePressEvent(event)
        items_under_mouse = []
        for item in self.items():
            if isinstance(item, GraphicsRectItem):
                if not item.isUnderMouse():
                    item.fill_selected(False)
                else:
                    items_under_mouse.append(item)

        if len(items_under_mouse) > 0:
            self.bbox_selected.emit(items_under_mouse[0].id)
            for item in items_under_mouse[0:]:
                item.fill_selected(False)

        if self._photo.isUnderMouse() and event.button() == Qt.LeftButton and self.image_path != '':
            self.origin = event.pos()
            # self.image_chages.append(self.map_image.img)
            if self.draw:
                self.map_image.do_action()
                self.drawing = True
                self.map_image.first_mask = True  # Activating or changing a channel
                self.lastPoint = self.mapToScene(self.origin).toPoint()
                # print(self.lastPoint)

            elif self.pixel_annotation:
                self.map_image.do_action()
                self.lastPoint = self.mapToScene(event.pos()).toPoint()
                self.map_image.drawPixel(self.lastPoint, self.drawing_mode)
                masked_image = self.map_image.apply_masks_to_image()
                self.setPixmapImage(masked_image)
                self.photoClicked.emit(True)

            elif self.rect:
                self.map_image.do_action()
                self.rubberBand.setGeometry(QRect(self.origin, QSize()))
                self.rubberBand.show()

            elif self.bbox:
                self.rubberBand.setGeometry(QRect(self.origin, QSize()))
                self.rubberBand.show()

            elif type(self.map_image.masks) != list:
                channels_selected = []
                x, y = int(self.mapToScene(self.origin).x()), int(self.mapToScene(self.origin).y())
                for channel in range(self.map_image.masks.shape[0]):
                    if self.map_image.masks[channel, y, x]:
                        channels_selected.append(channel)
                lowwest = 1000000
                fchannel = -1
                for channel in channels_selected:
                    if self.map_image.masks[channel].sum() < lowwest:
                        fchannel = channel
                        lowwest = self.map_image.masks[channel].sum()
                self.mask_selected.emit(fchannel)
            # else:
            # print(self.mapToScene(self.origin))

    def mouseMoveEvent(self, event):
        super(PhotoViewer, self).mouseMoveEvent(event)
        if self.image_path != '' and event.buttons() == Qt.LeftButton:
            if self.drawing and self.draw:
                # print(self.drawing_mode)
                self.map_image.drawMask(self.lastPoint,
                                        self.mapToScene(event.pos()).toPoint(), self.brushSize,
                                        self.drawing_mode)
                masked_image = self.map_image.apply_masks_to_image(keep_last=True)
                self.setPixmapImage(masked_image)
                self.lastPoint = self.mapToScene(event.pos()).toPoint()
                self.photoClicked.emit(True)

            elif self.pixel_annotation:
                # print(self.map_image.channel)
                self.map_image.drawPixel(self.lastPoint, self.drawing_mode)
                masked_image = self.map_image.apply_masks_to_image()
                self.setPixmapImage(masked_image)
                self.lastPoint = self.mapToScene(event.pos()).toPoint()
                self.photoClicked.emit(True)

            elif self.rect:
                if not self.origin.isNull():
                    self.rubberBand.setGeometry(QRect(self.origin, event.pos()).normalized())

            elif self.bbox:
                if not self.origin.isNull():
                    self.rubberBand.setGeometry(QRect(self.origin, event.pos()).normalized())

    def mouseReleaseEvent(self, event):
        super(PhotoViewer, self).mouseReleaseEvent(event)
        has_changed = False
        if event.button() == Qt.LeftButton:
            self.drawing = False

            if self.rect:
                if not self.origin == event.pos():
                    self.map_image.do_action()
                    self.rubberBand.hide()
                    self.map_image.generate_roi(self.mapToScene(self.origin),
                                                self.mapToScene(event.pos()))

                    masked_image = self.map_image.apply_masks_to_image()
                    self.setPixmapImage(masked_image)

            elif self.bbox:
                self.rubberBand.hide()
                origin = self.mapToScene(self.origin)
                end = self.mapToScene(event.pos())
                x, y, w, he = self.bbox_limits(origin, end)
                if w > 10 or he > 10:
                    h, s, le = random(), 0.5 + random() / 2.0, 0.4 + random() / 5.0
                    r, g, b = [int(256 * i) for i in colorsys.hls_to_rgb(h, le, s)]
                    item = GraphicsRectItem(x, y, w, he, (r, g, b), self.pil_image.size)
                    item.id = 'id-' + str(int(time.time() * 1000))
                    self._scene.addItem(item)
                    self.bbox = False
                    self.bbox_created.emit([r, g, b, item.id])
                    has_changed = True
                    self.zoom_action.emit('done')
        self.save_current_bbox(has_changed)

    def closeMask(self):
        self.map_image.do_action()
        self.map_image.close()
        masked_image = self.map_image.apply_masks_to_image()
        self.setPixmapImage(masked_image)

    def setPixmapImage(self, pixImage):
        cvImg = self.map_image.array2pix(pixImage)
        self.image = QPixmap(cvImg)
        self._photo.setPixmap(self.image)

    def addbbox(self, bbox_list, class_names, colors, ids):
        # print(ids)
        for i, (bbox, class_name, color) in enumerate(zip(bbox_list, class_names, colors * 2)):
            x1, y1 = bbox[0]
            x2, y2 = bbox[1]
            x, y, w, h = int(x1), int(y1), int(x2 - x1), int(y2 - y1)
            item = GraphicsRectItem(x, y, w, h, [c * 255 for c in color], self.pil_image.size)
            item.label = class_name
            item.id = 'id-' + str(ids[i])
            self._scene.addItem(item)
        self.save_current_bbox(has_changed=True)

    def clear(self):
        self.deleteBbox(type='all')
        self.bbox_list = []  # List were the current bboxes are saved
        self.bbox_record = []  # list were the past groups of bboxes are saved
        self.undo_bbox_record = []  # list were the current bboxes are saved due to an undo acc

    def updatebbox(self, id, class_name):
        for item in self.items():
            if isinstance(item, GraphicsRectItem):
                if id == item.id:
                    item.label = class_name
                    item.update()

    def updatebboxColor(self, value):
        for item in self.items():
            if isinstance(item, GraphicsRectItem):
                item.alpha = item.base_alpha + value
                item.alpha_ = item.base_alpha_ + value
                # print(item.alpha, item.alpha_)
                item.update()

    def deleteBbox(self, type, id=None):
        if type == 'selected':
            if id is None:
                for item in self.items():
                    if isinstance(item, GraphicsRectItem):
                        if item.isSelected():
                            self._scene.removeItem(item)
            else:
                for item in self.items():
                    if isinstance(item, GraphicsRectItem):
                        if item.id == id:
                            self._scene.removeItem(item)
        elif type == 'all':
            for item in self.items():
                if isinstance(item, GraphicsRectItem):
                    self._scene.removeItem(item)
        self.save_current_bbox(has_changed=True)

    def modificationBbox(self, listbbox, id):
        # print('Selected: ', id)
        for item in self.items():
            if isinstance(item, GraphicsRectItem):
                item.hide()
                if id == item.id:
                    item.fill_selected(True)
                else:
                    item.fill_selected(False)

                if listbbox[item.id]:
                    item.show()
                # if item.id not in listbbox:
                #     self._scene.removeItem(item)
                #     self.bbox_list.append(item)

        # if len(self.bbox_list) > 0:
        #     for item in self.bbox_list:
        #         if item.id in listbbox:
        #             self._scene.addItem(item)
        #             self.bbox_list.remove(item)

    def save_current_bbox(self, has_changed=False):
        current_bbox = []
        if not has_changed:
            for item in self.items():
                if isinstance(item, GraphicsRectItem):
                    if item.item_has_chanced:
                        has_changed = True
                        item.item_has_chanced = False
                        # print(item.label)
                        break
        if has_changed:
            for item in self.items():
                if isinstance(item, GraphicsRectItem):
                    # print(item.getData())
                    current_bbox.append(item.getData().copy())

        # Antialiasing condition. When undo action is performed.
        # if self.undo_bbox_record:
        #     self.bbox_record.append(self.undo_bbox_record)
        #     self.undo_bbox_record = []

        if has_changed and self.hasPhoto():
            self.bbox_record.append(current_bbox)
            self.statusBar().showMessage(f'Saving {len(self.bbox_record)} record')
            self.bbox_modified.emit(True)
            # print(f'Saving {len(self.bbox_record)+1} record')
        # print(len(self.bbox_record))

    def save_all(self):
        items = list()
        for item in self.items():
            if isinstance(item, GraphicsRectItem):
                items.append(item.getDataCCFormat())
        # print(items)
        return items

    def undo_action(self):
        self.instances = {}
        # Taking away all the bounding boxes
        for item in self.items():
            if isinstance(item, GraphicsRectItem):
                self._scene.removeItem(item)

        _ = self.bbox_record.pop(-1)
        self.undo_bbox_record = self.bbox_record[-1]
        for item_inf in self.undo_bbox_record:
            x, y, w, h, color, imgw, imgh, label, id, isVisible = item_inf

            item = GraphicsRectItem((x), (y), (w), (h), color, (imgw, imgh))
            item.label = label
            item.id = id
            self._scene.addItem(item)
            if not isVisible:
                item.hide()
            self.instances[id] = [label, color, isVisible]

    def bbox_limits(self, origin, end):
        P1 = origin.x(), origin.y()
        P2 = end.x(), end.y()
        width, height = self.pil_image.size
        h0, h1 = (int(P1[0]), int(P2[0])) if P1[0] < P2[0] else (int(P2[0]), int(P1[0]))
        w0, w1 = (int(P1[1]), int(P2[1])) if P1[1] < P2[1] else (int(P2[1]), int(P1[1]))
        h0 = 0 if h0 < 0 else h0
        h1 = width if h1 > width else h1
        w0 = 0 if w0 < 0 else w0
        w1 = height if w1 > height else w1
        return h0, w0, h1 - h0, w1 - w0
