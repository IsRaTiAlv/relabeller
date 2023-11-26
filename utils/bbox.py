import sys

from PyQt5.QtCore import Qt, QRectF, QPointF
from PyQt5.QtGui import QBrush, QColor, QPen, QPixmap, QFont
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsItem
from PyQt5 import QtWidgets


class GraphicsRectItem(QtWidgets.QGraphicsRectItem):

    handleTopLeft = 1
    # handleTopMiddle = 2
    handleTopRight = 3
    # handleMiddleLeft = 4
    # handleMiddleRight = 5
    handleBottomLeft = 6
    # handleBottomMiddle = 7
    handleBottomRight = 8

    handleSize = +6.0
    handleSpace = -6.0

    handleCursors = {
        handleTopLeft: Qt.SizeFDiagCursor,
        # handleTopMiddle: Qt.SizeVerCursor,
        handleTopRight: Qt.SizeBDiagCursor,
        # handleMiddleLeft: Qt.SizeHorCursor,
        # handleMiddleRight: Qt.SizeHorCursor,
        handleBottomLeft: Qt.SizeBDiagCursor,
        # handleBottomMiddle: Qt.SizeVerCursor,
        handleBottomRight: Qt.SizeFDiagCursor,
    }

    def __init__(self, x, y, w, h, color, shape):
        """
        Initialize the shape.
        """
        # super().__init__(*args)
        super().__init__(x, y, w, h)
        self.X, self.Y = 0, 0
        self.color = color
        self.handles = {}
        self.handleSelected = None
        self.handleHovered = None
        self.mousePressPos = None
        self.mousePressRect = None
        self.setAcceptHoverEvents(True)
        # self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)
        self.updateHandlesPos()
        self.brush = False
        self.itemSelected = False
        self.label = None
        self.id = None
        self.width, self.height = shape
        self.change_flag = False
        self.movement_flag = False
        self.resize_flag = False
        self.item_has_chanced = False
        self.alpha = 50
        self.alpha_ = 100
        self.base_alpha = 50
        self.base_alpha_ = 100

    def handleAt(self, point):
        """
        Returns the resize handle below the given point.
        """
        for k, v, in self.handles.items():
            if v.contains(point):
                return k
        return None

    # mouse hover event
    def hoverEnterEvent(self, event):
        self.brush = True
        self.update()
        # app.instance().setOverrideCursor(Qt.OpenHandCursor)
        # self.setBrush(Qt.blue)

    def hoverMoveEvent(self, moveEvent):
        """
        Executed when the mouse moves over the shape (NOT PRESSED).
        """
        if self.isSelected():
            self.brush = True
            self.update()
            self.handleHovered = self.handle = self.handleAt(moveEvent.pos())
            # if self.handle is not None:
            #     self.current_cursor = QCursor(Qt.CrossCursor)
            # else:
            #     self.current_cursor = QCursor(Qt.ArrowCursor)
            # # print(self.handle)
            # self.setCursor(self.current_cursor)
            # cursor = Qt.ArrowCursor if handle is None else self.handleCursors[handle]
            # self.setCursor(QCursor(cursor))
        super().hoverMoveEvent(moveEvent)

    def hoverLeaveEvent(self, moveEvent):
        """
        Executed when the mouse leaves the shape (NOT PRESSED).
        """
        self.handleHovered = None
        if not self.isSelected():
            self.brush = False
            self.update()
        # self.setCursor(QCursor(Qt.ArrowCursor))
        super().hoverLeaveEvent(moveEvent)

    def mousePressEvent(self, mouseEvent):
        """
        Executed when the mouse is pressed on the item.
        """
        # if not self.isSelected():
        #     self.brush = False
        #     self.update()
        # self.brush = True
        # self.update()
        self.change_flag = True
        self.handleSelected = self.handleAt(mouseEvent.pos())
        if self.handleSelected:
            self.mousePressPos = mouseEvent.pos()
            self.mousePressRect = self.boundingRect()
        super().mousePressEvent(mouseEvent)

    def mouseMoveEvent(self, mouseEvent):
        """
        Executed when the mouse is being moved over the item while being pressed.
        """
        if self.handleSelected is not None:
            self.interactiveResize(mouseEvent.pos())
            self.resize_flag = True
        else:
            super().mouseMoveEvent(mouseEvent)

            orig_cursor_pos = mouseEvent.lastScenePos()
            updated_cursor_pos = mouseEvent.scenePos()

            orig_position = self.scenePos()

            updated_x = updated_cursor_pos.x() - orig_cursor_pos.x() + orig_position.x()
            updated_y = updated_cursor_pos.y() - orig_cursor_pos.y() + orig_position.y()
            updated_x = updated_x if self.rect().x() + updated_x > 0 else -self.rect().x()
            updated_y = updated_y if self.rect().y() + updated_y > 0 else -self.rect().y()
            limit_x = self.rect().x() + updated_x + self.rect().width()
            limit_y = self.rect().y() + updated_y + self.rect().height()
            max_x = self.width - self.rect().width() - self.rect().x()
            max_y = self.height - self.rect().height() - self.rect().y()
            self.X = updated_x if limit_x < self.width else max_x
            self.Y = updated_y if limit_y < self.height else max_y
            self.setPos(QPointF(self.X, self.Y))
            self.movement_flag = True

    def mouseReleaseEvent(self, mouseEvent):
        """
        Executed when the mouse is released from the item.
        """
        # print('x: {0}, y: {1}'.format(self.pos().x(), self.pos().y()))
        self.handleSelected = None
        self.mousePressPos = None
        self.mousePressRect = None
        self.update()
        if self.change_flag and self.movement_flag:
            self.item_has_chanced = True
            self.change_flag = False
            self.movement_flag = False
        elif self.change_flag and self.resize_flag:
            self.item_has_chanced = True
            self.change_flag = False
            self.resize_flag = False
        else:
            self.item_has_chanced = False
            self.change_flag = False
            self.resize_flag = False
            self.movement_flag = False
        super().mouseReleaseEvent(mouseEvent)

    def boundingRect(self):
        """
        Returns the bounding rect of the shape (including the resize handles).
        """
        o = self.handleSize + self.handleSpace
        return self.rect().adjusted(-o, -o, o, o)

    def updateHandlesPos(self):
        """
        Update current resize handles according to the shape size and position.
        """
        s = self.handleSize
        b = self.boundingRect()
        self.handles[self.handleTopLeft] = QRectF(b.left(), b.top(), s, s)
        # self.handles[self.handleTopMiddle] = QRectF(b.center().x() - s / 2, b.top(), s, s)
        self.handles[self.handleTopRight] = QRectF(b.right() - s, b.top(), s, s)
        # self.handles[self.handleMiddleLeft] = QRectF(b.left(), b.center().y() - s / 2, s, s)
        # self.handles[self.handleMiddleRight] = QRectF(b.right() - s, b.center().y() - s / 2, s, s)
        self.handles[self.handleBottomLeft] = QRectF(b.left(), b.bottom() - s, s, s)
        # self.handles[self.handleBottomMiddle] = QRectF(b.center().x() - s / 2, b.bottom() -s,s,s)
        self.handles[self.handleBottomRight] = QRectF(b.right() - s, b.bottom() - s, s, s)

    def interactiveResize(self, mousePos):
        """
        Perform shape interactive resize.
        """
        offset = self.handleSize + self.handleSpace
        boundingRect = self.boundingRect()
        rect = self.rect()
        diff = QPointF(0, 0)

        self.prepareGeometryChange()

        if self.handleSelected == self.handleTopLeft:

            fromX = self.mousePressRect.left()
            fromY = self.mousePressRect.top()
            toX = fromX + mousePos.x() - self.mousePressPos.x()
            toY = fromY + mousePos.y() - self.mousePressPos.y()
            diff.setX(toX - fromX)
            diff.setY(toY - fromY)
            boundingRect.setLeft(toX)
            boundingRect.setTop(toY)
            # print(boundingRect.left() + offset, boundingRect.top() + offset)
            rect.setLeft(boundingRect.left() + offset)
            rect.setTop(boundingRect.top() + offset)
            self.setRect(rect)

        # elif self.handleSelected == self.handleTopMiddle:
        #
        #     fromY = self.mousePressRect.top()
        #     toY = fromY + mousePos.y() - self.mousePressPos.y()
        #     diff.setY(toY - fromY)
        #     boundingRect.setTop(toY)
        #     rect.setTop(boundingRect.top() + offset)
        #     self.setRect(rect)

        elif self.handleSelected == self.handleTopRight:

            fromX = self.mousePressRect.right()
            fromY = self.mousePressRect.top()
            toX = fromX + mousePos.x() - self.mousePressPos.x()
            toY = fromY + mousePos.y() - self.mousePressPos.y()
            diff.setX(toX - fromX)
            diff.setY(toY - fromY)
            boundingRect.setRight(toX)
            boundingRect.setTop(toY)
            rect.setRight(boundingRect.right() - offset)
            rect.setTop(boundingRect.top() + offset)
            self.setRect(rect)

        # elif self.handleSelected == self.handleMiddleLeft:
        #
        #     fromX = self.mousePressRect.left()
        #     toX = fromX + mousePos.x() - self.mousePressPos.x()
        #     diff.setX(toX - fromX)
        #     boundingRect.setLeft(toX)
        #     rect.setLeft(boundingRect.left() + offset)
        #     self.setRect(rect)
        #
        # elif self.handleSelected == self.handleMiddleRight:
        #     # print("MR")
        #     fromX = self.mousePressRect.right()
        #     toX = fromX + mousePos.x() - self.mousePressPos.x()
        #     diff.setX(toX - fromX)
        #     boundingRect.setRight(toX)
        #     rect.setRight(boundingRect.right() - offset)
        #     self.setRect(rect)

        elif self.handleSelected == self.handleBottomLeft:

            fromX = self.mousePressRect.left()
            fromY = self.mousePressRect.bottom()
            toX = fromX + mousePos.x() - self.mousePressPos.x()
            toY = fromY + mousePos.y() - self.mousePressPos.y()
            diff.setX(toX - fromX)
            diff.setY(toY - fromY)
            boundingRect.setLeft(toX)
            boundingRect.setBottom(toY)
            rect.setLeft(boundingRect.left() + offset)
            rect.setBottom(boundingRect.bottom() - offset)
            self.setRect(rect)

        # elif self.handleSelected == self.handleBottomMiddle:
        #
        #     fromY = self.mousePressRect.bottom()
        #     toY = fromY + mousePos.y() - self.mousePressPos.y()
        #     diff.setY(toY - fromY)
        #     boundingRect.setBottom(toY)
        #     rect.setBottom(boundingRect.bottom() - offset)
        #     self.setRect(rect)

        elif self.handleSelected == self.handleBottomRight:

            fromX = self.mousePressRect.right()
            fromY = self.mousePressRect.bottom()
            toX = fromX + mousePos.x() - self.mousePressPos.x()
            toY = fromY + mousePos.y() - self.mousePressPos.y()
            diff.setX(toX - fromX)
            diff.setY(toY - fromY)
            boundingRect.setRight(toX)
            boundingRect.setBottom(toY)
            rect.setRight(boundingRect.right() - offset)
            rect.setBottom(boundingRect.bottom() - offset)
            self.setRect(rect)

        # print(diff)
        self.updateHandlesPos()

    # def shape(self):
    #     """
    #     Returns the shape of this item as a QPainterPath in local coordinates.
    #     """
    #     path = QPainterPath()
    #     path.addRect(self.rect())
    #     if self.isSelected():
    #         for shape in self.handles.values():
    #             path.addEllipse(shape)
    #     # print(self.handles[self.handleTopLeft])
    #     print(type(path))
    #     # corners = path.boundingRect()
    #     # x, y, w, h = corners.x(), corners.y(), corners.width(), corners.height()
    #     return (x,y,w,h)
    def getData(self):
        return [
            self.rect().x() + self.X,
            self.rect().y() + self.Y,
            self.rect().width(),
            self.rect().height(), self.color, self.width, self.height, self.label, self.id,
            self.isVisible()
        ]

    def getDataCCFormat(self):
        '''Returns data in the format:
            [[(x1, y1), (x2, y2)], label, area]
        '''
        p1 = tuple([int(self.rect().x() + self.X), int(self.rect().y() + self.Y)])
        p2 = tuple([
            int(self.rect().width() + self.rect().x() + self.X),
            int(self.rect().height() + self.rect().y() + self.Y)
        ])
        return [[p1, p2], self.label, int(self.rect().height() * self.rect().width())]

    def fill_selected(self, action):
        self.brush = action
        self.update()

    def paint(self, painter, option, widget=None):
        """
        Paint the node in the graphic view.
        """
        r, g, b = self.color[0], self.color[1], self.color[2]
        if self.brush:
            painter.setBrush(QBrush(QColor(r, g, b, self.alpha)))
        painter.setPen(QPen(QColor(r, g, b, self.alpha_), 1, Qt.SolidLine))
        painter.drawRect(self.rect())

        # painter.setRenderHint(QPainter.Antialiasing)
        # painter.setBackground()
        '''Drawing the text'''
        painter.setFont(QFont('Decorative', 5))
        painter.setPen(QPen(QColor(255, 255, 255, 255), 1, Qt.SolidLine))
        painter.drawText(self.rect(), Qt.AlignTop | Qt.AlignLeft, self.label)

        if self.isSelected():
            painter.setBrush(QBrush(QColor(r, g, b, self.alpha)))
            painter.setPen(
                QPen(QColor(r, g, b, self.alpha_), 1.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            for handle, rect in self.handles.items():
                # if self.handleSelected is None or handle == self.handleHovered:
                if self.brush:
                    painter.drawRect(rect)
                # painter.drawEllipse(rect)

            painter.setBrush(QBrush(QColor(0, 0, 0, self.alpha)))
            color = QColor(r * 0.7, g * 0.7, b * 0.7, self.alpha_)
            painter.setPen(QPen(color, 1.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            for handle, rect in self.handles.items():
                # print(self.handleSelected, self.handleHovered, handle)
                if handle == self.handleHovered:
                    if self.brush:
                        painter.drawRect(rect)


def main():

    app = QApplication(sys.argv)

    grview = QGraphicsView()
    scene = QGraphicsScene()
    scene.setSceneRect(0, 0, 680, 459)

    scene.addPixmap(QPixmap('01.png'))
    grview.setScene(scene)

    item = GraphicsRectItem(0, 0, 300, 150)
    scene.addItem(item)

    grview.fitInView(scene.sceneRect(), Qt.KeepAspectRatio)
    grview.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
