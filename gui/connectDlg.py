# Connect da aplicação || Login
import sys
import os
import pyodbc
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# Conectar à BD
class Connect(QDialog):
    def __init__(self, width, heigth, windowTitle, uiPath):
        super(Connect, self).__init__()
        iconPath = os.path.join(uiPath, 'images', 'logo.jpg')
        self.setWindowIcon(QIcon(iconPath))  # Insere o icon
        self.setGeometry(400, 200, width, heigth)
        self.setWindowTitle(windowTitle)
        
        self.mainLayout = QVBoxLayout()
        
        # Layout em questionário
        self.formWidget = QWidget()
        self.formLayout = QFormLayout()
        self.hostNameField = QLineEdit()
        self.dbNameField = QLineEdit()
        self.usernameField = QLineEdit()
        self.userPasswordField = QLineEdit()
        self.userPasswordField.setEchoMode(QLineEdit.Password)  # mostra ** ou invés de caracteres
       
        self.formLayout.addRow(QLabel('Host Name:'), self.hostNameField)
        self.formLayout.addRow(QLabel('Database Name:'), self.dbNameField)
        self.formLayout.addRow(QLabel('Username:'), self.usernameField)
        self.formLayout.addRow(QLabel('Password:'), self.userPasswordField)
        self.formWidget.setLayout(self.formLayout)
        
        # Botões de OK/Cancel
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.userPasswordField.editingFinished.connect(self.Accept)
        self.buttonBox.rejected.connect(self.Back)
        
        
        self.mainLayout.addWidget(self.formWidget)
        self.mainLayout.addWidget(self.buttonBox)

        # Atribuíção do layout principal
        self.setLayout(self.mainLayout)

    def Back(self):
        sys.exit()

    # Chamada à função que liga à BD
    def Accept(self):
        # Conectar à BD
        self.buttonBox.accepted.connect(self.accept)

        '''
        # Debug à passagem dos dados 
        print("""====================== BD ======================  
    IP      : %s
    Hostname: %s
    Username: %s
    Password: %s
    ====================== BD ======================""" %(self.hostNameField.text(), self.dbNameField.text(), self.usernameField.text(), self.userPasswordField.text()))
        '''   
        
        conn = pyodbc.connect('DRIVER={SQL Server};SERVER='+self.hostNameField.text()+';DATABASE='+self.dbNameField.text()+';UID='+self.usernameField.text()+';PWD='+self.userPasswordField.text(), autocommit=False)
        ret = [self.dbNameField.text(), conn]
        return ret
        
