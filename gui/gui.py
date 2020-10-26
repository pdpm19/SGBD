# Main window da app
import sys
import os
import time
import pyodbc
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from connectDlg import Connect

# Para correr o timer do refresh automático
class Threads(QRunnable):
    def __init__(self, timer: int, stackedIndex: int, stop: bool):
        super(Threads, self).__init__()
        self._timer = timer
        self._stackedIndex = stackedIndex
        self._stop = stop
        
        self.run()
    
    @pyqtSlot()    
    def run(self):
        if self._stackedIndex == 2:
            while True:
                print('THREAD A BOMBAR!')
                time.sleep(self._timer)
                if self._stop:
                    break
                # Chamar a função
                app.RefreshBrowser()
        #if stackedIndex == 3:
        #if stackedIndex == 4:    

# Modal da TableView
class TableModel(QStandardItemModel):
    def __init__(self, data, setHeader: int):
        super(TableModel, self).__init__()
        self._data = data
        self._setHeader = setHeader
        
        print(self._data)
        self.FillsData()
    
    def FillsData(self):
        if self._setHeader == 0:
            self.setHorizontalHeaderLabels(['ID do Produto', 'Designação', 'Preço', 'Quantidade', 'ID do Cliente', 'Nome do Cliente', 'Morada do Cliente'])
        
        if self._setHeader == 1:
            self.setHorizontalHeaderLabels(['NumReg', 'EventType', 'Objecto', 'Valor', 'Referencia', 'UserID', 'TerminalID', 'TerminalName', 'DCriacao'])
        nRows, nColumns = self._data.shape
        
        for i in range(nRows):
            for j in range(nColumns):
                item = QStandardItem(str(self._data[i, j]))
                self.setItem(i, j, item)
        
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

        # Threads
        self.threadpool = QThreadPool()
        self.timer = 5
        
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
        self.numReg = []
        self.eventType = []
        self.objeto = []
        self.valor = []
        self.referencia = []
        self.userID = []
        self.terminalID = []
        self.terminalName = []
        self.dataCriacao = []
        

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
        app4Button.pressed.connect(self.DisplayLog)

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

        self.browserTable = QTableView()
        
        formLayout.addRow(QLabel('ID da encomenda:'), self.choosedEnc)
        formLayout.addRow(self.browserTable)

        formWidget.setLayout(formLayout)
        self.browserLayout.addWidget(formWidget)
        self.browserLayout.addWidget(buttonsWidget)
        self.browserWidgets.setLayout(self.browserLayout)
    
    # vai preencher o ID e a tabela
    def DisplayBrowser(self):
        self.stacked.setCurrentIndex(2)
        
        # Vai ativar a thread
        self.browserRefreshStop = False
        print(self.stacked.currentIndex())
        self.browser_thread = Threads(self.timer, self.stacked.currentIndex(), lambda: self.browserRefreshStop)
        self.threadpool.start(self.browser_thread)
        
        query = MakeTransaction(self.cursor, self.isolationComboBox.currentText(), 'SELECT', ['EncID'], self.dbName, 'Encomenda', [])   
        
        for row in query:
            self.encIDs.append(str(row[0]))

        self.choosedEnc.addItems(self.encIDs)
        self.choosedEnc.currentIndexChanged.connect(self.RefreshBrowser)

        query = MakeTransaction(self.cursor, self.isolationComboBox.currentText(), 'SELECT', ['*'], self.dbName, 'Encomenda', [['EncID', '=', self.choosedEnc.currentText()]]) 
                
        for row in query:
            clienteID = str(row[1])
            clienteNome = str(row[2])
            clienteMorada = (row[3])
                    
        query = MakeTransaction(self.cursor, self.isolationComboBox.currentText(), 'SELECT', ['*'], self.dbName, 'EncLinha', [['EncID', '=', self.choosedEnc.currentText()]])      

        self.ClearAuxiliar(2)           
        for row in query:
            self.produtoIDs.append(str(row[1]))
            self.designacao.append(str(row[2]))
            self.preco.append(str(row[3]))
            self.qtd.append(str(row[4]))

        aux = []
        # Vai preencher a lista auxiliar
        for i in range(len(self.qtd)):
            aux.append([self.produtoIDs[i], self.designacao[i], self.preco[i], self.qtd[i], clienteID, clienteNome, clienteMorada])
        print('AUXILIAR %d' %len(aux))
        data = np.matrix(aux)

        modal = TableModel(data, 0)
        self.browserTable.setModel(modal)    
        
    # vai dar refresh aos dados manualmente
    def RefreshBrowser(self):
        # vai limpar o que já existe
        if self.choosedEnc.currentText():
            self.browserTable.clearSpans()
            self.ClearAuxiliar(0)

            query = MakeTransaction(self.cursor, self.isolationComboBox.currentText(), 'SELECT', ['*'], self.dbName, 'Encomenda', [['EncID', '=', self.choosedEnc.currentText()]]) 
                
            for row in query:
                clienteID = str(row[1])
                clienteNome = str(row[2])
                clienteMorada = (row[3])
                    
            query = MakeTransaction(self.cursor, self.isolationComboBox.currentText(), 'SELECT', ['*'], self.dbName, 'EncLinha', [['EncID', '=', self.choosedEnc.currentText()]])      
                    
            for row in query:
                self.produtoIDs.append(str(row[1]))
                self.designacao.append(str(row[2]))
                self.preco.append(str(row[3]))
                self.qtd.append(str(row[4]))
                
            aux = []
            # Vai preencher a lista auxiliar
            for i in range(len(self.qtd)):
                aux.append([self.produtoIDs[i], self.designacao[i], self.preco[i], self.qtd[i], clienteID, clienteNome, clienteMorada])

            data = np.matrix(aux)

            modal = TableModel(data, 0)
            self.browserTable.setModel(modal)
        else:
            self.ClearAuxiliar(0)
            self.browserTable.clearSpans()

    # Fecha e limpa os dados
    def CloseBrowser(self):
        # Limpa as variáveis auxiliarews
        self.ClearAuxiliar(0)
        
        self.choosedEnc.clear()
        self.browserTable.clearSpans()
        
        self.ClearAuxiliar(0)
        
        self.browserRefreshStop = True
        self.stacked.setCurrentIndex(0)
    
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
        if op == 3:
            self.numReg.clear()
            self.eventType.clear()
            self.objeto.clear()
            self.valor.clear()
    
    def TimeLogUI(self):
        backButton = QPushButton('Voltar')
        backButton.pressed.connect(lambda: self.stacked.setCurrentIndex(0))
    
        self.timeLogLayout.addWidget(backButton)
        self.timeLogWidgets.setLayout(self.timeLogLayout)
    
    def LogUI(self):
        

        backButton = QPushButton('Voltar')
        backButton.pressed.connect(self.CloseLog)

        refreshButton = QPushButton('Refresh')
        refreshButton.pressed.connect(self.RefreshLog)

        buttonsLayout = QHBoxLayout()
        buttonsWidget = QWidget()

        buttonsLayout.addWidget(backButton)
        buttonsLayout.addWidget(refreshButton)
        buttonsWidget.setLayout(buttonsLayout)
        
        formLayout = QFormLayout()
        formWidget = QWidget()

        self.numberLines = QLineEdit()
        self.numberLines.setValidator(QIntValidator())

        self.logTable = QTableView()
        
        formLayout.addRow(QLabel('Nº de linhas:'), self.numberLines)
        formLayout.addRow(self.logTable)

        formWidget.setLayout(formLayout)

        self.logLayout.addWidget(formWidget)
        self.logLayout.addWidget(buttonsWidget)
        self.logWidgets.setLayout(self.logLayout)

    def DisplayLog(self):
        self.stacked.setCurrentIndex(4)
        
        '''
        # Vai ativar a thread
        self.logRefreshStop = False
        self.log_thread = Threads(self.timer, self.stacked.currentIndex(), lambda: self.logRefreshStop)
        self.threadpool.start(self.log_thread)
        '''
        query = MakeTransaction(self.cursor, self.isolationComboBox.currentText(), 'SELECT', ['*'], self.dbName, 'LogOperations', [])

        for row in query:
            self.numReg.append(str(row[0]))
            self.eventType.append(str(row[1]))
            self.objeto.append(str(row[2]))
            self.valor.append(str(row[3]))
            self.referencia.append(str(row[4]))
            self.userID.append(str(row[5]))
            self.terminalID.append(str(row[6]))
            self.terminalName.append(str(row[7]))
            self.dataCriacao.append(str(row[8]))
           
        aux = []
        for i in range(len(self.numReg)):
            aux.append([self.numReg[i], self.eventType[i], self.objeto[i], self.valor[i], self.referencia[i], self.userID[i], self.terminalID[i], self.terminalName[i], self.dataCriacao[i]])
            
        data = np.matrix(aux)

        modal = TableModel(data, 1)
        self.logTable.setModel(modal)

    # Vai preencher as n linhas do Log
    def RefreshLog(self):
        self.logTable.clearSpans()
        self.ClearAuxiliar(3)
        if int(self.numberLines.text()) != 0:
            query = MakeTransaction(self.cursor, self.isolationComboBox.currentText(), 'SELECT', ['*'], self.dbName, 'LogOperations', [])

            for row in query:
                self.numReg.append(str(row[0]))
                self.eventType.append(str(row[1]))
                self.objeto.append(str(row[2]))
                self.valor.append(str(row[3]))
                self.referencia.append(str(row[4]))
                self.userID.append(str(row[5]))
                self.terminalID.append(str(row[6]))
                self.terminalName.append(str(row[7]))
                self.dataCriacao.append(str(row[8]))
            
            aux = []
            for i in range(len(self.numReg) - int(self.numberLines.text()), len(self.numReg)):
                aux.append([self.numReg[i], self.eventType[i], self.objeto[i], self.valor[i], self.referencia[i], self.userID[i], self.terminalID[i], self.terminalName[i], self.dataCriacao[i]])
            
            data = np.matrix(aux)

            modal = TableModel(data, 1)
            self.logTable.setModel(modal)
            
    def CloseLog(self):
        self.numberLines.clear()
        self.ClearAuxiliar(3)
        self.logTable.clearSpans()
        self.stacked.setCurrentIndex(0)
        

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
    