from dataclasses import dataclass
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from typing import List, Dict
import sys
import cv2

TOOL_ADD_ARC = 0
TOOL_REMOVE_ARC = 1
TOOL_ADD_REGION = 2
TOOL_REMOVE_REGION = 3
TOOL_ADD_VerticalREGION = 4


class CarMarker(QGraphicsRectItem):
    SIZE = 10

    def __init__(self, position, car_id, selected, parent=None):
        super().__init__(
            position.x(),
            position.y(),
            CarMarker.SIZE,
            CarMarker.SIZE,
            parent,
        )
        self.setZValue(-1)
        self.setTransformOriginPoint(QPointF(CarMarker.SIZE / 2, CarMarker.SIZE / 2))
        self.setPos(self.pos() - QPointF(CarMarker.SIZE / 2, CarMarker.SIZE / 2))
        self.setPen(QPen(Qt.NoPen))

        if not selected:
            self.setBrush(Qt.magenta)
        else:
            self.setBrush(Qt.blue)

        self.car_id = car_id


# Car boundary marker

class Marker(QGraphicsEllipseItem):
    SIZE = 10

    def __init__(self, position, car_id, point_index, selected, parent=None):
        super().__init__(position.x(), position.y(), Marker.SIZE, Marker.SIZE, parent)
        self.setZValue(-1)
        self.setTransformOriginPoint(QPointF(Marker.SIZE / 2, Marker.SIZE / 2))
        self.setPos(self.pos() - QPointF(Marker.SIZE / 2, Marker.SIZE / 2))
        self.setPen(QPen(Qt.NoPen))

        if not selected:
            self.setBrush(Qt.white)
        else:
            self.setBrush(Qt.blue)

        self.car_id = car_id
        self.point_index = point_index


class MarkerConnection(QGraphicsLineItem):
    WIDTH = 3.5

    def __init__(self, marker_1, marker_2, parent=None):
        x1 = marker_1.rect().x()
        y1 = marker_1.rect().y()
        x2 = marker_2.rect().x()
        y2 = marker_2.rect().y()
        super().__init__(x1, y1, x2, y2, parent)
        self.setZValue(-2)

        pen = QPen()
        pen.setColor(QColor("red"))
        pen.setWidth(MarkerConnection.WIDTH)
        self.setPen(pen)

        self.marker_1 = marker_1
        self.marker_2 = marker_2


@dataclass
class FramePixmap:
    player_x: float
    player_y: float
    player_w: float
    player_h: float
    frame_w: float
    frame_h: float
    frame_index: int
    pixmap: QPixmap


@dataclass
class CarSelection:
    car_id: int


@dataclass
class MarkerSelection:
    frame_index: int
    car_id: int
    point_index: int


