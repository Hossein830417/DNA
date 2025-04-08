from qtpy.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                          QPushButton, QTextEdit, QTableWidget, 
                          QTableWidgetItem, QHeaderView, QMessageBox)
from qtpy.QtCore import Qt
from qtpy.QtGui import QColor
from analysis.sequence_db import SEQUENCE_DATABASE

class DetectionPanel(QWidget):
    def __init__(self, detector):
        super().__init__()
        self.detector = detector
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        
        # دکمه‌های تحلیل
        self.analyze_btn = QPushButton("Analyze DNA")
        self.export_btn = QPushButton("Export Results")
        self.analyze_btn.clicked.connect(self.analyze_sequence)
        
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.analyze_btn)
        btn_layout.addWidget(self.export_btn)
        
        # نمایش نتایج
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(3)
        self.results_table.setHorizontalHeaderLabels(["Feature", "Value", "Details"])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        
        self.layout.addLayout(btn_layout)
        self.layout.addWidget(self.results_table)
        self.layout.addWidget(self.details_text)
        self.setLayout(self.layout)

    def analyze_sequence(self):
        """آنالیز توالی DNA با اعتبارسنجی پیشرفته"""
        try:
            # دریافت توالی از پنجره اصلی
            main_window = self.window()  # روش مطمئن‌تر برای دسترسی به پنجره اصلی
            
            if not hasattr(main_window, 'get_current_sequence'):
                QMessageBox.critical(self, "Error", "Cannot access DNA sequence!")
                return
                
            sequence = main_window.get_current_sequence()
            
            # اعتبارسنجی پیشرفته
            if not sequence:
                QMessageBox.warning(self, "Error", "DNA sequence is empty!\nPlease enter a valid sequence.")
                return
                
            if not isinstance(sequence, str):
                QMessageBox.warning(self, "Error", "Invalid sequence type!\nMust be a string.")
                return
                
            sequence = sequence.upper().strip()
            valid_chars = {'A', 'T', 'C', 'G'}
            
            if not all(c in valid_chars for c in sequence):
                invalid_chars = set(sequence) - valid_chars
                QMessageBox.warning(
                    self, 
                    "Invalid Characters",
                    f"Sequence contains invalid DNA characters: {', '.join(invalid_chars)}\n"
                    "Only A, T, C, G are allowed."
                )
                return
                
            if len(sequence) < 10:
                QMessageBox.warning(self, "Error", "Sequence is too short!\nMinimum length is 10 bases.")
                return
                
            # اجرای تحلیل
            results = self.detector.detect_features(sequence)
            self.display_results(results)
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Analysis Failed", 
                f"An unexpected error occurred:\n{str(e)}"
            )

    def display_results(self, results):
        """نمایش نتایج با مدیریت خطا"""
        self.results_table.setRowCount(0)
        
        # بررسی وجود خطا
        if 'error' in results:
            self.add_table_row(
                "Error", 
                results['error'], 
                "Analysis failed",
                QColor(255, 200, 200)  # رنگ قرمز روشن
            )
            return
            
        # نمایش اطلاعات توالی (حتی اگر ناشناخته باشد)
        seq_info = results.get('sequence_info', {})
        self.add_table_row(
            "Sequence Identification",
            seq_info.get('name', 'Unknown'),
            f"Type: {seq_info.get('type', 'custom')}\n"
            f"{seq_info.get('description', 'No description available')}",
        )
        
        # نمایش سایر نتایج
        self.add_table_row("Length", f"{results.get('length', 0)} bp", "")

        # GC Content
        self.add_table_row("GC Content", f"{results['gc_content']}%", "Percentage of G and C nucleotides")
        
        # Patterns
        for pattern, matches in results['patterns'].items():
            self.add_table_row(
                f"{pattern.capitalize()} Sites", 
                str(len(matches)), 
                f"Positions: {', '.join(str(m['start']) for m in matches)}",
            )
        
        # ORFs
        orfs = results['orf']
        self.add_table_row(
            "ORFs", 
            str(len(orfs)), 
            f"Longest: {max((orf['length'] for orf in orfs), default=0)} bp",
        )
        
        # Repeats
        repeats = results['repeats']
        self.add_table_row(
            "Repeats", 
            str(len(repeats)), 
            f"Most frequent: {max(repeats.items(), key=lambda x: len(x[1]), default=('', []))[0]}",
        )

    def add_table_row(self, feature, value, details, bg_color=None):
        """اضافه کردن سطر جدید به جدول نتایج"""
        row = self.results_table.rowCount()
        self.results_table.insertRow(row)
        
        items = [
            QTableWidgetItem(feature),
            QTableWidgetItem(value),
            QTableWidgetItem(details)
        ]
        
        for i, item in enumerate(items):
            item.setFlags(item.flags() ^ Qt.ItemIsEditable)
            if bg_color:
                item.setBackground(bg_color)
            self.results_table.setItem(row, i, item)