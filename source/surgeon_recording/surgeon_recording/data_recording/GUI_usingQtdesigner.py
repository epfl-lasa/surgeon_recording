#IMPORTS
import sys
import numpy as np

from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi


# class to create the GUI
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
                      
    def dropdownmenu(self, cb): #passes the options for the handedness combo boxes
        cb.addItem("Always right hand")
        cb.addItem("Usually right hand")
        cb.addItem("No preference")
        cb.addItem("Usualy left hand")
        cb.addItem("Always left hand")
        return cb

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
        selected_ddm_writing = self.ddm_writing.currentText()
        selected_ddm_drawing = self.ddm_drawing.currentText()
        selected_ddm_throwing = self.ddm_throwing.currentText()
        selected_ddm_scissors = self.ddm_scissors.currentText()
        selected_ddm_teeth = self.ddm_teeth.currentText()
        selected_ddm_knife = self.ddm_knife.currentText()
        selected_ddm_spoon = self.ddm_spoon.currentText()
        selected_ddm_broom = self.ddm_broom.currentText()
        selected_ddm_match = self.ddm_match.currentText()
        selected_ddm_jar = self.ddm_jar.currentText()
                
        L1, R1 = self.convertDdmToNumber(selected_ddm_writing)
        L2, R2 = self.convertDdmToNumber(selected_ddm_drawing)
        L3, R3 = self.convertDdmToNumber(selected_ddm_throwing)
        L4, R4 = self.convertDdmToNumber(selected_ddm_scissors)
        L5, R5 = self.convertDdmToNumber(selected_ddm_teeth)
        L6, R6 = self.convertDdmToNumber(selected_ddm_knife)
        L7, R7 = self.convertDdmToNumber(selected_ddm_spoon)
        L8, R8 = self.convertDdmToNumber(selected_ddm_broom)
        L9, R9 = self.convertDdmToNumber(selected_ddm_match)
        L10, R10 = self.convertDdmToNumber(selected_ddm_jar)
        
        sum_R = R1 + R2 + R3 + R4 + R5 + R6 + R7 + R8 + R9 + R10 # sum of right scores 
        sum_L = L1 + L2 + L3 + L4 + L5 + L6 + L7 + L8 + L9 + L10 # sum of left scores
    
        handedness_formula = 100 *((sum_R - sum_L) / (sum_R + sum_L)) #formula to compute handedness
        print("handedness = ", handedness_formula)

        return handedness_formula
    
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
        return text
        
    
    def on_clicked(self): #save the information and says thanks
        #save entered data
        data = np.array([self.getText(self.subjectnb),                #0
                         self.getText(self.date),                     #1
                         self.getText(self.starttime),                #2
                         self.getText(self.age),                      #3
                         self.sex_cb.currentText(),                   #4
                         self.getText(self.occupation),               #5
                         self.getText(self.exp_microsurg),            #6
                         self.tweezer_cb.currentText(),               #7
                         self.needleholder_cb.currentText(),          #8
                         self.anastomosis_cb.currentText(),           #9
                         self.nbAnastomosis_cb.currentText(),         #10
                         self.nbCourses_cb.currentText(),             #11
                         self.confidenceAnastomosis_cb.currentText(), #12
                        self.ddm_writing.currentText(),               #13
                        self.ddm_drawing.currentText(),               #14
                        self.ddm_throwing.currentText(),              #15
                        self.ddm_scissors.currentText(),              #16
                        self.ddm_teeth.currentText(),                 #17
                        self.ddm_knife.currentText(),                 #18
                        self.ddm_spoon.currentText(),                 #19
                        self.ddm_broom.currentText(),                 #20
                        self.ddm_match.currentText(),                 #21
                        self.ddm_jar.currentText(),                   #22
                        self.eye_cb.currentText()                     #23
                        ])
        
        #save the created array ina .npy format
        np.save("S_" + self.getText(self.subjectnb) + "_general_info.npy", data)
        
        message = QMessageBox()
        message.setText("Thanks for your participation!")
        message.exec_()
        print("data saved")

    #Creates and displa the GUI
    def initUI(self):
        
        #WINDOW PARAMETERS
        loadUi("GUImicrosurgery.ui", self) # Load the .ui file into the MyWindow
        # self.adjustWindowSize() #adjust window size to fit the screen
        
                        
        #WINDODW CONTENT 
        sex_list = ["F", "M"]
        self.sex_cb.addItems(sex_list)
        
        tweezer_list = [" ", "L", "R"]
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
        ## Defining variables 
        self.handedness_list =[self.ddm_writing, self.ddm_drawing, self.ddm_throwing, self.ddm_scissors, 
                               self.ddm_teeth, self.ddm_knife, self.ddm_spoon, self.ddm_broom, self.ddm_match, self.ddm_jar]
        # self.id_handednesss_list = [self.id_ddm_writing, self.id_ddm_drawing, self.id_ddm_throwing, self.id_ddm_scissors, 
        #                        self.id_ddm_teeth, self.id_ddm_knife, self.id_ddm_spoon, self.id_ddm_broom, self.id_ddm_match, self.id_ddm_jar]
        
        for i in range (10):            
            self.handedness_list[i]= self.dropdownmenu(self.handedness_list[i]) #add the dropdownmenu to each item of the handedness questionnaire
            self.handedness_list[i].currentIndexChanged.connect(self.updateHandedness) # Connect signals to update Handedness method
        
        self.eye_cb = self.dropdownmenu(self.eye_cb)
        
        # self.ddm_writing = self.dropdownmenu(self.ddm_writing)
        # self.ddm_drawing = self.dropdownmenu(self.ddm_drawing)
        # self.ddm_throwing = self.dropdownmenu(self.ddm_throwing)
        # self.ddm_scissors = self.dropdownmenu(self.ddm_scissors)
        # self.ddm_teeth = self.dropdownmenu(self.ddm_teeth)
        # self.ddm_knife = self.dropdownmenu(self.ddm_knife)
        # self.ddm_spoon = self.dropdownmenu(self.ddm_spoon)
        # self.ddm_broom = self.dropdownmenu(self.ddm_broom)
        # self.ddm_match = self.dropdownmenu(self.ddm_match)
        # self.ddm_jar = self.dropdownmenu(self.ddm_jar)
        
        # Connect signals to update Handedness method
        # self.ddm_writing.currentIndexChanged.connect(self.updateHandedness) 
        # self.ddm_drawing.currentIndexChanged.connect(self.updateHandedness) 
        # self.ddm_throwing.currentIndexChanged.connect(self.updateHandedness)
        # self.ddm_scissors.currentIndexChanged.connect(self.updateHandedness) 
        # self.ddm_teeth.currentIndexChanged.connect(self.updateHandedness) 
        # self.ddm_knife.currentIndexChanged.connect(self.updateHandedness) 
        # self.ddm_spoon.currentIndexChanged.connect(self.updateHandedness) 
        # self.ddm_broom.currentIndexChanged.connect(self.updateHandedness)
        # self.ddm_match.currentIndexChanged.connect(self.updateHandedness) 
        # self.ddm_jar.currentIndexChanged.connect(self.updateHandedness) 

        #Compute handedness
        self.handedness = self.Edinburgh_handedness()
        
        
        #SAVE DATA ENTERED BY USER
        #Use button save to save data
        self.saveButton.clicked.connect(lambda: self.on_clicked())

    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
