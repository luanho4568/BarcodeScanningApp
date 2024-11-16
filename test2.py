import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QPushButton,
    QFileDialog,
    QVBoxLayout,
    QWidget,
    QMessageBox,
    QProgressBar,
    QHBoxLayout,
)
from PyQt5.QtGui import QPixmap, QImage, QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from pyzbar.pyzbar import decode
import cv2
import time


class BarcodeScannerWorker(QThread):
    result_ready = pyqtSignal(str)
    progress_updated = pyqtSignal(int)

    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path

    def run(self):
        """Quét mã vạch trong một luồng riêng biệt."""
        image = cv2.imread(self.image_path)
        if image is None:
            self.result_ready.emit(
                "Không thể đọc ảnh. Vui lòng kiểm tra định dạng file."
            )
            return

        # Giả lập quá trình quét
        for i in range(101):
            time.sleep(
                0.005
            )  # Thay đổi thời gian này để làm chậm hoặc nhanh quá trình quét
            self.progress_updated.emit(i)

        self.scan_with_pyzbar(image)

    def scan_with_pyzbar(self, image):
        """Sử dụng Pyzbar để quét mã vạch."""
        decoded_objects = decode(image)
        if decoded_objects:
            result_text = "Kết quả quét mã vạch:\n"
            for obj in decoded_objects:
                barcode_type = obj.type  # Loại mã vạch (QR, CODE128, v.v.)
                barcode_data = obj.data.decode("utf-8")  # Dữ liệu trong mã vạch
                result_text += f"Loại: {barcode_type}\nNội dung: {barcode_data}\n\n"
            self.result_ready.emit(result_text)
        else:
            self.result_ready.emit("Không tìm thấy mã vạch trong ảnh.")


class BarcodeScannerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ứng Dụng Đọc Mã Vạch")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #f0f2f5;")
        font = QFont("Arial", 10)
        self.setFont(font)
        self.create_ui_components()
        self.image_path = None

    def create_ui_components(self):
        """Tạo các thành phần giao diện cho ứng dụng."""
        self.image_label = QLabel("Tải ảnh lên để quét mã vạch")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet(
            "border: 2px solid #ccc; border-radius: 8px; background-color: #ffffff;"
        )
        self.image_label.setFixedSize(600, 400)

        # Căn giữa ô hiển thị ảnh
        self.image_layout = QHBoxLayout()
        self.image_layout.addStretch()  # Thêm khoảng trống bên trái
        self.image_layout.addWidget(self.image_label)
        self.image_layout.addStretch()  # Thêm khoảng trống bên phải

        self.load_button = QPushButton("Chọn ảnh")
        self.load_button.clicked.connect(self.load_image)
        self.load_button.setStyleSheet(
            "background-color: #4CAF50; color: white; padding: 10px; border-radius: 8px;"
        )

        self.scan_button = QPushButton("Quét mã vạch")
        self.scan_button.clicked.connect(self.scan_barcode)
        self.scan_button.setStyleSheet(
            "background-color: #2196F3; color: white; padding: 10px; border-radius: 8px;"
        )

        self.result_label = QLabel("Kết quả quét sẽ hiển thị ở đây")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet(
            "border: 2px solid #ccc; border-radius: 8px; background-color: #ffffff; padding: 10px;"
        )

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet(
            """
                QProgressBar {
                    background-color: #e0e0e0;
                    border-radius: 5px;
                    text-align: center; /* Căn giữa chữ trong thanh */
                }
                QProgressBar::chunk {
                    background-color: #4CAF50;  /* Màu xanh lá cây */
                    border-radius: 5px;
                }
                QProgressBar::text {
                    color: white;  /* Màu chữ trắng */
                }
            """
        )

        self.progress_bar.hide()  # Ẩn thanh tiến trình ngay từ đầu

        self.layout_ui()

    def layout_ui(self):
        """Bố cục các thành phần giao diện trong cửa sổ."""
        layout = QVBoxLayout()
        layout.addLayout(self.image_layout)  # Thêm bố cục ảnh vào layout chính
        layout.addWidget(self.load_button)
        layout.addWidget(self.scan_button)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.result_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def load_image(self):
        """Tải ảnh từ máy tính."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Chọn ảnh", "", "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            try:
                self.image_path = file_path
                self.display_image(file_path)
                self.result_label.setText(
                    "Ảnh đã được tải lên, nhấn 'Quét mã vạch' để tiếp tục."
                )
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể tải ảnh: {str(e)}")

    def display_image(self, file_path):
        """Hiển thị ảnh đã tải lên."""
        image = QImage(file_path)
        self.image_label.setPixmap(
            QPixmap.fromImage(image).scaled(600, 400, Qt.KeepAspectRatio)
        )

    def scan_barcode(self):
        """Quét mã vạch từ ảnh đã tải lên."""
        if self.image_path:
            self.progress_bar.setValue(0)  # Đặt thanh tiến trình về 0
            self.progress_bar.show()  # Hiện thanh tiến trình
            self.result_label.setText("Đang quét mã vạch...")

            self.thread = BarcodeScannerWorker(self.image_path)
            self.thread.result_ready.connect(self.display_result)
            self.thread.progress_updated.connect(self.update_progress)
            self.thread.start()
        else:
            self.result_label.setText("Vui lòng tải ảnh lên trước")

    def update_progress(self, value):
        """Cập nhật giá trị của thanh tiến trình và hiển thị số %."""
        self.progress_bar.setValue(value)
        # Cập nhật định dạng số % để hiển thị bên trong thanh tiến trình
        if value < 100:
            self.progress_bar.setFormat(f"{value}%")
        else:
            self.progress_bar.setFormat("100%")  # Đặt lại về "100%" khi hoàn thành
            self.progress_bar.hide()  # Ẩn thanh tiến trình khi hoàn thành

    def display_result(self, result_text):
        """Hiển thị kết quả quét mã vạch."""
        self.result_label.setText(result_text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BarcodeScannerApp()
    window.show()
    sys.exit(app.exec_())
