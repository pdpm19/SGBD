# Main window da app
import sys
import os
import pyodbc
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from connectDlg import Connect

# Torna input em Table Mode View
class TableModel(QAbstractTableModel):
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]
    
    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0])


# Aplicação principal-
class GUI(QMainWindow):
    def __init__(self, windowTitle, uiPath, cursor, dbName):
        super(GUI, self).__init__()
        iconPath = os.path.join(uiPath, 'images', 'logo.jpg')
        self.setWindowIcon(QIcon(iconPath))
        self.setGeometry(400, 200, 600, 400)
        self.setWindowTitle(windowTitle)
        self.dbName = dbName
        self.cursor = cursor
        
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
        app1Button.pressed.connect(self.DisplayEdit)
        
        app2Button = QPushButton('App2 - Browser')
        app2Button.pressed.connect(lambda: self.stacked.setCurrentIndex(2))

        app3Button = QPushButton('App3 - Log tempo')
        app3Button.pressed.connect(lambda: self.stacked.setCurrentIndex(3))

        app4Button = QPushButton('App4 - Log')
        app4Button.pressed.connect(lambda: self.stacked.setCurrentIndex(4))

        appsLayout.addWidget(app1Button, 0,0)
        appsLayout.addWidget(app2Button, 0,1)
        appsLayout.addWidget(app3Button, 1,0)
        appsLayout.addWidget(app4Button, 1,1)

        appsWidget.setLayout(appsLayout)
        
        isolationLayout = QFormLayout()
        isolationWidget = QWidget()
        
        self.isolationComboBox = QComboBox()
        self.isolationComboBox.addItems(['Read Uncommitted', 'Read Committed', 'Repeatable Read', 'Serializable'])
        
        isolationLayout.addRow(QLabel('Nível de isolamento:'), self.isolationComboBox)
        isolationWidget.setLayout(isolationLayout)
        
        self.homepageLayout.addWidget(appsWidget)
        self.homepageLayout.addWidget(isolationWidget)
        self.homepageWidgets.setLayout(self.homepageLayout)
    
    # Vai permitir ao utilizador Editar as encomendas
    def EditUI(self):
        backButton = QPushButton('Voltar')
        acceptButton = QPushButton('Aceitar')
        
        buttonsLayout = QHBoxLayout()
        buttonsWidget = QWidget()

        buttonsLayout.addWidget(backButton)
        buttonsLayout.addWidget(acceptButton)
        buttonsWidget.setLayout(buttonsLayout)
        
        backButton.pressed.connect(self.CloseEdit)
        acceptButton.pressed.connect(self.EditFunction)
        
        formLayout = QFormLayout()
        formWidget = QWidget()

        self.encIDField = QComboBox()
        self.encIDs = []
        self.clientIDField = QLineEdit()
        self.clientIDs = []
        self.clientNameField = QLineEdit()
        self.clientName = []
        self.clientAddressField = QLineEdit()
        self.clientAddress = []
        
        formLayout.addRow(QLabel('ID da Encomenda:'), self.encIDField)
        formLayout.addRow(QLabel('ID do Cliente:'), self.clientIDField)
        formLayout.addRow(QLabel('Nome do Cliente:'), self.clientNameField)
        formLayout.addRow(QLabel('Morada do Cliente:'), self.clientAddressField) 
        formWidget.setLayout(formLayout)       
        
        self.editLayout.addWidget(formWidget)
        self.editLayout.addWidget(buttonsWidget)
        self.editWidgets.setLayout(self.editLayout)
    
    # Carrega a página de Editar & preenche os campos
    def DisplayEdit(self):
        self.stacked.setCurrentIndex(1)
        # Faz o pedido à BD 
        query = MakeTransaction(self.cursor, self.isolationComboBox.currentText(), 'SELECT', ['*'], self.dbName, 'Encomenda', [])
        
        for row in query:
            self.encIDs.append(str(row[0]))
            self.clientIDs.append(str(row[1]))
            self.clientName.append(str(row[2]))
            self.clientAddress.append(str(row[3]))
        

        self.encIDField.addItems(self.encIDs)
        self.clientNameField.setText(self.clientName[0])
        self.clientIDField.setText(self.clientIDs[0])
        self.clientAddressField.setText(self.clientAddress[0])
        
        self.encIDField.currentIndexChanged.connect(self.UpdateEdit)
    
    # Fecha a página de Editar
    def CloseEdit(self):
        # Vai limpar todos os campos
        self.encIDField.clear()
        self.clientIDField.clear()
        self.clientNameField.clear()
        self.clientAddressField.clear()

        # vai limpar todos os vetores auxiliares
        self.encIDs.clear()
        self.clientIDs.clear()
        self.clientName.clear()
        self.clientAddress.clear()

        self.stacked.setCurrentIndex(0)
    
    # Atualiza os campos consoante o ID da encomenda selecionado
    def UpdateEdit(self):
        currentID = self.encIDField.currentIndex()
        
        self.clientNameField.clear()
        self.clientNameField.setText(self.clientName[currentID])

        self.clientIDField.clear()
        self.clientIDField.setText(self.clientIDs[currentID])

        self.clientAddressField.clear()
        self.clientAddressField.setText(self.clientAddress[currentID])
    
    # Grava as alterações feitas
    def EditFunction(self):
        print('yo')
    
    def BrowserUI(self):
        backButton = QPushButton('Voltar')
        backButton.pressed.connect(lambda: self.stacked.setCurrentIndex(0))

        self.browserLayout.addWidget(backButton)
        self.browserWidgets.setLayout(self.browserLayout)

    def TimeLogUI(self):
        backButton = QPushButton('Voltar')
        backButton.pressed.connect(lambda: self.stacked.setCurrentIndex(0))
    
        self.timeLogLayout.addWidget(backButton)
        self.timeLogWidgets.setLayout(self.timeLogLayout)
    
    def LogUI(self):
        backButton = QPushButton('Voltar')
        backButton.pressed.connect(lambda: self.stacked.setCurrentIndex(0))

        self.logLayout.addWidget(backButton)
        self.logWidgets.setLayout(self.logLayout)

