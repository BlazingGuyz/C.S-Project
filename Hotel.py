# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QPoint
from PyQt5.QtCore import QThread,pyqtSignal
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt
import ctypes
import playsound
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QWidget
import mysql.connector
import cv2
import random
import numpy as np

PASSWORD="toor"
PORT=19488

NotificationThread=0
NewNotificationCont=""
NewCheckInDate=""
NewCheckOutDate=""
PicName=""
mydb = mysql.connector.connect(		#This one is for the regular Data sending and Receiving 
  host="0.tcp.in.ngrok.io",
  user="root",
  passwd=PASSWORD,
  database="hotelkvs",
  port=PORT
  )
mycursor=mydb.cursor(buffered=True)

mydbnotif = mysql.connector.connect(	#This one is specifically for Notification Loop to avoid traffic.
			host="0.tcp.in.ngrok.io",
  			user="root",
  			passwd=PASSWORD,
  			database="hotelkvs",
  			port=PORT
  			)
mycursornotif=mydbnotif.cursor(buffered=True)
RoomTypeDict={101:"Deluxe Room",102:"Deluxe Room",103:"Deluxe Room",104:"Deluxe Room",201:"Super Deluxe Room",202:"Super Deluxe Room",203:"Super Deluxe Room",301:"Suite",302:"Suite",303:"Suite"}
roomAvailable=[101,102,103,104,201,202,203,301,302,303]

#class EmailSendThread(QThread):
#	sentMail=pyqtSignal(int)
#	import email, smtplib, ssl
#	
#	from email import encoders
#	from email.mime.base import MIMEBase
#	from email.mime.multipart import MIMEMultipart
#	from email.mime.text import MIMEText
#	
#	subject = "An email with attachment from Python"
#	body = "This is an email with attachment sent from Python"
#	sender_email = "my@gmail.com"
#	receiver_email = "your@gmail.com"
#	password = input("Type your password and press enter:")
#	
#	# Create a multipart message and set headers
#	message = MIMEMultipart()
#	message["From"] = sender_email
#	message["To"] = receiver_email
#	message["Subject"] = subject
#	message["Bcc"] = receiver_email  # Recommended for mass emails
#	
#	# Add body to email
#	message.attach(MIMEText(body, "plain"))
#	
#	filename = "document.pdf"  # In same directory as script
#	
#	# Open PDF file in binary mode
#	with open(filename, "rb") as attachment:
#	    # Add file as application/octet-stream
#	    # Email client can usually download this automatically as attachment
#	    part = MIMEBase("application", "octet-stream")
#	    part.set_payload(attachment.read())
#	
#	# Encode file in ASCII characters to send by email    
#	encoders.encode_base64(part)
#	
#	# Add header as key/value pair to attachment part
#	part.add_header(
#	    "Content-Disposition",
#	    f"attachment; filename= {filename}",
#	)
#	
#	# Add attachment to message and convert message to string
#	message.attach(part)
#	text = message.as_string()
#	
#	# Log in to server using secure context and send email
#	context = ssl.create_default_context()
#	with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
#	    server.login(sender_email, password)
#	    server.sendmail(sender_email, receiver_email, text)
#	
class getAvailableRoomsThread(QThread):
	fetchedAvailablerooms=pyqtSignal(int)
	def run(self):
		global roomAvailable
		roomAvailable=[]
		mycursor.execute('select RoomNo from Room where RoomStatus="unoccupied";')
		for rooms in mycursor.fetchall():
			roomAvailable.append(rooms[0])
		#print(roomAvailable)
		self.fetchedAvailablerooms.emit(1)

class NotificationCheckThread(QThread):#Add to Autorun on execution
	NewNotification=pyqtSignal(int)
	def run(self):
		print("Running Me!")
		mydbnotif = mysql.connector.connect(	#This one is specifically for Notification Loop to avoid traffic.
			host="0.tcp.in.ngrok.io",
  			user="root",
  			passwd=PASSWORD,
  			database="hotelkvs",
  			port=PORT
  			)
		mycursornotif=mydbnotif.cursor(buffered=True)
		global NewNotificationCont
		NewNotificationNumber=0
		OldNotificationNumber=0
		mycursornotif.execute("select COUNT(*) from Notify")
		OldNotificationNumber=mycursornotif.fetchone()[0]
		while True:
			mydbnotif.reset_session()
			mycursornotif.execute("select COUNT(*) from Notify")
			NewNotificationNumber=mycursornotif.fetchone()[0]
			if NewNotificationNumber!=OldNotificationNumber:
				mycursornotif.execute("select * from Notify")
				NewNotificationCont=mycursornotif.fetchall()
				self.NewNotification.emit(1)
				playsound.playsound("sound/NotifSound.mp3")
				OldNotificationNumber=NewNotificationNumber
			else:
				pass
			
class addtoBillThread(QThread):
	addedtoBillThread=pyqtSignal(int)
	def run(self):
		global SelRoomNo,AddtoBillAmount,AddtoBillChargedfor,AddtoBillDate
		mycursor.execute("insert into R%s values('%s',%s,'%s',NULL);"%(SelRoomNo,AddtoBillChargedfor,AddtoBillAmount,AddtoBillDate))
		mydb.commit()
		self.addedtoBillThread.emit(1)

class getGuestBillInfo(QThread):
	gotBillingInfo=pyqtSignal(int)
	def run(self):
		global fetchedBillingData,SelRoomNo
		mycursor.execute("select Date,Chargedfor,Amount from R%s;"%SelRoomNo)
		fetchedBillingData=mycursor.fetchall()
		self.gotBillingInfo.emit(1)

class ModifyCheckInThread(QThread):
	ModifiedCheckIn=pyqtSignal(int)
	def run(self):
		global SelRoomNo,NewCheckInDate
		mycursor.execute("select Date,Time from GData where Room='%s'"%SelRoomNo)
		LocalNewCheckInDate=NewCheckInDate
		data=mycursor.fetchone()
		Date=data[0]
		Time=data[1]
		Date=Date.split(".")
		Time=Time.split(".")
		#print(NewCheckInDate)
		NewCheckInDate=NewCheckInDate.split(" ")
		#print(NewCheckInDate)
		Date=Date[1]+"."+NewCheckInDate[0]
		Time=Time[1]+"."+NewCheckInDate[1]
		#print("Time:",Time,"Date:",Date)
		mycursor.execute("update GData set Time='%s',Date='%s' Where Room='%s'"%(Time,Date,SelRoomNo))
		mydb.commit()
		NewCheckInDate=LocalNewCheckInDate
		self.ModifiedCheckIn.emit(1)

class ModifyCheckOutThread(QThread):
	ModifiedCheckOut=pyqtSignal(int)
	def run(self):
		global SelRoomNo,NewCheckOutDate
		mycursor.execute("select Date,Time from GData where Room='%s'"%SelRoomNo)
		LocalNewCheckOutDate=NewCheckOutDate
		data=mycursor.fetchone()
		Date=data[0]
		Time=data[1]
		Date=Date.split(".")
		Time=Time.split(".")
		#print(NewCheckOutDate)
		NewCheckOutDate=NewCheckOutDate.split(" ")
		#print(NewCheckOutDate)
		Date=Date[0]+"."+NewCheckOutDate[0]
		Time=Time[0]+"."+NewCheckOutDate[1]
		#print("Time:",Time,"Date:",Date)
		mycursor.execute("update GData set Time='%s',Date='%s' Where Room='%s'"%(Time,Date,SelRoomNo))
		mydb.commit()
		NewCheckOutDate=LocalNewCheckOutDate
		self.ModifiedCheckOut.emit(1)

class getGuestInfo(QThread):
	fetchedGuestInfo=pyqtSignal(int)
	def run(self):
		global d1,d2,d3,d6,d7,SelRoomNo
		mycursor.execute("select Serialno,Details,Date,Time,Email,Phoneno from GData Where Room='%s';"%SelRoomNo)
		data=mycursor.fetchall()#(Serialno,Details,Date,Time,Email,Phoneno,Room)
		if data!=[]:
			data=data[0]
			d1=data[1]#Name
			tempdate=data[2]
			d2=tempdate.split('.')[0]#Check-In Date
			d3=tempdate.split('.')[1]#Check-Out Date
			temptime=data[3]
			d4=temptime.split('.')[0]#Check-In Time
			d5=temptime.split('.')[1]#Check-Out Time
			d2=d2+" "+d4
			d3=d3+" "+d5
			d6=data[4]#EmailID
			d7=data[5]#Phoneno
		else:
			d1="Unoccupied"
			d2="Unoccupied"
			d3="Unoccupied"
			d6="Unoccupied"
			d7="Unoccupied"
		self.fetchedGuestInfo.emit(1)

class IDScanThread(QThread):
	ScanComplete=pyqtSignal(int)
	def run(self):
		global PicName
		video = cv2.VideoCapture(0) 
		while True:
			__,frame = video.read()
			frame=cv2.flip(frame,1)
			cv2.imshow("Scanning",frame)
			key = cv2.waitKey(1)
			if key == ord('c'):
				break
		video.release()
		cv2.destroyAllWindows()
		frame=cv2.flip(frame,1)
		r = cv2.selectROI(frame)
		try:
			imCrop = frame[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]
			cv2.imshow("Scanned Image", imCrop)
			cv2.waitKey()
			PicName=str(random.randint(1100,111110))+".jpg"
			cv2.imwrite(PicName , imCrop)
			cv2.destroyAllWindows()
			self.ScanComplete.emit(1)
		except:
			ctypes.windll.user32.MessageBoxW(0, "Scan Cancelled!", "Scan error", 0)

class RegistrationThread(QThread):
	QueryComplete=pyqtSignal(int)
	def run(self):
		global x1,x2,x3,x4,x5,x6,x7,room
		with open('SerialNo.txt', 'r') as file:
			for i in file.readlines():
				y=int(i)
		mycursor.execute("insert into GData values(%s,%s,%s,%s,%s,%s,%s,%s,NULL)",(y,x1,x2,x3,x4,x5,x6,room))
		dict={101:2000,102:2000,103:2000,104:2000,201:2500,202:2500,203:2500,301:3750,302:3750,303:3750}
		#mycursor.execute("insert into R%s(Details,Date,Time,Email,Serialno,Phoneno) select Details,Date,Time,Email,Serialno,Phoneno from GData;"%room)
		amount=dict[int(room)]
		mycursor.execute("insert into R%s values('Accommodation',%s,'%s',NULL)"%(room,amount,x7))
		mycursor.execute("update Room set RoomStatus='occupied' where RoomNo=%s;"%room)
		mydb.commit()
		with open('SerialNo.txt','a') as file:#fix this part remove this and add DB serial No
			p=y+1#fix this part remove this and add DB serial No
			file.write("\n")#fix this part remove this and add DB serial No
			file.write("%s"%p)	#fix this part remove this and add DB serial No
		self.QueryComplete.emit(1)#fix this part remove this and add DB serial No



