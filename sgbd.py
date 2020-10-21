# Função inicial da aplicação
import os
import sys

workingDirectory = os.getcwd()
uiPath = os.path.join(workingDirectory, 'gui')

sys.path.append(uiPath)

from gui import DisplayGUI

if __name__ == "__main__":
    DisplayGUI(uiPath)
