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
                      
    def dropdownmenu(self, cb):
        cb.addItem("Always right hand")
        cb.addItem("Usually right hand")
        cb.addItem("No preference")
        cb.addItem("Usualy left hand")
        return(cb)
    
    def convertDdmToNumber(self, ddm):
        if ddm == "Always right hand" :
            self.sum_R = 2 
        elif ddm == "Usually right hand":
            self.sum_R +=1  
        elif ddm == "No preference":
            self.sum_L += 1
            self.sum_R += 1
        elif ddm == "Usualy left hand":
            self.sum_L += 1
        elif ddm == "Always left hand":
            self.sum_L += 2
        return ( self.sum_L, self.sum_R)
        
    def Edinburgh_handedness(self):
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
        
        self.sum_L = 0
        self.sum_R = 0
        
        sum_L, sum_R = self.convertDdmToNumber(selected_ddm1)
        sum_L, sum_R = self.convertDdmToNumber(selected_ddm2)
        sum_L, sum_R = self.convertDdmToNumber(selected_ddm3)
        sum_L, sum_R = self.convertDdmToNumber(selected_ddm4)
        sum_L, sum_R = self.convertDdmToNumber(selected_ddm5)
        sum_L, sum_R = self.convertDdmToNumber(selected_ddm6)
        sum_L, sum_R = self.convertDdmToNumber(selected_ddm7)
        sum_L, sum_R = self.convertDdmToNumber(selected_ddm8)
        sum_L, sum_R = self.convertDdmToNumber(selected_ddm9)
        sum_L, sum_R = self.convertDdmToNumber(selected_ddm10)
        
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
        
    
    def on_clicked(self, data): #save the information and says thanks
        np.save("S_x_general_info.npy", data)
        
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
        
        self.handedness = self.Edinburgh_handedness()

        self.ddm1.currentIndexChanged.connect(self.updateHandedness) # Connect signal to update Handedness method
        self.ddm2.currentIndexChanged.connect(self.updateHandedness) 
        self.ddm3.currentIndexChanged.connect(self.updateHandedness)
        self.ddm4.currentIndexChanged.connect(self.updateHandedness) 
        self.ddm5.currentIndexChanged.connect(self.updateHandedness) 
        self.ddm6.currentIndexChanged.connect(self.updateHandedness) 
        self.ddm7.currentIndexChanged.connect(self.updateHandedness) 
        self.ddm8.currentIndexChanged.connect(self.updateHandedness)
        self.ddm9.currentIndexChanged.connect(self.updateHandedness) 
        self.ddm10.currentIndexChanged.connect(self.updateHandedness) 


        #Save data
        data = self.sex
        self.saveButton.clicked.connect(lambda: self.on_clicked(name.toPlainText()))
        
        

    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
