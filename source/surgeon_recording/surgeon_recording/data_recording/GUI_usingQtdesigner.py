from PyQt5.QtWidgets import * 
from PyQt5.QtGui import QFont, QIcon
import sys
import numpy as np
from PyQt5.uic import loadUi

class MyWindow(QDialog):
    def __init__(self):
        super().__init__() #calls the __init__() method of the parent class, which is QWidget here. 
                          #It ensures that the necessary initialization from the parent class is 
                          #performed before any additional initialization specific to MyWindow is done.
        
        self.initUI() #to initialize the user interface of the window. It is defined in the MyWindow class, 
                      #and it sets up the layout and adds the checkbox widget to the window.
                      
    def dropdownmenu(self):
        cb.addItem("Right hand strongly preferred")
        cb.addItem("Right hand preferred")
        cb.addItem("No preference")
        cb.addItem("Left hand preferred")
        cb.addItem("Left hand strongly preferred")
        return(cb)
    
    def Edinburgh_handedness(self, task, cb):
        
        cb = self.dropdownmenu() 
        return (ddm)
                   
    #Function to avoid having the same arm for both tools (tweezers and needle holder)
    def updateNeedleHolder_cb(self): 
        self.needleholder_cb.clear() #clear existing item
        selected_tweezer = self.tweezer_cb.currentText()
        
        if selected_tweezer == "L":
            self.needleholder_cb.addItem("R")
        else:
            self.needleholder_cb.addItem("L")
        
    
    def on_clicked(self,msg): #save the information and says thanks
        np.save("S_x_general_info.npy",msg)
        
        message = QMessageBox()
        # message.setText(msg)
        message.setText("Thanks for your participation!")
        message.exec_()
        print("data saved")

    def initUI(self):
        
        #WINDOW PARAMETERS
        loadUi("GUImicrosurgery.ui", self) # Load the .ui file into the MyWindow
        
                
        #WINDODW CONTENT 

        sex_list = ["F", "M"]
        self.sex_cb.addItems(sex_list)
        
        tweezer_list = ["L", "R"]
        self.tweezer_cb.addItems(tweezer_list)
        self.tweezer_cb.currentIndexChanged.connect(self.updateNeedleHolder_cb) # Connect signal to updateNeedleHolder_cb method
    
        anastomosis_list = ["Yes", "No"]
        self.anastomosis_cb.addItems(anastomosis_list)
        
        nbAnastomosis_list = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "10-15", "15-20", "20-25", "25-30", "30+"]
        self.nbAnastomosis_cb.addItems(nbAnastomosis_list)
    
        nbCourses_list = ["0", "1", "2", "3", "4", "5", "5+"]
        self.nbCourses_cb.addItems(nbCourses_list)
        
        confidenceAnastomosis_list = ["0", "1", "2", "3", "4", "5"]
        self.confidenceAnastomosis_cb.addItems(confidenceAnastomosis_list)
    
        #Handedness questionnaire
        for i in range(1,11):
            self.ddm + str(i) = self.dropdownmenu( )
        # label_writing, = self.Edinburgh_handedness("1. Writing", self.ddm1 )
        # label_drawing, self.ddm2 = self.Edinburgh_handedness("2. Drawing")
        # label_throwing, self.ddm3 = self.Edinburgh_handedness("3. Throwing")
        # label_scissors, self.ddm4 = self.Edinburgh_handedness("4. Using scissors")
        # label_teeth, self.ddm5 = self.Edinburgh_handedness("5. Brushing teeth")
        # label_knife, self.ddm6 = self.Edinburgh_handedness("6. Using knife (without fork)")
        # label_spoon, self.ddm7 = self.Edinburgh_handedness("7. Using a spoon")
        # label_broom, self.ddm8 = self.Edinburgh_handedness("8. Using a broom (dominant hand)")
        # label_match, self.ddm9 = self.Edinburgh_handedness("9. Striking a match")
        # label_jar, self.ddm10 = self.Edinburgh_handedness("10. Opening a jar")
        
        #Save data
        self.saveButton.clicked.connect(lambda: self.on_clicked(name.toPlainText()))
        
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