class Editor(QWidget):
    def __init__(self, player, car_id_edit, car_info_save_btn, parent=None, ):
        super().__init__(parent)

        # self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # self.setContentsMargins(0, 0, 0, 0)
        scene = QGraphicsScene(QRectF(self.rect()), self)

        frame_number = QGraphicsTextItem()
        frame_number.setPos(10, 10)
        scene.addItem(frame_number)

        video_pixmap = QGraphicsPixmapItem()
        video_pixmap.setZValue(-100)
        scene.addItem(video_pixmap)

        view = QGraphicsView(scene, self)
        view.setFrameStyle(QFrame.NoFrame)
        view.setFrameShape(QFrame.Shape.NoFrame)
        view.setFrameShadow(QFrame.Shadow.Plain)
        view.setContentsMargins(0, 0, 0, 0)
        view.setViewportMargins(QMargins(0, 0, 0, 0))
        view.setStyleSheet("border-width: 0; border-color: transparent")
        # view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        car_id_edit.setEnabled(False)
        car_id_edit.setValidator(QIntValidator(self))
        car_info_save_btn.setEnabled(False)
        car_info_save_btn.clicked.connect(self.saveCarInfo)

        self.player = player
        self.car_id_edit = car_id_edit
        self.car_info_save_btn = car_info_save_btn
        self.addedIndex = False
        self.totalframe = player.frame_count
        self.scene = scene
        self.frame_number = frame_number
        self.video_pixmap = video_pixmap
        self.view = view
        self.data = dict()
        self.zoom_multiplier = 1.0
        self.fixtool = False
        self.frame_pixmap = None
        self.selection = None
        self.active_tool = None

    def zoomIn(self):
        if self.zoom_multiplier < 10:
            self.zoom_multiplier += 0.2
            self.view.resetTransform()
            self.view.scale(self.zoom_multiplier, self.zoom_multiplier)

    def zoomOut(self):
        if self.zoom_multiplier > 1.0:
            self.zoom_multiplier -= 0.2
            self.view.resetTransform()
            self.view.scale(self.zoom_multiplier, self.zoom_multiplier)

    def addIndex(self):
        if self.addedIndex == True:
            self.addedIndex = False
            print(self.addedIndex)
        else:
            self.addedIndex = True
            print(self.addedIndex)

    def toggleTool(self, tool):
        # print(tool)

        if tool == self.active_tool:
            self.active_tool = None
        else:
            self.active_tool = tool

            if tool == TOOL_ADD_ARC:
                self.selection = None

            elif tool == TOOL_REMOVE_ARC:
                # Remove marker
                if type(self.selection) is MarkerSelection:
                    car_id = self.selection.car_id
                    point_index = self.selection.point_index
                    self.selection = None
                    self.removePoint(car_id, point_index)

                self.active_tool = None

            elif tool == TOOL_ADD_REGION:
                self.selection = None
            elif tool == TOOL_ADD_VerticalREGION:
                self.selection = None
            elif tool == TOOL_REMOVE_REGION:
                # Remove car
                if type(self.selection) is CarSelection:
                    car_id = self.selection.car_id
                    self.selection = None
                    self.removeCar(car_id)

                self.active_tool = None

        self.player.pause()
        self.redraw()

    def getActiveTool(self):
        return self.active_tool

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            scene_pos = self.view.mapToScene(event.pos())
            item = self.scene.itemAt(scene_pos, QTransform())

            if self.active_tool == TOOL_ADD_ARC:
                if type(item) is MarkerConnection:
                    connection: MarkerConnection = item

                    frame_index = self.frame_pixmap.frame_index
                    car_id = connection.marker_2.car_id
                    point_index = connection.marker_2.point_index

                    player_x = self.frame_pixmap.player_x
                    player_y = self.frame_pixmap.player_y
                    player_w = self.frame_pixmap.player_w
                    player_h = self.frame_pixmap.player_h
                    frame_w = self.frame_pixmap.frame_w
                    frame_h = self.frame_pixmap.frame_h

                    rescaled_x = (scene_pos.x() - player_x) / player_w * frame_w
                    rescaled_y = (scene_pos.y() - player_y) / player_h * frame_h

                    point_index = self.addPoint(
                        car_id, point_index, Point(rescaled_x, rescaled_y)
                    )
                    self.selection = MarkerSelection(frame_index, car_id, point_index)
                    self.active_tool = None


            elif self.active_tool == TOOL_ADD_REGION:
                if type(item) is QGraphicsPixmapItem:
                    # Add car
                    player_x = self.frame_pixmap.player_x
                    player_y = self.frame_pixmap.player_y
                    player_w = self.frame_pixmap.player_w
                    player_h = self.frame_pixmap.player_h
                    frame_w = self.frame_pixmap.frame_w
                    frame_h = self.frame_pixmap.frame_h

                    rescaled_x = (scene_pos.x() - player_x) / player_w * frame_w
                    rescaled_y = (scene_pos.y() - player_y) / player_h * frame_h
                    car_id = self.addCar(Point(rescaled_x, rescaled_y), 0, self.addedIndex)
                    self.selection = None
                    current_frame = self.player.frameIndex()

                    center_x = self.data.frames.get(current_frame).cars.get(car_id).getCenter().x
                    center_y = self.data.frames.get(current_frame).cars.get(car_id).getCenter().y
                    if self.fixtool:
                        self.fix_frame(center_x, center_y, rescaled_x, rescaled_y, 0)

            elif self.active_tool == TOOL_ADD_VerticalREGION:
                if type(item) is QGraphicsPixmapItem:
                    player_x = self.frame_pixmap.player_x
                    player_y = self.frame_pixmap.player_y
                    player_w = self.frame_pixmap.player_w
                    player_h = self.frame_pixmap.player_h
                    frame_w = self.frame_pixmap.frame_w
                    frame_h = self.frame_pixmap.frame_h

                    rescaled_x = (scene_pos.x() - player_x) / player_w * frame_w
                    rescaled_y = (scene_pos.y() - player_y) / player_h * frame_h

                    car_id = self.addCar(Point(rescaled_x, rescaled_y), 1, self.addedIndex)
                    self.selection = None
                    current_frame = self.player.frameIndex()

                    center_x = self.data.frames.get(current_frame).cars.get(car_id).getCenter().x
                    center_y = self.data.frames.get(current_frame).cars.get(car_id).getCenter().y

                    if self.fixtool:
                        self.fix_frame(center_x, center_y, rescaled_x, rescaled_y, 1)
            elif self.active_tool is None:
                if type(item) is Marker:
                    # Select marker
                    marker: Marker = item

                    frame_index = self.frame_pixmap.frame_index
                    car_id = marker.car_id
                    point_index = marker.point_index

                    self.selection = MarkerSelection(frame_index, car_id, point_index)

                elif type(item) is CarMarker:
                    # Select car
                    marker: CarMarker = item
                    car_id = marker.car_id
                    self.selection = CarSelection(car_id)

                elif type(self.selection) is MarkerSelection:
                    # Move selected marker
                    car_id = self.selection.car_id
                    point_index = self.selection.point_index

                    player_x = self.frame_pixmap.player_x
                    player_y = self.frame_pixmap.player_y
                    player_w = self.frame_pixmap.player_w
                    player_h = self.frame_pixmap.player_h
                    frame_w = self.frame_pixmap.frame_w
                    frame_h = self.frame_pixmap.frame_h

                    rescaled_x = (scene_pos.x() - player_x) / player_w * frame_w
                    rescaled_y = (scene_pos.y() - player_y) / player_h * frame_h

                    self.movePoint(car_id, point_index, Point(rescaled_x, rescaled_y))

        elif event.button() == Qt.MouseButton.RightButton:
            self.selection = None

        if self.selection:
            self.player.pause()

        self.redraw()

    def addCar(self, position, way, is_added):
        if (way == 0):
            bounding_box = [
                Point(position.x - 48, position.y + 20),
                Point(position.x + 48, position.y + 20),
                Point(position.x + 48, position.y - 20),
                Point(position.x - 48, position.y - 20),
            ]
        elif (way == 1):
            bounding_box = [
                Point(position.x - 20, position.y + 48),
                Point(position.x + 20, position.y + 48),
                Point(position.x + 20, position.y - 48),
                Point(position.x - 20, position.y - 48),
            ]

        car = Car(
            car_center_x=0,
            car_center_y=0,
            car_w=0,
            car_l=0,
            course=0,
            head_x=0,
            head_y=0,
            tail_x=0,
            tail_y=0,
            lost_counter=0,
            bounding_box=bounding_box,
        )

        car_id = self.data.next_car_id
        if is_added == False:
            self.data.next_car_id += 1

        frame_data = self.data.frames[self.frame_pixmap.frame_index]
        frame_data.cars[car_id] = car
        return car_id

    def addstopvehicle(self):
        if self.fixtool == False:
            self.fixtool = True
        else:
            self.fixtool = False

    def fix_frame(self, centerx, centery, carx, cary, way):
        existed_car = False
        count = 0
        while (not existed_car):
            self.player.nextFrame()
            count += 1
            frame_index = self.player.frameIndex()
            car = self.data.frames.get(frame_index).cars
            car_idlist = list(car)
            for i in car_idlist:

                car_x = self.data.frames.get(frame_index).cars.get(i).getCenter().x
                car_y = self.data.frames.get(frame_index).cars.get(i).getCenter().y
                if (abs(centerx + centery - car_x - car_y) < 2) or (frame_index == self.player.frame_count) or (
                        count == 50):
                    existed_car = True
                    break
            car_id = self.addCar(Point(carx, cary), way, True)

        ##while(True):
        ## i = self.player.frameIndex()
        ## if(self.data.frames)
        ##while (i < 5):
        ##i += 1
        ##self.player.nextFrame()

        ##for car_id, car in self.data.frame.cars.items():
        ##print(car.car_center_x)
        ##print(lastx)
        ##if(car.car_center_x + car.car_center_y - lastx - lasty < 10):
        ##break
        ## car_id = self.addCar(Point(lastx, lasty))

    def removeCar(self, car_id):
        for frame in self.data.frames.values():
            if car_id in frame.cars:
                del frame.cars[car_id]

    def addPoint(self, car_id, point_index, position):
        frame_data: Frame = self.data.frames[self.frame_pixmap.frame_index]
        # count = len(frame_data.cars[car_id].bounding_box)
        index = point_index + 1
        # print(point_index, count)
        frame_data.cars[car_id].bounding_box.insert(index, position)
        return index

    def removePoint(self, car_id, point_index):
        frame_data: Frame = self.data.frames[self.frame_pixmap.frame_index]
        del frame_data.cars[car_id].bounding_box[point_index]

        # Remove car if it has no points
        if len(frame_data.cars[car_id].bounding_box) == 0:
            del frame_data.cars[car_id]

    def movePoint(self, car_id, point_index, new_position):
        frame_data: Frame = self.data.frames[self.frame_pixmap.frame_index]
        frame_data.cars[car_id].bounding_box[point_index] = new_position

    def getcarinfo(self):
        return

    def saveCarInfo(self):
        old_car_id = self.selection.car_id
        new_car_id = int(self.car_id_edit.text())

        if new_car_id == old_car_id:
            return

        for frame in self.data.frames.values():
            if new_car_id not in frame.cars and old_car_id in frame.cars:
                frame.cars[new_car_id] = frame.cars.pop(old_car_id)
                self.selection = CarSelection(new_car_id)
                self.redraw()

    def setData(self, data):
        self.data = data
        self.redraw()

    def getData(self):
        return self.data

    def redraw(self):
        if type(self.selection) is CarSelection:
            self.car_id_edit.setText(str(self.selection.car_id))
            self.car_id_edit.setEnabled(True)
            self.car_info_save_btn.setEnabled(True)
        else:
            self.car_id_edit.setText("")
            self.car_id_edit.setEnabled(False)
            self.car_info_save_btn.setEnabled(False)

        if self.frame_pixmap is None:
            return

        player_x = self.frame_pixmap.player_x
        player_y = self.frame_pixmap.player_y
        player_w = self.frame_pixmap.player_w
        player_h = self.frame_pixmap.player_h
        frame_w = self.frame_pixmap.frame_w
        frame_h = self.frame_pixmap.frame_h
        frame_index = self.frame_pixmap.frame_index
        pixmap = self.frame_pixmap.pixmap

        self.scene.clear()

        self.frame_number = QGraphicsTextItem()
        self.frame_number.setPos(player_x + 5, player_y)
        self.frame_number.setDefaultTextColor(QColor("white"))
        font = self.frame_number.font()
        font.setPointSize(25)
        self.frame_number.setFont(font)
        self.frame_number.setPlainText(str(int(frame_index)))
        self.frame_number.setZValue(-50)
        self.scene.addItem(self.frame_number)

        self.video_pixmap = QGraphicsPixmapItem()
        self.video_pixmap.setPos(player_x, player_y)
        self.video_pixmap.setZValue(-100)
        self.video_pixmap.setPixmap(pixmap)
        self.scene.addItem(self.video_pixmap)

        car_id_font = self.frame_number.font()
        car_id_font.setPointSize(16)

        if self.data and frame_index in self.data.frames:
            cars = self.data.frames[frame_index].cars

            for car_id, car in cars.items():
                # Center
                selected = (
                        type(self.selection) is CarSelection
                        and self.selection.car_id == car_id
                )
                center_point = car.getCenter()
                center_x = player_x + center_point.x / frame_w * player_w
                center_y = player_y + center_point.y / frame_h * player_h
                center = CarMarker(QPointF(center_x, center_y), car_id, selected)
                self.scene.addItem(center)

                # Car ID
                corner = car.getLowerLeftCorner()
                corner_x = player_x + corner.x / frame_w * player_w
                corner_y = player_y + corner.y / frame_h * player_h
                car_id_text = QGraphicsTextItem(str(car_id))
                car_id_text.setDefaultTextColor(QColor("white"))
                car_id_text.setPos(corner_x - 10, corner_y + 5)
                car_id_text.setFont(car_id_font)
                self.scene.addItem(car_id_text)

                # Boundary markers
                first_marker = None
                last_marker = None

                for point_index, point in enumerate(car.bounding_box):
                    rescaled_x = player_x + point.x / frame_w * player_w
                    rescaled_y = player_y + point.y / frame_h * player_h

                    selected = (
                            type(self.selection) is MarkerSelection
                            and self.selection.frame_index == frame_index
                            and self.selection.car_id == car_id
                            and self.selection.point_index == point_index
                    )

                    marker = Marker(
                        QPointF(rescaled_x, rescaled_y),
                        car_id,
                        point_index,
                        selected,
                    )
                    self.scene.addItem(marker)

                    if not first_marker:
                        first_marker = marker

                    if last_marker:
                        connection = MarkerConnection(marker, last_marker)
                        self.scene.addItem(connection)

                    last_marker = marker

                connection = MarkerConnection(first_marker, last_marker)
                self.scene.addItem(connection)

    def setFramePixmap(
            self,
            player_x,
            player_y,
            player_w,
            player_h,
            frame_w,
            frame_h,
            frame_index,
            pixmap,
    ):
        # If this is a different frame then reset selection
        if self.frame_pixmap and self.frame_pixmap.frame_index != frame_index:
            self.selection = None

        self.frame_pixmap = FramePixmap(
            player_x,
            player_y,
            player_w,
            player_h,
            frame_w,
            frame_h,
            frame_index,
            pixmap,
        )

        self.redraw()

    def resizeEvent(self, event):
        width, height = event.size().width(), event.size().height()
        self.view.resize(width, height)
        self.view.setSceneRect(QRectF(self.view.contentsRect()))


