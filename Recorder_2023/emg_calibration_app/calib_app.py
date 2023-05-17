# importing libraries
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QLabel, QPushButton
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QFont, QPixmap, QMovie
from PyQt5.QtCore import QTimer, Qt
import sys
import simpleaudio as sa
import os
from sensor_handlers.emg_handler import EMGHandler

class Window(QMainWindow):

	def __init__(self, emg_handle):
		super().__init__()

		# setting title
		self.setWindowTitle("Calibration Instructions")

		# setting geometry
		self.setGeometry(100, 100, 900, 600)

		# Set emgHandler object
		self.emg_handle = emg_handle

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
			'Palm down - Wrist flat, push thumb to the side agaisnt assistant'
		]

		self.gif_path_dict = [
			os.path.join(os.path.dirname(os.path.abspath(__file__)), 'audio_video_files', 'Flexors_activation.gif'),
			os.path.join(os.path.dirname(os.path.abspath(__file__)), 'audio_video_files', 'Thumb_flexion.gif'),
			os.path.join(os.path.dirname(os.path.abspath(__file__)), 'audio_video_files', 'Extensors_activation.gif'),
			os.path.join(os.path.dirname(os.path.abspath(__file__)), 'audio_video_files', 'Thumb_extension.gif')
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
		self.label.setGeometry(500, 50, 250, 70)
		# adding border to the label
		self.label.setStyleSheet("border : 4px solid black;")
		# setting text to the label
		self.label.setText(str(self.count))
		# setting font to the label
		self.label.setFont(QFont('Arial', 25))
		# setting alignment to the text of label
		self.label.setAlignment(Qt.AlignCenter)

		# TODO : add progresion bar ? self.pbar = QProgressBar(self), self.pbar.setValue(i)

		# creating a label to display current Action Status : Rest, activation 
		self.status = QLabel(self)
		# setting geometry of label
		self.status.setGeometry(75, 40, 270, 90)
		# adding border to the label
		self.status.setStyleSheet("border : 2px solid black; background-color: lightgreen")
		# setting text to the label
		self.status.setText("Rest")
		# setting font to the label
		self.status.setFont(QFont('Arial', 18))
		# setting alignment to the text of label
		self.status.setAlignment(Qt.AlignCenter)

		# Vertical line for Aesthetic 
		self.vertical_line = QLabel(self)
		# setting geometry of label
		self.vertical_line.setGeometry(115, 370, 10, 205)
		# adding border to the label
		self.vertical_line.setStyleSheet("border : 1px solid black; background-color: lightblue")

		# creating a UP NEXT label
		self.up_next = QLabel(self)
		# setting geometry of label
		self.up_next.setGeometry(100, 325, 230, 50)
		# setting text to the label
		self.up_next.setText("Next Activation :")
		# adding border to the label
		self.up_next.setStyleSheet("border : 1px solid black; background-color: lightblue")
		# setting font to the label
		self.up_next.setFont(QFont('Arial', 15))
		# setting alignment to the text of label
		self.up_next.setAlignment(Qt.AlignCenter)

		# creating a label to show the arm to activate
		self.arm_label = QLabel(self)
		# setting geometry of label
		self.arm_label.setGeometry(135, 385, 500, 25)
		# setting text to the label
		self.arm_label.setText("Arm : Right")
		# setting font to the label
		self.arm_label.setFont(QFont('Arial', 12))

		# creating a label to show the flex counter
		self.flex_counter = QLabel(self)
		# setting geometry of label
		self.flex_counter.setGeometry(135, 420, 500, 25)
		# setting text to the label
		self.flex_counter.setText("Activation # : 1/4")
		# setting font to the label
		self.flex_counter.setFont(QFont('Arial', 12))

		# creating a label to show the activation movement
		self.movement = QLabel(self)
		# setting geometry of label
		self.movement.setGeometry(135, 460, 1000, 50)
		# setting text to the label
		self.movement.setText("Activation Movement : \n\t"+ str(self.activation_mvmt_dict[self.dict_index]))
		# setting font to the label
		self.movement.setFont(QFont('Arial', 12))

		# creating a label to show the muscle name
		self.muscle_name = QLabel(self)
		# setting geometry of label
		self.muscle_name.setGeometry(135, 520, 1000, 50)
		# setting text to the label
		self.muscle_name.setText("Muscle Names : \n\t" + str(self.muscle_name_dict[self.dict_index]))
		# setting font to the label
		self.muscle_name.setFont(QFont('Arial', 12))
		# setting alignment to the text of label
		# self.muscle_name.setAlignment(Qt.AlignCenter)

		# Add gifs of aactivation movement
		self.image = QLabel(self)
		self.movie = QMovie(self.gif_path_dict[self.dict_index])
		self.image.setMovie(self.movie)
		self.movie.start()
		self.image.setGeometry(400, 175, self.movie.currentImage().size().width(), self.movie.currentImage().size().height())
		self.image.setAlignment(Qt.AlignCenter)

		# creating start button
		start = QPushButton("Start", self)
		# setting geometry to the button
		start.setGeometry(135, 150, 150, 40)
		# add action to the method
		start.pressed.connect(self.Start)

		# creating pause button
		pause = QPushButton("Pause", self)
		# setting geometry to the button
		pause.setGeometry(135, 200, 150, 40)
		# add action to the method
		pause.pressed.connect(self.Pause)

		# creating reset button
		advance = QPushButton("Advance", self)
		# setting geometry to the button
		advance.setGeometry(135, 250, 150, 40)
		# add action to the method
		advance.pressed.connect(self.Advance)

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
			if self.current_status == 'Activate':
				
				# Reset counter
				self.count = 250 

				# Change current status
				self.current_status = 'Rest'
				self.status.setStyleSheet("border : 2px solid black; background-color: lightgreen")

				# Change 'Next Activation'
				self.up_next.setText("Next Activation :")

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
				self.current_status = 'Activate'
				self.status.setStyleSheet("border : 2px solid black; background-color: red")

				# Change 'Next Activation'
				self.up_next.setText("Current Activation :")

				# Reset gif
				self.movie.jumpToFrame(0)

			# Switch display for DIFFERENT muscle
			if self.flex_count == 4:
				
				# Reset flex count
				self.flex_count = 0

				# Set longer rest time (between different movements)
				self.count = 550

				# Update muscle name and activation mvmt	
				self.dict_index +=1
				if self.dict_index < len(self.muscle_name_dict):
					self.muscle_name.setText("Muscle Names : \n\t" + str(self.muscle_name_dict[self.dict_index]))
					self.movement.setText("Activation Movement : \n\t"+ str(self.activation_mvmt_dict[self.dict_index]))
					self.movie = QMovie(self.gif_path_dict[self.dict_index])
					self.image.setMovie(self.movie)
					self.movie.start()
				else:
					# FINISHED
					self.count = 0
					self.Pause()
					self.current_status = "FINSIHED"
					self.status.setStyleSheet("border : 2px solid black; background-color: blue")
					self.movie.stop()				
				
			# Update display
			self.status.setText(str(self.current_status))
			self.arm_label.setText("Arm : " + str(self.current_arm))
			self.flex_counter.setText("Activation # : " + str(self.flex_count+1)+"/4")



		# 	self.image.setPixmap(self.pixmap2)


	def beep(self, duration='short'):
		if duration == 'short':
			wave_obj = sa.WaveObject.from_wave_file(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'audio_video_files', 'beep-07a.wav'))
			play_obj = wave_obj.play()
			# play_obj.wait_done()
		elif duration == 'long':
			wave_obj = sa.WaveObject.from_wave_file(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'audio_video_files', 'beep-04.wav'))
			play_obj = wave_obj.play()
			# play_obj.wait_done()


	def Start(self):

		# Start recording duration for calib
		self.emg_handle.update_start_time()

		# making flag to true
		self.flag = True

	def Pause(self):

		# making flag to False
		self.flag = False

	def Advance(self):

		# making flag to false
		self.flag = False

		# resetting the counts
		self.count = 0

		# setting text to label
		self.label.setText(str(self.count))
	
	def closeEvent(self, *args):
		self.emg_handle.shutdown_emg()


def openApp(emg_handle):
	# create pyqt5 app
	App = QApplication(sys.argv)

	# create the instance of our Window
	window = Window(emg_handle)
	
	# Display window on foreground
	window.activateWindow()

	# start the app
	# sys.exit(App.exec())
	App.exec()


if __name__ == '__main__':
	emg_handle = EMGHandler(os.path.join(os.getcwd(), 'emg_calib_duration.csv'))
	openApp(emg_handle)