class Ui_MainWindow(QWidget):
	def setupUi(self, MainWindow):
		MainWindow.setObjectName("MainWindow")
		MainWindow.resize(830, 635)
		MainWindow.setWindowIcon(QtGui.QIcon("icons/LogoHead.png"))
		MainWindow.setMinimumSize(QtCore.QSize(830, 635))
		MainWindow.setMaximumSize(QtCore.QSize(830, 635))
		MainWindow.setStyleSheet("QMainWindow {background: transparent; }\n"
"QToolTip {\n"
"    color: #ffffff;\n"
"    background-color: rgba(27, 29, 35, 160);\n"
"    border: 1px solid rgb(40, 40, 40);\n"
"    border-radius: 2px;\n"
"}")
		MainWindow.setTabShape(QtWidgets.QTabWidget.Rounded)
		MainWindow.setUnifiedTitleAndToolBarOnMac(False)
		self.centralwidget = QtWidgets.QWidget(MainWindow)
		self.centralwidget.setObjectName("centralwidget")
		self.RegistrationPage = QtWidgets.QWidget(self.centralwidget)
		self.RegistrationPage.setGeometry(QtCore.QRect(0, 90, 831, 571))
		palette = QtGui.QPalette()
		brush = QtGui.QBrush(QtGui.QColor(39, 44, 54))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(39, 44, 54))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(39, 44, 54))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(39, 44, 54))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(39, 44, 54))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(39, 44, 54))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(39, 44, 54))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(39, 44, 54))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(39, 44, 54))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
		self.RegistrationPage.setPalette(palette)
		self.RegistrationPage.setStyleSheet("background-color: rgb(39, 44, 54);")
		self.RegistrationPage.setObjectName("RegistrationPage")
		self.SubRegistrationPage = QtWidgets.QWidget(self.RegistrationPage)
		self.SubRegistrationPage.setGeometry(QtCore.QRect(50, 10, 731, 501))
		self.SubRegistrationPage.setStyleSheet("border:1px solid;\n"
"border-color:transparent;\n"
"border-radius:15px;\n"
"background-color:rgba(86, 91, 100, 190);")

		self.SubRegistrationPage.setObjectName("SubRegistrationPage")
		self.GuestName = QtWidgets.QLineEdit(self.SubRegistrationPage)
		self.GuestName.setGeometry(QtCore.QRect(50, 120, 421, 31))
		palette = QtGui.QPalette()
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 180))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 180))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 180))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(98, 98, 98))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.PlaceholderText, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 180))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 180))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 180))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(98, 98, 98))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.PlaceholderText, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 180))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 180))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 180))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(98, 98, 98))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.PlaceholderText, brush)
		self.GuestName.setPalette(palette)
		self.GuestName.setStyleSheet("QLineEdit {\n"
"    background-color: rgba(27, 29, 35,180);\n"
"    border-radius: 5px;\n"
"    border: 2px solid rgb(27, 29, 35);\n"
"    padding-left: 10px;\n"
"}\n"
"QLineEdit:hover {\n"
"    border: 2px solid rgb(64, 71, 88);\n"
"}\n"
"QLineEdit:focus {\n"
"    border: 2px solid rgb(91, 101, 124);\n"
"}")
		self.GuestName.setText("")
		self.GuestName.setObjectName("GuestName")
		self.GuestPhoneNo = QtWidgets.QLineEdit(self.SubRegistrationPage)
		self.GuestPhoneNo.setGeometry(QtCore.QRect(50, 170, 131, 31))
		palette = QtGui.QPalette()
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 180))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 180))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 180))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(98, 98, 98))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.PlaceholderText, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 180))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 180))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 180))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(98, 98, 98))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.PlaceholderText, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 180))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 180))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 180))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(98, 98, 98))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.PlaceholderText, brush)
		self.GuestPhoneNo.setPalette(palette)
		self.GuestPhoneNo.setStyleSheet("QLineEdit {\n"
"    background-color: rgba(27, 29, 35,180);\n"
"    border-radius: 5px;\n"
"    border: 2px solid rgb(27, 29, 35);\n"
"    padding-left: 10px;\n"
"}\n"
"QLineEdit:hover {\n"
"    border: 2px solid rgb(64, 71, 88);\n"
"}\n"
"QLineEdit:focus {\n"
"    border: 2px solid rgb(91, 101, 124);\n"
"}")
		self.GuestPhoneNo.setText("")
		self.GuestPhoneNo.setObjectName("GuestPhoneNo")
		self.GuestEmailID = QtWidgets.QLineEdit(self.SubRegistrationPage)
		self.GuestEmailID.setGeometry(QtCore.QRect(210, 170, 261, 31))
		palette = QtGui.QPalette()
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 180))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 180))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 180))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(98, 98, 98))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.PlaceholderText, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 180))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 180))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 180))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(98, 98, 98))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.PlaceholderText, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 180))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 180))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 180))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(98, 98, 98))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.PlaceholderText, brush)
		self.GuestEmailID.setPalette(palette)
		self.GuestEmailID.setStyleSheet("QLineEdit {\n"
"    background-color: rgba(27, 29, 35,180);\n"
"    border-radius: 5px;\n"
"    border: 2px solid rgb(27, 29, 35);\n"
"    padding-left: 10px;\n"
"}\n"
"QLineEdit:hover {\n"
"    border: 2px solid rgb(64, 71, 88);\n"
"}\n"
"QLineEdit:focus {\n"
"    border: 2px solid rgb(91, 101, 124);\n"
"}")
		self.GuestEmailID.setText("")
		self.GuestEmailID.setObjectName("GuestEmailID")
		self.RoomType = QtWidgets.QComboBox(self.SubRegistrationPage)
		self.RoomType.setGeometry(QtCore.QRect(50, 240, 171, 22))
		self.RoomType.setStyleSheet("QComboBox {\n"
"    background-color: rgba(27, 29, 35,180);\n"
"    border-radius: 5px;\n"
"    border: 2px solid rgb(27, 29, 35);\n"
"    padding-left: 10px;\n"
"    color:rgb(158, 158, 179);\n"
"}\n"
"QComboBox:hover {\n"
"    border: 2px solid rgb(64, 71, 88);\n"
"}\n"
"QComboBox:focus {\n"
"    border: 2px solid rgb(91, 101, 124);\n"
"}\n"
"QComboBox QListView{\n"
"	border:1px solid;\n"
"	border-radius:0px;\n"
"}")
		self.RoomType.setObjectName("RoomType")
		self.CheckInLab = QtWidgets.QLabel(self.SubRegistrationPage)
		self.CheckInLab.setGeometry(QtCore.QRect(50, 280, 61, 31))
		palette = QtGui.QPalette()
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(213, 213, 213))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.HighlightedText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.PlaceholderText, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(213, 213, 213))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.HighlightedText, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210, 128))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.PlaceholderText, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(213, 213, 213))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.HighlightedText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.PlaceholderText, brush)
		self.CheckInLab.setPalette(palette)
		font = QtGui.QFont()
		font.setPointSize(10)
		self.CheckInLab.setFont(font)
		self.CheckInLab.setStyleSheet("background-color:transparent;")
		self.CheckInLab.setObjectName("CheckInLab")
		self.CheckOutLab = QtWidgets.QLabel(self.SubRegistrationPage)
		self.CheckOutLab.setGeometry(QtCore.QRect(280, 280, 71, 31))
		palette = QtGui.QPalette()
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(98, 98, 98))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.PlaceholderText, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(98, 98, 98))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.PlaceholderText, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(98, 98, 98))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.PlaceholderText, brush)
		self.CheckOutLab.setPalette(palette)
		font = QtGui.QFont()
		font.setPointSize(10)
		self.CheckOutLab.setFont(font)
		self.CheckOutLab.setStyleSheet("background-color:transparent;")
		self.CheckOutLab.setObjectName("CheckOutLab")
		self.CheckOut = QtWidgets.QDateTimeEdit(self.SubRegistrationPage)
		self.CheckOut.setGeometry(QtCore.QRect(280, 310, 194, 22))
		palette = QtGui.QPalette()
		brush = QtGui.QBrush(QtGui.QColor(182, 182, 182))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 180))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(182, 182, 182))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(182, 182, 182))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
		brush.setStyle(QtCore.Qt.NoBrush)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 180))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(97, 97, 97))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.HighlightedText, brush)
		brush = QtGui.QBrush(QtGui.QColor(98, 98, 98))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.PlaceholderText, brush)
		brush = QtGui.QBrush(QtGui.QColor(182, 182, 182))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 180))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(182, 182, 182))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(182, 182, 182))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
		brush.setStyle(QtCore.Qt.NoBrush)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 180))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(97, 97, 97))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.HighlightedText, brush)
		brush = QtGui.QBrush(QtGui.QColor(98, 98, 98))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.PlaceholderText, brush)
		brush = QtGui.QBrush(QtGui.QColor(182, 182, 182))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 180))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(182, 182, 182))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(182, 182, 182))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
		brush.setStyle(QtCore.Qt.NoBrush)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 180))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(97, 97, 97))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.HighlightedText, brush)
		brush = QtGui.QBrush(QtGui.QColor(98, 98, 98))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.PlaceholderText, brush)
		self.CheckOut.setPalette(palette)
		self.CheckOut.setStyleSheet("QDateTimeEdit {\n"
"    background-color: rgba(27, 29, 35,180);\n"
"    border-radius: 5px;\n"
"    border: 2px solid rgb(27, 29, 35);\n"
"    color:rgb(182, 182, 182);\n"
"    padding-left: 10px;\n"
"}\n"
"QDateTimeEdit:hover {\n"
"    border: 2px solid rgb(64, 71, 88);\n"
"}\n"
"QDateTimeEdit:focus {\n"
"    border: 2px solid rgb(91, 101, 124);\n"
"    color:rgb(182, 182, 182)\n"
"}\n"
"QCalendarWidget QWidget{\n"
"background-color: rgb(39, 44, 54);\n"
"\n"
"border-radius:0px;\n"
"color:rgb(181, 181, 195)\n"
"}\n"
"\n"
"QCalendarWidget QWidget:hover {\n"
"    border: 2px solid rgb(64, 71, 88);\n"
"}\n"
"QCalendarWidget QToolButton{\n"
"color:rgb(181, 181, 195);\n"
"border:1px solid rgb(27, 29, 35);\n"
"border-bottom:0px;\n"
"border-radius:0px;\n"
"icon-size: 30px;\n"
"}\n"
"\n"
"QCalendarWidget QMenu{\n"
"background-color: rgb(39, 44, 54);\n"
"border:1px solid;\n"
"color:rgb(181, 181, 195)\n"
"\n"
"}\n"
"\n"
"QCalendarWidget QAbstractItemView:enabled{\n"
"background-color: rgb(39, 44, 54);\n"
"color:rgb(108, 108, 108);\n"
"}\n"
"\n"
"\n"
"QCalendarWidget QAbstractItemView:disabled{\n"
"background-color: rgb(39, 44, 54);\n"
"color: rgb(182, 182, 197);\n"
"}\n"
"\n"
"QCalendarWidget QSpinBox{\n"
"    background-color: rgb(39, 44, 54);\n"
"}")
		self.CheckOut.setButtonSymbols(QtWidgets.QAbstractSpinBox.UpDownArrows)
		self.CheckOut.setProperty("showGroupSeparator", False)
		self.CheckOut.setDate(QtCore.QDate(2020, 1, 1))
		self.CheckOut.setMinimumDate(QtCore.QDate(2020, 1, 1))
		self.CheckOut.setCalendarPopup(True)
		self.CheckOut.setObjectName("CheckOut")
		self.CheckIn = QtWidgets.QDateTimeEdit(self.SubRegistrationPage)
		self.CheckIn.setGeometry(QtCore.QRect(50, 310, 194, 22))
		palette = QtGui.QPalette()
		brush = QtGui.QBrush(QtGui.QColor(182, 182, 182))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 180))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(182, 182, 182))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.BrightText, brush)
		brush = QtGui.QBrush(QtGui.QColor(182, 182, 182))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
		brush.setStyle(QtCore.Qt.NoBrush)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 180))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(213, 213, 213))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.HighlightedText, brush)
		brush = QtGui.QBrush(QtGui.QColor(98, 98, 98))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.PlaceholderText, brush)
		brush = QtGui.QBrush(QtGui.QColor(182, 182, 182))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 180))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(182, 182, 182))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.BrightText, brush)
		brush = QtGui.QBrush(QtGui.QColor(182, 182, 182))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
		brush.setStyle(QtCore.Qt.NoBrush)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 180))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(213, 213, 213))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.HighlightedText, brush)
		brush = QtGui.QBrush(QtGui.QColor(98, 98, 98))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.PlaceholderText, brush)
		brush = QtGui.QBrush(QtGui.QColor(182, 182, 182))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 180))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(182, 182, 182))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.BrightText, brush)
		brush = QtGui.QBrush(QtGui.QColor(182, 182, 182))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
		brush.setStyle(QtCore.Qt.NoBrush)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 180))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(213, 213, 213))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.HighlightedText, brush)
		brush = QtGui.QBrush(QtGui.QColor(98, 98, 98))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.PlaceholderText, brush)
		self.CheckIn.setPalette(palette)
		self.CheckIn.setStyleSheet("QDateTimeEdit {\n"
"    background-color: rgba(27, 29, 35,180);\n"
"    border-radius: 5px;\n"
"    border: 2px solid rgb(27, 29, 35);\n"
"    color:rgb(182, 182, 182);\n"
"    padding-left: 10px;\n"
"}\n"
"QDateTimeEdit:hover {\n"
"    border: 2px solid rgb(64, 71, 88);\n"
"}\n"
"QDateTimeEdit:focus {\n"
"    border: 2px solid rgb(91, 101, 124);\n"
"    color:rgb(182, 182, 182)\n"
"}\n"
"QCalendarWidget QWidget{\n"
"background-color: rgb(39, 44, 54);\n"
"\n"
"border-radius:0px;\n"
"color:rgb(181, 181, 195)\n"
"}\n"
"\n"
"QCalendarWidget QWidget:hover {\n"
"    border: 2px solid rgb(64, 71, 88);\n"
"}\n"
"QCalendarWidget QToolButton{\n"
"color:rgb(181, 181, 195);\n"
"border:1px solid rgb(27, 29, 35);\n"
"border-bottom:0px;\n"
"border-radius:0px;\n"
"icon-size: 30px;\n"
"}\n"
"\n"
"QCalendarWidget QMenu{\n"
"background-color: rgb(39, 44, 54);\n"
"border:1px solid;\n"
"color:rgb(181, 181, 195)\n"
"\n"
"}\n"
"\n"
"QCalendarWidget QAbstractItemView:enabled{\n"
"background-color: rgb(39, 44, 54);\n"
"color:rgb(108, 108, 108);\n"
"}\n"
"\n"
"\n"
"QCalendarWidget QAbstractItemView:disabled{\n"
"background-color: rgb(39, 44, 54);\n"
"color: rgb(182, 182, 197);\n"
"}\n"
"\n"
"QCalendarWidget QSpinBox{\n"
"    background-color: rgb(39, 44, 54);\n"
"}")
		self.CheckIn.setButtonSymbols(QtWidgets.QAbstractSpinBox.UpDownArrows)
		self.CheckIn.setDate(QtCore.QDate(2020, 1, 1))
		self.CheckIn.setMinimumDateTime(QtCore.QDateTime(QtCore.QDate(2020, 1, 1), QtCore.QTime(0, 0, 0)))
		self.CheckIn.setCalendarPopup(True)
		self.CheckIn.setObjectName("CheckIn")
		self.RoomNumber = QtWidgets.QComboBox(self.SubRegistrationPage)
		self.RoomNumber.setGeometry(QtCore.QRect(278, 240, 171, 22))
		self.RoomNumber.setStyleSheet("QComboBox {\n"
"    background-color: rgba(27, 29, 35,180);\n"
"    border-radius: 5px;\n"
"    border: 2px solid rgb(27, 29, 35);\n"
"    padding-left: 10px;\n"
"    color:rgb(158, 158, 179);\n"
"}\n"
"QComboBox:hover {\n"
"    border: 2px solid rgb(64, 71, 88);\n"
"}\n"
"QComboBox:focus {\n"
"    border: 2px solid rgb(91, 101, 124);\n"
"}\n"
"QComboBox QListView{\n"
"	border:1px solid;\n"
"	border-radius:0px;\n"
"}")
		self.RoomNumber.setObjectName("RoomNumber")
		self.RegistrationDiv1 = QtWidgets.QFrame(self.SubRegistrationPage)
		self.RegistrationDiv1.setGeometry(QtCore.QRect(0, 72, 731, 3))
		self.RegistrationDiv1.setFrameShape(QtWidgets.QFrame.HLine)
		self.RegistrationDiv1.setFrameShadow(QtWidgets.QFrame.Sunken)
		self.RegistrationDiv1.setObjectName("RegistrationDiv1")
		self.RegistrationDiv2 = QtWidgets.QFrame(self.SubRegistrationPage)
		self.RegistrationDiv2.setGeometry(QtCore.QRect(483, 90, 4, 391))
		self.RegistrationDiv2.setFrameShape(QtWidgets.QFrame.VLine)
		self.RegistrationDiv2.setFrameShadow(QtWidgets.QFrame.Sunken)
		self.RegistrationDiv2.setObjectName("RegistrationDiv2")
		self.Book = QtWidgets.QPushButton(self.SubRegistrationPage)
		self.Book.setGeometry(QtCore.QRect(60, 430, 121, 41))
		palette = QtGui.QPalette()
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.PlaceholderText, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210, 128))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.PlaceholderText, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.PlaceholderText, brush)
		self.Book.setPalette(palette)
		self.Book.setStyleSheet("QPushButton {\n"
"    border: 2px solid rgb(52, 59, 72);\n"
"    border-radius: 5px;    \n"
"    background-color: rgb(52, 59, 72);\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: rgb(57, 65, 80);\n"
"    border: 2px solid rgb(61, 70, 86);\n"
"}\n"
"QPushButton:pressed {    \n"
"    background-color: rgb(35, 40, 49);\n"
"    border: 2px solid rgb(43, 50, 61);\n"
"}")
		icon = QtGui.QIcon()
		icon.addPixmap(QtGui.QPixmap("icons/cil-book.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.Book.setIcon(icon)
		self.Book.setIconSize(QtCore.QSize(30, 30))
		self.Book.setObjectName("Book")
		self.IDScan = QtWidgets.QPushButton(self.SubRegistrationPage)
		self.IDScan.setGeometry(QtCore.QRect(60, 360, 121, 41))
		self.IDScan.setPalette(palette)
		self.IDScan.setStyleSheet("QPushButton {\n"
"    border: 2px solid rgb(52, 59, 72);\n"
"    border-radius: 5px;    \n"
"    background-color: rgb(52, 59, 72);\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: rgb(57, 65, 80);\n"
"    border: 2px solid rgb(61, 70, 86);\n"
"}\n"
"QPushButton:pressed {    \n"
"    background-color: rgb(35, 40, 49);\n"
"    border: 2px solid rgb(43, 50, 61);\n"
"}")
		icon1 = QtGui.QIcon()
		icon1.addPixmap(QtGui.QPixmap("icons/cil-scanning.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.IDScan.setIcon(icon1)
		self.IDScan.setIconSize(QtCore.QSize(30, 30))
		self.IDScan.setObjectName("IDScan")
		self.IDPreview = QtWidgets.QLabel(self.SubRegistrationPage)
		self.IDPreview.setGeometry(QtCore.QRect(500, 120, 221, 141))
		self.IDPreview.setStyleSheet("background-color:transparent;\n"
"border:transparent;\n"
"border-radius:0px;")
		self.IDPreview.setText("")
		self.IDPreview.setPixmap(QtGui.QPixmap("icons/ID.png"))
		self.IDPreview.setScaledContents(True)
		self.IDPreview.setObjectName("IDPreview")
		self.HotelWelcome = QtWidgets.QLabel(self.SubRegistrationPage)
		self.HotelWelcome.setGeometry(QtCore.QRect(70, 7, 651, 60))
		palette = QtGui.QPalette()
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.PlaceholderText, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210, 128))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.PlaceholderText, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.PlaceholderText, brush)
		self.HotelWelcome.setPalette(palette)
		font = QtGui.QFont()
		font.setPointSize(35)
		self.HotelWelcome.setFont(font)
		self.HotelWelcome.setStyleSheet("background-color: transparent;\n"
"")
		self.HotelWelcome.setObjectName("HotelWelcome")
		self.HotelLogo = QtWidgets.QLabel(self.SubRegistrationPage)
		self.HotelLogo.setGeometry(QtCore.QRect(10, 6, 61, 61))
		self.HotelLogo.setLayoutDirection(QtCore.Qt.LeftToRight)
		self.HotelLogo.setStyleSheet("background-color: Transparent;\n"
"border:0px solid;\n"
"border-radius:0px\n"
"")
		self.HotelLogo.setText("")
		self.HotelLogo.setPixmap(QtGui.QPixmap("icons/LogoHead.png"))
		self.HotelLogo.setScaledContents(True)
		self.HotelLogo.setObjectName("HotelLogo")
		self.RBG_3 = QtWidgets.QLabel(self.RegistrationPage)
		self.RBG_3.setGeometry(QtCore.QRect(10, -10, 811, 541))
		self.RBG_3.setText("")
		self.RBG_3.setPixmap(QtGui.QPixmap("background/bg1.jpg"))
		self.RBG_3.setScaledContents(True)
		self.RBG_3.setObjectName("RBG_3")
		self.RBG_3.raise_()
		self.SubRegistrationPage.raise_()
		self.BillingPage = QtWidgets.QWidget(self.centralwidget)
		self.BillingPage.setGeometry(QtCore.QRect(0, 90, 831, 571))
		palette = QtGui.QPalette()
		brush = QtGui.QBrush(QtGui.QColor(39, 44, 54))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(39, 44, 54))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(39, 44, 54))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(39, 44, 54))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(39, 44, 54))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(39, 44, 54))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(39, 44, 54))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(39, 44, 54))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(39, 44, 54))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
		self.BillingPage.setPalette(palette)
		self.BillingPage.setStyleSheet("background-color: rgb(39, 44, 54);")
		self.BillingPage.setObjectName("BillingPage")
		self.SubBillingPage = QtWidgets.QWidget(self.BillingPage)
		self.SubBillingPage.setGeometry(QtCore.QRect(50, 10, 731, 501))
		self.SubBillingPage.setStyleSheet("border:1px solid;\n"
"border-color:transparent;\n"
"border-radius:15px;\n"
"background-color:rgba(86, 91, 100, 190);")
		self.SubBillingPage.setObjectName("SubBillingPage")
		self.BillingDiv = QtWidgets.QFrame(self.SubBillingPage)
		self.BillingDiv.setGeometry(QtCore.QRect(0, 60, 731, 3))
		self.BillingDiv.setFrameShape(QtWidgets.QFrame.HLine)
		self.BillingDiv.setFrameShadow(QtWidgets.QFrame.Sunken)
		self.BillingDiv.setObjectName("BillingDiv")
		self.ReceiptGen = QtWidgets.QPushButton(self.SubBillingPage)
		self.ReceiptGen.setGeometry(QtCore.QRect(40, 420, 131, 41))
		palette = QtGui.QPalette()
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.PlaceholderText, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210, 128))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.PlaceholderText, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.PlaceholderText, brush)
		self.ReceiptGen.setPalette(palette)
		self.ReceiptGen.setStyleSheet("QPushButton {\n"
"    border: 2px solid rgb(52, 59, 72);\n"
"    border-radius: 5px;    \n"
"    background-color: rgb(52, 59, 72);\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: rgb(57, 65, 80);\n"
"    border: 2px solid rgb(61, 70, 86);\n"
"}\n"
"QPushButton:pressed {    \n"
"    background-color: rgb(35, 40, 49);\n"
"    border: 2px solid rgb(43, 50, 61);\n"
"}")
		icon2 = QtGui.QIcon()
		icon2.addPixmap(QtGui.QPixmap("icons/cil-print.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.ReceiptGen.setIcon(icon2)
		self.ReceiptGen.setIconSize(QtCore.QSize(29, 29))
		self.ReceiptGen.setObjectName("ReceiptGen")
		self.DetailReceipt = QtWidgets.QTableWidget(self.SubBillingPage)
		self.DetailReceipt.setGeometry(QtCore.QRect(26, 80, 681, 331))
		palette = QtGui.QPalette()
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72, 150))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
		brush.setStyle(QtCore.Qt.NoBrush)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72, 150))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72, 150))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
		brush.setStyle(QtCore.Qt.NoBrush)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72, 150))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72, 150))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
		brush.setStyle(QtCore.Qt.NoBrush)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72, 150))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
		self.DetailReceipt.setPalette(palette)
		self.DetailReceipt.setDragDropOverwriteMode(False)
		#self.DetailReceipt.setAlternatingRowColors(True)
		self.DetailReceipt.setCornerButtonEnabled(False)
		self.DetailReceipt.setObjectName("DetailReceipt")
		self.DetailReceipt.setColumnCount(3)
		self.DetailReceipt.setRowCount(0)
		self.DetailReceipt.setStyleSheet("""QTableWidget{
background-color: rgba(52, 59, 72,150);
border:1px solid;
border-radius:8px;
}
QTableCornerButton {
border:1px transparent;
border-top-left-radius:8px;
background-color:transparent;
}
QTableCornerButton::section {
border:1px transparent;
border-top-left-radius:8px;
background-color:transparent;
}

QScrollBar{
	border:1px transparent;
	background:rgb(52, 59, 72);
	margin: 0px 21px 0 21px;
	border-radius:8px;
 }

 QScrollBar::add-page, QScrollBar::sub-page
 {
	 background: none;
 }

QScrollBar::add-line{
	  border: none;
	  background: none;
}

QScrollBar::sub-line {
	  border: none;
	  background: none;
}

QScrollBar::handle {
	border:1px solid;
	border-color:rgb(105, 180, 255);
	background:rgb(105, 180, 255);
	border-radius: 8px;
 }

QTableWidget::horizontalHeader {	
	background-color: rgb(81, 255, 0);
}

QTableWidget::item{
	background-color: transparent;
	border-left:1px solid;
	border-top:1px solid;
}
QTableWidget::item:hover{
	background-color: rgba(57, 65, 80,150);
}
QTableWidget::item:selected{
	background-color: rgb(85, 170, 255);
}

QHeaderView{
background-color:transparent;
}

QHeaderView::section:horizontal
{
	border: 1px solid rgb(32, 34, 42);
	background-color: rgb(27, 29, 35);
	padding: 3px;
	color:rgb(175, 175, 185);
	border-top-left-radius: 8px;
	border-top-right-radius: 8px;
}

QHeaderView::section:vertical
{
	border: 1px solid rgb(32, 34, 42);
	background-color: rgb(27, 29, 35);
	padding-left:2px;
	color:rgb(175, 175, 185);
	border-bottom-right-radius:6px;
	border-top-right-radius: 6px;
}""")
		item = QtWidgets.QTableWidgetItem()
		self.DetailReceipt.setHorizontalHeaderItem(0, item)
		item = QtWidgets.QTableWidgetItem()
		self.DetailReceipt.setHorizontalHeaderItem(1, item)
		item = QtWidgets.QTableWidgetItem()
		self.DetailReceipt.setHorizontalHeaderItem(2, item)
		self.DetailReceipt.horizontalHeader().setDefaultSectionSize(220)
		self.TotalAmount = QtWidgets.QLabel(self.SubBillingPage)
		self.TotalAmount.setGeometry(QtCore.QRect(246, 11, 451, 41))
		font = QtGui.QFont()
		font.setPointSize(20)
		self.TotalAmount.setFont(font)
		self.TotalAmount.setStyleSheet("background-color:rgba(85, 85, 101,190);\n"
"padding:2px")
		self.TotalAmount.setObjectName("TotalAmount")
		self.RBG_4 = QtWidgets.QLabel(self.BillingPage)
		self.RBG_4.setGeometry(QtCore.QRect(10, -10, 811, 541))
		self.RBG_4.setText("")
		self.RBG_4.setPixmap(QtGui.QPixmap("background/bg2.png"))
		self.RBG_4.setScaledContents(True)
		self.RBG_4.setObjectName("RBG_4")
		self.RoomPage = QtWidgets.QWidget(self.BillingPage)
		self.RoomPage.setGeometry(QtCore.QRect(0, 0, 831, 571))
		palette = QtGui.QPalette()
		brush = QtGui.QBrush(QtGui.QColor(39, 44, 54))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(39, 44, 54))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(39, 44, 54))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(39, 44, 54))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(39, 44, 54))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(39, 44, 54))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(39, 44, 54))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(39, 44, 54))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(39, 44, 54))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
		self.RoomPage.setPalette(palette)
		self.RoomPage.setStyleSheet("background-color: rgb(39, 44, 54);")
		self.RoomPage.setObjectName("RoomPage")
		self.SubRoomPage = QtWidgets.QWidget(self.RoomPage)
		self.SubRoomPage.setGeometry(QtCore.QRect(50, 20, 731, 501))
		self.SubRoomPage.setStyleSheet("border:1px solid;\n"
"border-color:transparent;\n"
"border-radius:15px;\n"
"background-color:rgba(86, 91, 100, 190);")
		self.SubRoomPage.setObjectName("SubRoomPage")
		self.Partition = QtWidgets.QFrame(self.SubRoomPage)
		self.Partition.setGeometry(QtCore.QRect(0, 175, 731, 3))
		self.Partition.setFrameShape(QtWidgets.QFrame.HLine)
		self.Partition.setFrameShadow(QtWidgets.QFrame.Sunken)
		self.Partition.setObjectName("Partition")
		self.Partition2 = QtWidgets.QFrame(self.SubRoomPage)
		self.Partition2.setGeometry(QtCore.QRect(0, 350, 731, 3))
		self.Partition2.setFrameShape(QtWidgets.QFrame.HLine)
		self.Partition2.setFrameShadow(QtWidgets.QFrame.Sunken)
		self.Partition2.setObjectName("Partition2")
		self.Partition3 = QtWidgets.QFrame(self.SubRoomPage)
		self.Partition3.setGeometry(QtCore.QRect(270, 0, 3, 341))
		self.Partition3.setFrameShape(QtWidgets.QFrame.VLine)
		self.Partition3.setFrameShadow(QtWidgets.QFrame.Sunken)
		self.Partition3.setObjectName("Partition3")
		self.Partition4 = QtWidgets.QFrame(self.SubRoomPage)
		self.Partition4.setGeometry(QtCore.QRect(470, 0, 3, 341))
		self.Partition4.setFrameShape(QtWidgets.QFrame.VLine)
		self.Partition4.setFrameShadow(QtWidgets.QFrame.Sunken)
		self.Partition4.setObjectName("Partition4")
		self.Partition5 = QtWidgets.QFrame(self.SubRoomPage)
		self.Partition5.setGeometry(QtCore.QRect(160, 350, 3, 150))
		self.Partition5.setFrameShape(QtWidgets.QFrame.VLine)
		self.Partition5.setFrameShadow(QtWidgets.QFrame.Sunken)
		self.Partition5.setObjectName("Partition5")
		self.Partition6 = QtWidgets.QFrame(self.SubRoomPage)
		self.Partition6.setGeometry(QtCore.QRect(360, 350, 3, 150))
		self.Partition6.setFrameShape(QtWidgets.QFrame.VLine)
		self.Partition6.setFrameShadow(QtWidgets.QFrame.Sunken)
		self.Partition6.setObjectName("Partition6")
		self.Partition7 = QtWidgets.QFrame(self.SubRoomPage)
		self.Partition7.setGeometry(QtCore.QRect(560, 350, 3, 150))
		self.Partition7.setFrameShape(QtWidgets.QFrame.VLine)
		self.Partition7.setFrameShadow(QtWidgets.QFrame.Sunken)
		self.Partition7.setObjectName("Partition7")
		self.Label303 = QtWidgets.QLabel(self.SubRoomPage)
		self.Label303.setGeometry(QtCore.QRect(550, 130, 51, 21))
		font = QtGui.QFont()
		font.setPointSize(15)
		self.Label303.setFont(font)
		self.Label303.setStyleSheet("background-color:transparent;\n"
"")
		self.Label303.setAlignment(QtCore.Qt.AlignCenter)
		self.Label303.setObjectName("Label303")
		RoomButtonStyle="""QPushButton{
background-color:transparent;
}
QPushButton:hover{
background-color:rgba(172, 172, 172,130);
}
"""
		self.Button203 = QtWidgets.QPushButton(self.SubRoomPage)
		self.Button203.setGeometry(QtCore.QRect(540, 180, 111, 151))
		self.Button203.setStyleSheet(RoomButtonStyle)
		self.Button203.setText("")
		icon3 = QtGui.QIcon()
		icon3.addPixmap(QtGui.QPixmap("icons/RoomIco.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.Button203.setIcon(icon3)
		self.Button203.setIconSize(QtCore.QSize(90, 255))
		self.Button203.setObjectName("Button203")
		self.Button102 = QtWidgets.QPushButton(self.SubRoomPage)
		self.Button102.setGeometry(QtCore.QRect(219, 339, 111, 151))
		self.Button102.setStyleSheet(RoomButtonStyle)
		self.Button102.setText("")
		self.Button102.setIcon(icon3)
		self.Button102.setIconSize(QtCore.QSize(90, 255))
		self.Button102.setObjectName("Button102")
		self.Label302 = QtWidgets.QLabel(self.SubRoomPage)
		self.Label302.setGeometry(QtCore.QRect(333, 128, 51, 21))
		font = QtGui.QFont()
		font.setPointSize(15)
		self.Label302.setFont(font)
		self.Label302.setStyleSheet("background-color:transparent;\n"
"")
		self.Label302.setAlignment(QtCore.Qt.AlignCenter)
		self.Label302.setObjectName("Label302")
		self.Label201 = QtWidgets.QLabel(self.SubRoomPage)
		self.Label201.setGeometry(QtCore.QRect(130, 290, 51, 21))
		font = QtGui.QFont()
		font.setPointSize(15)
		self.Label201.setFont(font)
		self.Label201.setStyleSheet("background-color:transparent;\n"
"")
		self.Label201.setAlignment(QtCore.Qt.AlignCenter)
		self.Label201.setObjectName("Label201")
		self.Button202 = QtWidgets.QPushButton(self.SubRoomPage)
		self.Button202.setGeometry(QtCore.QRect(319, 180, 111, 151))
		self.Button202.setStyleSheet(RoomButtonStyle)
		self.Button202.setText("")
		self.Button202.setIcon(icon3)
		self.Button202.setIconSize(QtCore.QSize(90, 255))
		self.Button202.setObjectName("Button202")
		self.Button302 = QtWidgets.QPushButton(self.SubRoomPage)
		self.Button302.setGeometry(QtCore.QRect(322, 9, 111, 161))
		self.Button302.setStyleSheet(RoomButtonStyle)
		self.Button302.setText("")
		self.Button302.setIcon(icon3)
		self.Button302.setIconSize(QtCore.QSize(90, 255))
		self.Button302.setObjectName("Button302")
		self.Label203 = QtWidgets.QLabel(self.SubRoomPage)
		self.Label203.setGeometry(QtCore.QRect(550, 290, 51, 21))
		font = QtGui.QFont()
		font.setPointSize(15)
		self.Label203.setFont(font)
		self.Label203.setStyleSheet("background-color:transparent;\n"
"")
		self.Label203.setAlignment(QtCore.Qt.AlignCenter)
		self.Label203.setObjectName("Label203")
		self.Button104 = QtWidgets.QPushButton(self.SubRoomPage)
		self.Button104.setGeometry(QtCore.QRect(610, 339, 111, 151))
		self.Button104.setStyleSheet(RoomButtonStyle)
		self.Button104.setText("")
		self.Button104.setIcon(icon3)
		self.Button104.setIconSize(QtCore.QSize(90, 255))
		self.Button104.setObjectName("Button104")
		self.Button103 = QtWidgets.QPushButton(self.SubRoomPage)
		self.Button103.setGeometry(QtCore.QRect(419, 339, 111, 151))
		self.Button103.setStyleSheet(RoomButtonStyle)
		self.Button103.setText("")
		self.Button103.setIcon(icon3)
		self.Button103.setIconSize(QtCore.QSize(90, 255))
		self.Button103.setObjectName("Button103")
		self.Button301 = QtWidgets.QPushButton(self.SubRoomPage)
		self.Button301.setGeometry(QtCore.QRect(119, 9, 111, 161))
		self.Button301.setStyleSheet(RoomButtonStyle)
		self.Button301.setText("")
		self.Button301.setIcon(icon3)
		self.Button301.setIconSize(QtCore.QSize(90, 255))
		self.Button301.setObjectName("Button301")
		self.Button201 = QtWidgets.QPushButton(self.SubRoomPage)
		self.Button201.setGeometry(QtCore.QRect(120, 180, 111, 151))
		self.Button201.setStyleSheet(RoomButtonStyle)
		self.Button201.setText("")
		self.Button201.setIcon(icon3)
		self.Button201.setIconSize(QtCore.QSize(90, 255))
		self.Button201.setObjectName("Button201")
		self.Button101 = QtWidgets.QPushButton(self.SubRoomPage)
		self.Button101.setGeometry(QtCore.QRect(19, 339, 111, 151))
		self.Button101.setStyleSheet(RoomButtonStyle)
		self.Button101.setText("")
		self.Button101.setIcon(icon3)
		self.Button101.setIconSize(QtCore.QSize(90, 255))
		self.Button101.setObjectName("Button101")
		self.Label102 = QtWidgets.QLabel(self.SubRoomPage)
		self.Label102.setGeometry(QtCore.QRect(230, 454, 51, 21))
		font = QtGui.QFont()
		font.setPointSize(15)
		self.Label102.setFont(font)
		self.Label102.setStyleSheet("background-color:transparent;\n"
"")
		self.Label102.setAlignment(QtCore.Qt.AlignCenter)
		self.Label102.setObjectName("Label102")
		self.Label104 = QtWidgets.QLabel(self.SubRoomPage)
		self.Label104.setGeometry(QtCore.QRect(620, 454, 51, 21))
		font = QtGui.QFont()
		font.setPointSize(15)
		self.Label104.setFont(font)
		self.Label104.setStyleSheet("background-color:transparent;\n"
"")
		self.Label104.setAlignment(QtCore.Qt.AlignCenter)
		self.Label104.setObjectName("Label104")
		self.Label103 = QtWidgets.QLabel(self.SubRoomPage)
		self.Label103.setGeometry(QtCore.QRect(430, 454, 51, 21))
		font = QtGui.QFont()
		font.setPointSize(15)
		self.Label103.setFont(font)
		self.Label103.setStyleSheet("background-color:transparent;\n"
"")
		self.Label103.setAlignment(QtCore.Qt.AlignCenter)
		self.Label103.setObjectName("Label103")
		self.Label301 = QtWidgets.QLabel(self.SubRoomPage)
		self.Label301.setGeometry(QtCore.QRect(129, 128, 51, 21))
		font = QtGui.QFont()
		font.setPointSize(15)
		self.Label301.setFont(font)
		self.Label301.setStyleSheet("background-color:transparent;\n"
"")
		self.Label301.setAlignment(QtCore.Qt.AlignCenter)
		self.Label301.setObjectName("Label301")
		self.Label101 = QtWidgets.QLabel(self.SubRoomPage)
		self.Label101.setGeometry(QtCore.QRect(30, 454, 51, 21))
		font = QtGui.QFont()
		font.setPointSize(15)
		self.Label101.setFont(font)
		self.Label101.setStyleSheet("background-color:transparent;\n"
"")
		self.Label101.setAlignment(QtCore.Qt.AlignCenter)
		self.Label101.setObjectName("Label101")
		self.Button303 = QtWidgets.QPushButton(self.SubRoomPage)
		self.Button303.setGeometry(QtCore.QRect(540, 9, 111, 161))
		self.Button303.setStyleSheet(RoomButtonStyle)
		self.Button303.setText("")
		self.Button303.setIcon(icon3)
		self.Button303.setIconSize(QtCore.QSize(90, 255))
		self.Button303.setObjectName("Button303")
		self.Label202 = QtWidgets.QLabel(self.SubRoomPage)
		self.Label202.setGeometry(QtCore.QRect(330, 290, 51, 21))
		font = QtGui.QFont()
		font.setPointSize(15)
		self.Label202.setFont(font)
		self.Label202.setStyleSheet("background-color:transparent;\n"
"")
		self.Label202.setAlignment(QtCore.Qt.AlignCenter)
		self.Label202.setObjectName("Label202")
		self.Partition.raise_()
		self.Partition2.raise_()
		self.Partition3.raise_()
		self.Partition4.raise_()
		self.Partition5.raise_()
		self.Partition6.raise_()
		self.Partition7.raise_()
		self.Button203.raise_()
		self.Button102.raise_()
		self.Button202.raise_()
		self.Button302.raise_()
		self.Label203.raise_()
		self.Button104.raise_()
		self.Button103.raise_()
		self.Button301.raise_()
		self.Button201.raise_()
		self.Button101.raise_()
		self.Label102.raise_()
		self.Label104.raise_()
		self.Label103.raise_()
		self.Label301.raise_()
		self.Label101.raise_()
		self.Button303.raise_()
		self.Label202.raise_()
		self.Label303.raise_()
		self.Label302.raise_()
		self.Label201.raise_()
		self.RBG = QtWidgets.QLabel(self.RoomPage)
		self.RBG.setGeometry(QtCore.QRect(10, 0, 811, 531))
		self.RBG.setText("")
		self.RBG.setPixmap(QtGui.QPixmap("background/bg4.jpg"))
		self.RBG.setScaledContents(True)
		self.RBG.setObjectName("RBG")
		self.RBG.raise_()
		self.SubRoomPage.raise_()
		self.GMSPage = QtWidgets.QWidget(self.BillingPage)
		self.GMSPage.setGeometry(QtCore.QRect(0, 0, 831, 571))
		palette = QtGui.QPalette()
		brush = QtGui.QBrush(QtGui.QColor(39, 44, 54))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(39, 44, 54))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(39, 44, 54))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(39, 44, 54))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(39, 44, 54))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(39, 44, 54))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(39, 44, 54))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(39, 44, 54))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(39, 44, 54))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
		self.GMSPage.setPalette(palette)
		self.GMSPage.setStyleSheet("background-color: rgb(39, 44, 54);")
		self.GMSPage.setObjectName("GMSPage")
		self.SubGMSPage = QtWidgets.QWidget(self.GMSPage)
		self.SubGMSPage.setGeometry(QtCore.QRect(50, 10, 731, 501))
		self.SubGMSPage.setStyleSheet("border:1px solid;\n"
"border-color:transparent;\n"
"border-radius:15px;\n"
"background-color:rgba(86, 91, 100, 190);")
		self.SubGMSPage.setObjectName("SubGMSPage")
		self.GMSDiv = QtWidgets.QFrame(self.SubGMSPage)
		self.GMSDiv.setGeometry(QtCore.QRect(1, 60, 729, 3))
		self.GMSDiv.setFrameShape(QtWidgets.QFrame.HLine)
		self.GMSDiv.setFrameShadow(QtWidgets.QFrame.Sunken)
		self.GMSDiv.setObjectName("GMSDiv")
		self.ServiceDate = QtWidgets.QDateTimeEdit(self.SubGMSPage)
		self.ServiceDate.setGeometry(QtCore.QRect(500, 280, 221, 22))
		self.ServiceDate.setStyleSheet("QDateTimeEdit {\n"
"    background-color: rgba(27, 29, 35,180);\n"
"    border-radius: 5px;\n"
"    border: 2px solid rgb(27, 29, 35);\n"
"    color:rgb(182, 182, 182);\n"
"    padding-left: 10px;\n"
"}\n"
"QDateTimeEdit:hover {\n"
"    border: 2px solid rgb(64, 71, 88);\n"
"}\n"
"QDateTimeEdit:focus {\n"
"    border: 2px solid rgb(91, 101, 124);\n"
"    color:rgb(182, 182, 182)\n"
"}\n"
"QCalendarWidget QWidget{\n"
"background-color: rgb(39, 44, 54);\n"
"\n"
"border-radius:0px;\n"
"color:rgb(181, 181, 195)\n"
"}\n"
"\n"
"QCalendarWidget QWidget:hover {\n"
"    border: 2px solid rgb(64, 71, 88);\n"
"}\n"
"QCalendarWidget QToolButton{\n"
"color:rgb(181, 181, 195);\n"
"border:1px solid rgb(27, 29, 35);\n"
"border-bottom:0px;\n"
"border-radius:0px;\n"
"icon-size: 30px;\n"
"}\n"
"\n"
"QCalendarWidget QMenu{\n"
"background-color: rgb(39, 44, 54);\n"
"border:1px solid;\n"
"color:rgb(181, 181, 195)\n"
"\n"
"}\n"
"\n"
"QCalendarWidget QAbstractItemView:enabled{\n"
"background-color: rgb(39, 44, 54);\n"
"color:rgb(108, 108, 108);\n"
"}\n"
"\n"
"\n"
"QCalendarWidget QAbstractItemView:disabled{\n"
"background-color: rgb(39, 44, 54);\n"
"color: rgb(182, 182, 197);\n"
"}\n"
"\n"
"QCalendarWidget QSpinBox{\n"
"    background-color: rgb(39, 44, 54);\n"
"}")
		self.ServiceDate.setWrapping(False)
		self.ServiceDate.setButtonSymbols(QtWidgets.QAbstractSpinBox.UpDownArrows)
		self.ServiceDate.setMinimumDate(QtCore.QDate(2020, 3, 13))
		self.ServiceDate.setCurrentSection(QtWidgets.QDateTimeEdit.DaySection)
		self.ServiceDate.setCalendarPopup(True)
		self.ServiceDate.setObjectName("ServiceDate")
		self.ServiceDateLabel = QtWidgets.QLabel(self.SubGMSPage)
		self.ServiceDateLabel.setGeometry(QtCore.QRect(500, 260, 47, 13))
		palette = QtGui.QPalette()
		brush = QtGui.QBrush(QtGui.QColor(222, 213, 226))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(222, 213, 226))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(222, 213, 226))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(222, 213, 226, 128))
		brush.setStyle(QtCore.Qt.NoBrush)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.PlaceholderText, brush)
		brush = QtGui.QBrush(QtGui.QColor(222, 213, 226))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(222, 213, 226))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(222, 213, 226))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(222, 213, 226, 128))
		brush.setStyle(QtCore.Qt.NoBrush)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.PlaceholderText, brush)
		brush = QtGui.QBrush(QtGui.QColor(222, 213, 226))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(222, 213, 226))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(222, 213, 226))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(222, 213, 226, 128))
		brush.setStyle(QtCore.Qt.NoBrush)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.PlaceholderText, brush)
		self.ServiceDateLabel.setPalette(palette)
		font = QtGui.QFont()
		font.setPointSize(10)
		self.ServiceDateLabel.setFont(font)
		self.ServiceDateLabel.setStyleSheet("background-color:transparent;\n"
"color: rgb(222, 213, 226);")
		self.ServiceDateLabel.setObjectName("ServiceDateLabel")
		self.ServiceDescription = QtWidgets.QLineEdit(self.SubGMSPage)
		self.ServiceDescription.setGeometry(QtCore.QRect(500, 120, 221, 31))
		palette = QtGui.QPalette()
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 180))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 180))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 180))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(98, 98, 98))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.PlaceholderText, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 180))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 180))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 180))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(98, 98, 98))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.PlaceholderText, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 180))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 180))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 180))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(98, 98, 98))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.PlaceholderText, brush)
		self.ServiceDescription.setPalette(palette)
		self.ServiceDescription.setStyleSheet("QLineEdit {\n"
"    background-color: rgba(27, 29, 35,180);\n"
"    border-radius: 5px;\n"
"    border: 2px solid rgb(27, 29, 35);\n"
"    padding-left: 10px;\n"
"}\n"
"QLineEdit:hover {\n"
"    border: 2px solid rgb(64, 71, 88);\n"
"}\n"
"QLineEdit:focus {\n"
"    border: 2px solid rgb(91, 101, 124);\n"
"}")
		self.ServiceDescription.setText("")
		self.ServiceDescription.setObjectName("ServiceDescription")
		self.ServiceCharge = QtWidgets.QLineEdit(self.SubGMSPage)
		self.ServiceCharge.setGeometry(QtCore.QRect(500, 210, 221, 31))
		self.ServiceCharge.setPalette(palette)
		self.ServiceCharge.setStyleSheet("QLineEdit {\n"
"    background-color: rgba(27, 29, 35,180);\n"
"    border-radius: 5px;\n"
"    border: 2px solid rgb(27, 29, 35);\n"
"    padding-left: 10px;\n"
"}\n"
"QLineEdit:hover {\n"
"    border: 2px solid rgb(64, 71, 88);\n"
"}\n"
"QLineEdit:focus {\n"
"    border: 2px solid rgb(91, 101, 124);\n"
"}")
		self.ServiceCharge.setText("")
		self.ServiceCharge.setObjectName("ServiceCharge")
		self.Quantity = QtWidgets.QSpinBox(self.SubGMSPage)
		self.Quantity.setGeometry(QtCore.QRect(500, 170, 81, 22))
		palette = QtGui.QPalette()
		brush = QtGui.QBrush(QtGui.QColor(181, 172, 193))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 180))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(181, 172, 193))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(181, 172, 193))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
		brush.setStyle(QtCore.Qt.NoBrush)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 180))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(181, 172, 193, 128))
		brush.setStyle(QtCore.Qt.NoBrush)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.PlaceholderText, brush)
		brush = QtGui.QBrush(QtGui.QColor(181, 172, 193))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 180))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(181, 172, 193))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(181, 172, 193))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
		brush.setStyle(QtCore.Qt.NoBrush)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 180))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(181, 172, 193, 128))
		brush.setStyle(QtCore.Qt.NoBrush)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.PlaceholderText, brush)
		brush = QtGui.QBrush(QtGui.QColor(181, 172, 193))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 180))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(181, 172, 193))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(181, 172, 193))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
		brush.setStyle(QtCore.Qt.NoBrush)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 180))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(181, 172, 193, 128))
		brush.setStyle(QtCore.Qt.NoBrush)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.PlaceholderText, brush)
		self.Quantity.setPalette(palette)
		self.Quantity.setStyleSheet("QSpinBox {\n"
"    background-color: rgba(27, 29, 35,180);\n"
"    border-radius: 5px;\n"
"    border: 2px solid rgb(27, 29, 35);\n"
"    padding-left: 10px;\n"
"    color:rgb(181, 172, 193)\n"
"}\n"
"QSpinBox:hover {\n"
"    border: 2px solid rgb(64, 71, 88);\n"
"}\n"
"QSpinBox:focus {\n"
"    border: 2px solid rgb(91, 101, 124);\n"
"}")
		self.Quantity.setObjectName("Quantity")
		self.GMSDiv2 = QtWidgets.QFrame(self.SubGMSPage)
		self.GMSDiv2.setGeometry(QtCore.QRect(490, 70, 3, 411))
		self.GMSDiv2.setFrameShape(QtWidgets.QFrame.VLine)
		self.GMSDiv2.setFrameShadow(QtWidgets.QFrame.Sunken)
		self.GMSDiv2.setObjectName("GMSDiv2")
		self.AddtoBillButton = QtWidgets.QPushButton(self.SubGMSPage)
		self.AddtoBillButton.setGeometry(QtCore.QRect(500, 340, 71, 31))
		palette = QtGui.QPalette()
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.PlaceholderText, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210, 128))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.PlaceholderText, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.PlaceholderText, brush)
		self.AddtoBillButton.setPalette(palette)
		self.AddtoBillButton.setStyleSheet("QPushButton {\n"
"    border: 2px solid rgb(52, 59, 72);\n"
"    border-radius: 5px;    \n"
"    background-color: rgb(52, 59, 72);\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: rgb(57, 65, 80);\n"
"    border: 2px solid rgb(61, 70, 86);\n"
"}\n"
"QPushButton:pressed {    \n"
"    background-color: rgb(35, 40, 49);\n"
"    border: 2px solid rgb(43, 50, 61);\n"
"}")
		icon4 = QtGui.QIcon()
		icon4.addPixmap(QtGui.QPixmap("icons/cil-plus.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.AddtoBillButton.setIcon(icon4)
		self.AddtoBillButton.setIconSize(QtCore.QSize(30, 25))
		self.AddtoBillButton.setObjectName("AddtoBillButton")
		self.RoomDetailsLab = QtWidgets.QLabel(self.SubGMSPage)
		self.RoomDetailsLab.setGeometry(QtCore.QRect(30, 10, 231, 41))
		palette = QtGui.QPalette()
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(98, 98, 98))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.PlaceholderText, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(98, 98, 98))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.PlaceholderText, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(98, 98, 98))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.PlaceholderText, brush)
		self.RoomDetailsLab.setPalette(palette)
		font = QtGui.QFont()
		font.setFamily("Segoe UI")
		font.setPointSize(20)
		font.setBold(True)
		font.setWeight(75)
		self.RoomDetailsLab.setFont(font)
		self.RoomDetailsLab.setStyleSheet("background-color:transparent;")
		self.RoomDetailsLab.setObjectName("RoomDetailsLab")
		self.GuestNameLab = QtWidgets.QLabel(self.SubGMSPage)
		self.GuestNameLab.setGeometry(QtCore.QRect(30, 90, 451, 31))
		self.GuestNameLab.setPalette(palette)
		font = QtGui.QFont()
		font.setFamily("Segoe UI")
		font.setPointSize(14)
		font.setBold(False)
		font.setWeight(50)
		self.GuestNameLab.setFont(font)
		self.GuestNameLab.setStyleSheet("""QLabel{
background-color:transparent;
}
QLabel:hover{
background-color:rgba(120, 120, 120, 200)
}""")
		self.GuestNameLab.setObjectName("GuestNameLab")

		self.GuestEmailIDLab = QtWidgets.QLabel(self.SubGMSPage)
		self.GuestEmailIDLab.setGeometry(QtCore.QRect(30, 120, 451, 31))
		self.GuestEmailIDLab.setPalette(palette)
		font = QtGui.QFont()
		font.setFamily("Segoe UI")
		font.setPointSize(14)
		font.setBold(False)
		font.setWeight(50)
		self.GuestEmailIDLab.setFont(font)
		self.GuestEmailIDLab.setStyleSheet("""QLabel{
background-color:transparent;
}
QLabel:hover{
background-color:rgba(120, 120, 120, 200)
}""")
		self.GuestEmailIDLab.setObjectName("GuestEmailIDLab")

		self.GuestPhoneNoLab = QtWidgets.QLabel(self.SubGMSPage)
		self.GuestPhoneNoLab.setGeometry(QtCore.QRect(30, 150, 451, 31))
		self.GuestPhoneNoLab.setPalette(palette)
		font = QtGui.QFont()
		font.setFamily("Segoe UI")
		font.setPointSize(14)
		font.setBold(False)
		font.setWeight(50)
		self.GuestPhoneNoLab.setFont(font)
		self.GuestPhoneNoLab.setStyleSheet("""QLabel{
background-color:transparent;
}
QLabel:hover{
background-color:rgba(120, 120, 120, 200)
}""")
		self.GuestPhoneNoLab.setObjectName("GuestPhoneNoLab")

		self.RoomTypeLab = QtWidgets.QLabel(self.SubGMSPage)
		self.RoomTypeLab.setGeometry(QtCore.QRect(30, 180, 421, 31))
		self.RoomTypeLab.setPalette(palette)
		font = QtGui.QFont()
		font.setFamily("Segoe UI")
		font.setPointSize(14)
		font.setBold(False)
		font.setWeight(50)
		self.RoomTypeLab.setFont(font)
		self.RoomTypeLab.setStyleSheet("""QLabel{
background-color:transparent;
}
QLabel:hover{
background-color:rgba(120, 120, 120, 200)
}""")
		self.RoomTypeLab.setObjectName("RoomTypeLab")
		self.RoomNoLab = QtWidgets.QLabel(self.SubGMSPage)
		self.RoomNoLab.setGeometry(QtCore.QRect(30, 213, 421, 31))
		self.RoomNoLab.setPalette(palette)
		font = QtGui.QFont()
		font.setFamily("Segoe UI")
		font.setPointSize(14)
		font.setBold(False)
		font.setWeight(50)
		self.RoomNoLab.setFont(font)
		self.RoomNoLab.setStyleSheet("""QLabel{
background-color:transparent;
}
QLabel:hover{
background-color:rgba(120, 120, 120, 200)
}""")
		self.RoomNoLab.setObjectName("RoomNoLab")
		self.GuestCheckInLab = QtWidgets.QLabel(self.SubGMSPage)
		self.GuestCheckInLab.setGeometry(QtCore.QRect(30, 247, 411, 31))
		
		self.GuestCheckInLab.setPalette(palette)
		font = QtGui.QFont()
		font.setFamily("Segoe UI")
		font.setPointSize(14)
		font.setBold(False)
		font.setWeight(50)
		self.GuestCheckInLab.setFont(font)
		self.GuestCheckInLab.setStyleSheet("""QLabel{
background-color:transparent;
}
QLabel:hover{
background-color:rgba(120, 120, 120, 200)
}""")
		self.GuestCheckInLab.setObjectName("GuestCheckInLab")
		self.GuestCheckOutLab = QtWidgets.QLabel(self.SubGMSPage)
		self.GuestCheckOutLab.setGeometry(QtCore.QRect(30, 280, 431, 31))
		self.GuestCheckOutLab.setPalette(palette)
		font = QtGui.QFont()
		font.setFamily("Segoe UI")
		font.setPointSize(14)
		font.setBold(False)
		font.setWeight(50)
		self.GuestCheckOutLab.setFont(font)
		self.GuestCheckOutLab.setStyleSheet("""QLabel{
background-color:transparent;
}
QLabel:hover{
background-color:rgba(120, 120, 120, 200)
}""")
		self.GuestCheckOutLab.setObjectName("GuestCheckOutLab")
		self.ModifyCheckOut = QtWidgets.QDateTimeEdit(self.SubGMSPage)
		self.ModifyCheckOut.setGeometry(QtCore.QRect(40, 380, 221, 22))
		self.ModifyCheckOut.setStyleSheet("QDateTimeEdit {\n"
"    background-color: rgba(27, 29, 35,180);\n"
"    border-radius: 5px;\n"
"    border: 2px solid rgb(27, 29, 35);\n"
"    color:rgb(182, 182, 182);\n"
"    padding-left: 10px;\n"
"}\n"
"QDateTimeEdit:hover {\n"
"    border: 2px solid rgb(64, 71, 88);\n"
"}\n"
"QDateTimeEdit:focus {\n"
"    border: 2px solid rgb(91, 101, 124);\n"
"    color:rgb(182, 182, 182)\n"
"}\n"
"QCalendarWidget QWidget{\n"
"background-color: rgb(39, 44, 54);\n"
"\n"
"border-radius:0px;\n"
"color:rgb(181, 181, 195)\n"
"}\n"
"\n"
"QCalendarWidget QWidget:hover {\n"
"    border: 2px solid rgb(64, 71, 88);\n"
"}\n"
"QCalendarWidget QToolButton{\n"
"color:rgb(181, 181, 195);\n"
"border:1px solid rgb(27, 29, 35);\n"
"border-bottom:0px;\n"
"border-radius:0px;\n"
"icon-size: 30px;\n"
"}\n"
"\n"
"QCalendarWidget QMenu{\n"
"background-color: rgb(39, 44, 54);\n"
"border:1px solid;\n"
"color:rgb(181, 181, 195)\n"
"\n"
"}\n"
"\n"
"QCalendarWidget QAbstractItemView:enabled{\n"
"background-color: rgb(39, 44, 54);\n"
"color:rgb(108, 108, 108);\n"
"}\n"
"\n"
"\n"
"QCalendarWidget QAbstractItemView:disabled{\n"
"background-color: rgb(39, 44, 54);\n"
"color: rgb(182, 182, 197);\n"
"}\n"
"\n"
"QCalendarWidget QSpinBox{\n"
"    background-color: rgb(39, 44, 54);\n"
"}")
		self.ModifyCheckOut.setWrapping(False)
		self.ModifyCheckOut.setButtonSymbols(QtWidgets.QAbstractSpinBox.UpDownArrows)
		self.ModifyCheckOut.setMinimumDate(QtCore.QDate(2020, 1, 1))
		self.ModifyCheckOut.setCurrentSection(QtWidgets.QDateTimeEdit.DaySection)
		self.ModifyCheckOut.setCalendarPopup(True)
		self.ModifyCheckOut.setObjectName("ModifyCheckOut")
		self.ModifyCheckOutButton = QtWidgets.QPushButton(self.SubGMSPage)
		self.ModifyCheckOutButton.setGeometry(QtCore.QRect(40, 420, 81, 31))
		palette = QtGui.QPalette()
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.PlaceholderText, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210, 128))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.PlaceholderText, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.PlaceholderText, brush)
		self.ModifyCheckOutButton.setPalette(palette)
		self.ModifyCheckOutButton.setStyleSheet("QPushButton {\n"
"    border: 2px solid rgb(52, 59, 72);\n"
"    border-radius: 5px;    \n"
"    background-color: rgb(52, 59, 72);\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: rgb(57, 65, 80);\n"
"    border: 2px solid rgb(61, 70, 86);\n"
"}\n"
"QPushButton:pressed {    \n"
"    background-color: rgb(35, 40, 49);\n"
"    border: 2px solid rgb(43, 50, 61);\n"
"}")
		icon5 = QtGui.QIcon()
		icon5.addPixmap(QtGui.QPixmap("icons/cil-checkout.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.ModifyCheckOutButton.setIcon(icon5)
		self.ModifyCheckOutButton.setIconSize(QtCore.QSize(20, 20))
		self.ModifyCheckOutButton.setObjectName("ModifyCheckOutButton")
		self.ModifyCheckInButton = QtWidgets.QPushButton(self.SubGMSPage)
		self.ModifyCheckInButton.setGeometry(QtCore.QRect(280, 420, 81, 31))
		self.ModifyCheckInButton.setPalette(palette)
		self.ModifyCheckInButton.setStyleSheet("QPushButton {\n"
"    border: 2px solid rgb(52, 59, 72);\n"
"    border-radius: 5px;    \n"
"    background-color: rgb(52, 59, 72);\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: rgb(57, 65, 80);\n"
"    border: 2px solid rgb(61, 70, 86);\n"
"}\n"
"QPushButton:pressed {    \n"
"    background-color: rgb(35, 40, 49);\n"
"    border: 2px solid rgb(43, 50, 61);\n"
"}")
		self.ModifyCheckInButton.setIcon(icon5)
		self.ModifyCheckInButton.setIconSize(QtCore.QSize(20, 20))
		self.ModifyCheckInButton.setObjectName("ModifyCheckInButton")
		self.GMSDiv3 = QtWidgets.QFrame(self.SubGMSPage)
		self.GMSDiv3.setGeometry(QtCore.QRect(10, 320, 471, 3))
		self.GMSDiv3.setFrameShape(QtWidgets.QFrame.HLine)
		self.GMSDiv3.setFrameShadow(QtWidgets.QFrame.Sunken)
		self.GMSDiv3.setObjectName("GMSDiv3")
		self.ModifyCheckOutLab = QtWidgets.QLabel(self.SubGMSPage)
		self.ModifyCheckOutLab.setGeometry(QtCore.QRect(40, 330, 211, 31))
		palette = QtGui.QPalette()
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(98, 98, 98))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.PlaceholderText, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(98, 98, 98))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.PlaceholderText, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(98, 98, 98))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.PlaceholderText, brush)
		self.ModifyCheckOutLab.setPalette(palette)
		font = QtGui.QFont()
		font.setFamily("Segoe UI")
		font.setPointSize(14)
		font.setBold(False)
		font.setWeight(50)
		self.ModifyCheckOutLab.setFont(font)
		self.ModifyCheckOutLab.setStyleSheet("background-color:transparent;")
		self.ModifyCheckOutLab.setObjectName("ModifyCheckOutLab")
		self.ModifyCheckIn = QtWidgets.QDateTimeEdit(self.SubGMSPage)
		self.ModifyCheckIn.setGeometry(QtCore.QRect(270, 380, 221, 22))
		self.ModifyCheckIn.setStyleSheet("QDateTimeEdit {\n"
"    background-color: rgba(27, 29, 35,180);\n"
"    border-radius: 5px;\n"
"    border: 2px solid rgb(27, 29, 35);\n"
"    color:rgb(182, 182, 182);\n"
"    padding-left: 10px;\n"
"}\n"
"QDateTimeEdit:hover {\n"
"    border: 2px solid rgb(64, 71, 88);\n"
"}\n"
"QDateTimeEdit:focus {\n"
"    border: 2px solid rgb(91, 101, 124);\n"
"    color:rgb(182, 182, 182)\n"
"}\n"
"QCalendarWidget QWidget{\n"
"background-color: rgb(39, 44, 54);\n"
"\n"
"border-radius:0px;\n"
"color:rgb(181, 181, 195)\n"
"}\n"
"\n"
"QCalendarWidget QWidget:hover {\n"
"    border: 2px solid rgb(64, 71, 88);\n"
"}\n"
"QCalendarWidget QToolButton{\n"
"color:rgb(181, 181, 195);\n"
"border:1px solid rgb(27, 29, 35);\n"
"border-bottom:0px;\n"
"border-radius:0px;\n"
"icon-size: 30px;\n"
"}\n"
"\n"
"QCalendarWidget QMenu{\n"
"background-color: rgb(39, 44, 54);\n"
"border:1px solid;\n"
"color:rgb(181, 181, 195)\n"
"\n"
"}\n"
"\n"
"QCalendarWidget QAbstractItemView:enabled{\n"
"background-color: rgb(39, 44, 54);\n"
"color:rgb(108, 108, 108);\n"
"}\n"
"\n"
"\n"
"QCalendarWidget QAbstractItemView:disabled{\n"
"background-color: rgb(39, 44, 54);\n"
"color: rgb(182, 182, 197);\n"
"}\n"
"\n"
"QCalendarWidget QSpinBox{\n"
"    background-color: rgb(39, 44, 54);\n"
"}")
		self.ModifyCheckIn.setWrapping(False)
		self.ModifyCheckIn.setButtonSymbols(QtWidgets.QAbstractSpinBox.UpDownArrows)
		self.ModifyCheckIn.setMinimumDate(QtCore.QDate(2020, 1, 1))
		self.ModifyCheckIn.setCurrentSection(QtWidgets.QDateTimeEdit.DaySection)
		self.ModifyCheckIn.setCalendarPopup(True)
		self.ModifyCheckIn.setObjectName("ModifyCheckIn")
		self.ModifyCheckInLab = QtWidgets.QLabel(self.SubGMSPage)
		self.ModifyCheckInLab.setGeometry(QtCore.QRect(270, 330, 211, 31))
		self.ModifyCheckInLab.setPalette(palette)
		font = QtGui.QFont()
		font.setFamily("Segoe UI")
		font.setPointSize(14)
		font.setBold(False)
		font.setWeight(50)
		self.ModifyCheckInLab.setFont(font)
		self.ModifyCheckInLab.setStyleSheet("background-color:transparent;")
		self.ModifyCheckInLab.setObjectName("ModifyCheckInLab")
		self.AddtoBillLab = QtWidgets.QLabel(self.SubGMSPage)
		self.AddtoBillLab.setGeometry(QtCore.QRect(500, 76, 211, 31))
		self.AddtoBillLab.setPalette(palette)
		font = QtGui.QFont()
		font.setFamily("Segoe UI")
		font.setPointSize(14)
		font.setBold(False)
		font.setWeight(50)
		self.AddtoBillLab.setFont(font)
		self.AddtoBillLab.setStyleSheet("background-color:transparent;")
		self.AddtoBillLab.setObjectName("AddtoBillLab")		
		self.ContToBillingButton = QtWidgets.QPushButton(self.SubGMSPage)
		self.ContToBillingButton.setGeometry(QtCore.QRect(580, 450, 141, 41))
		palette = QtGui.QPalette()
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.PlaceholderText, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210, 128))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.PlaceholderText, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.PlaceholderText, brush)
		self.ContToBillingButton.setPalette(palette)
		self.ContToBillingButton.setStyleSheet("QPushButton {\n"
"    border: 2px solid rgb(52, 59, 72);\n"
"    border-radius: 5px;    \n"
"    background-color: rgb(52, 59, 72);\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: rgb(57, 65, 80);\n"
"    border: 2px solid rgb(61, 70, 86);\n"
"}\n"
"QPushButton:pressed {    \n"
"    background-color: rgb(35, 40, 49);\n"
"    border: 2px solid rgb(43, 50, 61);\n"
"}")
		icon6 = QtGui.QIcon()
		icon6.addPixmap(QtGui.QPixmap("icons/cil-bill.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.ContToBillingButton.setIcon(icon6)
		self.ContToBillingButton.setIconSize(QtCore.QSize(25, 25))
		self.ContToBillingButton.setObjectName("ContToBillingButton")
		
		
		self.RBG_8 = QtWidgets.QLabel(self.GMSPage)
		self.RBG_8.setGeometry(QtCore.QRect(10, -10, 811, 541))
		self.RBG_8.setText("")
		self.RBG_8.setPixmap(QtGui.QPixmap("background/bg3.jpg"))
		self.RBG_8.setScaledContents(True)
		self.RBG_8.setObjectName("RBG_8")
		self.RBG_8.raise_()
		self.SubGMSPage.raise_()
		self.RBG_4.raise_()
		self.SubBillingPage.raise_()
		self.GMSPage.raise_()
		self.RoomPage.raise_()
		self.FrameTop = QtWidgets.QWidget(self.centralwidget)
		self.FrameTop.setGeometry(QtCore.QRect(0, 0, 831, 91))
		self.FrameTop.setStyleSheet("background-color: rgba(27, 29, 35, 200)")
		self.FrameTop.setObjectName("FrameTop")
		self.FrameSubTop = QtWidgets.QWidget(self.FrameTop)
		self.FrameSubTop.setGeometry(QtCore.QRect(0, 0, 831, 91))
		self.FrameSubTop.setStyleSheet("background-color: rgba(27, 29, 35, 200)")
		self.FrameSubTop.setObjectName("FrameSubTop")
		self.FrameSubbedTop = QtWidgets.QWidget(self.FrameSubTop)
		self.FrameSubbedTop.setGeometry(QtCore.QRect(0, 0, 831, 91))
		self.FrameSubbedTop.setStyleSheet("background-color: rgba(27, 29, 35, 200)")
		self.FrameSubbedTop.setObjectName("FrameSubbedTop")
		self.ExitButton = QtWidgets.QPushButton(self.FrameSubbedTop)
		self.ExitButton.setGeometry(QtCore.QRect(800, 0, 31, 31))
		self.ExitButton.setStyleSheet("QPushButton {    \n"
"    border: none;\n"
"    background-color: transparent;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: rgb(52, 59, 72);\n"
"}\n"
"QPushButton:pressed {    \n"
"    background-color: rgb(85, 170, 255);\n"
"}")
		self.ExitButton.setText("")
		icon7 = QtGui.QIcon()
		icon7.addPixmap(QtGui.QPixmap("icons/cil-x.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.ExitButton.setIcon(icon7)
		self.ExitButton.setObjectName("ExitButton")
		self.MinimizeButton = QtWidgets.QPushButton(self.FrameSubbedTop)
		self.MinimizeButton.setGeometry(QtCore.QRect(770, 0, 31, 31))
		self.MinimizeButton.setStyleSheet("QPushButton {    \n"
"    border: none;\n"
"    background-color: transparent;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: rgb(52, 59, 72);\n"
"}\n"
"QPushButton:pressed {    \n"
"    background-color: rgb(85, 170, 255);\n"
"}")
		self.MinimizeButton.setText("")
		icon8 = QtGui.QIcon()
		icon8.addPixmap(QtGui.QPixmap("icons/cil-window-minimize.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.MinimizeButton.setIcon(icon8)
		self.MinimizeButton.setObjectName("MinimizeButton")
		self.MainLab = QtWidgets.QLabel(self.FrameSubbedTop)
		self.MainLab.setGeometry(QtCore.QRect(10, 5, 211, 21))
		palette = QtGui.QPalette()
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 200))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 200))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 200))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(98, 98, 98))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.PlaceholderText, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 200))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 200))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 200))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(98, 98, 98))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.PlaceholderText, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 200))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 200))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(27, 29, 35, 200))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(98, 98, 98))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.PlaceholderText, brush)
		self.MainLab.setPalette(palette)
		font = QtGui.QFont()
		font.setFamily("Segoe UI")
		font.setPointSize(10)
		font.setBold(True)
		font.setWeight(75)
		self.MainLab.setFont(font)
		self.MainLab.setObjectName("MainLab")
		self.FrameButton = QtWidgets.QWidget(self.FrameSubbedTop)
		self.FrameButton.setGeometry(QtCore.QRect(0, 30, 831, 331))
		palette = QtGui.QPalette()
		brush = QtGui.QBrush(QtGui.QColor(39, 44, 54))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(39, 44, 54))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(39, 44, 54))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(39, 44, 54))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(39, 44, 54))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(39, 44, 54))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(39, 44, 54))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(39, 44, 54))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(39, 44, 54))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
		self.FrameButton.setPalette(palette)
		self.FrameButton.setStyleSheet("background-color: rgb(39, 44, 54);")
		self.FrameButton.setObjectName("FrameButton")
		self.RegistrationButton = QtWidgets.QPushButton(self.FrameButton)
		self.RegistrationButton.setGeometry(QtCore.QRect(10, 6, 121, 41))
		palette = QtGui.QPalette()
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.PlaceholderText, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210, 128))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.PlaceholderText, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.PlaceholderText, brush)
		self.RegistrationButton.setPalette(palette)
		self.RegistrationButton.setStyleSheet("QPushButton {\n"
"    border: 2px solid rgb(52, 59, 72);\n"
"    border-radius: 5px;    \n"
"    background-color: rgb(52, 59, 72);\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: rgb(57, 65, 80);\n"
"    border: 2px solid rgb(61, 70, 86);\n"
"}\n"
"QPushButton:pressed {    \n"
"    background-color: rgb(35, 40, 49);\n"
"    border: 2px solid rgb(43, 50, 61);\n"
"}")
		icon9 = QtGui.QIcon()
		icon9.addPixmap(QtGui.QPixmap("icons/cil-register.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.RegistrationButton.setIcon(icon9)
		self.RegistrationButton.setIconSize(QtCore.QSize(30, 30))
		self.RegistrationButton.setObjectName("RegistrationButton")
		self.PageLine = QtWidgets.QFrame(self.FrameButton)
		self.PageLine.setGeometry(QtCore.QRect(3, 46, 821, 16))
		self.PageLine.setFrameShape(QtWidgets.QFrame.HLine)
		self.PageLine.setFrameShadow(QtWidgets.QFrame.Sunken)
		self.PageLine.setObjectName("PageLine")
		self.RoomsButton = QtWidgets.QPushButton(self.FrameButton)
		self.RoomsButton.setGeometry(QtCore.QRect(140, 6, 121, 41))
		palette = QtGui.QPalette()
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.PlaceholderText, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210, 128))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.PlaceholderText, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.PlaceholderText, brush)
		self.RoomsButton.setPalette(palette)
		self.RoomsButton.setStyleSheet("QPushButton {\n"
"    border: 2px solid rgb(52, 59, 72);\n"
"    border-radius: 5px;    \n"
"    background-color: rgb(52, 59, 72);\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: rgb(57, 65, 80);\n"
"    border: 2px solid rgb(61, 70, 86);\n"
"}\n"
"QPushButton:pressed {    \n"
"    background-color: rgb(35, 40, 49);\n"
"    border: 2px solid rgb(43, 50, 61);\n"
"}")
		icon10 = QtGui.QIcon()
		icon10.addPixmap(QtGui.QPixmap("icons/cil-bed.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.RoomsButton.setIcon(icon10)
		self.RoomsButton.setIconSize(QtCore.QSize(30, 25))
		self.RoomsButton.setObjectName("RoomsButton")
		self.NotificationButton = QtWidgets.QPushButton(self.FrameButton)
		self.NotificationButton.setGeometry(QtCore.QRect(700, 6, 121, 41))
		palette = QtGui.QPalette()
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.PlaceholderText, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210, 128))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.PlaceholderText, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(52, 59, 72))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.PlaceholderText, brush)
		self.NotificationButton.setPalette(palette)
		self.NotificationButton.setStyleSheet("QPushButton {\n"
"    border: 2px solid rgb(52, 59, 72);\n"
"    border-radius: 5px;    \n"
"    background-color: rgb(52, 59, 72);\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: rgb(57, 65, 80);\n"
"    border: 2px solid rgb(61, 70, 86);\n"
"}\n"
"QPushButton:pressed {    \n"
"    background-color: rgb(35, 40, 49);\n"
"    border: 2px solid rgb(43, 50, 61);\n"
"}")
		icon11 = QtGui.QIcon()
		icon11.addPixmap(QtGui.QPixmap("icons/cil-bell.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.NotificationButton.setIcon(icon11)
		self.NotificationButton.setIconSize(QtCore.QSize(20, 20))
		self.NotificationButton.setCheckable(True)
		self.NotificationButton.setObjectName("NotificationButton")
		self.InfoButton = QtWidgets.QPushButton(self.FrameSubbedTop)
		self.InfoButton.setGeometry(QtCore.QRect(740, 0, 31, 31))
		self.InfoButton.setStyleSheet("QPushButton {    \n"
"    border: none;\n"
"    background-color: transparent;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: rgb(52, 59, 72);\n"
"}\n"
"QPushButton:pressed {    \n"
"    background-color: rgb(85, 170, 255);\n"
"}")
		self.InfoButton.setText("")
		icon12 = QtGui.QIcon()
		icon12.addPixmap(QtGui.QPixmap("icons/cil-info.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.InfoButton.setIcon(icon12)
		self.InfoButton.setObjectName("InfoButton")
		self.FrameButton.raise_()
		self.ExitButton.raise_()
		self.MinimizeButton.raise_()
		self.MainLab.raise_()
		self.InfoButton.raise_()
		self.NotifyPage = QtWidgets.QWidget(self.centralwidget)
		self.NotifyPage.setGeometry(QtCore.QRect(0, 80, 831, 571))
		self.NotifyPage.setStyleSheet("background-color:transparent;")
		self.NotifyPage.setObjectName("NotifyPage")
		self.Notifications = QtWidgets.QListWidget(self.NotifyPage)
		self.Notifications.setGeometry(QtCore.QRect(15, 0, 811, 321))
		self.Notifications.setStyleSheet("""QListWidget {
	border: 2px solid rgb(52, 59, 72);
	border-radius: 5px;	
	background-color: rgba(52, 59, 72,190);
}
QListWidget:hover {
	background-color: rgba(57, 65, 80,190);
	border: 2px solid rgb(61, 70, 86);
}
QListWidget:focused {	
	background-color: rgb(35, 40, 49);
	border: 2px solid rgb(43, 50, 61);
}

 QScrollBar {
	border:1px transparent;
	background:rgb(52, 59, 72);
	margin: 5px 5px 5px 5px;
	border-radius:5px;
	width:20px;
 }
 QScrollBar::add-pagel, QScrollBar::sub-page
 {
	 background: none;
 }
QScrollBar::add-line {
	  border: none;
	  background: none;
}

QScrollBar::sub-line {
	  border: none;
	  background: none;
}
QScrollBar::handle {
	border:1px transparent;
	border-color:rgb(105, 180, 255);
	background:rgb(46, 172, 255);
	border-radius: 5px;
 }
 QScrollBar:horizontal {
	border:1px transparent;
	background:rgb(52, 59, 72);
	margin: 5px 5px 5px 5px;
	border-radius:5px;
	height:20px;
 }""")
		self.Notifications.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
		self.Notifications.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
		font = QtGui.QFont()
		font.setFamily("Segoe UI")
		font.setPointSize(13)
		font.setBold(False)
		font.setWeight(50)
		self.Notifications.setFont(font)
		self.Notifications.setObjectName("Notifications")
		self.NotifyPage.raise_()
		self.FrameTop.raise_()
		self.BillingPage.raise_()
		self.RegistrationPage.raise_()
		MainWindow.setCentralWidget(self.centralwidget)
		self.ExitButton.clicked.connect(lambda:exit())
		self.Book.clicked.connect(lambda:self.Registration())
		self.RegistrationButton.clicked.connect(lambda:self.setupUi(MainWindow))
		self.RoomsButton.clicked.connect(lambda:self.RoomDisplay())
		self.IDScan.clicked.connect(lambda :self.IDScanFunc())
		self.ModifyCheckOutButton.clicked.connect(lambda:self.ModifyCheckOutFunc())
		self.ModifyCheckInButton.clicked.connect(lambda:self.ModifyCheckInFunc())
		self.ContToBillingButton.clicked.connect(lambda :self.BillingInfoFunc())
		self.NotificationButton.setCheckable(True)
		self.NotificationButton.clicked.connect(lambda:self.DisplayNotification())
		self.AddtoBillButton.clicked.connect(lambda:self.AddtoBillFunc())
		#self.NotificationPage.setGeometry(QtCore.QRect(0, 0, 830, 21))
		self.MinimizeButton.clicked.connect(lambda:MainWindow.showMinimized())
		self.RoomType.activated.connect(lambda:self.filterRoomNo())
		self.retranslateUi(MainWindow)
		QtCore.QMetaObject.connectSlotsByName(MainWindow)
		self.NotificationCheckThreadRunnerFunc()
		
	
		def moveWindow(event):
			if event.buttons() == Qt.LeftButton:
				MainWindow.move(MainWindow.pos() + event.globalPos() - self.dragPos)
				self.dragPos = event.globalPos()
			event.accept()

		def pressWindow(event):
			# MOVE WINDOW
			self.dragPos = event.globalPos()

			
			#if event.buttons() == Qt.LeftButton:
			#	self.move(self.pos() + event.globalPos() - self.dragPos)
			#	self.dragPos = event.globalPos()
			#	event.accept()

		def releasedWindow(event):
			# MOVE WINDOW
			pass

		self.FrameSubbedTop.mouseMoveEvent=moveWindow
		self.FrameSubbedTop.mousePressEvent=pressWindow
		self.FrameSubbedTop.mouseReleaseEvent=releasedWindow
		self.getAvailableRooms()


	def filterRoomNo(self):
		global roomAvailable
		self.RoomNumber.clear()
		if self.RoomType.currentText()=="Deluxe Room":
			if 101 in roomAvailable:
				self.RoomNumber.addItem(str(101))
			if 102 in roomAvailable:
				self.RoomNumber.addItem(str(102))
			if 103 in roomAvailable:
				self.RoomNumber.addItem(str(103))
			if 104 in roomAvailable:
				self.RoomNumber.addItem(str(104))
		elif self.RoomType.currentText()=="Super Deluxe Room":
			if 201 in roomAvailable:
				self.RoomNumber.addItem(str(201))
			if 202 in roomAvailable:
				self.RoomNumber.addItem(str(202))
			if 203 in roomAvailable:
				self.RoomNumber.addItem(str(203))
		elif self.RoomType.currentText()=="Suite":
			if 301 in roomAvailable:
				self.RoomNumber.addItem(str(301))
			if 302 in roomAvailable:
				self.RoomNumber.addItem(str(302))
			if 303 in roomAvailable:
				self.RoomNumber.addItem(str(303))

	def getAvailableRooms(self):
		self.getAvailableRoomsThreadrunner=getAvailableRoomsThread()
		self.getAvailableRoomsThreadrunner.start()
		self.getAvailableRoomsThreadrunner.fetchedAvailablerooms.connect(lambda:self.DisplayAvailableRooms())
		
	def DisplayAvailableRooms(self):
		global roomAvailable
		curRoomList=[]
		for rooms in roomAvailable:
			if RoomTypeDict[int(rooms)] not in curRoomList:
				self.RoomType.addItem(RoomTypeDict[int(rooms)])
				curRoomList.append(RoomTypeDict[int(rooms)])
			self.RoomNumber.addItem(str(rooms))
				

	def DisplayNotification(self):
		global NewNotificationCont
		if self.NotificationButton.isChecked():
			self.Notifications.setStyleSheet("""QListWidget {
	border: 2px solid rgb(52, 59, 72);
	border-radius: 5px;	
	background-color: rgba(52, 59, 72,190);
}
QListWidget:hover {
	background-color: rgba(57, 65, 80,190);
	border: 2px solid rgb(61, 70, 86);
}
QListWidget:focused {	
	background-color: rgb(35, 40, 49);
	border: 2px solid rgb(43, 50, 61);
}

 QScrollBar {
	border:1px transparent;
	background:rgb(52, 59, 72);
	margin: 5px 5px 5px 5px;
	border-radius:5px;
	width:20px;
 }
 QScrollBar::add-pagel, QScrollBar::sub-page
 {
	 background: none;
 }
QScrollBar::add-line {
	  border: none;
	  background: none;
}

QScrollBar::sub-line {
	  border: none;
	  background: none;
}
QScrollBar::handle {
	border:1px transparent;
	border-color:rgb(105, 180, 255);
	background:rgb(46, 172, 255);
	border-radius: 5px;
 }
 QScrollBar:horizontal {
	border:1px transparent;
	background:rgb(52, 59, 72);
	margin: 5px 5px 5px 5px;
	border-radius:5px;
	height:20px;
 }""")
			#print("Displaying Notification")
			self.NotifyPage.raise_()
			for Value in NewNotificationCont:
				if Value[0]=="Food":
					toadd="""Date: %s | RoomNo. %s | Item: %s(x%s) | Special Note: %s """%(Value[1],Value[5],Value[2],Value[3],Value[4])
				elif Value[0]=="Room Service":
					toadd="""Guest at Room No. %s requested Room Serivce"""%Value[5]
				elif Value[0]=="Change CheckOut Date":
					toadd="""Guest at Room No. %s requested to Change the CheckOut Date to %s"""%(Value[5],Value[2])
				elif Value[0]=="Front Desk":
					toadd="""Guest at Room No. %s pinged Front Desk"""%Value[5]
				elif Value[0]=="DND On":
					toadd="""Guest at Room No. %s initiated DND"""%Value[5]
				elif Value[0]=="DND Off":
					toadd="""Guest at Room No. %s removed DND"""%Value[5]
				self.Notifications.addItem(toadd)

			self.NotificationButton.setText("Notifications")
			NewNotificationCont=[]
		else:
			self.NotifyPage.lower()
			self.Notifications.clear()

	def NotificationCheckThreadRunnerFunc(self):
		global NotificationThread
		#print(self.NotificationCheckThreadrunner.isFinished())
		if NotificationThread!=0:
			pass
		else:
			print("Starting the Thread")
			NotificationThread=1
			self.NotificationCheckThreadrunner=NotificationCheckThread()
			self.NotificationCheckThreadrunner.start()
			self.NotificationCheckThreadrunner.NewNotification.connect(lambda:self.NotificationButton.setText("Notifications*"))

	def AddtoBillFunc(self):
		global SelRoomNo,AddtoBillAmount,AddtoBillChargedfor,AddtoBillDate
		AddtoBillChargedfor=self.ServiceDescription.text()
		itemQuantity=self.Quantity.text()
		Amount=self.ServiceCharge.text()
		AddtoBillDate=self.ServiceDate.text()
		AddtoBillAmount=int(Amount)*int(itemQuantity)
		self.addtoBillThreadrunner=addtoBillThread()
		self.addtoBillThreadrunner.start()
		self.addtoBillThreadrunner.addedtoBillThread.connect(lambda:ctypes.windll.user32.MessageBoxW(0, f"Added {AddtoBillChargedfor} to bill successfully!", "GMS Notifier", 0))#Add ctypes notification

	def BillingInfoFunc(self):
		self.GMSPage.setGeometry(QtCore.QRect(0, 0, 0, 571))
		self.BillingPage.setGeometry(QtCore.QRect(0, 90, 831, 571))
		self.getBillingInforunner=getGuestBillInfo()
		self.getBillingInforunner.start()
		self.getBillingInforunner.gotBillingInfo.connect(lambda:self.DisplayFetchedData())
		self.DetailReceipt.setStyleSheet("""QTableWidget{
background-color: rgba(52, 59, 72,150);
border:1px solid;
border-radius:8px;
}
QTableCornerButton {
border:1px transparent;
border-top-left-radius:8px;
background-color:transparent;
}
QTableCornerButton::section {
border:1px transparent;
border-top-left-radius:8px;
background-color:transparent;
}

QScrollBar{
	border:1px transparent;
	background:rgb(52, 59, 72);
	margin: 0px 21px 0 21px;
	border-radius:8px;
 }

 QScrollBar::add-page, QScrollBar::sub-page
 {
	 background: none;
 }

QScrollBar::add-line{
	  border: none;
	  background: none;
}

QScrollBar::sub-line {
	  border: none;
	  background: none;
}

QScrollBar::handle {
	border:1px solid;
	border-color:rgb(105, 180, 255);
	background:rgb(105, 180, 255);
	border-radius: 8px;
 }

QTableWidget::horizontalHeader {	
	background-color: rgb(81, 255, 0);
}

QTableWidget::item{
	background-color: transparent;
	border-left:1px solid;
	border-top:1px solid;
}
QTableWidget::item:hover{
	background-color: rgba(57, 65, 80,150);
}
QTableWidget::item:selected{
	background-color: rgb(85, 170, 255);
}

QHeaderView{
background-color:transparent;
}

QHeaderView::section:horizontal
{
	border: 1px solid rgb(32, 34, 42);
	background-color: rgb(27, 29, 35);
	padding: 3px;
	color:rgb(175, 175, 185);
	border-top-left-radius: 8px;
	border-top-right-radius: 8px;
}

QHeaderView::section:vertical
{
	border: 1px solid rgb(32, 34, 42);
	background-color: rgb(27, 29, 35);
	padding-left:2px;
	color:rgb(175, 175, 185);
	border-bottom-right-radius:6px;
	border-top-right-radius: 6px;
}""")

	def DisplayFetchedData(self):
		global fetchedBillingData
		TotalCost=0
		for data in fetchedBillingData:
			column=0
			row = self.DetailReceipt.rowCount()
			self.DetailReceipt.insertRow(row)
			while column!=3:
				if column==2:
					Moneydata="₹"+str(data[column])
					self.DetailReceipt.setItem(row, column, QtWidgets.QTableWidgetItem(Moneydata))
				else:
					self.DetailReceipt.setItem(row, column, QtWidgets.QTableWidgetItem(str(data[column])))	
				column+=1		
			TotalCost+=int(data[2])
		self.TotalAmount.setText(self.TotalAmount.text()+str(TotalCost))

	def IDScanCompleteFunc(self):	
		global x2
		global PicName
		self.IDPreview.setPixmap(QtGui.QPixmap(PicName))
		self.IDPreview.setScaledContents(True)
		with open(PicName, 'rb') as file:
			x2=file.read()
		self.IDScan.setEnabled(True)

	def ModifyCheckInFunc(self):
		global NewCheckInDate
		self.ModifyCheckInButton.setEnabled(False)
		NewCheckInDate=self.ModifyCheckIn.text()
		self.ModifyCheckInThreadRunner=ModifyCheckInThread()
		self.ModifyCheckInThreadRunner.start()
		self.ModifyCheckInThreadRunner.ModifiedCheckIn.connect(lambda:self.CheckInModification())	
	def CheckInModification(self):
		self.ModifyCheckInButton.setEnabled(True)
		self.GuestCheckInLab.setText("Check-In Date: "+NewCheckInDate)
		ctypes.windll.user32.MessageBoxW(0, "Check-In Date Modified Sucessfully", "GMS Notifier", 0)

	def ModifyCheckOutFunc(self):
		global NewCheckOutDate
		self.ModifyCheckOutButton.setEnabled(False)
		NewCheckOutDate=self.ModifyCheckOut.text()
		self.ModifyCheckOutTheadRunner=ModifyCheckOutThread()
		self.ModifyCheckOutTheadRunner.start()
		self.ModifyCheckOutTheadRunner.ModifiedCheckOut.connect(lambda:self.CheckOutModification())	
	def CheckOutModification(self):
		self.ModifyCheckOutButton.setEnabled(True)
		self.GuestCheckOutLab.setText("Check-Out Date: "+NewCheckOutDate)
		ctypes.windll.user32.MessageBoxW(0, "Check-Out Date Modified Sucessfully", "GMS Notifier", 0)

	def IDScanFunc(self):
		self.IDScan.setEnabled(False)
		self.ScanThread=IDScanThread()
		self.ScanThread.start()
		self.ScanThread.ScanComplete.connect(lambda :self.IDScanCompleteFunc())
		
	def RoomSel(self,SelRoomNoOrig):
		global SelRoomNo
		SelRoomNo=SelRoomNoOrig
		#print("SelRoomNo0 ",SelRoomNo)
		self.RoomPage.setGeometry(QtCore.QRect(0, 0, 0, 571))
		self.GMSPage.setGeometry(QtCore.QRect(0, 0, 831, 571))
		self.getGuestInforunner=getGuestInfo()
		self.getGuestInforunner.start()
		self.getGuestInforunner.fetchedGuestInfo.connect(lambda:self.displayGuestInfo())

	def displayGuestInfo(self):
		#print(self.getGuestInforunner.isFinished())
		global d1,d2,d3,d4,d5,d6,d7,SelRoomNo
		self.GuestNameLab.setText(self.GuestNameLab.text()+d1)
		self.GuestEmailIDLab.setText(self.GuestEmailIDLab.text()+d6)
		self.GuestPhoneNoLab.setText(self.GuestPhoneNoLab.text()+d7)
		self.GuestCheckInLab.setText(self.GuestCheckInLab.text()+d2)
		self.GuestCheckOutLab.setText(self.GuestCheckOutLab.text()+d3)
		tempdata=RoomTypeDict[int(SelRoomNo)]
		tempdata=self.RoomTypeLab.text()+tempdata
		self.RoomTypeLab.setText(tempdata)
		self.RoomNoLab.setText(self.RoomNoLab.text()+str(SelRoomNo))

	def RoomDisplay(self):
			self.setupUi(MainWindow)
			self.RegistrationPage.setGeometry(QtCore.QRect(0, 90, 0, 571))
			self.RoomPage.setGeometry(QtCore.QRect(0, 0, 831, 571))
			self.Button101.clicked.connect(lambda:self.RoomSel(101))
			self.Button102.clicked.connect(lambda:self.RoomSel(102))
			self.Button103.clicked.connect(lambda:self.RoomSel(103))
			self.Button104.clicked.connect(lambda:self.RoomSel(104))
			self.Button201.clicked.connect(lambda:self.RoomSel(201))
			self.Button202.clicked.connect(lambda:self.RoomSel(202))
			self.Button203.clicked.connect(lambda:self.RoomSel(203))
			self.Button301.clicked.connect(lambda:self.RoomSel(301))
			self.Button302.clicked.connect(lambda:self.RoomSel(302))
			self.Button303.clicked.connect(lambda:self.RoomSel(303))

		
	def Registration(self):
		global x1,x2,x3,x4,x5,x6,x7,room
		x1=self.GuestName.text()
		x3=self.CheckIn.text()
		x7=x3
		checkoutvar=self.CheckOut.text()
		#print(checkoutvar)
		timevar2=str(checkoutvar).split(" ")
		timevar2=timevar2[1]
		timevar=str(x3).split(" ")[1]
		x3=str(str(x3).split(" ")[0])+"."+str(str(checkoutvar).split(" ")[0])
		#print(x3)
		x4=timevar+"."+timevar2
		x5=self.GuestEmailID.text()
		x6=self.GuestPhoneNo.text()
		room=self.RoomNumber.currentText()
		self.QueryThread=RegistrationThread()
		self.Book.setEnabled(False)
		self.QueryThread.start()
		self.QueryThread.QueryComplete.connect(lambda:self.doneRegistration())

	def doneRegistration(self):
		ctypes.windll.user32.MessageBoxW(0, "Room Booked", "Registration", 0)
		self.setupUi(MainWindow)	
		self.Book.setEnabled(True)

	def retranslateUi(self, MainWindow):
		_translate = QtCore.QCoreApplication.translate
		MainWindow.setWindowTitle(_translate("MainWindow", "KVS Hotel Groups"))
		self.GuestName.setPlaceholderText(_translate("MainWindow", "Guest\' s Name"))
		self.GuestPhoneNo.setPlaceholderText(_translate("MainWindow", "Guest\' s Phone No."))
		self.GuestEmailID.setPlaceholderText(_translate("MainWindow", "Guest\' s Email ID"))
		self.RoomType.setPlaceholderText(_translate("MainWindow", "Room Type"))
		self.CheckInLab.setText(_translate("MainWindow", "Check-In"))
		self.CheckOutLab.setText(_translate("MainWindow", "Check-Out"))
		self.RoomNumber.setPlaceholderText(_translate("MainWindow", "Room Number"))
		self.Book.setText(_translate("MainWindow", "Book"))
		self.IDScan.setText(_translate("MainWindow", "ID Scan"))
		self.HotelWelcome.setText(_translate("MainWindow", "Welcome to KVS Hotel Groups"))
		self.ReceiptGen.setText(_translate("MainWindow", "Generate Receipt"))
		item = self.DetailReceipt.horizontalHeaderItem(0)
		item.setText(_translate("MainWindow", "Date"))
		item = self.DetailReceipt.horizontalHeaderItem(1)
		item.setText(_translate("MainWindow", "Description"))
		item = self.DetailReceipt.horizontalHeaderItem(2)
		item.setText(_translate("MainWindow", "Amount"))
		self.TotalAmount.setText(_translate("MainWindow", "Total Amount: ₹"))
		self.Label303.setText(_translate("MainWindow", "303"))
		self.Label302.setText(_translate("MainWindow", "302"))
		self.Label201.setText(_translate("MainWindow", "201"))
		self.Label203.setText(_translate("MainWindow", "203"))
		self.Label102.setText(_translate("MainWindow", "102"))
		self.Label104.setText(_translate("MainWindow", "104"))
		self.Label103.setText(_translate("MainWindow", "103"))
		self.Label301.setText(_translate("MainWindow", "301"))
		self.Label101.setText(_translate("MainWindow", "101"))
		self.Label202.setText(_translate("MainWindow", "202"))
		self.ServiceDateLabel.setText(_translate("MainWindow", "Date"))
		self.ServiceDescription.setPlaceholderText(_translate("MainWindow", "Description"))
		self.Quantity.setSpecialValueText(_translate("MainWindow", "Quantity"))
		self.ServiceCharge.setPlaceholderText(_translate("MainWindow", "Amount"))
		self.AddtoBillButton.setText(_translate("MainWindow", "Add"))
		self.RoomDetailsLab.setText(_translate("MainWindow", "Room Details"))
		self.GuestNameLab.setText(_translate("MainWindow", "Guest\'s Name: "))
		self.GuestEmailIDLab.setText(_translate("MainWindow", "Guest\'s EmailID: "))
		self.GuestPhoneNoLab.setText(_translate("MainWindow", "Guest\'s Phone No.: "))
		self.RoomTypeLab.setText(_translate("MainWindow", "Room Type: "))
		self.RoomNoLab.setText(_translate("MainWindow", "Room No.: "))
		self.GuestCheckInLab.setText(_translate("MainWindow", "Check-In Date: "))
		self.GuestCheckOutLab.setText(_translate("MainWindow", "Check-Out Date: "))
		self.ModifyCheckOutButton.setText(_translate("MainWindow", " Modify"))
		self.ModifyCheckOutLab.setText(_translate("MainWindow", "Modify Check-Out Date:"))
		self.ContToBillingButton.setText(_translate("MainWindow", "Continue to Billing →"))
		self.ModifyCheckInLab.setText(_translate("MainWindow", "Modify Check-In Date:"))
		self.AddtoBillLab.setText(_translate("MainWindow", "Add to Bill:"))
		self.ModifyCheckInButton.setText(_translate("MainWindow", " Modify"))
		self.MainLab.setText(_translate("MainWindow", "KVS Hotel Management Software"))
		self.RegistrationButton.setText(_translate("MainWindow", "Registration"))
		self.RoomsButton.setText(_translate("MainWindow", "    Rooms"))
		self.NotificationButton.setText(_translate("MainWindow", "Notifications"))


if __name__ == "__main__":
	import sys
	app = QtWidgets.QApplication(sys.argv)
	app.setStyleSheet('QMainWindow{background-color: darkgray;border: 1px solid black;}')
	MainWindow = QtWidgets.QMainWindow()
	ui = Ui_MainWindow()
	ui.setMouseTracking(True)
	MainWindow.setWindowFlags(QtCore.Qt.FramelessWindowHint)
	ui.setupUi(MainWindow)
	MainWindow.show()
	sys.exit(app.exec_())