import sys
from PyQt6.QtCore import QSize, QLocale
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QFrame,
    QPushButton, QRadioButton, QLabel, QLineEdit,
    QButtonGroup, QGridLayout, QGroupBox, QMessageBox
)
from PyQt6.QtGui import QDoubleValidator

import wenner
import schlumberger
import trojele_for
import trojele_bac

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class PlotCanvas(FigureCanvas):
    def __init__(self):
        self.figure = Figure()
        super().__init__(self.figure)

        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Wykres")
        self.draw()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Liczenie oporności pozornej")
        self.setFixedSize(QSize(1000, 600))

        central = QWidget()
        self.setCentralWidget(central)

        self.main_layout = QVBoxLayout()
        central.setLayout(self.main_layout)

        top_frame = QFrame()
        top_layout = QHBoxLayout()
        top_frame.setLayout(top_layout)

        self.radio1 = QRadioButton("Układ Wennera")
        self.radio2 = QRadioButton("Układ Schlumbergera")
        self.radio3 = QRadioButton("Trójelektrodowy (forward)")
        self.radio4 = QRadioButton("Trójelektrodowy (backward)")

        self.radio1.setChecked(True)

        self.radio_group = QButtonGroup()
        for r in [self.radio1, self.radio2, self.radio3, self.radio4]:
            self.radio_group.addButton(r)
            top_layout.addWidget(r)
            r.toggled.connect(self.update_inputs)

        self.main_layout.addWidget(top_frame)

        middle_layout = QHBoxLayout()

        self.left_frame = QGroupBox("Parametry pomiaru")
        left_layout = QVBoxLayout()
        self.left_frame.setLayout(left_layout)

        self.inputs_layout = QGridLayout()
        left_layout.addLayout(self.inputs_layout)
        left_layout.addStretch()

        middle_layout.addWidget(self.left_frame, 2)

        right_frame = QFrame()
        right_layout = QVBoxLayout()
        right_frame.setLayout(right_layout)

        self.plot_canvas = PlotCanvas()
        right_layout.addWidget(self.plot_canvas)

        middle_layout.addWidget(right_frame, 3)

        self.main_layout.addLayout(middle_layout)

        bottom_frame = QFrame()
        bottom_layout = QHBoxLayout()
        bottom_frame.setLayout(bottom_layout)

        self.calc_button = QPushButton("Oblicz")
        self.clear_button = QPushButton("Wyczyść")

        bottom_layout.addStretch()
        bottom_layout.addWidget(self.calc_button)
        bottom_layout.addWidget(self.clear_button)
        bottom_layout.addStretch()

        self.main_layout.addWidget(bottom_frame)

        self.calc_button.clicked.connect(self.update_plot)
        self.clear_button.clicked.connect(self.clear_all)

        self.update_inputs()

    def clear_inputs(self):
        while self.inputs_layout.count():
            item = self.inputs_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def add_input(self, label_text, row, unit=""):
        label = QLabel(label_text)
        edit = QLineEdit()
        edit.setPlaceholderText("0.0")

        validator = QDoubleValidator()
        validator.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))
        edit.setValidator(validator)

        unit_label = QLabel(unit)

        self.inputs_layout.addWidget(label, row, 0)
        self.inputs_layout.addWidget(edit, row, 1)
        self.inputs_layout.addWidget(unit_label, row, 2)

        return edit

    def update_inputs(self):
        sender = self.sender()
        if sender and not sender.isChecked():
            return

        self.clear_inputs()
        self.current_inputs = []

        row = 0

        if self.radio1.isChecked():
            self.current_inputs.append(self.add_input("Rozstaw elektrod (a)", row, "m")); row += 1
            self.current_inputs.append(self.add_input("Krok pomiarowy (Δx)", row, "m")); row += 1
            self.current_inputs.append(self.add_input("Oporność (ϱ1)", row, "Ω·m")); row += 1
            self.current_inputs.append(self.add_input("Oporność (ϱ2)", row, "Ω·m")); row += 1

        elif self.radio2.isChecked():
            self.current_inputs.append(self.add_input("Rozstaw elektrod (a)", row, "m")); row += 1
            self.current_inputs.append(self.add_input("Krotność rozstawu (n)", row, "")); row += 1
            self.current_inputs.append(self.add_input("Krok pomiarowy (Δx)", row, "m")); row += 1
            self.current_inputs.append(self.add_input("Oporność (ϱ1)", row, "Ω·m")); row += 1
            self.current_inputs.append(self.add_input("Oporność (ϱ2)", row, "Ω·m")); row += 1

        elif self.radio3.isChecked():
            self.current_inputs.append(self.add_input("Rozstaw elektrod (a)", row, "m")); row += 1
            self.current_inputs.append(self.add_input("Krotność rozstawu (n)", row, "")); row += 1
            self.current_inputs.append(self.add_input("Krok pomiarowy (Δx)", row, "m")); row += 1
            self.current_inputs.append(self.add_input("Oporność (ϱ1)", row, "Ω·m")); row += 1
            self.current_inputs.append(self.add_input("Oporność (ϱ2)", row, "Ω·m")); row += 1

        elif self.radio4.isChecked():
            self.current_inputs.append(self.add_input("Rozstaw elektrod (a)", row, "m")); row += 1
            self.current_inputs.append(self.add_input("Krotność rozstawu (n)", row, "")); row += 1
            self.current_inputs.append(self.add_input("Krok pomiarowy (Δx)", row, "m")); row += 1
            self.current_inputs.append(self.add_input("Oporność (ϱ1)", row, "Ω·m")); row += 1
            self.current_inputs.append(self.add_input("Oporność (ϱ2)", row, "Ω·m")); row += 1

    def clear_all(self):
        self.update_inputs()
        self.plot_canvas.ax.clear()
        self.plot_canvas.draw()

    def update_plot(self):
        try:
            values = [float(inp.text()) for inp in self.current_inputs]
        except ValueError:
            QMessageBox.warning(self, "Błąd", "Wprowadź poprawne liczby!")
            return

        if self.radio1.isChecked():
            data = wenner.oblicz(*values)
        elif self.radio2.isChecked():
            data = schlumberger.oblicz(*values)
        elif self.radio3.isChecked():
            data = trojele_for.oblicz(*values)
        elif self.radio4.isChecked():
            data = trojele_bac.oblicz(*values)
        else:
            return

        x = [d[0] for d in data]
        y = [d[1] for d in data]

        self.plot_canvas.ax.clear()
        self.plot_canvas.ax.plot(x, y)
        self.plot_canvas.ax.set_title("Wynik obliczeń")
        self.plot_canvas.ax.set_xlabel("Odległość [m]")
        self.plot_canvas.ax.set_ylabel("Oporność [Ω·m]")
        self.plot_canvas.ax.grid()

        self.plot_canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())