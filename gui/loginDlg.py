# Connect da aplicação || Login
import sys
import os
import pyodbc
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# Conectar à BD
class LoginDlg(QDialog):
    def __init__(self, width, heigth, windowTitle, uiPath):
        super(LoginDlg, self).__init__()
        iconPath = os.path.join(uiPath, 'images', 'logo.jpg')
        self.setWindowIcon(QIcon(iconPath))  # Insere o icon
        self.setGeometry(400, 200, width, heigth)
        self.setWindowTitle(windowTitle)
        
        self.mainLayout = QVBoxLayout()
        
        # Layou em questionário
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
        self.buttonBox.accepted.connect(self.Accept)
        self.buttonBox.rejected.connect(self.Back)
        
        
        self.mainLayout.addWidget(self.formWidget)
        self.mainLayout.addWidget(self.buttonBox)

        # Atribuíção do layout principal
        self.setLayout(self.mainLayout)
        
    # Chamada à função que liga à BD
    def Accept(self):
        DBFunctions(self.hostNameField.text(), self.dbNameField.text(), self.usernameField.text(), self.userPasswordField.text())

    def Back(self):
        sys.exit()

# Função de ligação e queries à BD
def DBFunctions(serverIP: str, dbName: str, username: str, password: str):
    
        # Só para dar debug à passagem dos dados

    print("""====================== BD ======================  
    IP      : %s
    Hostname: %s
    Username: %s
    Password: %s
    ====================== BD ======================""" %(serverIP, dbName, username, password))
        # Conectar à BD
    cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER='+serverIP+';DATABASE='+dbName+';UID='+username+';PWD='+ password)
    cursor = cnxn.cursor()

        # Para testar a conexão
    cursor.execute('SELECT * FROM ' + dbName + '.dbo.EncLinha;')

    for row in cursor:
        print(row)
        # Verificar se o user tem acesso
        # Deixar fazer as queries....
        # ....

def DisplayLogin(args):
    uiPath = args
    app = QApplication([])
    window = LoginDlg(400,200, 'Login', uiPath)
    window.show()
    app.exec_()