@dataclass
class Point:
    x: int
    y: int


@dataclass
class Car:
    car_center_x: int
    car_center_y: int
    car_w: float
    car_l: float
    course: float
    head_x: int
    head_y: int
    tail_x: int
    tail_y: int
    lost_counter: int
    bounding_box: List[Point]

    def getCenter(self) -> Point:
        x = 0
        y = 0
        for point in self.bounding_box:
            x += point.x
            y += point.y
        x /= len(self.bounding_box)
        y /= len(self.bounding_box)
        return Point(x, y)

    def getLowerLeftCorner(self) -> Point:
        x = sys.maxsize
        y = 0
        for point in self.bounding_box:
            x = min(x, point.x)
            y = max(y, point.y)
        return Point(x, y)


@dataclass
class Frame:
    cars: Dict[int, Car]


@dataclass
class Data:
    frames: Dict[int, Frame]
    next_car_id: int
    max_frame: int


def loadCSV(path):
    with open(path) as file:
        rows = file.readlines()

        data = Data(frames=dict(), next_car_id=0, max_frame=0)
        for row in rows[1:]:
            (
                frame_num,
                car_id,
                car_center_x,
                car_center_y,
                car_w,
                car_l,
                course,
                head_x,
                head_y,
                tail_x,
                tail_y,
                lost_counter,
                *bounding,
            ) = row.split(",")

            # Ignore cars with no bounding box
            if len(bounding) == 0:
                continue

            bounding_box = []
            for i in range(0, len(bounding), 2):
                x = int(bounding[i])
                y = int(bounding[i + 1])
                bounding_box.append(Point(x, y))

            car = Car(
                car_center_x=int(car_center_x),
                car_center_y=int(car_center_y),
                car_w=float(car_w),
                car_l=float(car_l),
                course=float(course),
                head_x=int(head_x),
                head_y=int(head_y),
                tail_x=int(tail_x),
                tail_y=int(tail_y),
                lost_counter=int(lost_counter),
                bounding_box=bounding_box,
            )

            frame_num = int(frame_num)

            if frame_num not in data.frames:
                data.frames[frame_num] = Frame(cars=dict())

            car_id = int(car_id)
            data.frames[frame_num].cars[car_id] = car
            data.next_car_id = max(data.next_car_id, car_id + 1)
            data.max_frame = max(data.max_frame, frame_num)

        return data