# As transações de leitura são feitas aqui
def MakeTransaction(cursor, isolationLevel: str, operation : str, returnRow: list, dbName: str, tableName: str, restrictor: list):
    sqlCommand = 'SET TRANSACTION ISOLATION LEVEL ' + isolationLevel.upper() + ';\n'
    sqlCommand = sqlCommand + 'BEGIN TRANSACTION;\n'
    
    # SELECT, UPDATE or DELETE
    if len(returnRow) == 1:
        sqlCommand = sqlCommand + operation.upper() + ' ' + returnRow[0] + ' FROM '
    else:
        sqlCommand = sqlCommand + operation.upper() + ' '
        for i in returnRow:
            sqlCommand = sqlCommand + i + ', '
        sqlCommand = sqlCommand[:len(sqlCommand-2)] + ' FROM '

    
    # Introduz o nome da table
    sqlCommand = sqlCommand + dbName + '.dbo.' +  tableName
    
    # Não tem nada a restringir
    if len(restrictor) == 0:
        sqlCommand = sqlCommand + ';'
    else:
        sqlCommand = sqlCommand + 'WHERE '
        for i in restrictor:
            aux = i
            # Última restrição
            if len(aux) == 3:
                sqlCommand = sqlCommand + aux[0] + aux[1] + aux[2] + ';'
            else:
                sqlCommand = sqlCommand + aux[0] + aux[1] + aux[2] + ' ' + aux[3] + ' '

    
    sqlCommand = sqlCommand + '\nCOMMIT TRANSACTION;'
    
    # Faz por fim a query à BD
    print(sqlCommand)
    query = cursor.execute(sqlCommand)
    
    return query

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
        window = GUI('Aplicação', uiPath, cursor, dbName)
        window.show()
    sys.exit(app.exec_())
    