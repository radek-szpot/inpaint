import sys
from typing import Optional
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QColor, QFont, QImage, QPainter, QPixmap, QMovie
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QGridLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStatusBar,
    QWidget,
)
from app.inpaint import inpaint_algorithms, cv, np
from threading import *

COMBO_MAP = {
    'Skimage-biharmonic': 5,
    'OpenCV-NS': 0,
    'OpenCV-TELEA': 1,
    'OpenCV-Shiftmap': 4,
    'OpenCV-FSR fast': 2,
    'OpenCV-FSR best': 3,
}


class ImageLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setText('Drop image to inpaint here')
        self.setStyleSheet('''QLabel{border: 4px dashed #aaa}''')


class Canvas(QLabel):
    def __init__(self, w, h):
        super().__init__()
        self.mask_array = np.zeros(shape=(h, w, 1), dtype=np.uint8)
        pixmap = QPixmap(w, h)
        pixmap.fill(Qt.transparent)
        self.setPixmap(pixmap)

        self.last_x, self.last_y = None, None
        self.pen_color = Qt.white

    def set_pen_color(self, c):
        self.pen_color = QColor(c)

    def mouseMoveEvent(self, e):
        if self.last_x is None:  # First event.
            self.last_x = e.x()
            self.last_y = e.y()
            return  # Ignore the first time.

        painter = QPainter(self.pixmap())
        painter.setOpacity(0.2)
        p = painter.pen()
        p.setWidth(7)
        p.setColor(self.pen_color)
        painter.setPen(p)
        painter.drawLine(self.last_x, self.last_y, e.x(), e.y())
        painter.end()
        self.update()
        self.mask_array[self.last_y, self.last_x] = 255
        self.mask_array[e.y(), e.x()] = 255

        # Update the origin for next time.
        self.last_x = e.x()
        self.last_y = e.y()

    def mouseReleaseEvent(self, e):
        self.last_x = None
        self.last_y = None