def saveCSV(path, data: Data):
    rows = [
        # Header row
        [
            "frameNUM",
            "carID",
            "carCenterX",
            "carCenterY",
            "carW",
            "carL",
            "course",
            "headX",
            "headY",
            "tailX",
            "tailY",
            "lostCountert",
        ]
    ]

    # Maximum number of points in the bounding box, used for adding columns to the CSV
    bounding_box_max_points = 0

    for frame_id, frame in data.frames.items():
        for car_id, car in frame.cars.items():
            row = [
                str(frame_id),
                str(car_id),
                str(car.car_center_x),
                str(car.car_center_y),
                str(car.car_w),
                str(car.car_l),
                str(car.course),
                str(car.head_x),
                str(car.head_y),
                str(car.tail_x),
                str(car.tail_y),
                str(car.lost_counter),
            ]

            bounding_box_max_points = max(
                bounding_box_max_points, len(car.bounding_box)
            )

            for point in car.bounding_box:
                row.append(str(int(round(point.x))))
                row.append(str(int(round(point.y))))

            rows.append(row)

    # Update header row with bounding box headers
    for i in range(bounding_box_max_points):
        rows[0].append(f"boundingBox{i + 1}X")
        rows[0].append(f"boundingBox{i + 1}Y")

    with open(path, "w") as file:
        for row in rows:
            file.write(",".join(row))
            file.write("\n")
