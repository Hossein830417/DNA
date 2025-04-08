import sys
from qtpy.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QLabel, QTextEdit, QPushButton, QFileDialog, QMessageBox,
                           QGraphicsScene, QGraphicsView, QGraphicsRectItem, QGraphicsTextItem)
from qtpy.QtCore import Qt, QRectF
from qtpy.QtGui import QColor, QBrush, QPen, QFont
from Bio.Seq import Seq
from Bio.SeqUtils import gc_fraction

class DNAGraphicsScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.nucleotides = []
        self.current_pos = 0
        self.setBackgroundBrush(QBrush(Qt.white))
        
    def add_nucleotide(self, nucleotide):
        """افزودن یک نوکلئوتید به صحنه گرافیکی"""
        x = self.current_pos * 40
        colors = {'A': QColor('#FF6B6B'), 'T': QColor('#4ECDC4'), 
                 'C': QColor('#45B7D1'), 'G': QColor('#FFD166')}
        
        # رسم مستطیل رنگی
        rect = QGraphicsRectItem(x, 0, 35, 35)
        rect.setBrush(QBrush(colors.get(nucleotide, Qt.white)))
        rect.setPen(QPen(Qt.black))
        self.addItem(rect)
        
        # اضافه کردن متن نوکلئوتید
        text = QGraphicsTextItem(nucleotide)
        text.setPos(x + 12, 5)
        font = QFont()
        font.setBold(True)
        font.setPointSize(16)
        text.setFont(font)
        self.addItem(text)
        
        self.nucleotides.append(nucleotide)
        self.current_pos += 1
        
    def get_sequence(self):
        """دریافت توالی DNA از صحنه گرافیکی"""
        return ''.join(self.nucleotides)
    
    def clear_sequence(self):
        """پاک کردن تمام توالی"""
        self.clear()
        self.nucleotides = []
        self.current_pos = 0

class DNAAnalyzer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("تجزیه و تحلیل DNA با رابط گرافیکی")
        self.resize(1000, 700)
        self.init_ui()
    
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # بخش گرافیکی
        self.scene = DNAGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setFixedHeight(100)
        main_layout.addWidget(self.view)
        
        # دکمه‌های نوکلئوتیدها
        nucleotide_layout = QHBoxLayout()
        for nt in ['A', 'T', 'C', 'G']:
            btn = QPushButton(nt)
            btn.setFixedSize(50, 50)
            btn.setStyleSheet(f"font-size: 16px; background-color: {'#FF6B6B' if nt == 'A' else '#4ECDC4' if nt == 'T' else '#45B7D1' if nt == 'C' else '#FFD166'};")
            btn.clicked.connect(lambda _, x=nt: self.scene.add_nucleotide(x))
            nucleotide_layout.addWidget(btn)
        
        # دکمه پاک کردن
        clear_btn = QPushButton("پاک کردن توالی")
        clear_btn.clicked.connect(self.scene.clear_sequence)
        nucleotide_layout.addWidget(clear_btn)
        main_layout.addLayout(nucleotide_layout)
        
        # بخش ورودی دستی
        self.dna_input = QTextEdit()
        self.dna_input.setPlaceholderText("یا توالی DNA را اینجا وارد کنید...")
        main_layout.addWidget(self.dna_input)
        
        # دکمه‌های عملیاتی
        btn_layout = QHBoxLayout()
        self.btn_load = QPushButton("بارگذاری از فایل")
        self.btn_load.clicked.connect(self.load_from_file)
        btn_layout.addWidget(self.btn_load)
        
        self.btn_analyze = QPushButton("تجزیه و تحلیل")
        self.btn_analyze.clicked.connect(self.analyze_dna)
        btn_layout.addWidget(self.btn_analyze)
        
        self.btn_clear = QPushButton("پاک کردن همه")
        self.btn_clear.clicked.connect(self.clear_all)
        btn_layout.addWidget(self.btn_clear)
        main_layout.addLayout(btn_layout)
        
        # بخش نتایج
        self.result_label = QLabel("نتایج تجزیه و تحلیل اینجا نمایش داده می‌شود")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setWordWrap(True)
        self.result_label.setStyleSheet("font-size: 14px; padding: 10px;")
        main_layout.addWidget(self.result_label)
    
    def analyze_dna(self):
        # دریافت توالی از هر دو منبع
        graphic_seq = self.scene.get_sequence()
        text_seq = self.dna_input.toPlainText().strip().upper()
        
        # ترکیب توالی‌ها (اولویت با توالی گرافیکی)
        dna_sequence = graphic_seq if graphic_seq else text_seq
        
        if not dna_sequence:
            QMessageBox.warning(self, "خطا", "لطفاً توالی DNA را وارد کنید")
            return
        
        try:
            valid_nucleotides = {'A', 'T', 'C', 'G', ' '}
            if not all(c in valid_nucleotides for c in dna_sequence if c != ' '):
                raise ValueError("توالی DNA نامعتبر است - فقط حروف A, T, C, G مجاز هستند")
            
            dna_sequence = dna_sequence.replace(' ', '')
            seq = Seq(dna_sequence)
            gc = gc_fraction(seq) * 100
            complement = str(seq.complement())
            reverse_complement = str(seq.reverse_complement())
            length = len(seq)
            
            result_text = (
                f"نتایج تجزیه و تحلیل DNA:\n\n"
                f"طول توالی: {length} نوکلئوتید\n"
                f"محتوی GC: {gc:.2f}%\n\n"
                f"توالی مکمل:\n{complement}\n\n"
                f"توالی مکمل معکوس:\n{reverse_complement}"
            )
            
            self.result_label.setText(result_text)
            
        except Exception as e:
            QMessageBox.critical(self, "خطای تجزیه و تحلیل", f"خطا: {str(e)}")
    
    def load_from_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self, "بارگذاری فایل DNA", "", 
            "Text Files (*.txt);;FASTA Files (*.fasta);;All Files (*)", 
            options=options)
        
        if file_name:
            try:
                with open(file_name, 'r') as file:
                    content = file.read()
                    self.dna_input.setPlainText(content)
            except Exception as e:
                QMessageBox.warning(self, "خطا", f"خطا در بارگذاری فایل: {str(e)}")
    
    def clear_all(self):
        self.scene.clear_sequence()
        self.dna_input.clear()
        self.result_label.setText("نتایج تجزیه و تحلیل اینجا نمایش داده می‌شود")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = app.font()
    font.setPointSize(12)
    app.setFont(font)
    window = DNAAnalyzer()
    window.show()
    sys.exit(app.exec())