from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLineEdit,
                             QPushButton, QLabel, QColorDialog, QCheckBox)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import pyqtSignal, QTimer

class CellEditor(QWidget):
    cell_updated = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        self.form_layout = QFormLayout()
        self.layout.addLayout(self.form_layout)

        self.cell = None
        self.gene_inputs = {}

        for gene in ['size', 'speed', 'energy_efficiency', 'division_threshold', 'consumption_size_ratio', 'nitrogen_reserve', 'radiation_sensitivity']:
            self.gene_inputs[gene] = QLineEdit()
            self.gene_inputs[gene].setEnabled(False)
            self.form_layout.addRow(gene.replace('_', ' ').title(), self.gene_inputs[gene])

        self.color_button = QPushButton("Change Colour")
        self.color_button.clicked.connect(self.change_color)
        self.color_button.setEnabled(False)
        self.form_layout.addRow("Color", self.color_button)

        self.has_tail_checkbox = QCheckBox("Has Tail")
        self.has_tail_checkbox.stateChanged.connect(self.update_has_tail)
        self.has_tail_checkbox.setEnabled(False)
        self.form_layout.addRow("Tail", self.has_tail_checkbox)

        self.can_consume_checkbox = QCheckBox("Can Consume")
        self.can_consume_checkbox.stateChanged.connect(self.update_can_consume)
        self.can_consume_checkbox.setEnabled(False)
        self.form_layout.addRow("Type", self.can_consume_checkbox)

        self.adhesin_checkbox = QCheckBox("Adhesin")
        self.adhesin_checkbox.stateChanged.connect(self.update_adhesin)
        self.adhesin_checkbox.setEnabled(False)
        self.form_layout.addRow("Adhesin", self.adhesin_checkbox)

        self.never_consume_checkbox = QCheckBox("Never Consume")
        self.never_consume_checkbox.stateChanged.connect(self.update_never_consume)
        self.never_consume_checkbox.setEnabled(True)
        self.form_layout.addRow("Never Consume", self.never_consume_checkbox)

        self.dna_label = QLabel()
        self.form_layout.addRow("DNA", self.dna_label)

        self.energy_label = QLabel()
        self.form_layout.addRow("Energy", self.energy_label)

        self.apply_button = QPushButton("Apply Changes")
        self.apply_button.clicked.connect(self.apply_changes)
        self.apply_button.setEnabled(False)
        self.layout.addWidget(self.apply_button)

        # Timer to update the energy level in real-time
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_energy_label)
        self.update_timer.start(100)  # Update every 100 milliseconds

    def set_cell(self, cell):
        self.cell = cell
        if cell:
            for gene, input_field in self.gene_inputs.items():
                input_field.setText(str(cell.genome.genes[gene]))
                input_field.setEnabled(True)
            self.color_button.setStyleSheet(f"background-color: rgb({int(cell.genome.genes['color'][0]*255)}, {int(cell.genome.genes['color'][1]*255)}, {int(cell.genome.genes['color'][2]*255)})")
            self.color_button.setEnabled(True)
            self.has_tail_checkbox.setChecked(cell.genome.genes['has_tail'])
            self.has_tail_checkbox.setEnabled(True)
            self.can_consume_checkbox.setChecked(cell.genome.genes['can_consume'])
            self.can_consume_checkbox.setEnabled(True)
            self.adhesin_checkbox.setChecked(cell.genome.genes['adhesin'])
            self.adhesin_checkbox.setEnabled(True)
            self.dna_label.setText(f"{cell.dna:08X}")
            self.apply_button.setEnabled(True)
            self.update_energy_label()
        else:
            for input_field in self.gene_inputs.values():
                input_field.clear()
                input_field.setEnabled(False)
            self.color_button.setStyleSheet("")
            self.color_button.setEnabled(False)
            self.has_tail_checkbox.setChecked(False)
            self.has_tail_checkbox.setEnabled(False)
            self.can_consume_checkbox.setChecked(False)
            self.can_consume_checkbox.setEnabled(False)
            self.adhesin_checkbox.setChecked(False)
            self.adhesin_checkbox.setEnabled(False)
            self.dna_label.clear()
            self.energy_label.clear()
            self.apply_button.setEnabled(False)

    def apply_changes(self):
        if self.cell:
            for gene, input_field in self.gene_inputs.items():
                self.cell.genome.genes[gene] = float(input_field.text())
            self.cell.genome.never_consume = self.never_consume_checkbox.isChecked()
            self.cell_updated.emit(self.cell)

    def change_color(self):
        if self.cell:
            color = QColorDialog.getColor()
            if color.isValid():
                self.cell.genome.genes['color'] = (color.redF(), color.greenF(), color.blueF())
                self.color_button.setStyleSheet(f"background-color: {color.name()}")
                self.cell_updated.emit(self.cell)

    def update_has_tail(self, state):
        if self.cell:
            self.cell.genome.genes['has_tail'] = bool(state)
            self.cell_updated.emit(self.cell)

    def update_can_consume(self, state):
        if self.cell:
            self.cell.genome.genes['can_consume'] = bool(state)
            self.cell_updated.emit(self.cell)

    def update_adhesin(self, state):
        if self.cell:
            self.cell.genome.genes['adhesin'] = bool(state)
            self.cell_updated.emit(self.cell)

    def update_never_consume(self, state):
        if self.cell:
            if state == 2:  # Checked
                self.can_consume_checkbox.setEnabled(False)
                self.cell.genome.never_consume = True
            else:
                self.can_consume_checkbox.setEnabled(True)
                self.cell.genome.never_consume = False
            self.cell_updated.emit(self.cell)

    def update_energy_label(self):
        if self.cell:
            self.energy_label.setText(f"Energy: {self.cell.energy:.2f}")
