from PyQt5.QtWidgets import * 
from PyQt5.QtGui import QFont, QIcon
import sys
import numpy as np

class MyWindow(QWidget):
    def __init__(self):
        super().__init__() #calls the __init__() method of the parent class, which is QWidget here. 
                          #It ensures that the necessary initialization from the parent class is 
                          #performed before any additional initialization specific to MyWindow is done.
        
        self.initUI() #to initialize the user interface of the window. It is defined in the MyWindow class, 
                      #and it sets up the layout and adds the checkbox widget to the window.
                      
    def dropdownmenu(self):
        cb = QComboBox()
        cb.addItem("Right hand strongly preferred")
        cb.addItem("Right hand preferred")
        cb.addItem("No preference")
        cb.addItem("Left hand preferred")
        cb.addItem("Left hand strongly preferred")
        return(cb)
    
    def Edinburgh_handedness(self, task):
        label = QLabel(task)
        ddm = self.dropdownmenu()     
        return (label,ddm)
        
    
    def on_clicked(self,msg): #save the information and says thanks
        np.save("S_x_general_info.npy",msg)
        
        message = QMessageBox()
        # message.setText(msg)
        message.setText("Thanks for your participation!")
        message.exec_()
        print("data saved")

    def initUI(self):
        self.setGeometry(100, 100, 2600, 1600)
        self.setWindowTitle("GUI microsurgery questionnaire")
        # self.setWindowIcon(QIcon('xxx.png'))
        
        layout = QVBoxLayout() #vertical layout
        
        label_intro = QLabel("Bla bla introduction")
        
        label_form = QLabel("General information")
        label_form.setFont(QFont('Arial',11))
        
        label_age = QLabel("What is your age?")
        age = QTextEdit()
        
        label_sex = QLabel("What is your biological sex?")
        sex_cb = QComboBox()
        sex_cb.addItem("F")
        sex_cb.addItem("M")
        
        label_occupation = QLabel("What is your occupation and expertise?")
        occupation = QTextEdit()
        
        
        label_questionaire = QLabel("Handedness questionnaire")
        label_questionaire.setFont(QFont("Arial", 11))
        label_questionaire_description = QLabel("After you use the mouse to indicate your preference for the ten items in the table, your handedness score will be automatically calculated. Please indicate which hand you prefer for each of the following activities.")
        
        label_writing, ddm1 = self.Edinburgh_handedness("1. Writing")
        label_drawing, ddm2 = self.Edinburgh_handedness("2. Drawing")
        label_throwing, ddm3 = self.Edinburgh_handedness("3. Throwing")
        label_scissors, ddm4 = self.Edinburgh_handedness("4. Using scissors")
        label_teeth, ddm5 = self.Edinburgh_handedness("5. Brusinh teeth")
        label_knife, ddm6 = self.Edinburgh_handedness("6. Using knife (without fork)")
        label_spoon, ddm7 = self.Edinburgh_handedness("7. Using a spoon")
        label_broom, ddm8 = self.Edinburgh_handedness("8. Using a broom (dominant hand)")
        label_match, ddm9 = self.Edinburgh_handedness("9. Striking a match")
        label_jar, ddm10 = self.Edinburgh_handedness("10. Opening a jar")
        
        button = QPushButton("Save")
        button.clicked.connect(lambda: self.on_clicked(name.toPlainText()))
        
        
        #LAYOUTS
        layout.addWidget(label_intro)
        
        layout.addWidget(label_form)
        
        layout.addWidget(label_age)
        layout.addWidget(age)

        layout.addWidget(label_sex)
        layout.addWidget(sex_cb)
        
        layout.addWidget(label_occupation)
        layout.addWidget(occupation)
        
        layout.addWidget(label_questionaire)
        layout.addWidget(label_questionaire_description)
        layout.addWidget(label_writing)
        layout.addWidget(ddm1)
        layout.addWidget(label_drawing)
        layout.addWidget(ddm2)
        layout.addWidget(label_throwing)
        layout.addWidget(ddm3)
        layout.addWidget(label_scissors)
        layout.addWidget(ddm4)
        layout.addWidget(label_teeth)
        layout.addWidget(ddm5)
        layout.addWidget(label_knife)
        layout.addWidget(ddm6)
        layout.addWidget(label_spoon)
        layout.addWidget(ddm7)
        layout.addWidget(label_broom)
        layout.addWidget(ddm8)
        layout.addWidget(label_match)
        layout.addWidget(ddm9)
        layout.addWidget(label_jar)
        layout.addWidget( ddm10)
        
        layout.addWidget(button)
        
        self.setLayout(layout)
            
        self.show()
        app.exec_()
        
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    sys.exit(app.exec_())
