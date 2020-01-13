

import sys
from PyQt5 import QtWidgets
from CTRL_USB_main import mywindow
if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    application = mywindow()
    application.show()
    sys.exit(app.exec())

