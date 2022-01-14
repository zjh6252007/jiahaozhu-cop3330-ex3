from editor import (
    Editor,
    TOOL_ADD_ARC,
    TOOL_ADD_REGION,
    TOOL_ADD_VerticalREGION,
    TOOL_REMOVE_ARC,
    TOOL_REMOVE_REGION,
    loadCSV,
    saveCSV,
)
import os
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
from player import Player
import sys

##os.chdir(os.path.dirname(sys.argv[0]))

QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)

app = QApplication(sys.argv)

app.setStyle(QStyleFactory.create("fusion"))
palette = QPalette()
palette.setColor(QPalette.Window, QColor(19, 19, 19))
palette.setColor(QPalette.WindowText, QColor(194, 194, 194))
palette.setColor(QPalette.Base, QColor(100, 100, 100))
palette.setColor(QPalette.Background, QColor(19, 19, 19))
palette.setColor(QPalette.Text, Qt.white)
palette.setColor(QPalette.Button, QColor(100, 100, 100))
palette.setColor(QPalette.ButtonText, Qt.white)
palette.setColor(QPalette.BrightText, Qt.white)
app.setPalette(palette)

window = QMainWindow()
uic.loadUi("../ui/MainWindow.ui", window)

video_parent = window.findChild(QWidget, "videoParent")
video_next_btn = window.findChild(QPushButton, "videoNextBtn")
video_pause_btn = window.findChild(QPushButton, "videoPauseBtn")
video_play_btn = window.findChild(QPushButton, "videoPlayBtn")
video_previous_btn = window.findChild(QPushButton, "videoPreviousBtn")
video_stop_btn = window.findChild(QPushButton, "videoStopBtn")

action_open_csv = window.findChild(QAction, "actionOpen_CSV")
action_open_video = window.findChild(QAction, "actionOpen_Video")
action_save_csv = window.findChild(QAction, "actionSave_CSV")
action_save_csv_as = window.findChild(QAction, "actionSave_CSV_As")
action_quit = window.findChild(QAction, "actionQuit")
action_add_arc = window.findChild(QAction, "actionAdd_Arc")
action_remove_arc = window.findChild(QAction, "actionRemove_Arc")
action_add_region = window.findChild(QAction, "actionAdd_Region")
action_add_region.setShortcut("Ctrl+Z")
action_add_verticalregion = window.findChild(QAction, "actionAdd_vRegion")
action_add_verticalregion.setShortcut("Ctrl+X")
action_remove_region = window.findChild(QAction, "actionRemove_Region")
action_remove_region.setShortcut("Delete")


action_add_index = window.findChild(QAction, "actionAdd_Index")
action_zoom_in = window.findChild(QAction, "actionZoom_In")
action_zoom_out = window.findChild(QAction, "actionZoom_Out")
action_add_stopvehicle = window.findChild(QAction,"actionAdd_StopVehicle")
frames_slider = window.findChild(QSlider, "framesSlider")
frames_count_label = window.findChild(QLabel, "framesCountLabel")
frame_spin_box = window.findChild(QSpinBox, "frameSpinBox")


car_id_edit = window.findChild(QLineEdit, "carIDEdit")
car_info_save_btn = window.findChild(QPushButton, "carInfoSaveBtn")

neighbor_frames = window.findChild(QListWidget, "neighborFrames")

player = Player(neighbor_frames)
video_parent.layout().addWidget(player, 0, 0)

video_next_btn.clicked.connect(lambda: player.nextFrame())
video_pause_btn.clicked.connect(lambda: player.pause())
video_play_btn.clicked.connect(lambda: player.play())
video_previous_btn.clicked.connect(lambda: player.prevFrame())
video_stop_btn.clicked.connect(lambda: player.stop())

editor = Editor(player, car_id_edit, car_info_save_btn, video_parent)
video_parent.layout().addWidget(editor, 0, 0)
editor.raise_()
csv_path = None

