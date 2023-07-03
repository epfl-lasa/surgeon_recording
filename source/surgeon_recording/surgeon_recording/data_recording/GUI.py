from PyQt5.QtWidgets import * 
from PyQt5.QtGui import QFont
import sys

def on_clicked(msg):
    message = QMessageBox()
    message.setText(msg)
    #message.setText("Thanks for your participation!")
    message.exec_()
    
    print("data saved")

def main():
    app = QApplication([])
    window = QWidget()
    window.setGeometry(100, 100, 2600, 1600)
    window.setWindowTitle("GUI microsurgery questionnaire")
    
    layout = QVBoxLayout() #vertical layout
    
    label = QLabel("press button")
    
    textbox = QTextEdit()
    
    button = QPushButton("press me")
    button.clicked.connect(lambda: on_clicked(textbox.toPlainText()))
    
    layout.addWidget(label)
    layout.addWidget(textbox)
    layout.addWidget(button)
    
    window.setLayout(layout)
    
    # label = QLabel(window)
    # label.setText(" Microsurgery Questionnaire")  
    # label.setFont(QFont("Arial", 16))
    # label.move(50,100)
    
    window.show()
    app.exec_()
    
    #sys.exit(app.exec_())
    
if __name__ == '__main__':
    main()