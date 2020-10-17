# Função inicial da aplicação
import os
import sys

workingDirectory = os.getcwd()
uiPath = os.path.join(workingDirectory, 'gui')

sys.path.append(uiPath)

from loginDlg import DisplayLogin

if __name__ == "__main__":
    DisplayLogin(uiPath)
