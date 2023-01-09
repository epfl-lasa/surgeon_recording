# importing libraries
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QLabel, QPushButton
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import QTimer, Qt
import sys


class Window(QMainWindow):

	def __init__(self):
		super().__init__()

		# setting title
		self.setWindowTitle("Calibration Instructions")

		# setting geometry
		self.setGeometry(100, 100, 800, 700)

		# calling method
		self.UiComponents()

		# showing all the widgets
		self.show()

	# method for widgets
	def UiComponents(self):

		# counter
		self.count = 0
		self.flex_count = 0

		# creating flag
		self.flag = False

		# creating a label to show the time
		self.label = QLabel(self)
		# setting geometry of label
		self.label.setGeometry(75, 100, 250, 70)
		# adding border to the label
		self.label.setStyleSheet("border : 4px solid black;")
		# setting text to the label
		self.label.setText(str(self.count))
		# setting font to the label
		self.label.setFont(QFont('Arial', 25))
		# setting alignment to the text of label
		self.label.setAlignment(Qt.AlignCenter)

		# TODO : Make two labels to have a fiexed one with description and a changing one wiht timer
		# TODO : add label 'Next muscle?' 
		# TODO : add progresion bar ? self.pbar = QProgressBar(self), self.pbar.setValue(i)
		# creating a label to show the muscle name
		self.muscle_name = QLabel(self)
		# setting geometry of label
		self.muscle_name.setGeometry(50, 400, 500, 100)
		# setting text to the label
		self.muscle_name.setText("Muscle Name : Abductor Pollicis Brevis")
		# setting font to the label
		self.muscle_name.setFont(QFont('Arial', 12))
		# setting alignment to the text of label
		# self.muscle_name.setAlignment(Qt.AlignCenter)

		# creating a label to show the activation movement
		self.movement = QLabel(self)
		# setting geometry of label
		self.movement.setGeometry(50, 480, 500, 100)
		# setting text to the label
		self.movement.setText("Activation Movement: Thumb Abduction")
		# setting font to the label
		self.movement.setFont(QFont('Arial', 12))

		# creating a label to show the flex counter
		self.flex_counter = QLabel(self)
		# setting geometry of label
		self.flex_counter.setGeometry(50, 580, 500, 100)
		# setting text to the label
		self.flex_counter.setText("Flex counter : 0")
		# setting font to the label
		self.flex_counter.setFont(QFont('Arial', 12))

		# Add images of arm
		self.image = QLabel(self)
		self.pixmap = QPixmap('C:/Users/LASA/Pictures/arm.PNG')
		self.pixmap2 = QPixmap('C:/Users/LASA/Pictures/arm2.PNG')

		self.image.setPixmap(self.pixmap)
		# self.image.resize(self.pixmap.width(), self.pixmap.height())
		self.image.setGeometry(450, 50, self.pixmap.width(), self.pixmap.height())
		self.image.setAlignment(Qt.AlignCenter)

		# creating start button
		start = QPushButton("Start", self)
		# setting geometry to the button
		start.setGeometry(125, 250, 150, 40)
		# add action to the method
		start.pressed.connect(self.Start)

		# creating pause button
		pause = QPushButton("Pause", self)
		# setting geometry to the button
		pause.setGeometry(125, 300, 150, 40)
		# add action to the method
		pause.pressed.connect(self.Pause)

		# creating reset button
		re_set = QPushButton("Re-set", self)
		# setting geometry to the button
		re_set.setGeometry(125, 350, 150, 40)
		# add action to the method
		re_set.pressed.connect(self.Re_set)

		# creating a timer object
		timer = QTimer(self)
		# adding action to timer
		timer.timeout.connect(self.showTime)
		# update the timer every tenth second
		timer.start(100)

    

	# method called by timer, every 0.1 second
	def showTime(self):

		# checking if flag is true
		if self.flag:

			# incrementing the counter
			self.count+= 1

		# getting text from count
		text = str(self.count / 10)

		# showing text
		self.label.setText(text)

		# TODO : make as function here to switch 
		# image+ 
		# muscle name+ 
		# flex counter+ 
		# activation movement description 
		# 	depending on time 
		# TODO : improve count logic 
		if self.count%30 == 0 and self.count !=0:
			self.flex_count +=1
			self.flex_counter.setText("Flex counter : " +str(self.flex_count))
		
		if self.flex_count == 3:
			self.flex_count = 0 
			self.image.setPixmap(self.pixmap2)
			self.muscle_name.setText("Muscle Name : Flexor carpi Radialis")
			self.movement.setText("Acitvation Movement: Wrist Flexion")
			self.flex_counter.setText("Flex counter : " +str(self.flex_count))



	def Start(self):

		# making flag to true
		self.flag = True

	def Pause(self):

		# making flag to False
		self.flag = False

	def Re_set(self):

		# making flag to false
		self.flag = False

		# reseeting the count
		self.count = 0

		# setting text to label
		self.label.setText(str(self.count))


# create pyqt5 app
App = QApplication(sys.argv)

# create the instance of our Window
window = Window()

# start the app
sys.exit(App.exec())
