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
                      
    # def adjustWindowSize(self):
    #     # Get the screen resolution
    #     screen_geometry = QDesktopWidget().screenGeometry()
    #     screen_width = screen_geometry.width()
    #     screen_height = screen_geometry.height()

    #     # Set window size as a percentage of the screen size
    #     window_width = int(screen_width * 0.9)  # 90% of screen width
    #     window_height = int(screen_height * 0.9)  #90% of screen height
    #     self.resize(window_width, window_height)
                      
    def dropdownmenu(self, cb):
        # cb.addItem("< Choose options >")
        cb.addItem("Always right hand")
        cb.addItem("Usually right hand")
        cb.addItem("No preference")
        cb.addItem("Usualy left hand")
        cb.addItem("Always left hand")
        return(cb)

    def convertDdmToNumber(self, ddm): #converts the preferenced entered by the user into a number 
        R = 0 
        L = 0
        if ddm == "Always right hand" :
            R = 2 
        elif ddm == "Usually right hand":
            R = 1  
        elif ddm == "No preference":
            L = 1
            R = 1
        elif ddm == "Usualy left hand":
            L = 1
        elif ddm == "Always left hand":
            L = 2
        return ( L, R)
        
    def Edinburgh_handedness(self): # computes the handedness
        selected_ddm1 = self.ddm1.currentText()
        selected_ddm2 = self.ddm2.currentText()
        selected_ddm3 = self.ddm3.currentText()
        selected_ddm4 = self.ddm4.currentText()
        selected_ddm5 = self.ddm5.currentText()
        selected_ddm6 = self.ddm6.currentText()
        selected_ddm7 = self.ddm7.currentText()
        selected_ddm8 = self.ddm8.currentText()
        selected_ddm9 = self.ddm9.currentText()
        selected_ddm10 = self.ddm10.currentText()
                
        L1, R1 = self.convertDdmToNumber(selected_ddm1)
        L2, R2 = self.convertDdmToNumber(selected_ddm2)
        L3, R3 = self.convertDdmToNumber(selected_ddm3)
        L4, R4 = self.convertDdmToNumber(selected_ddm4)
        L5, R5 = self.convertDdmToNumber(selected_ddm5)
        L6, R6 = self.convertDdmToNumber(selected_ddm6)
        L7, R7 = self.convertDdmToNumber(selected_ddm7)
        L8, R8 = self.convertDdmToNumber(selected_ddm8)
        L9, R9 = self.convertDdmToNumber(selected_ddm9)
        L10, R10 = self.convertDdmToNumber(selected_ddm10)
        
        sum_R = R1 + R2 + R3 + R4 + R5 + R6 + R7 + R8 + R9 + R10 # sum of right scores 
        sum_L = L1 + L2 + L3 + L4 + L5 + L6 + L7 + L8 + L9 + L10 # sum of left scores
    
        handedness_formula = 100 *((sum_R - sum_L) / (sum_R + sum_L)) #formula to compute handedness
        print("handedness = ", handedness_formula)

        return (handedness_formula)
    
    def updateHandedness(self):
        self.handedness = self.Edinburgh_handedness()
        
    #Function to avoid having the same arm for both tools (tweezers and needle holder)
    def updateNeedleHolder_cb(self): 
        self.needleholder_cb.clear() #clear existing item
        selected_tweezer = self.tweezer_cb.currentText()
        
        if selected_tweezer == "L":
            self.needleholder_cb.addItem("R")
        else:
            self.needleholder_cb.addItem("L")
            
    def getText(self, qTextEdit):
        text = qTextEdit.toPlainText()
        if text:
            try:
                qTextEdit = str(text)
            except ValueError:
                print("Invalid input. Please enter a valid integer.")
        else:
            print("The "+ str(qTextEdit) +" box is empty.")
        return (text)
        
    
    def on_clicked(self): #save the information and says thanks
        data = np.zeros(23)
        
        #
        data[self.id_subjectnb] = self.getText(self.subjectnb)
        data[self.id_date] = self.getText(self.date)
        data[self.id_starttime] = self.getText(self.starttime)
        data[self.id_age] = self.getText(self.age)
        data[self.id_sex_cb] = self.sex_cb.currentText()
        data[self.id_occupation] = self.getText(occupation)
        data[self.id_expmicrosurg] = self.getText(self.exp_microsurg)
        data[self.id_tweezer_cb] = self.tweezer_cb.currentText()
        data[self.id_needleholder_cb] = self.needleholder_cb.currentText()
        data[self.id_anastomosis_cb] = self.anastomosis_cb.currentText()
        data[self.id_nbAnastomosis_cb] = self.nbAnastomosis_cb.currentText()
        data[self.id_nbCourses_cb] = self.nbCourses_cb.currentText()
        data[self.id_confidenceAnastomosis_cb] = self.confidenceAnastomosis_cb.currentText() 
        data[self.id_ddm1] = self.ddm1.currentText()
        data[self.id_ddm2] = self.ddm2.currentText()
        data[self.id_ddm3] = self.ddm3.currentText()
        data[self.id_ddm4] = self.ddm4.currentText()
        data[self.id_ddm5] = self.ddm5.currentText()
        data[self.id_ddm6] = self.ddm6.currentText()
        data[self.id_ddm7] = self.ddm7.currentText()
        data[self.id_ddm8] = self.ddm8.currentText()
        data[self.id_ddm9] = self.ddm9.currentText()
        data[self.id_ddm10] = self.ddm10.currentText()
        
    
        np.save("S_" + self.getText(self.subjectnb) + "_general_info.npy", data)
        
        message = QMessageBox()
        # message.setText(msg)
        message.setText("Thanks for your participation!")
        message.exec_()
        print("data saved")

    def initUI(self):
        
        #WINDOW PARAMETERS
        loadUi("GUImicrosurgery.ui", self) # Load the .ui file into the MyWindow
        # self.adjustWindowSize() #adjust window size to fit the screen
                        
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
        self.ddm1 = self.dropdownmenu(self.ddm1)
        self.ddm2 = self.dropdownmenu(self.ddm2)
        self.ddm3 = self.dropdownmenu(self.ddm3)
        self.ddm4 = self.dropdownmenu(self.ddm4)
        self.ddm5 = self.dropdownmenu(self.ddm5)
        self.ddm6 = self.dropdownmenu(self.ddm6)
        self.ddm7 = self.dropdownmenu(self.ddm7)
        self.ddm8 = self.dropdownmenu(self.ddm8)
        self.ddm9 = self.dropdownmenu(self.ddm9)
        self.ddm10 = self.dropdownmenu(self.ddm10)
        
        # Connect signals to update Handedness method
        self.ddm1.currentIndexChanged.connect(self.updateHandedness) 
        self.ddm2.currentIndexChanged.connect(self.updateHandedness) 
        self.ddm3.currentIndexChanged.connect(self.updateHandedness)
        self.ddm4.currentIndexChanged.connect(self.updateHandedness) 
        self.ddm5.currentIndexChanged.connect(self.updateHandedness) 
        self.ddm6.currentIndexChanged.connect(self.updateHandedness) 
        self.ddm7.currentIndexChanged.connect(self.updateHandedness) 
        self.ddm8.currentIndexChanged.connect(self.updateHandedness)
        self.ddm9.currentIndexChanged.connect(self.updateHandedness) 
        self.ddm10.currentIndexChanged.connect(self.updateHandedness) 

        #Compute handedness
        self.handedness = self.Edinburgh_handedness()
        
        
        #SAVE DATA ENTERED BU USER
        # give names to index
        self.id_subjectnb = 0
        self.id_date = 1
        self.id_starttime = 2
        self.id_age = 3
        self.id_sex_cb = 4
        self.id_occupation = 5
        self.id_expmicrosurg = 6
        self.id_tweezer_cb = 7
        self.id_needleholder_cb = 8
        self.id_anastomosis_cb = 9
        self.id_nbAnastomosis_cb = 10
        self.id_nbCourses_cb = 11
        self.id_confidenceAnastomosis_cb = 12
        self.id_ddm1 = 13
        self.id_ddm2 = 14
        self.id_ddm3 = 15
        self.id_ddm4 = 16
        self.id_ddm5 = 17
        self.id_ddm6 = 18
        self.id_ddm7 = 19
        self.id_ddm8 = 20
        self.id_ddm9 = 21
        self.id_ddm10 = 22


        #Use button save to save data
        # self.saveButton.clicked.connect(lambda: self.on_clicked(data.toPlainText()))
        self.saveButton.clicked.connect(lambda: self.on_clicked())

        

    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
