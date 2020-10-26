# Main window da app
import sys
import os
import pyodbc
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from connectDlg import Connect

# Modal da TableView
class TableModel(QStandardItemModel):
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data
        print(self._data)
        self.setHorizontalHeaderLabels(['ID do Produto', 'Designação', 'Preço', 'Quantidade', 'ID do Cliente', 'Nome do Cliente', 'Morada do Cliente'])
        self.FillsData()
    
    def FillsData(self):
        nRows = 0
        nColumns = 7
        for i in self._data:
            nRows += 1

        for j in range(nRows):
            aux = self._data[j]
            for i in aux:
                item = QStandardItem(i)
            self.appendRow(j, item)
# Aplicação principal
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

        # Variáveis auxiliares para o preenchimento dos campos
        self.encIDs = []
        self.clienteIDs = []
        self.clienteNome = []
        self.clienteMorada = []
        self.produtoIDs = []
        self.designacao = []
        self.preco = []
        self.qtd = []

    # Vai mostrar as aplicações & O nivel de isolamento pretendido
    def HomepageUI(self):
        appsLayout = QGridLayout()
        appsWidget = QWidget()
        
        app1Button = QPushButton('App1 - Editar')
        app1Button.pressed.connect(self.DisplayEdit)
        
        app2Button = QPushButton('App2 - Browser')
        app2Button.pressed.connect(self.DisplayBrowser)

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
        self.clientIDField = QLineEdit()
        self.clientIDField.setReadOnly(True)
        self.clientNameField = QLineEdit()
        self.clientNameField.setReadOnly(True)
        self.clienteMoradaField = QLineEdit()
        self.productIDField = QComboBox()
        self.productDesignationField = QLineEdit()
        self.productDesignationField.setReadOnly(True)
        self.productPriceField = QLineEdit()
        self.productPriceField.setReadOnly(True)
        self.productQtdField = QLineEdit()
        self.productQtdField.setValidator(QIntValidator())

        
        
        formLayout.addRow(QLabel('ID da Encomenda:'), self.encIDField)
        formLayout.addRow(QLabel('ID do Cliente:'), self.clientIDField)
        formLayout.addRow(QLabel('Nome do Cliente:'), self.clientNameField)
        formLayout.addRow(QLabel('Morada do Cliente:'), self.clienteMoradaField) 
        formLayout.addRow(QLabel('ID do Produto:'), self.productIDField)
        formLayout.addRow(QLabel('Designação do Produto:'), self.productDesignationField)
        formLayout.addRow(QLabel('Preço do Produto:'), self.productPriceField)
        formLayout.addRow(QLabel('Quantidade do Produto:'), self.productQtdField)
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
            self.clienteIDs.append(str(row[1]))
            self.clienteNome.append(str(row[2]))
            self.clienteMorada.append(str(row[3]))
        
        self.encIDField.addItems(self.encIDs)
        self.clientNameField.setText(self.clienteNome[0])
        self.clientIDField.setText(self.clienteIDs[0])
        self.clienteMoradaField.setText(self.clienteMorada[0])

        if self.encIDField.currentText() and not self.productIDField.currentText():
            query = MakeTransaction(self.cursor, self.isolationComboBox.currentText(), 'SELECT', ['*'], self.dbName, 'EncLinha', [['EncID', '=', self.encIDField.currentText()]])
                
            for row in query:
                self.produtoIDs.append(str(row[1]))
                self.designacao.append(str(row[2]))
                self.preco.append(str(row[3]))
                self.qtd.append(str(row[4]))

            self.productIDField.addItems(self.produtoIDs)
            self.productDesignationField.setText(self.designacao[0])
            self.productPriceField.setText(self.preco[0])
            self.productQtdField.setText(self.qtd[0])
        
        self.encIDField.currentIndexChanged.connect(self.UpdateUserEdit)
        self.productIDField.currentIndexChanged.connect(self.UpdateProductEdit)
    
    # Fecha a página de Editar
    def CloseEdit(self):
        # Vai limpar todos os campos
        self.encIDField.clear()
        self.clientIDField.clear()
        self.clientNameField.clear()
        self.clienteMoradaField.clear()
        self.productIDField.clear()
        self.productDesignationField.clear()
        self.productPriceField.clear()
        self.productQtdField.clear()
        
        # vai limpar todos os vetores auxiliares
        self.ClearAuxiliar(0)

        self.stacked.setCurrentIndex(0)
    
    # Atualiza os campos da tabela Encomenda consoante o ID da encomenda selecionado
    def UpdateUserEdit(self):
        if self.encIDField.currentText():
            currentID = self.encIDField.currentIndex()
                
            self.clientIDField.clear()
            self.clientIDField.setText(self.clienteIDs[currentID])

            self.clientNameField.clear()
            self.clientNameField.setText(self.clienteNome[currentID])

            self.clienteMoradaField.clear()
            self.clienteMoradaField.setText(self.clienteMorada[currentID])

            query = MakeTransaction(self.cursor, self.isolationComboBox.currentText(), 'SELECT', ['*'], self.dbName, 'EncLinha', [['EncID', '=', self.encIDField.currentText()]])
            
            self.ClearAuxiliar(2)
            if self.productIDField.currentText():
                self.productIDField.clear()
            for row in query:
                self.produtoIDs.append(str(row[1]))
                self.designacao.append(str(row[2]))
                self.preco.append(str(row[3]))
                self.qtd.append(str(row[4]))

            self.productIDField.addItems(self.produtoIDs)
            self.productDesignationField.setText(self.designacao[0])
            self.productPriceField.setText(self.preco[0])
            self.productQtdField.setText(self.qtd[0])


    # Atualiza os campos da tabela EncLinha consoante o ID do produto
    def UpdateProductEdit(self):
        if self.productIDField.currentText():
            currentID = self.productIDField.currentIndex()

            self.productDesignationField.clear()
            self.productDesignationField.setText(self.designacao[currentID])
            
            self.productPriceField.clear()
            self.productPriceField.setText(self.preco[currentID])
            
            self.productQtdField.clear()
            self.productQtdField.setText(self.qtd[currentID])
            
    # Grava as alterações feitas
    def EditFunction(self):
        print('yo')
    
    def BrowserUI(self):
        backButton = QPushButton('Voltar')
        backButton.pressed.connect(self.CloseBrowser)

        refreshButton = QPushButton('Refresh')
        refreshButton.pressed.connect(self.RefreshBrowser)

        buttonsLayout = QHBoxLayout()
        buttonsWidget = QWidget()

        buttonsLayout.addWidget(backButton)
        buttonsLayout.addWidget(refreshButton)
        buttonsWidget.setLayout(buttonsLayout)
        
        formLayout = QFormLayout()
        formWidget = QWidget()

        self.choosedEnc = QComboBox()

        
        self.table = QTableView()
        data = []
        data.append(['1', '2', '3', '4', '5', '6', '7'])
        data.append(['1', '2', '3', '4', '5', '6', '7'])
        
        modal = TableModel(data)
        self.table.setModel(modal)
        
        formLayout.addRow(QLabel('ID da encomenda:'), self.choosedEnc)
        formLayout.addRow(self.table)

        formWidget.setLayout(formLayout)
        self.browserLayout.addWidget(formWidget)
        self.browserLayout.addWidget(buttonsWidget)
        self.browserWidgets.setLayout(self.browserLayout)
    
    # vai preencher o ID e a tabela
    def DisplayBrowser(self):
        self.stacked.setCurrentIndex(2)
        
        query = MakeTransaction(self.cursor, self.isolationComboBox.currentText(), 'SELECT', ['EncID'], self.dbName, 'Encomenda', [])   
        
        for row in query:
            self.encIDs.append(str(row[0]))
        
        self.choosedEnc.addItems(self.encIDs)
        if self.choosedEnc.currentText():
            self.choosedEnc.currentIndexChanged.connect(self.RefreshBrowser)
    
    # vai dar refresh aos dados
    def RefreshBrowser(self):
        # vai limpar o que já existe
        if self.choosedEnc.currentText():
            self.table.clearSpans()

            currentID = self.choosedEnc.currentText()
            
            # Conteúdo tabela Encomenda
            query = MakeTransaction(self.cursor, self.isolationComboBox.currentText(), 'SELECT', ['*'], self.dbName, 'Encomenda', [['EncID', '=', str(currentID)]])
            for row in query:
                self.clienteIDs.append(str(row[0]))
                self.clienteNome.append(str(row[1]))
                self.clienteMorada.append(str(row[2]))
                
            # Conteúdo tabela EncLinha
            query = MakeTransaction(self.cursor, self.isolationComboBox.currentText(), 'SELECT', ['*'], self.dbName, 'EncLinha', [['EncID', '=', str(currentID)]])
            for row in query:
                self.produtoIDs.append(str(row[0]))
                self.designacao.append(str(row[1]))
                self.preco.append(str(row[2]))
                self.qtd.append(str(row[3]))

    # Fecha e limpa os dados
    def CloseBrowser(self):
        self.stacked.setCurrentIndex(0)
        
        # Limpa as
        self.choosedEnc.clear()
        # Limpa as variáveis auxiliarews
        self.ClearAuxiliar(0)
        self.table.clearSpans()
    
    def ClearAuxiliar(self, op):
        if op == 0:
            self.encIDs.clear()
            self.clienteIDs.clear()
            self.clienteNome.clear()
            self.clienteMorada.clear()
            self.produtoIDs.clear()
            self.designacao.clear()
            self.preco.clear()
            self.qtd.clear()
        if op == 1:
            self.encIDs.clear()
            self.clienteIDs.clear()
            self.clienteNome.clear()
            self.clienteMorada.clear()
        if op == 2:
            self.produtoIDs.clear()
            self.designacao.clear()
            self.preco.clear()
            self.qtd.clear()
    
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
        sqlCommand = sqlCommand + '\nWHERE '
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
    