# This script uses PyQt5 for GUI functionality. Make sure PyQt5 is installed in your environment.
# You can install it using: pip install PyQt5

import sys
import time

try:
    from PyQt5.QtWidgets import (
        QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout,
        QGridLayout, QMessageBox, QComboBox, QFrame, QTextEdit
    )
    from PyQt5.QtCore import Qt, QTimer
    from PyQt5.QtGui import QFont
except ModuleNotFoundError:
    print("PyQt5 is not installed. Please run 'pip install PyQt5' and try again.")
    sys.exit(1)

PHASES = ["Start", "In", "End"]

class Cart:
    def __init__(self, id):
        self.id = id
        self.scene = ((id - 1) // 3) + 1
        self.phase = (id - 1) % 3
        self.active = True
        self.running = True
        self.history = []

    def status(self):
        if not self.active:
            return "Out of Commission"
        return "Running" if self.running else "Stopped"

    def log_movement(self):
        timestamp = time.strftime("%H:%M:%S")
        scene_name = "Loading Bay" if self.scene == 7 else f"Scene {self.scene}"
        phase = PHASES[self.phase]
        self.history.append(f"[{timestamp}] {phase} - {scene_name}")

class RideControlSystem(QWidget):
    def __init__(self):
        self.blink_flag = False
        super().__init__()
        self.setWindowTitle("🎢 Ride Control System")
        self.setMinimumSize(1000, 700)
        self.setStyleSheet("background-color: #f0f4f7;")
        self.carts = [Cart(i + 1) for i in range(21)]
        self.blink_flag = False
        self.init_ui()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.advance_carts)
        self.timer.start(5000)
        self.blink_timer = QTimer(self)
        self.blink_timer.timeout.connect(self.toggle_blink)
        self.blink_timer.start(5000)

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Ride Vehicle Tracker")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.grid = QGridLayout()
        self.cart_labels = []
        for i, cart in enumerate(self.carts):
            label = QLabel(self.cart_display(cart))
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("border: 1px solid #ccc; border-radius: 10px; padding: 8px; background-color: white;")
            self.grid.addWidget(label, cart.scene, i % 3)
            self.cart_labels.append(label)

        layout.addLayout(self.grid)

        control_frame = QFrame()
        control_frame.setStyleSheet("background-color: #e1ecf4; border-radius: 8px;")
        control_box = QVBoxLayout(control_frame)

        control_layout = QHBoxLayout()
        self.cart_selector = QComboBox()
        self.cart_selector.addItems([f"Boat {c.id}" for c in self.carts])

        btn_stop_one = QPushButton("Stop Selected")
        btn_start_one = QPushButton("Start Selected")
        btn_remove = QPushButton("Remove Boat")
        btn_restore = QPushButton("Restore Boat")

        for btn in (btn_stop_one, btn_start_one, btn_remove, btn_restore):
            btn.setStyleSheet("padding: 6px 12px; border-radius: 5px; background-color: #d6eaff;")

        btn_stop_one.clicked.connect(self.stop_one)
        btn_start_one.clicked.connect(self.start_one)
        btn_remove.clicked.connect(self.remove_one)
        btn_restore.clicked.connect(self.restore_one)

        control_layout.addWidget(self.cart_selector)
        control_layout.addWidget(btn_stop_one)
        control_layout.addWidget(btn_start_one)
        control_layout.addWidget(btn_remove)
        control_layout.addWidget(btn_restore)

        control_box.addLayout(control_layout)

        scene_assign_layout = QHBoxLayout()
        self.scene_selector = QComboBox()
        self.scene_selector.addItems(["Scene 1", "Scene 2", "Scene 3", "Scene 4", "Scene 5", "Scene 6", "Loading Bay"])
        self.phase_selector = QComboBox()
        self.phase_selector.addItems(PHASES)
        btn_assign_scene = QPushButton("Move Boat to Selected Scene")
        btn_assign_scene.setStyleSheet("padding: 6px 12px; border-radius: 5px; background-color: #d6eaff;")
        btn_assign_scene.clicked.connect(self.assign_scene)
        scene_assign_layout.addWidget(self.scene_selector)
        scene_assign_layout.addWidget(self.phase_selector)
        scene_assign_layout.addWidget(btn_assign_scene)
        control_box.addLayout(scene_assign_layout)

        all_control_layout = QHBoxLayout()
        btn_stop_all = QPushButton("Emergency Stop All")
        btn_start_all = QPushButton("Start All Boat")
        for btn in (btn_stop_all, btn_start_all):
            btn.setStyleSheet("padding: 10px; font-weight: bold; background-color: #fddede; border-radius: 8px;")

        btn_stop_all.clicked.connect(self.stop_all)
        btn_start_all.clicked.connect(self.start_all)

        all_control_layout.addWidget(btn_stop_all)
        all_control_layout.addWidget(btn_start_all)

        control_box.addLayout(all_control_layout)

        self.history_log = QTextEdit()
        self.history_log.setReadOnly(True)
        self.history_log.setStyleSheet("background-color: #ffffff; border-radius: 5px; padding: 5px;")
        self.history_log.setFixedHeight(150)
        control_box.addWidget(QLabel("Boat Movement Log:"))
        control_box.addWidget(self.history_log)

        layout.addWidget(control_frame)
        self.setLayout(layout)
        self.update_display()

    def cart_display(self, cart):
        scene_name = "Loading Bay" if cart.scene == 7 else f"Scene {cart.scene}"
        phase = PHASES[cart.phase]
        return f"Boat {cart.id}\n{scene_name} ({phase})\nStatus: {cart.status()}"

    def update_display(self):
        blink_on = self.blink_flag
        for i, cart in enumerate(self.carts):
            self.cart_labels[i].setText(self.cart_display(cart))
            if not cart.active:
                color = "#ffcccc"
            elif cart.running:
                color = "#b3ffcc"
            else:
                color = "#ffe0b3"
            if blink_on and cart.running:
                color = "#a0f0a0"
            style = f"border: 1px solid #aaa; border-radius: 10px; padding: 8px; background-color: {color};"
            self.cart_labels[i].setStyleSheet(style)
        self.update_history_log()

    def update_history_log(self):
        lines = []
        for cart in self.carts:
            if cart.history:
                lines.append(f"Boat {cart.id} History:")
                lines.extend(["  " + entry for entry in cart.history[-3:]])
        self.history_log.setText("\n".join(lines))

    def stop_all(self):
        for cart in self.carts:
            if cart.active:
                cart.running = False
        self.update_display()

    def start_all(self):
        for cart in self.carts:
            if cart.active:
                cart.running = True
        self.update_display()

    def stop_one(self):
        cart = self.get_selected_cart()
        if cart and cart.active:
            cart.running = False
        self.update_display()

    def start_one(self):
        cart = self.get_selected_cart()
        if cart and cart.active:
            cart.running = True
        self.update_display()

    def remove_one(self):
        cart = self.get_selected_cart()
        if cart:
            cart.active = False
            cart.running = False
        self.update_display()

    def restore_one(self):
        cart = self.get_selected_cart()
        if cart and not cart.active:
            cart.active = True
            cart.running = False
            cart.scene = self.scene_selector.currentIndex() + 1
            cart.phase = self.phase_selector.currentIndex()
            cart.history.append("[Manual] Restored to system")
        self.update_display()

    def assign_scene(self):
        cart = self.get_selected_cart()
        if cart and cart.active:
            new_scene = self.scene_selector.currentIndex() + 1
            new_phase = self.phase_selector.currentIndex()
            cart.scene = new_scene
            cart.phase = new_phase
            cart.log_movement()
        self.update_display()

    def get_selected_cart(self):
        index = self.cart_selector.currentIndex()
        if index >= 0 and index < len(self.carts):
            return self.carts[index]
        return None

    def toggle_blink(self):
        self.blink_flag = not self.blink_flag
        self.update_display()

    def advance_carts(self):
        self.blink_flag = not self.blink_flag
        for cart in self.carts:
            if cart.active and cart.running:
                if cart.phase < 2:
                    cart.phase += 1
                else:
                    cart.scene = 1 if cart.scene == 7 else cart.scene + 1
                    cart.phase = 0
                cart.log_movement()
        self.update_display()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RideControlSystem()
    window.show()
    sys.exit(app.exec_())
