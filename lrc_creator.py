from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QSettings, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QBrush, QIcon
from tkinter import filedialog, messagebox
import available_list
import lrc_creator_model

import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

form = resource_path("lrc_creator.ui")
form_class = uic.loadUiType(form)[0]

# form_class = uic.loadUiType('lrc_creator.ui')[0]
settings = QSettings('MyApp', 'LRC Creator')

class MyApp(QMainWindow, form_class):
  
    def __init__(self):
        super().__init__()
        lastSearchLineEditText = settings.value("SearchLineEditText")
        
        self.setupUi(self)
        if lastSearchLineEditText is not None:
            self.searchLineEdit.setText(lastSearchLineEditText)
        
        self.setWindowIcon(QIcon('../images/icon_image(2)_48x40px.png'))
        
        self.thread = progressThread()
        self.thread.progress.connect(self.progressBar.setValue)
        self.directoryPushButton.clicked.connect(self.searchFolderPath)
        self.searchLineEdit.returnPressed.connect(self.viewTableData)
        self.searchPushButton.clicked.connect(self.viewTableData)
        self.lrcCreatorPushButton.clicked.connect(self.lrcCreatorPushEnter)
        
        self.tableWidget.setColumnWidth(0, 100)
        self.tableWidget.setColumnWidth(1, 800)
        self.tableWidget.setColumnWidth(2, 100)
        self.tableWidget.setColumnWidth(3, 300)
        self.tableWidget.setColumnWidth(4, 300)
        self.tableWidget.setColumnWidth(5, 100)
        
        settings.setValue("setting_file_types", "flac,mp3,m4a,wav")
        
        self.statusBar().showMessage('준비')
        self.setWindowTitle('LRC 생성기 68')
        self.setGeometry(10,10, 1280, 720)
        window_frame = self.frameGeometry()
        window_frame.moveCenter(QDesktopWidget().availableGeometry().center())
        self.move(window_frame.topLeft())

        self.available_files = None
    
    def tableInit(self):
        self.tableWidget.setRowCount(0)
        for row in range(0, self.tableWidget.rowCount()):
            self.tableWidget.removeRow(row)
       
    def searchFolderPath(self):
        self.tableInit()
        directoryPath = filedialog.askdirectory()
        if directoryPath is None or directoryPath == "": return
        self.searchLineEdit.setText(directoryPath)
        
    
    def viewTableData(self):
        if self.searchLineEdit.text() is None or self.searchLineEdit.text() == '': return
        self.tableInit()
        
        self.statusBar().showMessage('목록 작성 중')
        
        settings.setValue("SearchLineEditText", self.searchLineEdit.text())
        self.available_files = available_list.set_list(self.searchLineEdit.text(), settings.value("setting_file_types"), 2)
        
        progBarMaximum = len(self.available_files) - 1
        if len(self.available_files) == 0 or len(self.available_files) is None: progBarMaximum = 0
        self.progressBar.setMaximum(progBarMaximum)
        
        self.thread.start()
        
        self.makeRowToTable(self.available_files,)
        self.statusBar().showMessage('준비')
        
    def makeRowToTable(self, available_files):
        for row_no in range(0, len(available_files)):
            #self.thread.setCurrentValue(row_no,)
            self.progressBar.setValue(row_no)
            self.tableWidget.insertRow(row_no)
            tags_row_data = []

            # col tags            
            tags_row_data.append(available_files[row_no]['album'])
            tags_row_data.append(available_files[row_no]['title'])
            tags_row_data.append(available_files[row_no]['artist'])

            # col0
            value_col0 = ''
            if available_files[row_no]['lrc_status'] == 1: value_col0 = '생성됨'
            item_data = QTableWidgetItem(value_col0)
            self.tableWidget.setItem(row_no, 0, item_data)
            # col1
            item_data = QTableWidgetItem(available_files[row_no]['file_name'])
            self.tableWidget.setItem(row_no, 1, item_data)
            # col2
            item_data = QTableWidgetItem(available_files[row_no]['file_type'])
            self.tableWidget.setItem(row_no, 2, item_data)
            #col3
            item_data = QTableWidgetItem(tags_row_data[0])
            self.tableWidget.setItem(row_no, 3, item_data)
            # col4
            item_data = QTableWidgetItem(tags_row_data[1])
            self.tableWidget.setItem(row_no, 4, item_data)
            # col5
            item_data = QTableWidgetItem(tags_row_data[2])
            self.tableWidget.setItem(row_no, 5, item_data)
            # row color settings
            if (tags_row_data[0] is None
            or  tags_row_data[1] is None
            or  tags_row_data[2] is None):
                for col_no in range(0, 6):
                    row_item = self.tableWidget.item(row_no, col_no)
                    row_item.setForeground(QBrush(Qt.gray))
            elif available_files[row_no]['lrc_status'] == 1:
                for col_no in range(0, 6):
                    row_item = self.tableWidget.item(row_no, col_no)
                    row_item.setForeground(QBrush(Qt.blue))
            
        self.thread.stopThread()
                           
    def lrcCreatorPushEnter(self):
        if self.available_files is None: 
            messagebox.showinfo("알림", "해당하는 목록이 없습니다.")
            return        
    
        msgResponse = messagebox.askokcancel("생성/취소", "해당 목록의 LRC 가사 파일을 생성하겠습니까?")
        if msgResponse != 1: return
        
        self.statusBar().showMessage('LRC 파일 생성 중')
        
        progBarMaximum = len(self.available_files) - 1
        if len(self.available_files) == 0 or len(self.available_files) is None: progBarMaximum = 0
        self.progressBar.setMaximum(progBarMaximum)
        self.thread.start()
        lrc_creator_model.crawling_lrc(self.available_files, self.progressBar)
        self.thread.stopThread()
        messagebox.showinfo("알림", "작업을 완료했습니다.")
        self.viewTableData()
        self.statusBar().showMessage('준비')

class progressThread(QThread):
    progress = pyqtSignal(int)
    def __init__(self):
        super().__init__()
        self.value = 0
        self.statusFlag = True

    def run(self):
        while self.statusFlag:
            self.progress.emit(self.value)
        
    def stopThread(self):
        self.statusFlag = False
              
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    ex.show()
    sys.exit(app.exec_())