class MainWindow(QMainWindow):
    path_original: Optional[str] = ""
    path_mask: Optional[str] = ""
    path_saving: Optional[str] = ""
    img_inpainted = None
    img_mask = None
    canvas = None

    def __init__(self):
        super().__init__(parent=None)
        self.setWindowTitle("Inpaint app")
        self.resize(1024, 600)
        self.setAcceptDrops(True)
        # initialize ui fields
        self.drag_image = ImageLabel()
        self.image_after = QLabel("After inpaint the result will be displayed here")
        self.image_after.setAlignment(Qt.AlignCenter)
        self.btn_inpaint = QPushButton("Make inpaint with specified algorithm:")
        self.btn_inpaint.clicked.connect(self.inpaint_click)
        self.btn_mask = QPushButton("Upload proper mask for selected image")
        self.btn_mask.clicked.connect(self.mask_click)
        self.btn_save = QPushButton("Save inpainted image")
        self.btn_save.clicked.connect(self.save_click)
        self.combobox_inpaint = QComboBox()
        self.combobox_inpaint.addItems(COMBO_MAP.keys())
        self.btn_add_mask = QPushButton("Manually create mask on current image (not recommended)")
        self.btn_add_mask.clicked.connect(self.add_mask_click)
        self.btn_upload_mask = QPushButton("Upload mask added manually (not recommended)")
        self.btn_upload_mask.clicked.connect(self.upload_mask_click)
        self.movie = QMovie("../assets/loading.gif")
        self.loading_gif = QLabel()
        self.loading_gif.setMovie(self.movie)
        self.loading_gif.setAlignment(Qt.AlignCenter)
        # set layout and widgets
        self.layout = QGridLayout()
        self.widget = QWidget()
        self.layout.addWidget(self.btn_inpaint, 0, 0)
        self.layout.addWidget(self.combobox_inpaint, 0, 1)
        self.layout.addWidget(self.btn_mask, 1, 0)
        self.layout.addWidget(self.btn_save, 1, 1)
        self.layout.addWidget(self.drag_image, 2, 0)
        self.layout.addWidget(self.image_after, 2, 1)
        self.layout.addWidget(self.loading_gif, 2, 1)
        self.layout.addWidget(self.btn_add_mask, 3, 0)
        self.layout.addWidget(self.btn_upload_mask, 3, 1)
        self.widget.setLayout(self.layout)

        self.setCentralWidget(self.widget)
        self.create_menu()
        self.statusBar().setStyleSheet("background-color : #e6e6e6; border :1px inset #c7c7c7;")

    def create_menu(self):
        menu = self.menuBar().addMenu("&Menu")
        help = self.menuBar().addMenu("Help")
        menu.addAction("&Exit", self.close)
        # help.addAction()

    def _createStatusBar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def display_status_bar_message(self, message):
        self.statusBar().showMessage(message)
        self.statusBar().show()
        QTimer.singleShot(5000, self.statusBar().clearMessage)

    def dragEnterEvent(self, event):
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasImage:
            event.setDropAction(Qt.CopyAction)
            file_path = event.mimeData().urls()[0].toLocalFile()
            # TODO: add validation function callback if is graphic file
            self.path_original = file_path
            self.set_image(file_path)

            event.accept()
        else:
            event.ignore()

    def set_image(self, file_path):
        image = QPixmap(file_path)
        image = image.scaled(512, 512, Qt.KeepAspectRatio, Qt.FastTransformation)
        self.drag_image.setPixmap(image)

    def movie_start(self):
        self.display_status_bar_message("Loading")
        self.movie.setScaledSize(QSize().scaled(150, 150, Qt.KeepAspectRatio))
        self.movie.start()
        self.loading_gif.show()
        self.image_after.setText("")

    def movie_stop(self):
        self.movie.stop()
        self.loading_gif.hide()
        self.image_after.show()
        self.display_status_bar_message("Inpainted successfully")

    def inpaint_click(self):
        if self.path_original and (self.path_mask or self.img_mask is not None):
            self.movie_start()
            thread = Thread(target=self.inpaint_operation)
            thread.start()
        elif not self.path_original:
            self.display_status_bar_message(f"Please upload image to inpaint")
        else:
            self.display_status_bar_message(f"Please upload mask of image to inpaint")

    def inpaint_operation(self):
        inpaint_flag = COMBO_MAP[self.combobox_inpaint.currentText()]
        try:
            self.img_inpainted, error = inpaint_algorithms(
                img_path=self.path_original,
                mask_path=self.path_mask if self.path_mask else None,
                img_mask=self.img_mask,
                flag=inpaint_flag,
            )
            if error:
                self.display_status_bar_message(f"Unhandled error while inpainting: {error}")
            else:
                self.movie_stop()
                image_after = QImage(
                    self.img_inpainted,
                    self.img_inpainted.shape[1],
                    self.img_inpainted.shape[0],
                    self.img_inpainted.shape[1] * 3,
                    QImage.Format_RGB888
                )
                pixmap_img_after = QPixmap(image_after)
                pixmap_img_after = pixmap_img_after.scaled(512, 512, Qt.KeepAspectRatio, Qt.FastTransformation)
                self.image_after.setPixmap(pixmap_img_after)
        except Exception as e:
            self.display_status_bar_message(f"Error while inpainting: {e}")

    def mask_click(self):
        mask = QFileDialog.getOpenFileName(self, "Select mask for image", self.path_original, "All Files (*)")
        if mask[0]:
            # TODO: add validation function callback if is graphic file
            self.path_mask = mask[0]

    def save_click(self):
        if self.img_inpainted is None:
            self.display_status_bar_message(f"You must make proper inpaint first")
            return
        path_saving = QFileDialog.getSaveFileName(
            self,
            "Save inpainted image",
            f"{self.path_original}/inpainted_image",
            "All Files (*)"
        )
        if path_saving[0]:
            try:
                cv.imwrite(f'{path_saving[0]}.jpg', cv.cvtColor(self.img_inpainted, cv.COLOR_BGR2RGB))
                self.display_status_bar_message(f"Successfully saved in {path_saving[0]}")
            except Exception as e:
                self.display_status_bar_message(f"Error while saving: {e}")

    def add_mask_click(self):
        if self.canvas is None and not self.path_original:
            self.display_status_bar_message("First you need to add image to inpaint")
            return
        elif self.canvas is None:
            self.canvas = Canvas(self.drag_image.width(), self.drag_image.height())
            self.layout.addWidget(self.canvas, 2, 0)
        else:
            self.display_status_bar_message("Already added canvas try holding LPM on image to inpaint")

    def upload_mask_click(self):
        if self.canvas is None:
            self.display_status_bar_message('Before uploading mask you must create it ')
            return
        self.img_mask = self.canvas.mask_array
        if self.path_mask:
            self.path_mask = ""
        self.display_status_bar_message('Uploaded created mask to memory. See results with "Make inpaint" button')
