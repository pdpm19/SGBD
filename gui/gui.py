# Main window da app
import sys
import os
import pyodbc
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from connectDlg import Connect

# Aplicação principal-
class GUI(QMainWindow):
    def __init__(self, windowTitle, uiPath):
        super(GUI, self).__init__()
        iconPath = os.path.join(uiPath, 'images', 'logo.jpg')
        self.setWindowIcon(QIcon(iconPath))
        self.setGeometry(400, 200, 600, 400)
        self.setWindowTitle(windowTitle)
        
        # Vai conter 4 faces principais
        #   1. Página principal
        #   2. Editar
        #   3. Browser
        #   4. Log tempo
        #   5. Log
        self.stacked = QStackedWidget()
        
        # Scrollable
        self.scroll = QScrollArea()
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.stacked) 

        # Página principal
        self.homepageWidgets = QWidget()
        self.homepageLayout = QVBoxLayout()
        self.HomepageUI()
        
        # Editar
        self.editWidgets = QWidget()
        self.editLayout = QVBoxLayout()
        self.EditUI()
        
        # Browser
        self.browserWidgets = QWidget()
        self.browserLayout = QVBoxLayout()
        self.BrowserUI()
        
        # Log tempo
        self.timeLogWidgets = QWidget()
        self.timeLogLayout = QVBoxLayout()
        self.TimeLogUI()
        
        # Log
        self.logWidgets = QWidget()
        self.logLayout = QVBoxLayout()
        self.LogUI()
        
        self.stacked.addWidget(self.homepageWidgets)
        self.stacked.addWidget(self.editWidgets)
        self.stacked.addWidget(self.browserWidgets)
        self.stacked.addWidget(self.timeLogWidgets)
        self.stacked.addWidget(self.logWidgets)
        self.setCentralWidget(self.scroll)

    # Vai mostrar as aplicações & O nivel de isolamento pretendido
    def HomepageUI(self):
        appsLayout = QGridLayout()
        appsWidget = QWidget()
        
        app1Button = QPushButton('App1 - Editar')
        app2Button = QPushButton('App2 - Browser')
        app3Button = QPushButton('App3 - Log tempo')
        app4Button = QPushButton('App4 - Log')

        appsLayout.addWidget(app1Button, 0,0)
        appsLayout.addWidget(app2Button, 0,1)
        appsLayout.addWidget(app3Button, 1,0)
        appsLayout.addWidget(app4Button, 1,1)

        appsWidget.setLayout(appsLayout)
        
        isolationLayout = QFormLayout()
        isolationWidget = QWidget()
        
        self.isolationComboBox = QComboBox()
        self.isolationComboBox.addItems(['Read Uncommited', 'Read Committed', 'Repeatable Read', 'Serializable'])
        
        isolationLayout.addRow(QLabel('Nível de isolamento:'), self.isolationComboBox)
        isolationWidget.setLayout(isolationLayout)
        
        self.homepageLayout.addWidget(appsWidget)
        self.homepageLayout.addWidget(isolationWidget)
        self.homepageWidgets.setLayout(self.homepageLayout)
    
    # Vai permitir ao utilizador Editar as encomendas
    def EditUI(self):
        print('2')
    
    def BrowserUI(self):
        print('3')
    
    def TimeLogUI(self):
        print('4')
    
    def LogUI(self):
        print('5')

def DisplayGUI(args):
    uiPath = args
    app = QApplication([])
    
    connect = Connect(400, 200, 'Conectar', uiPath) 
    if connect.exec_():
        ret = connect.Accept()
        cursor = ret[1]
        dbName = ret[0]
        
        '''
        # Debug da passagem de argumentos
        cursor.execute('SELECT * FROM ' + dbName +'.dbo.EncLinha')

        for row in cursor:
            print(row)
        '''
        window = GUI('Aplicação', uiPath)
        window.show()
    sys.exit(app.exec_())
    