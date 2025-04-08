import sys
from qtpy.QtWidgets import QApplication
from gui.main_window import MainWindow
from gui.main_window import MainWindow
from qtpy.QtWidgets import QTabWidget
from gui.detection_panel import DetectionPanel
from analysis.dna_detector import DNADetector

class MainWindow(MainWindow):
    def __init__(self):
        super().__init__()
        # ... کدهای قبلی ...
        self.detector = DNADetector()
        self.init_detection_tab()  # اضافه کردن تب تشخیص
        
    def init_detection_tab(self):
        """اضافه کردن تب تشخیص به رابط کاربری"""
        tabs = QTabWidget()
        
        # تب اصلی
        main_tab = QTabWidget()
        main_tab.setLayout(self.main_layout)  # استفاده از لایه‌بندی قبلی
        
        # تب تشخیص
        detection_tab = DetectionPanel(self.detector)
        
        tabs.addTab(main_tab, "DNA Editor")
        tabs.addTab(detection_tab, "Analysis Tools")
        
        self.setCentralWidget(tabs)  # جایگزینی ویجت مرکزی با تب‌ها
        
    # اضافه کردن این متد به کلاس
    def get_current_sequence(self):
        """دریافت توالی جاری برای آنالیز"""
        return self.sequence
def main():
    app = QApplication(sys.argv)
    
    # Set application style and font
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()