def onOpenCSV():
    global total_frame
    global csv_path
    path, _ = QFileDialog.getOpenFileName(
        window,
        "Open CSV",
        filter="All files (*.*);;CSV (*.csv)",
    )
    if path:
        csv_path = path
        print(f"Loading CSV: {path}")
        data = loadCSV(csv_path)
        editor.setData(data)


def onOpenVideo():
    path, _ = QFileDialog.getOpenFileName(
        window,
        "Open video",
        filter="All files (*.*)",
    )
    if path:
        print(f"Loading video: {path}")
        player.load(path)


def onSaveCSV():
    global csv_path
    if csv_path:
        print(f"Saving CSV: {csv_path}")
        data = editor.getData()
        saveCSV(csv_path, data)
    else:
        onSaveCSVAs()


def onSaveCSVAs():
    global csv_path
    path, _ = QFileDialog.getSaveFileName(
        window,
        "Save CSV",
        filter="All files (*.*);;CSV (*.csv)",
    )
    if path:
        csv_path = path
        print(f"Saving CSV: {csv_path}")
        data = editor.getData()
        saveCSV(csv_path, data)


def activateTool(tool):
    editor.toggleTool(tool)

    active_tool = editor.getActiveTool()
    # print(active_tool)

    action_add_arc.blockSignals(True)
    action_add_arc.setChecked(active_tool == TOOL_ADD_ARC)
    action_add_arc.blockSignals(False)
    action_add_region.blockSignals(True)
    action_add_region.setChecked(active_tool == TOOL_ADD_REGION)
    action_add_region.blockSignals(False)

    action_add_verticalregion.blockSignals(True)
    action_add_verticalregion.setChecked(active_tool == TOOL_ADD_VerticalREGION)
    action_add_verticalregion.blockSignals(False)

action_open_csv.triggered.connect(onOpenCSV)
action_open_video.triggered.connect(onOpenVideo)
action_save_csv.triggered.connect(onSaveCSV)
action_save_csv_as.triggered.connect(onSaveCSVAs)
action_quit.triggered.connect(lambda: QApplication.quit())
action_add_arc.toggled.connect(lambda: activateTool(TOOL_ADD_ARC))
action_remove_arc.triggered.connect(lambda: activateTool(TOOL_REMOVE_ARC))
action_add_region.toggled.connect(lambda: activateTool(TOOL_ADD_REGION))
action_add_verticalregion.toggled.connect(lambda: activateTool(TOOL_ADD_VerticalREGION))
action_remove_region.triggered.connect(lambda: activateTool(TOOL_REMOVE_REGION))
action_zoom_in.triggered.connect(editor.zoomIn)
action_zoom_out.triggered.connect(editor.zoomOut)
action_add_stopvehicle.triggered.connect(editor.addstopvehicle)
action_add_index.triggered.connect(editor.addIndex)


frames_slider.valueChanged.connect(player.setFrame)
frame_spin_box.valueChanged.connect(player.setFrame)


def onLoad():
    frames_slider.setRange(0, player.frame_count - 1)
    frames_count_label.setText(f"/ {player.frame_count-1}")
    frame_spin_box.setRange(0, player.frame_count - 1)


def onFrame(
    player_x,
    player_y,
    player_w,
    player_h,
    frame_w,
    frame_h,
    frame_index,
    pixmap,
):
    editor.setFramePixmap(
        player_x,
        player_y,
        player_w,
        player_h,
        frame_w,
        frame_h,
        frame_index,
        pixmap,
    )

    frames_slider.blockSignals(True)
    frames_slider.setValue(frame_index)
    frames_slider.blockSignals(False)

    frame_spin_box.blockSignals(True)
    frame_spin_box.setValue(frame_index)
    frame_spin_box.blockSignals(False)


player.onLoad = onLoad
player.onFrame = onFrame
player.onResize = editor.setGeometry

# player.load("../data/DJI_0543.MP4")
# player.play()

# data = loadCSV("../data/DJI_0543stab.csv")
# editor.setData(data)

# save_csv("../test.csv", data)

window.show()
app.exec_()
