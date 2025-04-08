import sys
import math
from qtpy.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QLabel, QPushButton, QGraphicsView, QGraphicsScene, 
                           QGraphicsTextItem, QGraphicsEllipseItem, QMenuBar, QMenu,
                           QFileDialog, QMessageBox)
from qtpy.QtCore import Qt, QPointF, QRectF
from qtpy.QtGui import (QColor, QPen, QFont, QBrush, QPainterPath, QTransform, QPainter, QAction, QKeySequence)
from Bio.Seq import Seq

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DNA Analyzer")
        self.setGeometry(100, 100, 1000, 700)
        
        # متغیرهای DNA
        self.sequence = ""  # فقط نوکلئوتیدهای واقعی
        self.complement_sequence = ""
        self.scene_width = 1000
        self.visual_positions = []  # موقعیت‌های بصری (شامل نقاط تلاقی)
        
        # تنظیم رابط کاربری
        self.init_ui()
        
    def init_ui(self):
        # ایجاد منوی اصلی
        self.create_main_menu()
        
        # ویجت مرکزی
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(15)
        central_widget.setLayout(self.main_layout)
        
        # بخش نمایش توالی DNA
        self.dna_label = QLabel("DNA Sequence: ")
        self.dna_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.dna_label)
        
        # بخش نمایش مکمل توالی
        self.complement_label = QLabel("Complement: Ready for simulation")
        self.complement_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.complement_label)
        
        # دکمه‌های نوکلئوتیدها
        self.create_nucleotide_buttons()
        
        # نمایش گرافیکی DNA
        self.init_dna_graphics()
        
        # دکمه‌های عمل
        self.create_action_buttons()
        
    def create_main_menu(self):
        menubar = self.menuBar()
        
        # منوی File
        file_menu = menubar.addMenu("File")
        load_action = QAction("Load", self)
        load_action.triggered.connect(self.load_sequence)
        file_menu.addAction(load_action)
        
        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_sequence)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # منوی View
        view_menu = menubar.addMenu("View")
        theme_action = QAction("Toggle Theme", self)
        theme_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(theme_action)
        
    def create_nucleotide_buttons(self):
        nt_layout = QHBoxLayout()
        nt_layout.setAlignment(Qt.AlignCenter)
        
        for nt, color in [('A', '#e74c3c'), ('T', '#3498db'), ('C', '#2ecc71'), ('G', '#f1c40f')]:
            btn = QPushButton(nt)
            btn.setFixedSize(50, 50)
            btn.setStyleSheet(f"""
                QPushButton {{
                    font-size: 20px;
                    font-weight: bold;
                    background-color: {color};
                    color: white;
                    border-radius: 25px;
                    margin: 5px;
                }}
                QPushButton:hover {{
                    background-color: {QColor(color).darker(120).name()};
                }}
            """)
            btn.clicked.connect(lambda _, x=nt: self.add_nucleotide(x))
            nt_layout.addWidget(btn)
        
        delete_btn = QPushButton("⌫")
        delete_btn.setFixedSize(50, 50)
        delete_btn.setStyleSheet("""
            QPushButton {
                font-size: 20px;
                font-weight: bold;
                background-color: #95a5a6;
                color: white;
                border-radius: 25px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        delete_btn.clicked.connect(self.remove_last_nucleotide)
        nt_layout.addWidget(delete_btn)
        
        self.main_layout.addLayout(nt_layout)
        
    def init_dna_graphics(self):
        self.dna_scene = QGraphicsScene()
        self.dna_view = CustomGraphicsView(self.dna_scene)
        self.dna_view.setFixedHeight(350)
        self.dna_view.setRenderHint(QPainter.Antialiasing)
        self.dna_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.main_layout.addWidget(self.dna_view)
        self.dna_scene.setSceneRect(0, 0, self.scene_width, 350)
        
    def draw_dna_helix(self):
        self.dna_scene.clear()
        self.visual_positions = []
        
        if not self.sequence:
            return
            
        # رنگ‌های نوکلئوتیدها
        nt_colors = {
            'A': QColor('#e74c3c'),
            'T': QColor('#3498db'),
            'C': QColor('#2ecc71'),
            'G': QColor('#f1c40f')
        }
        
        # پارامترهای مارپیچ DNA
        center_y = 175
        radius = 80
        visual_index = 0
        sequence_index = 0
        
        # الگوی نمایش
        pattern = [False, True, True, True, True, False] + [True, True, True, True, False] * 100
        
        while sequence_index < len(self.sequence):
            x = 100 + visual_index * 50
            angle = visual_index * (2 * math.pi / 10)
            y1 = center_y - radius * math.sin(angle)
            y2 = center_y + radius * math.sin(angle)
            
            self.visual_positions.append((x, y1, y2))
            
            if pattern[visual_index % len(pattern)] and sequence_index < len(self.sequence):
                nt = self.sequence[sequence_index]
                
                # نمایش نوکلئوتیدها
                ellipse = QGraphicsEllipseItem(x - 15, y1 - 15, 30, 30)
                ellipse.setBrush(QBrush(nt_colors.get(nt, Qt.white)))
                ellipse.setPen(QPen(Qt.black, 1))
                ellipse.setZValue(2)
                self.dna_scene.addItem(ellipse)
                
                text = QGraphicsTextItem(nt)
                text.setPos(x - 8, y1 - 10)
                text.setFont(QFont("Arial", 12, QFont.Bold))
                text.setDefaultTextColor(Qt.white)
                text.setZValue(3)
                self.dna_scene.addItem(text)
                
                if self.complement_sequence and sequence_index < len(self.complement_sequence):
                    comp_nt = self.complement_sequence[sequence_index]
                    comp_ellipse = QGraphicsEllipseItem(x - 15, y2 - 15, 30, 30)
                    comp_ellipse.setBrush(QBrush(nt_colors.get(comp_nt, Qt.white)))
                    comp_ellipse.setPen(QPen(Qt.black, 1))
                    comp_ellipse.setZValue(2)
                    self.dna_scene.addItem(comp_ellipse)
                    
                    comp_text = QGraphicsTextItem(comp_nt)
                    comp_text.setPos(x - 8, y2 - 10)
                    comp_text.setFont(QFont("Arial", 12, QFont.Bold))
                    comp_text.setDefaultTextColor(Qt.white)
                    comp_text.setZValue(3)
                    self.dna_scene.addItem(comp_text)
                
                sequence_index += 1
            
            if visual_index > 0:
                prev_x, prev_y1, prev_y2 = self.visual_positions[visual_index - 1]
                
                path1 = QPainterPath()
                path1.moveTo(prev_x, prev_y1)
                path1.lineTo(x, y1)
                path_item1 = self.dna_scene.addPath(path1, QPen(QColor("#34495e"), 1.5))
                path_item1.setZValue(1)
                
                path2 = QPainterPath()
                path2.moveTo(prev_x, prev_y2)
                path2.lineTo(x, y2)
                path_item2 = self.dna_scene.addPath(path2, QPen(QColor("#34495e"), 1.5))
                path_item2.setZValue(1)
                
                connector = QPainterPath()
                connector.moveTo(x, y1)
                connector.lineTo(x, y2)
                connector_item = self.dna_scene.addPath(connector, QPen(QColor("#7f8c8d"), 1, Qt.DotLine))
                connector_item.setZValue(0)
            
            visual_index += 1
        
        new_width = max(1000, visual_index * 50 + 100)
        if new_width > self.scene_width:
            self.scene_width = new_width
            self.dna_scene.setSceneRect(0, 0, self.scene_width, 350)
        
        self.scroll_to_end()
        
    def scroll_to_end(self):
        if self.visual_positions:
            last_x = self.visual_positions[-1][0]
            scroll_pos = last_x - self.dna_view.width() + 100
            self.dna_view.horizontalScrollBar().setValue(scroll_pos)
        
    def keyPressEvent(self, event):
        key = event.text().upper()
        if key in ['A', 'T', 'C', 'G']:
            self.add_nucleotide(key)
        elif event.key() == Qt.Key_Backspace:
            self.remove_last_nucleotide()
        elif event.key() in [Qt.Key_Return, Qt.Key_Enter]:
            self.calculate_complement()
        else:
            super().keyPressEvent(event)
        
    def create_action_buttons(self):
        action_layout = QHBoxLayout()
        action_layout.setAlignment(Qt.AlignCenter)
        
        self.analyze_btn = QPushButton("Calculate Complement (Enter)")
        self.analyze_btn.setFixedWidth(220)
        self.analyze_btn.clicked.connect(self.calculate_complement)
        
        self.clear_btn = QPushButton("Clear All")
        self.clear_btn.setFixedWidth(120)
        self.clear_btn.clicked.connect(self.clear_all)
        
        action_layout.addWidget(self.analyze_btn)
        action_layout.addWidget(self.clear_btn)
        self.main_layout.addLayout(action_layout)
        
    def add_nucleotide(self, nucleotide):
        self.sequence += nucleotide
        self.dna_label.setText(f"DNA Sequence: {self.sequence}")
        self.draw_dna_helix()
        
    def remove_last_nucleotide(self):
        if self.sequence:
            self.sequence = self.sequence[:-1]
            self.dna_label.setText(f"DNA Sequence: {self.sequence if self.sequence else '---'}")
            self.complement_sequence = ""
            self.complement_label.setText("Complement: Ready for simulation")
            self.draw_dna_helix()
        
    def calculate_complement(self):
        if not self.sequence:
            return
            
        try:
            seq = Seq(self.sequence)
            self.complement_sequence = str(seq.complement())
            self.complement_label.setText(f"Complement: {self.complement_sequence}")
            self.draw_dna_helix()
        except Exception as e:
            print(f"Error: {str(e)}")
        
    def clear_all(self):
        self.sequence = ""
        self.complement_sequence = ""
        self.visual_positions = []
        self.dna_label.setText("DNA Sequence: ")
        self.complement_label.setText("Complement: Ready for simulation")
        self.draw_dna_helix()
        
    def load_sequence(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Load DNA Sequence", "", 
            "Text Files (*.txt);;All Files (*)", 
            options=options)
        
        if file_name:
            try:
                with open(file_name, 'r', encoding='utf-8') as file:
                    content = file.read().strip().upper()
                    valid_chars = {'A', 'T', 'C', 'G'}
                    self.sequence = ''.join([c for c in content if c in valid_chars])
                    self.dna_label.setText(f"DNA Sequence: {self.sequence}")
                    self.complement_sequence = ""
                    self.complement_label.setText("Complement: Ready for simulation")
                    self.draw_dna_helix()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to load file: {str(e)}")

    def save_sequence(self):
        if not self.sequence:
            QMessageBox.warning(self, "Error", "No DNA sequence to save")
            return
            
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save DNA Sequence", "", 
            "Text Files (*.txt);;All Files (*)", 
            options=options)
        
        if file_name:
            try:
                with open(file_name, 'w', encoding='utf-8') as file:
                    file.write(f"DNA Sequence: {self.sequence}\n")
                    if self.complement_sequence:
                        file.write(f"Complement Sequence: {self.complement_sequence}\n")
                QMessageBox.information(self, "Success", "Sequence saved successfully")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to save file: {str(e)}")
        
    def toggle_theme(self):
        pass

class CustomGraphicsView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setInteractive(True)
        
    def wheelEvent(self, event):
        scroll_bar = self.horizontalScrollBar()
        scroll_bar.setValue(scroll_bar.value() - event.angleDelta().y())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    font = QFont()
    font.setFamily("Arial")
    font.setPointSize(12)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())