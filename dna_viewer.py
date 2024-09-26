from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QRectF

class DNAViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(50)  # Set fixed height to 50 pixels
        self.layout = QVBoxLayout(self)
        self.dna_label = QLabel()
        self.layout.addWidget(self.dna_label)
        self.cell = None

    def set_cell(self, cell):
        self.cell = cell
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.cell:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Display DNA as hex
        dna_hex = f"{self.cell.dna:08X}"
        self.dna_label.setText(f"DNA: {dna_hex}")

        # Visualize DNA as colored rectangles
        rect_width = self.width() / 32
        rect_height = self.height() / 2

        for i in range(32):
            bit = (self.cell.dna >> (31 - i)) & 1
            color = Qt.black if bit else Qt.white
            painter.fillRect(QRectF(i * rect_width, rect_height, rect_width, rect_height), color)
            painter.setPen(QPen(Qt.gray, 1))
            painter.drawRect(QRectF(i * rect_width, rect_height, rect_width, rect_height))
