import cv2
import imutils
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import qimage2ndarray

#test2

class Player(QWidget):
    def __init__(self, neighbor_frames, parent=None):
        super().__init__(parent)

        self.setMinimumSize(200, 200)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setContentsMargins(0, 0, 0, 0)

        self.video_x = 0
        self.video_y = 0
        self.video_w = 0
        self.video_h = 0
        self.fps = 1
        self.frame_w = 0  # Original frame width
        self.frame_h = 0  # Original frame height
        self.frame_count = 0
        self.frame = None
        self.thumbnails_frame = None

        self.video_capture = cv2.VideoCapture()
        self.frame_timer = QTimer()
        self.frame_timer.timeout.connect(self.frame_func)

        frame_view = QLabel("", None)
        frame_view.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        frame_view.hide()
        self.frame_view = frame_view

        layout = QGridLayout()
        layout.addWidget(self.frame_view, 0, 0, Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        # layout.setMargin(0)
        self.setLayout(layout)
        # Events
        self.onLoad = lambda: None
        self.onFrame = lambda x, y, w, h, frame_w, frame_h, frame_index, pixmap: None
        self.onResize = lambda x, y, w, h: None

        # Neighbor frames widget
        self.neighbor_frames = neighbor_frames
        self.neighbor_frames.itemClicked.connect(self.frameNeighborClicked)

    def load(self, path):
        self.video_capture.open(path)
        self.video_capture.set(cv2.CAP_PROP_BUFFERSIZE, 60)
        self.frame_w = int(self.video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_h = int(self.video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = self.video_capture.get(cv2.CAP_PROP_FPS)
        self.frame_count = int(self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        self.frame = None
        self.thumbnails_frame = None
        self.calcVideoSize()
        self.frame_func()
        self.onLoad()

    def play(self):
        self.frame_timer.start(int(1000 // self.fps))
        self.frame_view.show()
        self.setNeighborFrames()

    def pause(self):
        self.frame_timer.stop()
        self.setNeighborFrames()

    def stop(self):
        self.setFrame(0)
        self.pause()

    def setFrame(self, frame_index):
        if self.frame_timer.isActive():
            self.frame_timer.stop()
            self.frame_timer.start()

        if frame_index >= 0 and frame_index < self.frame_count - 1:
            self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
            _, frame = self.video_capture.read()
            self.frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        self.drawFrame()
        self.setNeighborFrames()

    def nextFrame(self):
        self.setFrame(self.frameIndex() + 1)

    def prevFrame(self):
        self.setFrame(self.frameIndex() - 1)


    def setNeighborFrames(self):
        # Save the original frame index
        current_frame = self.frameIndex() + 1

        if self.thumbnails_frame == current_frame:
            return

        self.neighbor_frames.clear()

        # Do nothing to the thumbnail area if we're currently playing
        if self.frame_timer.isActive() or self.frame is None:
            return

        self.thumbnails_frame = current_frame

        width = 128  # Icon width
        space = self.neighbor_frames.width() - 15
        count = space // (width + 3)

        # Go to the first neighbor frame
        first_neighbor_frame = max(0, current_frame - count // 2)
        self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, first_neighbor_frame)

        for neighbor_frame in range(first_neighbor_frame, first_neighbor_frame + count):
            if neighbor_frame < self.frame_count - 1:
                _, frame = self.video_capture.read()
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = imutils.resize(frame, width=width)

                # Convert the neighbor frame to a QPixmap
                image = qimage2ndarray.array2qimage(frame)
                pixmap = QPixmap.fromImage(image)
                # pixmap = pixmap.scaled(QSize(256, 256), Qt.KeepAspectRatio)

                list_item = QListWidgetItem()
                # list_item.setIconSize(QSize(size[0], size[1]))
                list_item.setIcon(QIcon(pixmap))
                list_item.setText(f"Frame {neighbor_frame}")
                list_item.setData(0, neighbor_frame)

                self.neighbor_frames.addItem(list_item)

        # Restore original frame
        self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, current_frame)

    def frameNeighborClicked(self, item):
        frame = item.data(0)
        if frame != self.frameIndex():
            self.setFrame(frame)

    def frame_func(self):
        if self.video_capture.isOpened():
            if self.frameIndex() < self.frame_count - 1:
                _, frame = self.video_capture.read()
                self.frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:
                self.pause()
        self.drawFrame()

    # The frame that was last draw
    def frameIndex(self):
        if self.video_capture.isOpened():
            return int(self.video_capture.get(cv2.CAP_PROP_POS_FRAMES)) - 1
        else:
            return -1

    def drawFrame(self):
        if self.frame is not None:
            size = (self.video_w, self.video_h)

            frame = cv2.resize(self.frame, size, interpolation=cv2.INTER_AREA)
            image = qimage2ndarray.array2qimage(frame)
            pixmap = QPixmap.fromImage(image)

            # self.frame_view.setPixmap(pixmap)

            self.onFrame(
                self.video_x,
                self.video_y,
                self.video_w,
                self.video_h,
                self.frame_w,
                self.frame_h,
                self.frameIndex(),
                pixmap,
            )

    def calcVideoSize(self):
        if self.video_capture.isOpened():
            max_w = self.rect().width()
            max_h = self.rect().height()

            original_w = self.frame_w
            original_h = self.frame_h

            ratio_w = max_w / original_w
            ratio_h = max_h / original_h

            best_fit_ratio = min(ratio_w, ratio_h)

            self.video_w = round(original_w * best_fit_ratio)
            self.video_h = round(original_h * best_fit_ratio)

            self.video_x = round(max_w / 2 - self.video_w / 2)
            self.video_y = round(max_h / 2 - self.video_h / 2)

            # print(self.video_w, self.video_h, self.video_x, self.video_y)

        self.onResize(
            self.rect().x(),
            self.rect().y(),
            self.rect().width(),
            self.rect().height(),
        )

        self.drawFrame()

    def resizeEvent(self, event):
        self.calcVideoSize()
        # self.setNeighborFrames()  # Makes it very very slow

    def close_win(self):
        self.video_capture.release()
        cv2.destroyAllWindows()
        self.close()
