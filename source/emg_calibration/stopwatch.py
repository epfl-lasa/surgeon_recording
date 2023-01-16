# importing libraries
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QLabel, QPushButton
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import QTimer, Qt
import sys
import simpleaudio as sa
import os

class Window(QMainWindow):

	def __init__(self):
		super().__init__()

		# setting title
		self.setWindowTitle("Calibration Instructions")

		# setting geometry
		self.setGeometry(100, 100, 800, 700)

		# Set muscle dictionnaries 
		self.muscle_name_dict = ['Flexor Carpi Ulnaris/Radialis + Digitorum',
		'Abductor Pollicis Brevis',
        'Extensor Carpi Ulnaris/Radialis + Digitorum',
		'Abductor Pollicis longus and extensor pollicis brevis',
        ]

		self.activation_mvmt_dict = [
			'Palm up - Flex wrist up and push fingers up against assistant',
			'Palm up - Wrist flat, push thumb up against assistant',
			'Palm down - Extend wrist up and extend fingers up against assistant',
			'Palm down - Wrist flat, push thumb to the side agisnt assistant'
		]

		self.dict_index = 0

		# calling method
		self.UiComponents()

		# showing all the widgets
		self.show()

	# method for widgets
	def UiComponents(self):

		# Global status variables
		self.count = 50
		self.flex_count = 0
		self.current_status = 'Rest'
		self.current_arm = 'Right'

		# creating flag
		self.flag = False

		# creating a label to show the time
		self.label = QLabel(self)
		# setting geometry of label
		self.label.setGeometry(75, 150, 250, 70)
		# adding border to the label
		self.label.setStyleSheet("border : 4px solid black;")
		# setting text to the label
		self.label.setText(str(self.count))
		# setting font to the label
		self.label.setFont(QFont('Arial', 25))
		# setting alignment to the text of label
		self.label.setAlignment(Qt.AlignCenter)

		# TODO : Make two labels to have a fiexed one with description and a changing one wiht timer
		# TODO : add progresion bar ? self.pbar = QProgressBar(self), self.pbar.setValue(i)

		# creating a label to display current Action Status : Rest, activation 
		self.status = QLabel(self)
		# setting geometry of label
		self.status.setGeometry(75, 50, 250, 70)
		# adding border to the label
		self.status.setStyleSheet("border : 2px solid black; background-color: lightgreen")
		# setting text to the label
		self.status.setText("Rest")
		# setting font to the label
		self.status.setFont(QFont('Arial', 18))
		# setting alignment to the text of label
		self.status.setAlignment(Qt.AlignCenter)

		# creating a UP NEXT label
		self.up_next = QLabel(self)
		# setting geometry of label
		self.up_next.setGeometry(50, 425, 250, 50)
		# setting text to the label
		self.up_next.setText("Next Activation")
		# adding border to the label
		self.up_next.setStyleSheet("border : 1px solid black; background-color: lightblue")
		# setting font to the label
		self.up_next.setFont(QFont('Arial', 15))
		# setting alignment to the text of label
		self.up_next.setAlignment(Qt.AlignCenter)

		# creating a label to show the arm to activate
		self.arm_label = QLabel(self)
		# setting geometry of label
		self.arm_label.setGeometry(50, 475, 500, 30)
		# setting text to the label
		self.arm_label.setText("Arm : Right")
		# setting font to the label
		self.arm_label.setFont(QFont('Arial', 12))

		# creating a label to show the activation movement
		self.movement = QLabel(self)
		# setting geometry of label
		self.movement.setGeometry(50, 490, 1000, 125)
		# setting text to the label
		self.movement.setText("Activation Movement : \n\t"+ str(self.activation_mvmt_dict[self.dict_index]))
		# setting font to the label
		self.movement.setFont(QFont('Arial', 12))

		# creating a label to show the flex counter
		self.flex_counter = QLabel(self)
		# setting geometry of label
		self.flex_counter.setGeometry(50, 575, 500, 50)
		# setting text to the label
		self.flex_counter.setText("Flex counter : 0")
		# setting font to the label
		self.flex_counter.setFont(QFont('Arial', 12))

		# creating a label to show the muscle name
		self.muscle_name = QLabel(self)
		# setting geometry of label
		self.muscle_name.setGeometry(50, 590, 1000, 125)
		# setting text to the label
		self.muscle_name.setText("Muscle Names : \n\t" + str(self.muscle_name_dict[self.dict_index]))
		# setting font to the label
		self.muscle_name.setFont(QFont('Arial', 12))
		# setting alignment to the text of label
		# self.muscle_name.setAlignment(Qt.AlignCenter)

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
			self.count-= 1

		# getting text from count
		text = str(self.count / 10)

		# showing text
		self.label.setText(text)

		# Add beeps when close to 0
		if self.count == 30 or self.count == 20 or self.count == 10:
			self.beep('short')
		
		# Switch when reaching 0 
		if self.count == 0:
			self.beep('long')

			# Switch display for SAME muscle
			if self.current_status == 'Activation':
				
				# Reset counter
				self.count = 250 

				# Change current status
				self.current_status = 'Rest'
				self.status.setStyleSheet("border : 2px solid black; background-color: lightgreen")

				# Update arm (To other arm)
				if self.current_arm == 'Right':
					self.current_arm = 'Left'
				elif self.current_arm == 'Left':
					self.current_arm = 'Right'

				# Update flex counter
				self.flex_count +=1

			elif self.current_status == 'Rest':
				
				# Reset counter
				self.count = 50 
		
				# Change current Status
				self.current_status = 'Activation'
				self.status.setStyleSheet("border : 2px solid black; background-color: red")

			# Switch display for DIFFERENT muscle
			if self.flex_count == 4:
				
				# Reset flex count
				self.flex_count = 0

				# Set longer rest time (between different movements)
				self.count = 550

				# Update muscle naem and activation mvmt	
				self.dict_index +=1
				self.muscle_name.setText("Muscle Names : " + str(self.muscle_name_dict[self.dict_index]))
				self.movement.setText("Activation Movement : "+ str(self.activation_mvmt_dict[self.dict_index]))

				#TODO : update image (or gif-video )
				
				
			# Update display
			self.status.setText(str(self.current_status))
			self.arm_label.setText("Arm : " + str(self.current_arm))
			self.flex_counter.setText("Flex Counter : " + str(self.flex_count))


		# 	self.image.setPixmap(self.pixmap2)


	def beep(self, duration='short'):
		if duration == 'short':
			wave_obj = sa.WaveObject.from_wave_file('C:/Users/LASA/Documents/Recordings/surgeon_recording/source/emg_calibration/audio_files/beep-07a.wav')
			play_obj = wave_obj.play()
			# play_obj.wait_done()
		elif duration == 'long':
			wave_obj = sa.WaveObject.from_wave_file('C:/Users/LASA/Documents/Recordings/surgeon_recording/source/emg_calibration/audio_files/beep-04.wav')
			play_obj = wave_obj.play()
			# play_obj.wait_done()


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
