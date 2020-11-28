# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QPoint
from PyQt5.QtCore import QThread,pyqtSignal
from PyQt5.QtGui import QCursor, QMovie
from PyQt5.QtCore import Qt
import Menu
import ctypes
import sys
from datetime import datetime
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QWidget
import mysql.connector
from PyQt5 import QtWebEngineWidgets
from PyQt5.QtWebEngineWidgets import QWebEngineSettings

MB_OK = 0x0
MB_OKCL = 0x01
MB_YESNOCL = 0x03
MB_YESNO = 0x04
ICON_EXLAIM=0x30
ICON_INFO = 0x40
ICON_QUES = 0x20
ICON_STOP = 0x10

mydb = mysql.connector.connect(		#This one is for the regular Data sending and Receiving 
  host="localhost",
  user="root",
  passwd='<redacted>',
  database="hotelkvs",
  port=3306
  )
mycursor=mydb.cursor(buffered=True)

with open("room.data",'r') as file:
	RoomNumber=file.readlines()
	RoomNumber=RoomNumber[0]

class NotifyMenu(QThread):
	NotifiedMenu=pyqtSignal(int)
	def run(self):
		global TotalFoodItem
		Item=''
		Quantity=''
		SpecialNote=''
		for i in range(len(TotalFoodItem)):
			if i+1!=len(TotalFoodItem):
				Item+=TotalFoodItem[i][0]+'\n'
				Quantity+=TotalFoodItem[i][1]+'\n'
				SpecialNote+=TotalFoodItem[i][2]+'\n'
			else:
				Item+=TotalFoodItem[i][0]
				Quantity+=TotalFoodItem[i][1]
				SpecialNote+=TotalFoodItem[i][2]
				print("Final")
		print(Item, Quantity, SpecialNote)
		now = datetime.now()
		date = now.strftime("%d-%m-%Y %H:%M")
		mycursor.execute('insert into Notify values("Food","%s","%s","%s","%s","%s")'%(date,Item,Quantity,SpecialNote,RoomNumber))
		mydb.commit()
		self.NotifiedMenu.emit(1)

class RatingThread(QThread):
	RatingEntered=pyqtSignal(int)
	def run(self):
		global TotalRating
		mycursor.execute("Update GData set Rate='%s' where Room='%s'"%(TotalRating,RoomNumber))
		mydb.commit()
		self.RatingEntered.emit(1)


class FrontDeskPing(QThread):
	FrontDeskPingged=pyqtSignal(int)
	def run(self):
		mycursor.execute("insert into Notify values('Front Desk',NULL,NULL,NULL,NULL,'%s')"%RoomNumber)
		mydb.commit()
		self.FrontDeskPingged.emit(1)

	
class RequestDNDon(QThread):
	RequestedDNDon=pyqtSignal(int)
	def run(self):
		mycursor.execute("insert into Notify values('DND On',NULL,NULL,NULL,NULL,'%s')"%RoomNumber)
		mydb.commit()
		self.RequestedDNDon.emit(1)
class RequestDNDoff(QThread):
	RequestedDNDoff=pyqtSignal(int)
	def run(self):
		mycursor.execute("insert into Notify values('DND Off',NULL,NULL,NULL,NULL,'%s')"%RoomNumber)
		mydb.commit()
		self.RequestedDNDoff.emit(1)

class RequestRoomService(QThread):
	RequestedRoomService=pyqtSignal(int)
	def run(self):
		mycursor.execute("insert into Notify values('Room Service',NULL,NULL,NULL,NULL,'%s')"%RoomNumber)
		mydb.commit()
		self.RequestedRoomService.emit(1)

class getCurrentCheckoutdate(QThread):
	gotCurrentCheckoutDate=pyqtSignal(int)
	def run(self):
		global currentCheckoutDate
		mycursor.execute("select Date, Time from GData where Room='%s'"%RoomNumber)
		Data=mycursor.fetchone()
		Date=Data[0].split('.')[1]
		Time=Data[1].split('.')[1]
		currentCheckoutDate=Date+" "+Time
		self.gotCurrentCheckoutDate.emit(1) 


class NotifyNewCheckoutDate(QThread):
	NotifiedNewCheckoutDate=pyqtSignal(int)
	def run(self):
		global NewCheckOutDate
		mycursor.execute("insert into notify values('Change CheckOut Date',NULL,'%s',NULL,NULL,'%s')"%(NewCheckOutDate,RoomNumber))
		mydb.commit()
		self.NotifiedNewCheckoutDate.emit(1)

class Ui_MainWindow(QWidget):
	def setupUi(self, MainWindow):
		MainWindow.setObjectName("MainWindow")
		MainWindow.resize(800, 530)
		MainWindow.setMinimumSize(QtCore.QSize(800, 530))
		MainWindow.setMaximumSize(QtCore.QSize(800, 530))
		MainWindow.setWindowIcon(QtGui.QIcon("icons/LogoHead.png"))
		self.centralwidget = QtWidgets.QWidget(MainWindow)
		self.centralwidget.setObjectName("centralwidget")
		self.TopFrame = QtWidgets.QWidget(self.centralwidget)
		self.TopFrame.setGeometry(QtCore.QRect(0, 0, 801, 41))
		self.TopFrame.setStyleSheet("background-color:rgb(255, 255, 255)")
		self.TopFrame.setObjectName("TopFrame")
		self.SubTopFrame = QtWidgets.QWidget(self.TopFrame)
		self.SubTopFrame.setGeometry(QtCore.QRect(0, 0, 801, 41))
		self.SubTopFrame.setStyleSheet("background-color: rgb(75, 171, 255);")
		self.SubTopFrame.setObjectName("SubTopFrame")
		self.Exit = QtWidgets.QPushButton(self.SubTopFrame)
		self.Exit.setGeometry(QtCore.QRect(769, -1, 31, 31))
		self.Exit.setStyleSheet("QPushButton {    \n"
"    border: none;\n"
"    background-color: transparent;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: rgb(125, 188, 255);\n"
"}\n"
"QPushButton:pressed {    \n"
"    background-color:  rgb(250, 50, 50);\n"
"}")
		self.Exit.setText("")
		icon = QtGui.QIcon()
		icon.addPixmap(QtGui.QPixmap("icons/cil-x.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.Exit.setIcon(icon)
		self.Exit.setObjectName("Exit")
		self.Minimize = QtWidgets.QPushButton(self.SubTopFrame)
		self.Minimize.setGeometry(QtCore.QRect(740, -1, 31, 31))
		self.Minimize.setStyleSheet("QPushButton {    \n"
"    border: none;\n"
"    background-color: transparent;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: rgb(125, 188, 255);\n"
"}\n"
"QPushButton:pressed {    \n"
"    background-color:  rgb(125, 188, 255);\n"
"}")
		self.Minimize.setText("")
		icon1 = QtGui.QIcon()
		icon1.addPixmap(QtGui.QPixmap("icons/cil-window-minimize.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.Minimize.setIcon(icon1)
		self.Minimize.setObjectName("Minimize")
		self.Info = QtWidgets.QPushButton(self.SubTopFrame)
		self.Info.setGeometry(QtCore.QRect(710, -1, 31, 31))
		self.Info.setStyleSheet("QPushButton {    \n"
"    border: none;\n"
"    background-color: transparent;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: rgb(125, 188, 255);\n"
"}\n"
"QPushButton:pressed {    \n"
"    background-color:  rgb(125, 188, 255);\n"
"}")
		self.Info.setText("")
		icon2 = QtGui.QIcon()
		icon2.addPixmap(QtGui.QPixmap("icons/cil-information.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.Info.setIcon(icon2)
		self.Info.setObjectName("Info")
		self.MainLab = QtWidgets.QLabel(self.SubTopFrame)
		self.MainLab.setGeometry(QtCore.QRect(9, 4, 211, 21))
		palette = QtGui.QPalette()
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(75, 171, 255))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(75, 171, 255))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(75, 171, 255))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(98, 98, 98))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.PlaceholderText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(75, 171, 255))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(75, 171, 255))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(75, 171, 255))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
		brush = QtGui.QBrush(QtGui.QColor(98, 98, 98))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.PlaceholderText, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
		brush = QtGui.QBrush(QtGui.QColor(75, 171, 255))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
		brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
		brush = QtGui.QBrush(QtGui.QColor(75, 171, 255))
		brush.setStyle(QtCore.Qt.SolidPattern)
		palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
		brush = QtGui.QBrush(QtGui.QColor(75, 171, 255))
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
		self.MainLab.setStyleSheet("color:rgb(0, 0, 0)")
		self.MainLab.setObjectName("MainLab")
		self.Main = QtWidgets.QWidget(self.centralwidget)
		self.Main.setGeometry(QtCore.QRect(0, 30, 801, 521))
		self.Main.setStyleSheet("background-color:rgb(24, 255, 228);")
		self.Main.setObjectName("Main")
		self.SubMain = QtWidgets.QWidget(self.Main)
		self.SubMain.setGeometry(QtCore.QRect(30, 27, 741, 441))
		self.SubMain.setStyleSheet("background-color:rgba(250, 250, 250, 150);\n"
"border:3px solid;\n"
"border-radius:10px;\n"
"border-color: rgb(0, 36, 114);")
		self.SubMain.setObjectName("SubMain")
		self.Partition1 = QtWidgets.QFrame(self.SubMain)
		self.Partition1.setGeometry(QtCore.QRect(380, 0, 4, 441))
		self.Partition1.setFrameShape(QtWidgets.QFrame.VLine)
		self.Partition1.setFrameShadow(QtWidgets.QFrame.Sunken)
		self.Partition1.setObjectName("Partition1")
		self.Partition2 = QtWidgets.QFrame(self.SubMain)
		self.Partition2.setGeometry(QtCore.QRect(180, 0, 4, 441))
		self.Partition2.setFrameShape(QtWidgets.QFrame.VLine)
		self.Partition2.setFrameShadow(QtWidgets.QFrame.Sunken)
		self.Partition2.setObjectName("Partition2")
		self.Partition3 = QtWidgets.QFrame(self.SubMain)
		self.Partition3.setGeometry(QtCore.QRect(560, 0, 4, 441))
		self.Partition3.setFrameShape(QtWidgets.QFrame.VLine)
		self.Partition3.setFrameShadow(QtWidgets.QFrame.Sunken)
		self.Partition3.setObjectName("Partition3")
		self.Partition4 = QtWidgets.QFrame(self.SubMain)
		self.Partition4.setGeometry(QtCore.QRect(0, 220, 741, 4))
		self.Partition4.setToolTipDuration(5)
		self.Partition4.setFrameShape(QtWidgets.QFrame.HLine)
		self.Partition4.setFrameShadow(QtWidgets.QFrame.Sunken)
		self.Partition4.setObjectName("Partition4")
		self.MenuButton = QtWidgets.QPushButton(self.SubMain)
		self.MenuButton.setGeometry(QtCore.QRect(34, 30, 111, 121))
		self.MenuButton.setStyleSheet("QPushButton {    \n"
"    border: none;\n"
"    background-color: transparent;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: rgba(240, 240, 240,150);\n"
"}\n"
"QPushButton:pressed {    \n"
"    background-color:  rgba(240, 240, 240,150);\n"
"}")
		self.MenuButton.setText("")
		icon3 = QtGui.QIcon()
		icon3.addPixmap(QtGui.QPixmap("icons/cil-menu.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.MenuButton.setIcon(icon3)
		self.MenuButton.setIconSize(QtCore.QSize(100, 255))
		self.MenuButton.setObjectName("MenuButton")
		self.DNDButton = QtWidgets.QPushButton(self.SubMain)
		self.DNDButton.setGeometry(QtCore.QRect(230, 30, 111, 121))
		self.DNDButton.setStyleSheet("QPushButton {    \n"
"    border: none;\n"
"    background-color: transparent;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: rgba(240, 240, 240,150);\n"
"}\n"
"QPushButton:pressed {    \n"
"    background-color:  rgba(240, 240, 240,150);\n"
"}")
		self.DNDButton.setText("")
		icon4 = QtGui.QIcon()
		icon4.addPixmap(QtGui.QPixmap("icons/cil-dnd.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.DNDButton.setIcon(icon4)
		self.DNDButton.setIconSize(QtCore.QSize(100, 255))
		self.DNDButton.setObjectName("DNDButton")
		self.RoomServiceButton = QtWidgets.QPushButton(self.SubMain)
		self.RoomServiceButton.setGeometry(QtCore.QRect(228, 250, 111, 121))
		self.RoomServiceButton.setStyleSheet("QPushButton {    \n"
"    border: none;\n"
"    background-color: transparent;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: rgba(240, 240, 240,150);\n"
"}\n"
"QPushButton:pressed {    \n"
"    background-color:  rgba(240, 240, 240,150);\n"
"}")
		self.RoomServiceButton.setText("")
		icon5 = QtGui.QIcon()
		icon5.addPixmap(QtGui.QPixmap("icons/cil-housekeeping.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.RoomServiceButton.setIcon(icon5)
		self.RoomServiceButton.setIconSize(QtCore.QSize(100, 255))
		self.RoomServiceButton.setObjectName("RoomServiceButton")
		self.FrontDeskButton = QtWidgets.QPushButton(self.SubMain)
		self.FrontDeskButton.setGeometry(QtCore.QRect(600, 30, 111, 121))
		self.FrontDeskButton.setStyleSheet("QPushButton {    \n"
"    border: none;\n"
"    background-color: transparent;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: rgba(240, 240, 240,150);\n"
"}\n"
"QPushButton:pressed {    \n"
"    background-color:  rgba(240, 240, 240,150);\n"
"}")
		self.FrontDeskButton.setText("")
		icon6 = QtGui.QIcon()
		icon6.addPixmap(QtGui.QPixmap("icons/cil-deskbell.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.FrontDeskButton.setIcon(icon6)
		self.FrontDeskButton.setIconSize(QtCore.QSize(100, 255))
		self.FrontDeskButton.setObjectName("FrontDeskButton")
		self.CheckOutButton = QtWidgets.QPushButton(self.SubMain)
		self.CheckOutButton.setGeometry(QtCore.QRect(35, 250, 111, 121))
		self.CheckOutButton.setStyleSheet("QPushButton {    \n"
"    border: none;\n"
"    background-color: transparent;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: rgba(240, 240, 240,150);\n"
"}\n"
"QPushButton:pressed {    \n"
"    background-color:  rgba(240, 240, 240,150);\n"
"}")
		self.CheckOutButton.setText("")
		icon7 = QtGui.QIcon()
		icon7.addPixmap(QtGui.QPixmap("icons/cil-calendar.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.CheckOutButton.setIcon(icon7)
		self.CheckOutButton.setIconSize(QtCore.QSize(100, 255))
		self.CheckOutButton.setObjectName("CheckOutButton")
		self.AboutUsButton = QtWidgets.QPushButton(self.SubMain)
		self.AboutUsButton.setGeometry(QtCore.QRect(425, 250, 111, 121))
		self.AboutUsButton.setStyleSheet("QPushButton {    \n"
"    border: none;\n"
"    background-color: transparent;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: rgba(240, 240, 240,150);\n"
"}\n"
"QPushButton:pressed {    \n"
"    background-color:  rgba(240, 240, 240,150);\n"
"}")
		self.AboutUsButton.setText("")
		icon8 = QtGui.QIcon()
		icon8.addPixmap(QtGui.QPixmap("icons/cil-question.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.AboutUsButton.setIcon(icon8)
		self.AboutUsButton.setIconSize(QtCore.QSize(100, 255))
		self.AboutUsButton.setObjectName("AboutUsButton")
		self.ENPButton = QtWidgets.QPushButton(self.SubMain)
		self.ENPButton.setGeometry(QtCore.QRect(420, 30, 111, 121))
		self.ENPButton.setStyleSheet("QPushButton {    \n"
"    border: none;\n"
"    background-color: transparent;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: rgba(240, 240, 240,150);\n"
"}\n"
"QPushButton:pressed {    \n"
"    background-color:  rgba(240, 240, 240,150);\n"
"}")
		self.ENPButton.setText("")
		icon9 = QtGui.QIcon()
		icon9.addPixmap(QtGui.QPixmap("icons/cil-newspaper.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.ENPButton.setIcon(icon9)
		self.ENPButton.setIconSize(QtCore.QSize(100, 255))
		self.ENPButton.setObjectName("ENPButton")
		self.RateUsButton = QtWidgets.QPushButton(self.SubMain)
		self.RateUsButton.setGeometry(QtCore.QRect(600, 250, 111, 121))
		self.RateUsButton.setStyleSheet("QPushButton {    \n"
"    border: none;\n"
"    background-color: transparent;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: rgba(240, 240, 240,150);\n"
"}\n"
"QPushButton:pressed {    \n"
"    background-color:  rgba(240, 240, 240,150);\n"
"}")
		self.RateUsButton.setText("")
		icon10 = QtGui.QIcon()
		icon10.addPixmap(QtGui.QPixmap("icons/cil-star.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.RateUsButton.setIcon(icon10)
		self.RateUsButton.setIconSize(QtCore.QSize(100, 255))
		self.RateUsButton.setObjectName("RateUsButton")
		self.MenuLab = QtWidgets.QLabel(self.SubMain)
		self.MenuLab.setGeometry(QtCore.QRect(20, 160, 141, 31))
		font = QtGui.QFont()
		font.setFamily("Segoe UI")
		font.setPointSize(10)
		font.setBold(True)
		font.setWeight(75)
		self.MenuLab.setFont(font)
		self.MenuLab.setStyleSheet("background-color:rgb(0, 36, 114);\n"
"color:white;\n"
"border-color:rgb(0, 0, 0)")
		self.MenuLab.setAlignment(QtCore.Qt.AlignCenter)
		self.MenuLab.setObjectName("MenuLab")
		self.DNDLab = QtWidgets.QLabel(self.SubMain)
		self.DNDLab.setGeometry(QtCore.QRect(238, 160, 91, 31))
		font = QtGui.QFont()
		font.setFamily("Segoe UI")
		font.setPointSize(10)
		font.setBold(True)
		font.setWeight(75)
		self.DNDLab.setFont(font)
		self.DNDLab.setStyleSheet("background-color:rgb(0, 36, 114);\n"
"color:white;\n"
"border-color:rgb(0, 0, 0)")
		self.DNDLab.setAlignment(QtCore.Qt.AlignCenter)
		self.DNDLab.setObjectName("DNDLab")
		self.RoomServiceLab = QtWidgets.QLabel(self.SubMain)
		self.RoomServiceLab.setGeometry(QtCore.QRect(234, 380, 101, 31))
		font = QtGui.QFont()
		font.setFamily("Segoe UI")
		font.setPointSize(10)
		font.setBold(True)
		font.setWeight(75)
		self.RoomServiceLab.setFont(font)
		self.RoomServiceLab.setStyleSheet("background-color:rgb(0, 36, 114);\n"
"color:white;\n"
"border-color:rgb(0, 0, 0)")
		self.RoomServiceLab.setAlignment(QtCore.Qt.AlignCenter)
		self.RoomServiceLab.setObjectName("RoomServiceLab")
		self.FrontDeskLab = QtWidgets.QLabel(self.SubMain)
		self.FrontDeskLab.setGeometry(QtCore.QRect(604, 160, 101, 31))
		font = QtGui.QFont()
		font.setFamily("Segoe UI")
		font.setPointSize(10)
		font.setBold(True)
		font.setWeight(75)
		self.FrontDeskLab.setFont(font)
		self.FrontDeskLab.setStyleSheet("background-color:rgb(0, 36, 114);\n"
"color:white;\n"
"border-color:rgb(0, 0, 0)")
		self.FrontDeskLab.setAlignment(QtCore.Qt.AlignCenter)
		self.FrontDeskLab.setObjectName("FrontDeskLab")
		self.CheckOutLab = QtWidgets.QLabel(self.SubMain)
		self.CheckOutLab.setGeometry(QtCore.QRect(24, 380, 131, 41))
		font = QtGui.QFont()
		font.setFamily("Segoe UI")
		font.setPointSize(10)
		font.setBold(True)
		font.setWeight(75)
		self.CheckOutLab.setFont(font)
		self.CheckOutLab.setStyleSheet("background-color:rgb(0, 36, 114);\n"
"color:white;\n"
"border-color:rgb(0, 0, 0)")
		self.CheckOutLab.setAlignment(QtCore.Qt.AlignCenter)
		self.CheckOutLab.setObjectName("CheckOutLab")
		self.ENPLab = QtWidgets.QLabel(self.SubMain)
		self.ENPLab.setGeometry(QtCore.QRect(425, 160, 101, 31))
		font = QtGui.QFont()
		font.setFamily("Segoe UI")
		font.setPointSize(10)
		font.setBold(True)
		font.setWeight(75)
		self.ENPLab.setFont(font)
		self.ENPLab.setStyleSheet("background-color:rgb(0, 36, 114);\n"
"color:white;\n"
"border-color:rgb(0, 0, 0)")
		self.ENPLab.setAlignment(QtCore.Qt.AlignCenter)
		self.ENPLab.setObjectName("ENPLab")
		self.RateUsLab = QtWidgets.QLabel(self.SubMain)
		self.RateUsLab.setGeometry(QtCore.QRect(604, 380, 101, 31))
		font = QtGui.QFont()
		font.setFamily("Segoe UI")
		font.setPointSize(10)
		font.setBold(True)
		font.setWeight(75)
		self.RateUsLab.setFont(font)
		self.RateUsLab.setStyleSheet("background-color:rgb(0, 36, 114);\n"
"color:white;\n"
"border-color:rgb(0, 0, 0)")
		self.RateUsLab.setAlignment(QtCore.Qt.AlignCenter)
		self.RateUsLab.setObjectName("RateUsLab")
		self.AboutUsLab = QtWidgets.QLabel(self.SubMain)
		self.AboutUsLab.setGeometry(QtCore.QRect(430, 380, 101, 31))
		font = QtGui.QFont()
		font.setFamily("Segoe UI")
		font.setPointSize(10)
		font.setBold(True)
		font.setWeight(75)
		self.AboutUsLab.setFont(font)
		self.AboutUsLab.setStyleSheet("background-color:rgb(0, 36, 114);\n"
"color:white;\n"
"border-color:rgb(0, 0, 0)")
		self.AboutUsLab.setAlignment(QtCore.Qt.AlignCenter)
		self.AboutUsLab.setObjectName("AboutUsLab")
		self.BG = QtWidgets.QLabel(self.Main)
		self.BG.setGeometry(QtCore.QRect(0, 0, 801, 500))
		self.BG.setText("")
		self.BG.setPixmap(QtGui.QPixmap("background/bg7.jpg"))
		self.BG.setScaledContents(True)
		self.BG.setObjectName("BG")
		self.BG.raise_()
		self.SubMain.raise_()
		self.ENPPage = QtWidgets.QWidget(self.centralwidget)
		self.ENPPage.setGeometry(QtCore.QRect(0, 70, 0, 461))
		self.ENPPage.setStyleSheet("background-color:rgb(75, 171, 255);")
		self.ENPPage.setObjectName("ENPPage")

		self.SubENPPage1 = QtWebEngineWidgets.QWebEngineView(self.ENPPage)
		self.SubENPPage1.page().settings().setAttribute(QWebEngineSettings.AllowGeolocationOnInsecureOrigins, True)
		self.SubENPPage1.setZoomFactor(0.7)
		self.SubENPPage1.setGeometry(QtCore.QRect(9, 9, 781, 441))
		self.SubENPPage1.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"border:1px solid;\n"
"border-color:rgb(14, 36, 112);")
		self.SubENPPage1.setObjectName("SubENPPage1")

		self.SubENPPage = QtWebEngineWidgets.QWebEngineView(self.ENPPage)
		self.SubENPPage.page().settings().setAttribute(QWebEngineSettings.AllowGeolocationOnInsecureOrigins, True)
		self.SubENPPage.setZoomFactor(0.95)
		self.SubENPPage.setGeometry(QtCore.QRect(9, 9, 781, 441))
		self.SubENPPage.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"border:1px solid;\n"
"border-color:rgb(14, 36, 112);")
		self.SubENPPage.setObjectName("SubENPPage")
		self.RateUsPage = QtWidgets.QWidget(self.centralwidget)
		self.RateUsPage.setGeometry(QtCore.QRect(0, 70, 0, 461))
		self.RateUsPage.setStyleSheet("background-color:rgb(24, 255, 228);")
		self.RateUsPage.setObjectName("RateUsPage")
		self.BG2 = QtWidgets.QLabel(self.RateUsPage)
		self.BG2.setGeometry(QtCore.QRect(0, 0, 801, 461))
		self.BG2.setText("")
		self.BG2.setPixmap(QtGui.QPixmap("background/bg1.jpg"))
		self.BG2.setScaledContents(True)
		self.BG2.setObjectName("BG2")
		self.SubRateUsPage = QtWidgets.QWidget(self.RateUsPage)
		self.SubRateUsPage.setGeometry(QtCore.QRect(50, 30, 701, 391))
		self.SubRateUsPage.setStyleSheet("background-color:rgba(250, 250, 250, 150);\n"
"border:3px solid;\n"
"border-radius:10px;\n"
"border-color: rgb(0, 36, 114);")
		self.SubRateUsPage.setObjectName("SubRateUsPage")
		self.Star1 = QtWidgets.QPushButton(self.SubRateUsPage)
		self.Star1.setGeometry(QtCore.QRect(328, 55, 31, 31))
		self.Star1.setStyleSheet("background-color:transparent;\n"
"border:0px;")
		self.Star1.setText("")
		icon11 = QtGui.QIcon()
		icon11.addPixmap(QtGui.QPixmap("icons/cil-startrans.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.Star1.setIcon(icon11)
		self.Star1.setIconSize(QtCore.QSize(30, 30))
		self.Star1.setObjectName("Star1")
		self.Star1_2 = QtWidgets.QPushButton(self.SubRateUsPage)
		self.Star1_2.setGeometry(QtCore.QRect(392, 55, 31, 31))
		self.Star1_2.setStyleSheet("background-color:transparent;\n"
"border:0px;")
		self.Star1_2.setText("")
		self.Star1_2.setIcon(icon11)
		self.Star1_2.setIconSize(QtCore.QSize(30, 30))
		self.Star1_2.setObjectName("Star1_2")
		self.Star1_3 = QtWidgets.QPushButton(self.SubRateUsPage)
		self.Star1_3.setGeometry(QtCore.QRect(456, 55, 31, 31))
		self.Star1_3.setStyleSheet("background-color:transparent;\n"
"border:0px;")
		self.Star1_3.setText("")
		self.Star1_3.setIcon(icon11)
		self.Star1_3.setIconSize(QtCore.QSize(30, 30))
		self.Star1_3.setObjectName("Star1_3")
		self.Star1_4 = QtWidgets.QPushButton(self.SubRateUsPage)
		self.Star1_4.setGeometry(QtCore.QRect(520, 55, 31, 31))
		self.Star1_4.setStyleSheet("background-color:transparent;\n"
"border:0px;")
		self.Star1_4.setText("")
		self.Star1_4.setIcon(icon11)
		self.Star1_4.setIconSize(QtCore.QSize(30, 30))
		self.Star1_4.setObjectName("Star1_4")
		self.Star1_5 = QtWidgets.QPushButton(self.SubRateUsPage)
		self.Star1_5.setGeometry(QtCore.QRect(589, 55, 31, 31))
		self.Star1_5.setStyleSheet("background-color:transparent;\n"
"border:0px;")
		self.Star1_5.setText("")
		self.Star1_5.setIcon(icon11)
		self.Star1_5.setIconSize(QtCore.QSize(30, 30))
		self.Star1_5.setObjectName("Star1_5")
		self.Star2_2 = QtWidgets.QPushButton(self.SubRateUsPage)
		self.Star2_2.setGeometry(QtCore.QRect(392, 103, 31, 31))
		self.Star2_2.setStyleSheet("background-color:transparent;\n"
"border:0px;")
		self.Star2_2.setText("")
		self.Star2_2.setIcon(icon11)
		self.Star2_2.setIconSize(QtCore.QSize(30, 30))
		self.Star2_2.setObjectName("Star2_2")
		self.Star2_3 = QtWidgets.QPushButton(self.SubRateUsPage)
		self.Star2_3.setGeometry(QtCore.QRect(456, 103, 31, 31))
		self.Star2_3.setStyleSheet("background-color:transparent;\n"
"border:0px;")
		self.Star2_3.setText("")
		self.Star2_3.setIcon(icon11)
		self.Star2_3.setIconSize(QtCore.QSize(30, 30))
		self.Star2_3.setObjectName("Star2_3")
		self.Star2_4 = QtWidgets.QPushButton(self.SubRateUsPage)
		self.Star2_4.setGeometry(QtCore.QRect(520, 103, 31, 31))
		self.Star2_4.setStyleSheet("background-color:transparent;\n"
"border:0px;")
		self.Star2_4.setText("")
		self.Star2_4.setIcon(icon11)
		self.Star2_4.setIconSize(QtCore.QSize(30, 30))
		self.Star2_4.setObjectName("Star2_4")
		self.Star2_5 = QtWidgets.QPushButton(self.SubRateUsPage)
		self.Star2_5.setGeometry(QtCore.QRect(589, 103, 31, 31))
		self.Star2_5.setStyleSheet("background-color:transparent;\n"
"border:0px;")
		self.Star2_5.setText("")
		self.Star2_5.setIcon(icon11)
		self.Star2_5.setIconSize(QtCore.QSize(30, 30))
		self.Star2_5.setObjectName("Star2_5")
		self.Star2 = QtWidgets.QPushButton(self.SubRateUsPage)
		self.Star2.setGeometry(QtCore.QRect(328, 103, 31, 31))
		self.Star2.setStyleSheet("background-color:transparent;\n"
"border:0px;")
		self.Star2.setText("")
		self.Star2.setIcon(icon11)
		self.Star2.setIconSize(QtCore.QSize(30, 30))
		self.Star2.setObjectName("Star2")
		self.Star3_2 = QtWidgets.QPushButton(self.SubRateUsPage)
		self.Star3_2.setGeometry(QtCore.QRect(392, 154, 31, 31))
		self.Star3_2.setStyleSheet("background-color:transparent;\n"
"border:0px;")
		self.Star3_2.setText("")
		self.Star3_2.setIcon(icon11)
		self.Star3_2.setIconSize(QtCore.QSize(30, 30))
		self.Star3_2.setObjectName("Star3_2")
		self.Star3_3 = QtWidgets.QPushButton(self.SubRateUsPage)
		self.Star3_3.setGeometry(QtCore.QRect(456, 154, 31, 31))
		self.Star3_3.setStyleSheet("background-color:transparent;\n"
"border:0px;")
		self.Star3_3.setText("")
		self.Star3_3.setIcon(icon11)
		self.Star3_3.setIconSize(QtCore.QSize(30, 30))
		self.Star3_3.setObjectName("Star3_3")
		self.Star3_4 = QtWidgets.QPushButton(self.SubRateUsPage)
		self.Star3_4.setGeometry(QtCore.QRect(520, 154, 31, 31))
		self.Star3_4.setStyleSheet("background-color:transparent;\n"
"border:0px;")
		self.Star3_4.setText("")
		self.Star3_4.setIcon(icon11)
		self.Star3_4.setIconSize(QtCore.QSize(30, 30))
		self.Star3_4.setObjectName("Star3_4")
		self.Star3_5 = QtWidgets.QPushButton(self.SubRateUsPage)
		self.Star3_5.setGeometry(QtCore.QRect(589, 154, 31, 31))
		self.Star3_5.setStyleSheet("background-color:transparent;\n"
"border:0px;")
		self.Star3_5.setText("")
		self.Star3_5.setIcon(icon11)
		self.Star3_5.setIconSize(QtCore.QSize(30, 30))
		self.Star3_5.setObjectName("Star3_5")
		self.Star3 = QtWidgets.QPushButton(self.SubRateUsPage)
		self.Star3.setGeometry(QtCore.QRect(328, 154, 31, 31))
		self.Star3.setStyleSheet("background-color:transparent;\n"
"border:0px;")
		self.Star3.setText("")
		self.Star3.setIcon(icon11)
		self.Star3.setIconSize(QtCore.QSize(30, 30))
		self.Star3.setObjectName("Star3")
		self.FeedbackQuestion = QtWidgets.QLabel(self.SubRateUsPage)
		self.FeedbackQuestion.setGeometry(QtCore.QRect(88, 60, 151, 21))
		font = QtGui.QFont()
		font.setPointSize(12)
		font.setBold(True)
		font.setWeight(75)
		self.FeedbackQuestion.setFont(font)
		self.FeedbackQuestion.setStyleSheet("background:transparent;\n"
"border:0px;\n"
"")
		self.FeedbackQuestion.setObjectName("FeedbackQuestion")
		self.FeedbackBar = QtWidgets.QLabel(self.SubRateUsPage)
		self.FeedbackBar.setGeometry(QtCore.QRect(4, 10, 694, 31))
		font = QtGui.QFont()
		font.setBold(True)
		font.setWeight(75)
		self.FeedbackBar.setFont(font)
		self.FeedbackBar.setStyleSheet("border:2px;\n"
"border-radius:0px;")
		self.FeedbackBar.setObjectName("FeedbackBar")
		self.Star5 = QtWidgets.QPushButton(self.SubRateUsPage)
		self.Star5.setGeometry(QtCore.QRect(328, 259, 31, 31))
		self.Star5.setStyleSheet("background-color:transparent;\n"
"border:0px;")
		self.Star5.setText("")
		self.Star5.setIcon(icon11)
		self.Star5.setIconSize(QtCore.QSize(30, 30))
		self.Star5.setObjectName("Star5")
		self.Star5_2 = QtWidgets.QPushButton(self.SubRateUsPage)
		self.Star5_2.setGeometry(QtCore.QRect(392, 259, 31, 31))
		self.Star5_2.setStyleSheet("background-color:transparent;\n"
"border:0px;")
		self.Star5_2.setText("")
		self.Star5_2.setIcon(icon11)
		self.Star5_2.setIconSize(QtCore.QSize(30, 30))
		self.Star5_2.setObjectName("Star5_2")
		self.Star5_5 = QtWidgets.QPushButton(self.SubRateUsPage)
		self.Star5_5.setGeometry(QtCore.QRect(589, 259, 31, 31))
		self.Star5_5.setStyleSheet("background-color:transparent;\n"
"border:0px;")
		self.Star5_5.setText("")
		self.Star5_5.setIcon(icon11)
		self.Star5_5.setIconSize(QtCore.QSize(30, 30))
		self.Star5_5.setObjectName("Star5_5")
		self.Star5_4 = QtWidgets.QPushButton(self.SubRateUsPage)
		self.Star5_4.setGeometry(QtCore.QRect(520, 259, 31, 31))
		self.Star5_4.setStyleSheet("background-color:transparent;\n"
"border:0px;")
		self.Star5_4.setText("")
		self.Star5_4.setIcon(icon11)
		self.Star5_4.setIconSize(QtCore.QSize(30, 30))
		self.Star5_4.setObjectName("Star5_4")
		self.Star5_3 = QtWidgets.QPushButton(self.SubRateUsPage)
		self.Star5_3.setGeometry(QtCore.QRect(456, 259, 31, 31))
		self.Star5_3.setStyleSheet("background-color:transparent;\n"
"border:0px;")
		self.Star5_3.setText("")
		self.Star5_3.setIcon(icon11)
		self.Star5_3.setIconSize(QtCore.QSize(30, 30))
		self.Star5_3.setObjectName("Star5_3")
		self.Star6 = QtWidgets.QPushButton(self.SubRateUsPage)
		self.Star6.setGeometry(QtCore.QRect(328, 314, 31, 31))
		self.Star6.setStyleSheet("background-color:transparent;\n"
"border:0px;")
		self.Star6.setText("")
		self.Star6.setIcon(icon11)
		self.Star6.setIconSize(QtCore.QSize(30, 30))
		self.Star6.setObjectName("Star6")
		self.Star6_2 = QtWidgets.QPushButton(self.SubRateUsPage)
		self.Star6_2.setGeometry(QtCore.QRect(392, 314, 31, 31))
		self.Star6_2.setStyleSheet("background-color:transparent;\n"
"border:0px;")
		self.Star6_2.setText("")
		self.Star6_2.setIcon(icon11)
		self.Star6_2.setIconSize(QtCore.QSize(30, 30))
		self.Star6_2.setObjectName("Star6_2")
		self.Star6_5 = QtWidgets.QPushButton(self.SubRateUsPage)
		self.Star6_5.setGeometry(QtCore.QRect(589, 314, 31, 31))
		self.Star6_5.setStyleSheet("background-color:transparent;\n"
"border:0px;")
		self.Star6_5.setText("")
		self.Star6_5.setIcon(icon11)
		self.Star6_5.setIconSize(QtCore.QSize(30, 30))
		self.Star6_5.setObjectName("Star6_5")
		self.Star6_4 = QtWidgets.QPushButton(self.SubRateUsPage)
		self.Star6_4.setGeometry(QtCore.QRect(520, 314, 31, 31))
		self.Star6_4.setStyleSheet("background-color:transparent;\n"
"border:0px;")
		self.Star6_4.setText("")
		self.Star6_4.setIcon(icon11)
		self.Star6_4.setIconSize(QtCore.QSize(30, 30))
		self.Star6_4.setObjectName("Star6_4")
		self.Star6_3 = QtWidgets.QPushButton(self.SubRateUsPage)
		self.Star6_3.setGeometry(QtCore.QRect(456, 314, 31, 31))
		self.Star6_3.setStyleSheet("background-color:transparent;\n"
"border:0px;")
		self.Star6_3.setText("")
		self.Star6_3.setIcon(icon11)
		self.Star6_3.setIconSize(QtCore.QSize(30, 30))
		self.Star6_3.setObjectName("Star6_3")
		self.Star4 = QtWidgets.QPushButton(self.SubRateUsPage)
		self.Star4.setGeometry(QtCore.QRect(328, 206, 31, 31))
		self.Star4.setStyleSheet("background-color:transparent;\n"
"border:0px;")
		self.Star4.setText("")
		self.Star4.setIcon(icon11)
		self.Star4.setIconSize(QtCore.QSize(30, 30))
		self.Star4.setObjectName("Star4")
		self.Star4_2 = QtWidgets.QPushButton(self.SubRateUsPage)
		self.Star4_2.setGeometry(QtCore.QRect(392, 206, 31, 31))
		self.Star4_2.setStyleSheet("background-color:transparent;\n"
"border:0px;")
		self.Star4_2.setText("")
		self.Star4_2.setIcon(icon11)
		self.Star4_2.setIconSize(QtCore.QSize(30, 30))
		self.Star4_2.setObjectName("Star4_2")
		self.Star4_5 = QtWidgets.QPushButton(self.SubRateUsPage)
		self.Star4_5.setGeometry(QtCore.QRect(589, 206, 31, 31))
		self.Star4_5.setStyleSheet("background-color:transparent;\n"
"border:0px;")
		self.Star4_5.setText("")
		self.Star4_5.setIcon(icon11)
		self.Star4_5.setIconSize(QtCore.QSize(30, 30))
		self.Star4_5.setObjectName("Star4_5")
		self.Star4_4 = QtWidgets.QPushButton(self.SubRateUsPage)
		self.Star4_4.setGeometry(QtCore.QRect(520, 206, 31, 31))
		self.Star4_4.setStyleSheet("background-color:transparent;\n"
"border:0px;")
		self.Star4_4.setText("")
		self.Star4_4.setIcon(icon11)
		self.Star4_4.setIconSize(QtCore.QSize(30, 30))
		self.Star4_4.setObjectName("Star4_4")
		self.Star4_3 = QtWidgets.QPushButton(self.SubRateUsPage)
		self.Star4_3.setGeometry(QtCore.QRect(456, 206, 31, 31))
		self.Star4_3.setStyleSheet("background-color:transparent;\n"
"border:0px;")
		self.Star4_3.setText("")
		self.Star4_3.setIcon(icon11)
		self.Star4_3.setIconSize(QtCore.QSize(30, 30))
		self.Star4_3.setObjectName("Star4_3")
		self.FeedbackQuestion_2 = QtWidgets.QLabel(self.SubRateUsPage)
		self.FeedbackQuestion_2.setGeometry(QtCore.QRect(88, 110, 151, 21))
		font = QtGui.QFont()
		font.setPointSize(12)
		font.setBold(True)
		font.setWeight(75)
		self.FeedbackQuestion_2.setFont(font)
		self.FeedbackQuestion_2.setStyleSheet("background:transparent;\n"
"border:0px;\n"
"")
		self.FeedbackQuestion_2.setObjectName("FeedbackQuestion_2")
		self.FeedbackQuestion_3 = QtWidgets.QLabel(self.SubRateUsPage)
		self.FeedbackQuestion_3.setGeometry(QtCore.QRect(88, 161, 151, 21))
		font = QtGui.QFont()
		font.setPointSize(12)
		font.setBold(True)
		font.setWeight(75)
		self.FeedbackQuestion_3.setFont(font)
		self.FeedbackQuestion_3.setStyleSheet("background:transparent;\n"
"border:0px;\n"
"")
		self.FeedbackQuestion_3.setObjectName("FeedbackQuestion_3")
		self.FeedbackQuestion_4 = QtWidgets.QLabel(self.SubRateUsPage)
		self.FeedbackQuestion_4.setGeometry(QtCore.QRect(88, 214, 151, 21))
		font = QtGui.QFont()
		font.setPointSize(12)
		font.setBold(True)
		font.setWeight(75)
		self.FeedbackQuestion_4.setFont(font)
		self.FeedbackQuestion_4.setStyleSheet("background:transparent;\n"
"border:0px;\n"
"")
		self.FeedbackQuestion_4.setObjectName("FeedbackQuestion_4")
		self.FeedbackQuestion_5 = QtWidgets.QLabel(self.SubRateUsPage)
		self.FeedbackQuestion_5.setGeometry(QtCore.QRect(88, 262, 151, 21))
		font = QtGui.QFont()
		font.setPointSize(12)
		font.setBold(True)
		font.setWeight(75)
		self.FeedbackQuestion_5.setFont(font)
		self.FeedbackQuestion_5.setStyleSheet("background:transparent;\n"
"border:0px;\n"
"")
		self.FeedbackQuestion_5.setObjectName("FeedbackQuestion_5")
		self.FeedbackQuestion_6 = QtWidgets.QLabel(self.SubRateUsPage)
		self.FeedbackQuestion_6.setGeometry(QtCore.QRect(88, 312, 151, 21))
		font = QtGui.QFont()
		font.setPointSize(12)
		font.setBold(True)
		font.setWeight(75)
		self.FeedbackQuestion_6.setFont(font)
		self.FeedbackQuestion_6.setStyleSheet("background:transparent;\n"
"border:0px;\n"
"")
		self.FeedbackQuestion_6.setObjectName("FeedbackQuestion_6")
		self.NextButton = QtWidgets.QPushButton(self.SubRateUsPage)
		self.NextButton.setGeometry(QtCore.QRect(640, 350, 31, 31))
		font = QtGui.QFont()
		font.setFamily("Segoe UI")
		font.setBold(True)
		font.setWeight(75)
		self.NextButton.setFont(font)
		self.NextButton.setStyleSheet("QPushButton {    \n"
"    border: none;\n"
"    background-color:rgb(75, 171, 255);\n"
"    border-radius:5px;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: rgb(125, 188, 255);\n"
"}\n"
"QPushButton:pressed {    \n"
"    background-color:  rgb(125, 188, 255);\n"
"}")
		self.NextButton.setText("")
		icon12 = QtGui.QIcon()
		icon12.addPixmap(QtGui.QPixmap("icons/cil-next.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.NextButton.setIcon(icon12)
		self.NextButton.setObjectName("NextButton")
		self.SubbedRateUsPage = QtWidgets.QWidget(self.SubRateUsPage)
		self.SubbedRateUsPage.setGeometry(QtCore.QRect(0, 0, 701, 391))
		self.SubbedRateUsPage.setStyleSheet("background-color:rgb(250, 250, 250);\n"
"border:3px solid;\n"
"border-radius:10px;\n"
"border-color: rgb(0, 36, 114);")
		self.SubbedRateUsPage.setObjectName("SubbedRateUsPage")
		self.FeedbackDone = QtWidgets.QLabel(self.SubbedRateUsPage)
		self.FeedbackDone.setGeometry(QtCore.QRect(100, 10, 500, 375))
		self.FeedbackDone.setStyleSheet("background:transparent;\n"
"border:0px;\n"
"")
		self.FeedbackDone.setText("")
		self.FeedbackDone.setObjectName("FeedbackDone")
		self.DoneFeedback=QMovie("icons/cil-complete.gif")
		self.FeedbackDone.setMovie(self.DoneFeedback)
		self.FeedbackQuestion_7 = QtWidgets.QLabel(self.SubRateUsPage)
		self.FeedbackQuestion_7.setGeometry(QtCore.QRect(325, 36, 41, 20))
		font = QtGui.QFont()
		font.setPointSize(8)
		font.setBold(True)
		font.setWeight(75)
		self.FeedbackQuestion_7.setFont(font)
		self.FeedbackQuestion_7.setStyleSheet("background:transparent;\n"
"border:0px;\n"
"")
		self.FeedbackQuestion_7.setObjectName("FeedbackQuestion_7")
		self.FeedbackQuestion_8 = QtWidgets.QLabel(self.SubRateUsPage)
		self.FeedbackQuestion_8.setGeometry(QtCore.QRect(585, 36, 41, 20))
		font = QtGui.QFont()
		font.setPointSize(8)
		font.setBold(True)
		font.setWeight(75)
		self.FeedbackQuestion_8.setFont(font)
		self.FeedbackQuestion_8.setStyleSheet("background:transparent;\n"
"border:0px;\n"
"")
		self.FeedbackQuestion_8.setObjectName("FeedbackQuestion_8")
		self.Star1.raise_()
		self.Star1_2.raise_()
		self.Star1_3.raise_()
		self.Star1_4.raise_()
		self.Star1_5.raise_()
		self.Star2_2.raise_()
		self.Star2_3.raise_()
		self.Star2_4.raise_()
		self.Star2_5.raise_()
		self.Star2.raise_()
		self.Star3_2.raise_()
		self.Star3_3.raise_()
		self.Star3_4.raise_()
		self.Star3_5.raise_()
		self.Star3.raise_()
		self.FeedbackQuestion.raise_()
		self.FeedbackBar.raise_()
		self.Star5.raise_()
		self.Star5_2.raise_()
		self.Star5_5.raise_()
		self.Star5_4.raise_()
		self.Star5_3.raise_()
		self.Star6.raise_()
		self.Star6_2.raise_()
		self.Star6_5.raise_()
		self.Star6_4.raise_()
		self.Star6_3.raise_()
		self.Star4.raise_()
		self.Star4_2.raise_()
		self.Star4_5.raise_()
		self.Star4_4.raise_()
		self.Star4_3.raise_()
		self.FeedbackQuestion_2.raise_()
		self.FeedbackQuestion_3.raise_()
		self.FeedbackQuestion_4.raise_()
		self.FeedbackQuestion_5.raise_()
		self.FeedbackQuestion_6.raise_()
		self.NextButton.raise_()
		self.FeedbackQuestion_7.raise_()
		self.FeedbackQuestion_8.raise_()
		self.SubbedRateUsPage.raise_()
		self.MidFrame = QtWidgets.QWidget(self.centralwidget)
		self.MidFrame.setGeometry(QtCore.QRect(0, 30, 801, 41))
		self.MidFrame.setStyleSheet("background-color:rgb(255, 255, 255)")
		self.MidFrame.setObjectName("MidFrame")
		self.ReturnButton = QtWidgets.QPushButton(self.MidFrame)
		self.ReturnButton.setGeometry(QtCore.QRect(7, 5, 81, 31))
		font = QtGui.QFont()
		font.setFamily("Segoe UI")
		font.setBold(True)
		font.setWeight(75)
		self.ReturnButton.setFont(font)
		self.ReturnButton.setStyleSheet("QPushButton {    \n"
"    border: none;\n"
"    background-color:rgb(75, 171, 255);\n"
"    border-radius:5px;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: rgb(125, 188, 255);\n"
"}\n"
"QPushButton:pressed {    \n"
"    background-color:  rgb(125, 188, 255);\n"
"}")
		icon13 = QtGui.QIcon()
		icon13.addPixmap(QtGui.QPixmap("icons/cil-previous.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.ReturnButton.setIcon(icon13)
		self.ReturnButton.setObjectName("ReturnButton")
		self.CheckOutPage = QtWidgets.QWidget(self.centralwidget)
		self.CheckOutPage.setGeometry(QtCore.QRect(0, 70, 0, 461))
		self.CheckOutPage.setStyleSheet("background-color:rgb(170, 85, 0)")
		self.CheckOutPage.setObjectName("CheckOutPage")
		self.BG2_2 = QtWidgets.QLabel(self.CheckOutPage)
		self.BG2_2.setGeometry(QtCore.QRect(0, 0, 801, 461))
		self.BG2_2.setText("")
		self.BG2_2.setPixmap(QtGui.QPixmap("background/bg4.jpg"))
		self.BG2_2.setScaledContents(True)
		self.BG2_2.setObjectName("BG2_2")
		self.SubCheckOutPage = QtWidgets.QWidget(self.CheckOutPage)
		self.SubCheckOutPage.setGeometry(QtCore.QRect(50, 30, 701, 391))
		self.SubCheckOutPage.setStyleSheet("background-color:rgba(250, 250, 250, 150);\n"
"border:3px solid;\n"
"border-radius:10px;\n"
"border-color: rgb(0, 36, 114);")
		self.SubCheckOutPage.setObjectName("SubCheckOutPage")
		self.CheckOutCalen = QtWidgets.QDateTimeEdit(self.SubCheckOutPage)
		self.CheckOutCalen.setGeometry(QtCore.QRect(200, 190, 251, 31))
		self.CheckOutCalen.setStyleSheet("QDateTimeEdit {\n"
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
		self.CheckOutCalen.setCalendarPopup(True)
		self.CheckOutCalen.setObjectName("CheckOutCalen")
		self.CheckOutPageBar = QtWidgets.QLabel(self.SubCheckOutPage)
		self.CheckOutPageBar.setGeometry(QtCore.QRect(10, 10, 401, 31))
		font = QtGui.QFont()
		font.setFamily("Segoe UI")
		font.setPointSize(12)
		font.setBold(True)
		font.setWeight(75)
		self.CheckOutPageBar.setFont(font)
		self.CheckOutPageBar.setStyleSheet("background-color:transparent;\n"
"border:0px transparent;\n"
"border-radius:0px;")
		self.CheckOutPageBar.setTextFormat(QtCore.Qt.RichText)
		self.CheckOutPageBar.setScaledContents(True)
		self.CheckOutPageBar.setAlignment(QtCore.Qt.AlignCenter)
		self.CheckOutPageBar.setObjectName("CheckOutPageBar")
		self.RequestCheckOutBut = QtWidgets.QPushButton(self.SubCheckOutPage)
		self.RequestCheckOutBut.setGeometry(QtCore.QRect(200, 260, 131, 31))
		font = QtGui.QFont()
		font.setFamily("Segoe UI")
		font.setPointSize(10)
		font.setBold(False)
		font.setWeight(50)
		self.RequestCheckOutBut.setFont(font)
		self.RequestCheckOutBut.setStyleSheet("QPushButton {\n"
"    background-color: rgba(27, 29, 35,180);\n"
"    border-radius: 5px;\n"
"    border: 2px solid rgb(27, 29, 35);\n"
"}\n"
"QPushButton:hover {\n"
"    border: 2px solid rgb(64, 71, 88);\n"
"}\n"
"QPushButton:focus {\n"
"    border: 2px solid rgb(91, 101, 124);\n"
"}")
		self.RequestCheckOutBut.setObjectName("RequestCheckOutBut")
		self.CheckOutDiv = QtWidgets.QFrame(self.SubCheckOutPage)
		self.CheckOutDiv.setGeometry(QtCore.QRect(0, 50, 701, 3))
		self.CheckOutDiv.setFrameShape(QtWidgets.QFrame.HLine)
		self.CheckOutDiv.setFrameShadow(QtWidgets.QFrame.Sunken)
		self.CheckOutDiv.setObjectName("CheckOutDiv")
		self.CurrentCheckoutDate = QtWidgets.QLabel(self.SubCheckOutPage)
		self.CurrentCheckoutDate.setGeometry(QtCore.QRect(200, 120, 271, 31))
		font = QtGui.QFont()
		font.setBold(True)
		font.setWeight(75)
		self.CurrentCheckoutDate.setFont(font)
		self.CurrentCheckoutDate.setStyleSheet("border:0px;\n"
"border-radius:5px;")
		self.CurrentCheckoutDate.setObjectName("CurrentCheckoutDate")
		self.MenuPage = QtWidgets.QWidget(self.centralwidget)
		self.MenuPage.setGeometry(QtCore.QRect(0, 70, 0, 461))
		self.MenuPage.setStyleSheet("background-color:rgb(24, 255, 228);")
		self.MenuPage.setObjectName("MenuPage")
		self.BG2_3 = QtWidgets.QLabel(self.MenuPage)
		self.BG2_3.setGeometry(QtCore.QRect(0, 0, 801, 461))
		self.BG2_3.setText("")
		self.BG2_3.setPixmap(QtGui.QPixmap("background/bg1.jpg"))
		self.BG2_3.setScaledContents(True)
		self.BG2_3.setObjectName("BG2_3")
		self.SubMenuPage = QtWidgets.QWidget(self.MenuPage)
		self.SubMenuPage.setGeometry(QtCore.QRect(20, 30, 761, 411))
		self.SubMenuPage.setStyleSheet("background-color:rgba(250, 250, 250, 150);\n"
"border:3px solid;\n"
"border-radius:10px;\n"
"border-color: rgb(0, 36, 114);")
		self.SubMenuPage.setObjectName("SubMenuPage")
		self.ItemListWidget = QtWidgets.QListWidget(self.SubMenuPage)
		self.ItemListWidget.setGeometry(QtCore.QRect(40, 50, 641, 321))
		self.ItemListWidget.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked)
		self.ItemListWidget.setProperty("showDropIndicator", False)
		self.ItemListWidget.setAlternatingRowColors(False)
		self.ItemListWidget.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
		self.ItemListWidget.setSelectionRectVisible(True)
		self.ItemListWidget.setObjectName("ItemListWidget")
		self.OrderFoodButton = QtWidgets.QPushButton(self.SubMenuPage)
		self.OrderFoodButton.setGeometry(QtCore.QRect(630, 374, 121, 31))
		font = QtGui.QFont()
		font.setFamily("Segoe UI")
		font.setBold(True)
		font.setWeight(75)
		self.OrderFoodButton.setFont(font)
		self.OrderFoodButton.setStyleSheet("QPushButton {    \n"
"    border: none;\n"
"    background-color:rgb(75, 171, 255);\n"
"    border-radius:5px;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: rgb(125, 188, 255);\n"
"}\n"
"QPushButton:pressed {    \n"
"    background-color:  rgb(125, 188, 255);\n"
"}")
		self.OrderFoodButton.setText("")
		self.OrderFoodButton.setIcon(icon12)
		self.OrderFoodButton.setObjectName("OrderFoodButton")
		self.ConfirmOrderFoodButton = QtWidgets.QPushButton(self.SubMenuPage)
		self.ConfirmOrderFoodButton.setGeometry(QtCore.QRect(630, 374, 121, 31))
		font = QtGui.QFont()
		font.setFamily("Segoe UI")
		font.setBold(True)
		font.setWeight(75)
		self.ConfirmOrderFoodButton.setFont(font)
		self.ConfirmOrderFoodButton.setStyleSheet("QPushButton {    \n"
"    border: none;\n"
"    background-color:rgb(75, 171, 255);\n"
"    border-radius:5px;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: rgb(125, 188, 255);\n"
"}\n"
"QPushButton:pressed {    \n"
"    background-color:  rgb(125, 188, 255);\n"
"}")
		self.ConfirmOrderFoodButton.setText("")
		self.ConfirmOrderFoodButton.setIcon(icon12)
		self.ConfirmOrderFoodButton.setObjectName("ConfirmOrderFoodButton")
		self.ItemConfirmedWidget = QtWidgets.QTableWidget(self.SubMenuPage)
		self.ItemConfirmedWidget.setGeometry(QtCore.QRect(40, 50, 639, 0))
		self.ItemConfirmedWidget.setStyleSheet("""QTableWidget{
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
	border-radius:8px;
 }

 QScrollBar::add-page, QScrollBar::sub-page
 {
	border:none;
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
border:none;
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
		self.ItemConfirmedWidget.setFrameShadow(QtWidgets.QFrame.Plain)
		self.ItemConfirmedWidget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
		self.ItemConfirmedWidget.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked)
		self.ItemConfirmedWidget.setTabKeyNavigation(False)
		self.ItemConfirmedWidget.setProperty("showDropIndicator", False)
		self.ItemConfirmedWidget.setDragDropOverwriteMode(False)
		self.ItemConfirmedWidget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
		self.ItemConfirmedWidget.setGridStyle(QtCore.Qt.SolidLine)
		self.ItemConfirmedWidget.setObjectName("ItemConfirmedWidget")
		self.ItemConfirmedWidget.setColumnCount(3)
		self.ItemConfirmedWidget.setRowCount(0)
		item = QtWidgets.QTableWidgetItem()
		self.ItemConfirmedWidget.setHorizontalHeaderItem(0, item)
		item = QtWidgets.QTableWidgetItem()
		self.ItemConfirmedWidget.setHorizontalHeaderItem(1, item)
		item = QtWidgets.QTableWidgetItem()
		self.ItemConfirmedWidget.setHorizontalHeaderItem(2, item)
		self.ItemConfirmedWidget.horizontalHeader().setDefaultSectionSize(198)
		self.TopFrame.raise_()
		self.MidFrame.raise_()
		self.ENPPage.raise_()
		self.CheckOutPage.raise_()
		self.Main.raise_()
		self.RateUsPage.raise_()
		self.MenuPage.raise_()
		MainWindow.setCentralWidget(self.centralwidget)
		self.Exit.clicked.connect(lambda : self.exitFunc())
		self.Minimize.clicked.connect(lambda:MainWindow.showMinimized())
		self.ENPButton.clicked.connect(lambda : self.ENPShowPage())
		self.RateUsButton.clicked.connect(lambda : self.RateUsPageShow())
		self.ReturnButton.clicked.connect(lambda:self.setupUi(MainWindow))
		self.RoomServiceButton.clicked.connect(lambda:self.RoomServiceFunc())
		self.Star1.clicked.connect(lambda:self.RatingStar1(1))
		self.Star1_2.clicked.connect(lambda:self.RatingStar1(2))
		self.Star1_3.clicked.connect(lambda:self.RatingStar1(3))
		self.Star1_4.clicked.connect(lambda:self.RatingStar1(4))
		self.Star1_5.clicked.connect(lambda:self.RatingStar1(5))
		self.Star2_2.clicked.connect(lambda:self.RatingStar2(2))
		self.Star2_3.clicked.connect(lambda:self.RatingStar2(3))
		self.Star2_4.clicked.connect(lambda:self.RatingStar2(4))
		self.Star2_5.clicked.connect(lambda:self.RatingStar2(5))
		self.Star2.clicked.connect(lambda:self.RatingStar2(1))
		self.Star3_2.clicked.connect(lambda:self.RatingStar3(2))
		self.Star3_3.clicked.connect(lambda:self.RatingStar3(3))
		self.Star3_4.clicked.connect(lambda:self.RatingStar3(4))
		self.Star3_5.clicked.connect(lambda:self.RatingStar3(5))
		self.Star3.clicked.connect(lambda:self.RatingStar3(1))
		self.Star5.clicked.connect(lambda:self.RatingStar5(1))
		self.Star5_2.clicked.connect(lambda:self.RatingStar5(2))
		self.Star5_5.clicked.connect(lambda:self.RatingStar5(5))
		self.Star5_4.clicked.connect(lambda:self.RatingStar5(4))
		self.Star5_3.clicked.connect(lambda:self.RatingStar5(3))
		self.Star6.clicked.connect(lambda:self.RatingStar6(1))
		self.Star6_2.clicked.connect(lambda:self.RatingStar6(2))
		self.Star6_5.clicked.connect(lambda:self.RatingStar6(5))
		self.Star6_4.clicked.connect(lambda:self.RatingStar6(4))
		self.Star6_3.clicked.connect(lambda:self.RatingStar6(3))
		self.Star4.clicked.connect(lambda:self.RatingStar4(1))
		self.Star4_2.clicked.connect(lambda:self.RatingStar4(2))
		self.Star4_5.clicked.connect(lambda:self.RatingStar4(5))
		self.Star4_4.clicked.connect(lambda:self.RatingStar4(4))
		self.Star4_3.clicked.connect(lambda:self.RatingStar4(3))
		self.NextButton.clicked.connect(lambda:self.SubmitRating())
		self.MenuButton.clicked.connect(lambda:self.MenuLoad())
		self.SubENPPage.raise_()
		self.SubENPPage.setUrl(QtCore.QUrl("https://news.google.com"))
		self.CheckOutButton.clicked.connect(lambda:self.DisplayRequestCheck())
		self.AboutUsButton.clicked.connect(lambda:self.AboutUsDisplay())
		self.DNDButton.setCheckable(True)
		self.FrontDeskButton.clicked.connect(lambda:self.FrontDeskPingFunc())
		self.DNDButton.clicked.connect(lambda:self.CheckDNDButton())
		InfoText="""

Base Version: V2.2
GUI Version: V2.1
Developers: Kanad Nemade
                     Vishnu Padmakumar
                     Saikat Dhar

		   """	
		self.Info.clicked.connect(lambda:ctypes.windll.user32.MessageBoxW(0, InfoText, "Application Info", 0))
		self.retranslateUi(MainWindow)
		QtCore.QMetaObject.connectSlotsByName(MainWindow)

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

		self.SubTopFrame.mouseMoveEvent=moveWindow
		self.SubTopFrame.mousePressEvent=pressWindow
		self.SubTopFrame.mouseReleaseEvent=releasedWindow

	def exitFunc(self):
		mydb.close()
		exit()

	def FrontDeskPingFunc(self):
		self.FrontDeskPingrunner=FrontDeskPing()
		self.FrontDeskPingrunner.start()
		self.FrontDeskPingrunner.FrontDeskPingged.connect(lambda:ctypes.windll.user32.MessageBoxW(0, "Front Desk Notified", "GMS Notifier", 0))

	def RoomServiceFunc(self):
		if self.DNDButton.isChecked()==0:
			choice=ctypes.windll.user32.MessageBoxW(0, "Do you want Room Service?", "GMS Notifier", ICON_QUES | MB_YESNO)
			if choice==6:
				self.RequestRoomServicerunner=RequestRoomService()
				self.RequestRoomServicerunner.start()
				self.RequestRoomServicerunner.RequestedRoomService.connect(lambda:ctypes.windll.user32.MessageBoxW(0, "Room Service Notified", "GMS Notifier", 0))
			else:
				pass
		else:
			ctypes.windll.user32.MessageBoxW(0, "Please Disable DND First", "GMS Notifier", ICON_INFO | MB_OK)

	def AboutUsDisplay(self):
		self.SubENPPage1.raise_()
		self.SubENPPage1.setUrl(QtCore.QUrl("https://blazingguyz.github.io/C.S-Project/"))
		self.Main.setGeometry(QtCore.QRect(0, 30, 0, 521))
		self.ENPPage.setGeometry(QtCore.QRect(0, 70, 801, 461))	


	def CheckDNDButton(self):
		if self.DNDButton.isChecked()==True:
			print("Disable DND")
			self.DNDLab.setText("Disable DND")
			self.RequestDNDonrunner=RequestDNDon()
			self.RequestDNDonrunner.start()
			self.RequestDNDonrunner.RequestedDNDon.connect(lambda:ctypes.windll.user32.MessageBoxW(0, "DND Mode Turned on", "GMS Notifier", 0))
		else:
			print("Enable DND")
			self.RequestDNDoffrunner=RequestDNDoff()
			self.RequestDNDoffrunner.start()
			self.RequestDNDoffrunner.RequestedDNDoff.connect(lambda:ctypes.windll.user32.MessageBoxW(0, "DND Mode Turned off", "GMS Notifier", 0))
			self.DNDLab.setText("Enable DND")

	def DisplayRequestCheck(self):
		global currentCheckoutDate
		self.Main.setGeometry(QtCore.QRect(0, 30, 0, 521))
		self.CheckOutPage.setGeometry(QtCore.QRect(0, 70, 801, 461))
		self.getCurrentCheckoutdaterunner=getCurrentCheckoutdate()
		self.getCurrentCheckoutdaterunner.start()
		self.getCurrentCheckoutdaterunner.gotCurrentCheckoutDate.connect(lambda:DisplaycurrentDate())
		self.RequestCheckOutBut.clicked.connect(lambda : self.NewCheckOutDateFunc())
		def DisplaycurrentDate():
			self.CurrentCheckoutDate.setText(" Your current Checkout date is: "+currentCheckoutDate)

	def NewCheckOutDateFunc(self):
		global NewCheckOutDate
		NewCheckOutDate=self.CheckOutCalen.text()
		self.NotifyNewCheckoutDaterunner=NotifyNewCheckoutDate()
		self.NotifyNewCheckoutDaterunner.start()
		self.NotifyNewCheckoutDaterunner.NotifiedNewCheckoutDate.connect(lambda:NotifyGuestrequestplaced())
		def NotifyGuestrequestplaced():
			ctypes.windll.user32.MessageBoxW(0, "New Checkout Date requested!", "GMS Notifier", 0)


	def MenuLoad(self):
		global selectedItems
		self.ConfirmOrderFoodButton.lower()
		self.OrderFoodButton.raise_()
		self.Main.setGeometry(QtCore.QRect(0, 30, 0, 521))
		self.MenuPage.setGeometry(QtCore.QRect(0, 70, 801, 461))	
		BVeg=Menu.BreakFast("Veg")
		BNVeg=Menu.BreakFast("NonVeg")
		#BSeaFood=Menu.BreakFast("SeaFood")
		AVeg=Menu.All_Day("Veg")
		ANVeg=Menu.All_Day("NonVeg")
		ASeaFood=Menu.All_Day("SeaFood")
		LDVeg=Menu.LunchandDinner("Veg")
		LDNVeg=Menu.LunchandDinner("NonVeg")
		LDSeaFood=Menu.LunchandDinner("SeaFood")
		FoodCat=[BVeg,BNVeg,AVeg,ANVeg,ASeaFood,LDVeg,LDNVeg,LDSeaFood]
		FoodType=["BreakFast","BreakFast","All-Day","All-Day","All-Day","Lunch and Dinner","Lunch and Dinner","Lunch and Dinner"]
		FoodTypeDone=[]
		for i in range(len(FoodCat)):
			if FoodType[i] not in FoodTypeDone:
				item = QtWidgets.QListWidgetItem()
				item.setTextAlignment(QtCore.Qt.AlignCenter)
				brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
				brush.setStyle(QtCore.Qt.SolidPattern)
				item.setForeground(brush)
				font = QtGui.QFont()
				font.setFamily("Segoe UI")
				font.setPointSize(10)
				font.setBold(True)
				font.setWeight(65)
				item.setFont(font)
				item.setFlags(QtCore.Qt.ItemIsEnabled)
				item.setText(FoodType[i])
				self.ItemListWidget.addItem(item)
				FoodTypeDone.append(FoodType[i])
			for items in FoodCat[i]:
				if i==0 or i==2 or i==5:
					item = QtWidgets.QListWidgetItem()
					item.setTextAlignment(QtCore.Qt.AlignCenter)
					brush = QtGui.QBrush(QtGui.QColor(0, 150, 0))
					brush.setStyle(QtCore.Qt.SolidPattern)
					icon15 = QtGui.QIcon()
					icon15.addPixmap(QtGui.QPixmap("icons/cil-veg.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
					item.setIcon(icon15)
					item.setForeground(brush)
					item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled)
					item.setText(items)
					self.ItemListWidget.addItem(item)
				elif i==1 or i==3 or i==6:
					item = QtWidgets.QListWidgetItem()
					item.setTextAlignment(QtCore.Qt.AlignCenter)
					brush = QtGui.QBrush(QtGui.QColor( 250, 0, 0))
					brush.setStyle(QtCore.Qt.SolidPattern)
					icon15 = QtGui.QIcon()
					icon15.addPixmap(QtGui.QPixmap("icons/cil-nveg.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
					item.setIcon(icon15)
					item.setForeground(brush)
					item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled)
					item.setText(items)
					self.ItemListWidget.addItem(item)
				else:
					item = QtWidgets.QListWidgetItem()
					item.setTextAlignment(QtCore.Qt.AlignCenter)
					brush = QtGui.QBrush(QtGui.QColor( 0, 0, 250))
					brush.setStyle(QtCore.Qt.SolidPattern)
					icon15 = QtGui.QIcon()
					icon15.addPixmap(QtGui.QPixmap("icons/cil-sea.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
					item.setIcon(icon15)
					item.setForeground(brush)
					item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled)
					item.setText(items)
					self.ItemListWidget.addItem(item)
		self.OrderFoodButton.clicked.connect(lambda : confirmedItemList())
		def confirmedItemList():
			global selectedItems
			self.ConfirmOrderFoodButton.raise_()
			self.OrderFoodButton.lower()
			self.ConfirmOrderFoodButton.clicked.connect(lambda :self.OrderFoodFunc())
			self.ItemListWidget.setGeometry(QtCore.QRect(40, 50, 0, 321))#641x321
			self.ItemConfirmedWidget.setGeometry(QtCore.QRect(40, 50, 641, 321))
			selectedItems=[]	
			for items in self.ItemListWidget.selectedItems():
				items=items.text()
				items=items.replace("INR","")
				items=items.replace("  ","")
				selectedItems.append(items)
			print(selectedItems)
			for i in range(len(selectedItems)):
				self.ItemConfirmedWidget.insertRow(i)
				self.ItemConfirmedWidget.setItem(i,0,QtWidgets.QTableWidgetItem(selectedItems[i]))
				self.ItemConfirmedWidget.setItem(i,1,QtWidgets.QTableWidgetItem("1"))
				#self.ItemConfirmedWidget.setItem(i,2,QtWidgets.QTableWidgetItem("None"))
				self.ItemConfirmedWidget.setStyleSheet("""QTableWidget{
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
	border-radius:8px;
 }

 QScrollBar::add-page, QScrollBar::sub-page
 {
	border:none;
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
border:none;
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
	

	def OrderFoodFunc(self):
		print("Here!")
		global selectedItems,TotalFoodItem
		FoodItem=[]
		TotalFoodItem=[]
		for rows in range(len(selectedItems)):
			FoodItem=[]
			for column in range(3):
				fooditem=self.ItemConfirmedWidget.item(rows,column)
				if fooditem==None:
					fooditem="None"
				else:
					fooditem=fooditem.text()
				FoodItem.append(fooditem)
			TotalFoodItem.append(FoodItem)
		self.NotifyMenurunner=NotifyMenu()
		self.NotifyMenurunner.start()
		self.NotifyMenurunner.NotifiedMenu.connect(lambda:ctypes.windll.user32.MessageBoxW(0, "Order placed!", "GMS Notifier", 0))
		self.setupUi(MainWindow)

	def SubmitRating(self):
		global Star1Rating,Star2Rating,Star3Rating,Star4Rating,Star5Rating,Star6Rating,TotalRating
		self.SubbedRateUsPage.raise_()
		self.FeedbackDone.setScaledContents(True)
		self.DoneFeedback.start()
		TotalRating=Star1Rating+Star2Rating+Star3Rating+Star4Rating+Star5Rating+Star6Rating
		TotalRating=TotalRating/6
		self.RatingThreadrunner=RatingThread()
		self.RatingThreadrunner.start()
		self.RatingThreadrunner.RatingEntered.connect(lambda:ctypes.windll.user32.MessageBoxW(0, "Thank Your for rating us!", "Rating Manager", 0))
		print(TotalRating)

	def RatingStar1(self,Stars):
		global Star1Rating

		IconBright = QtGui.QIcon()
		IconBright.addPixmap(QtGui.QPixmap("icons/cil-star.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		IconDim = QtGui.QIcon()
		IconDim.addPixmap(QtGui.QPixmap("icons/cil-startrans.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.Star1.setIcon(IconDim)
		self.Star1_2.setIcon(IconDim)
		self.Star1_3.setIcon(IconDim)
		self.Star1_4.setIcon(IconDim)
		self.Star1_5.setIcon(IconDim)
		if Stars==1:
			self.Star1.setIcon(IconBright)
			Star1Rating=1
		elif Stars==2:
			self.Star1.setIcon(IconBright)
			self.Star1_2.setIcon(IconBright)
			Star1Rating=2
		elif Stars==3:
			self.Star1.setIcon(IconBright)
			self.Star1_2.setIcon(IconBright)
			self.Star1_3.setIcon(IconBright)
			Star1Rating=3
		elif Stars==4:
			self.Star1.setIcon(IconBright)
			self.Star1_2.setIcon(IconBright)
			self.Star1_3.setIcon(IconBright)
			self.Star1_4.setIcon(IconBright)
			Star1Rating=4
		elif Stars==5:
			self.Star1.setIcon(IconBright)
			self.Star1_2.setIcon(IconBright)
			self.Star1_3.setIcon(IconBright)
			self.Star1_4.setIcon(IconBright)
			self.Star1_5.setIcon(IconBright)
			Star1Rating=5
		else:
			pass
	
	def RatingStar2(self,Stars):
		global Star2Rating

		IconBright = QtGui.QIcon()
		IconBright.addPixmap(QtGui.QPixmap("icons/cil-star.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		IconDim = QtGui.QIcon()
		IconDim.addPixmap(QtGui.QPixmap("icons/cil-startrans.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.Star2.setIcon(IconDim)
		self.Star2_2.setIcon(IconDim)
		self.Star2_3.setIcon(IconDim)
		self.Star2_4.setIcon(IconDim)
		self.Star2_5.setIcon(IconDim)
		if Stars==1:
			self.Star2.setIcon(IconBright)
			Star2Rating=1
		elif Stars==2:
			self.Star2.setIcon(IconBright)
			self.Star2_2.setIcon(IconBright)
			Star2Rating=2
		elif Stars==3:
			self.Star2.setIcon(IconBright)
			self.Star2_2.setIcon(IconBright)
			self.Star2_3.setIcon(IconBright)
			Star2Rating=3
		elif Stars==4:
			self.Star2.setIcon(IconBright)
			self.Star2_2.setIcon(IconBright)
			self.Star2_3.setIcon(IconBright)
			self.Star2_4.setIcon(IconBright)
			Star2Rating=4
		elif Stars==5:
			self.Star2.setIcon(IconBright)
			self.Star2_2.setIcon(IconBright)
			self.Star2_3.setIcon(IconBright)
			self.Star2_4.setIcon(IconBright)
			self.Star2_5.setIcon(IconBright)
			Star2Rating=5
		else:
			pass

	def RatingStar3(self,Stars):
		global Star3Rating

		IconBright = QtGui.QIcon()
		IconBright.addPixmap(QtGui.QPixmap("icons/cil-star.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		IconDim = QtGui.QIcon()
		IconDim.addPixmap(QtGui.QPixmap("icons/cil-startrans.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.Star3.setIcon(IconDim)
		self.Star3_2.setIcon(IconDim)
		self.Star3_3.setIcon(IconDim)
		self.Star3_4.setIcon(IconDim)
		self.Star3_5.setIcon(IconDim)
		if Stars==1:
			self.Star3.setIcon(IconBright)
			Star3Rating=1
		elif Stars==2:
			self.Star3.setIcon(IconBright)
			self.Star3_2.setIcon(IconBright)
			Star3Rating=2
		elif Stars==3:
			self.Star3.setIcon(IconBright)
			self.Star3_2.setIcon(IconBright)
			self.Star3_3.setIcon(IconBright)
			Star3Rating=3
		elif Stars==4:
			self.Star3.setIcon(IconBright)
			self.Star3_2.setIcon(IconBright)
			self.Star3_3.setIcon(IconBright)
			self.Star3_4.setIcon(IconBright)
			Star3Rating=4
		elif Stars==5:
			self.Star3.setIcon(IconBright)
			self.Star3_2.setIcon(IconBright)
			self.Star3_3.setIcon(IconBright)
			self.Star3_4.setIcon(IconBright)
			self.Star3_5.setIcon(IconBright)
			Star3Rating=5
		else:
			pass

	def RatingStar4(self,Stars):
		global Star4Rating

		IconBright = QtGui.QIcon()
		IconBright.addPixmap(QtGui.QPixmap("icons/cil-star.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		IconDim = QtGui.QIcon()
		IconDim.addPixmap(QtGui.QPixmap("icons/cil-startrans.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.Star4.setIcon(IconDim)
		self.Star4_2.setIcon(IconDim)
		self.Star4_3.setIcon(IconDim)
		self.Star4_4.setIcon(IconDim)
		self.Star4_5.setIcon(IconDim)
		if Stars==1:
			self.Star4.setIcon(IconBright)
			Star4Rating=1
		elif Stars==2:
			self.Star4.setIcon(IconBright)
			self.Star4_2.setIcon(IconBright)
			Star4Rating=2
		elif Stars==3:
			self.Star4.setIcon(IconBright)
			self.Star4_2.setIcon(IconBright)
			self.Star4_3.setIcon(IconBright)
			Star4Rating=3
		elif Stars==4:
			self.Star4.setIcon(IconBright)
			self.Star4_2.setIcon(IconBright)
			self.Star4_3.setIcon(IconBright)
			self.Star4_4.setIcon(IconBright)
			Star4Rating=4
		elif Stars==5:
			self.Star4.setIcon(IconBright)
			self.Star4_2.setIcon(IconBright)
			self.Star4_3.setIcon(IconBright)
			self.Star4_4.setIcon(IconBright)
			self.Star4_5.setIcon(IconBright)
			Star4Rating=5
		else:
			pass

	def RatingStar5(self,Stars):
		global Star5Rating
		IconBright = QtGui.QIcon()
		IconBright.addPixmap(QtGui.QPixmap("icons/cil-star.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		IconDim = QtGui.QIcon()
		IconDim.addPixmap(QtGui.QPixmap("icons/cil-startrans.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.Star5.setIcon(IconDim)
		self.Star5_2.setIcon(IconDim)
		self.Star5_3.setIcon(IconDim)
		self.Star5_4.setIcon(IconDim)
		self.Star5_5.setIcon(IconDim)
		if Stars==1:
			self.Star5.setIcon(IconBright)
			Star5Rating=1
		elif Stars==2:
			self.Star5.setIcon(IconBright)
			self.Star5_2.setIcon(IconBright)
			Star5Rating=2
		elif Stars==3:
			self.Star5.setIcon(IconBright)
			self.Star5_2.setIcon(IconBright)
			self.Star5_3.setIcon(IconBright)
			Star5Rating=3
		elif Stars==4:
			self.Star5.setIcon(IconBright)
			self.Star5_2.setIcon(IconBright)
			self.Star5_3.setIcon(IconBright)
			self.Star5_4.setIcon(IconBright)
			Star5Rating=4
		elif Stars==5:
			self.Star5.setIcon(IconBright)
			self.Star5_2.setIcon(IconBright)
			self.Star5_3.setIcon(IconBright)
			self.Star5_4.setIcon(IconBright)
			self.Star5_5.setIcon(IconBright)
			Star5Rating=5
		else:
			pass

	def RatingStar6(self,Stars):
		global Star6Rating

		IconBright = QtGui.QIcon()
		IconBright.addPixmap(QtGui.QPixmap("icons/cil-star.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		IconDim = QtGui.QIcon()
		IconDim.addPixmap(QtGui.QPixmap("icons/cil-startrans.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.Star6.setIcon(IconDim)
		self.Star6_2.setIcon(IconDim)
		self.Star6_3.setIcon(IconDim)
		self.Star6_4.setIcon(IconDim)
		self.Star6_5.setIcon(IconDim)
		if Stars==1:
			self.Star6.setIcon(IconBright)
			Star6Rating=1
		elif Stars==2:
			self.Star6.setIcon(IconBright)
			self.Star6_2.setIcon(IconBright)
			Star6Rating=2
		elif Stars==3:
			self.Star6.setIcon(IconBright)
			self.Star6_2.setIcon(IconBright)
			self.Star6_3.setIcon(IconBright)
			Star6Rating=3
		elif Stars==4:
			self.Star6.setIcon(IconBright)
			self.Star6_2.setIcon(IconBright)
			self.Star6_3.setIcon(IconBright)
			self.Star6_4.setIcon(IconBright)
			Star6Rating=4
		elif Stars==5:
			self.Star6.setIcon(IconBright)
			self.Star6_2.setIcon(IconBright)
			self.Star6_3.setIcon(IconBright)
			self.Star6_4.setIcon(IconBright)
			self.Star6_5.setIcon(IconBright)
			Star6Rating=5
		else:
			pass

	def RateUsPageShow(self):
		self.Main.setGeometry(QtCore.QRect(0, 30, 0, 521))
		self.RateUsPage.setGeometry(QtCore.QRect(0, 70, 801, 461))
		self.SubbedRateUsPage.lower()


	def ENPShowPage(self):
		self.SubENPPage.raise_()
		self.Main.setGeometry(QtCore.QRect(0, 30, 0, 521))
		self.ENPPage.setGeometry(QtCore.QRect(0, 70, 801, 461))	

	def retranslateUi(self, MainWindow):
		_translate = QtCore.QCoreApplication.translate
		MainWindow.setWindowTitle(_translate("MainWindow", "KVS Hotel Groups"))
		self.MainLab.setText(_translate("MainWindow", "KVS Hotel Management Software"))
		self.MenuLab.setText(_translate("MainWindow", "Order to your room"))
		self.DNDLab.setText(_translate("MainWindow", "Enable DND"))
		self.RoomServiceLab.setText(_translate("MainWindow", "Room Service"))
		self.FrontDeskLab.setText(_translate("MainWindow", "Front Desk"))
		self.CheckOutLab.setText(_translate("MainWindow", " Request Check-Out \n"
"date modification "))
		self.ENPLab.setText(_translate("MainWindow", "E-Newspaper"))
		self.RateUsLab.setText(_translate("MainWindow", "Rate Us"))
		self.AboutUsLab.setText(_translate("MainWindow", "About Us"))
		self.FeedbackQuestion.setText(_translate("MainWindow", "Decor of the hotel"))
		self.FeedbackBar.setText(_translate("MainWindow", "      Can we know a little about your stay with us? Based on your stay with us, please rate us on the following "))
		self.FeedbackQuestion_2.setText(_translate("MainWindow", "Staff Friendliness"))
		self.FeedbackQuestion_3.setText(_translate("MainWindow", "Check-in process"))
		self.FeedbackQuestion_4.setText(_translate("MainWindow", "Flexibility"))
		self.FeedbackQuestion_5.setText(_translate("MainWindow", "Facilities"))
		self.FeedbackQuestion_6.setText(_translate("MainWindow", "Reservation"))
		self.FeedbackQuestion_7.setText(_translate("MainWindow", "1 Star"))
		self.FeedbackQuestion_8.setText(_translate("MainWindow", "5 Stars"))
		self.ReturnButton.setText(_translate("MainWindow", "Return"))
		self.CheckOutPageBar.setText(_translate("MainWindow", "Enjoying your stay? Request a new checkout date!"))
		self.RequestCheckOutBut.setText(_translate("MainWindow", "Place your Request"))
		self.CurrentCheckoutDate.setText(_translate("MainWindow", "   Your current Checkout date is:"))
		__sortingEnabled = self.ItemListWidget.isSortingEnabled()
		self.ItemListWidget.setSortingEnabled(False)
		#item = self.ItemListWidget.item(0)
		#item.setText(_translate("MainWindow", "Vegetarian"))
		#item = self.ItemListWidget.item(1)
		#item.setText(_translate("MainWindow", "Non Vegetarian"))
		#item = self.ItemListWidget.item(2)
		#item.setText(_translate("MainWindow", "Sea Food"))
		self.ItemListWidget.setSortingEnabled(__sortingEnabled)
		item = self.ItemConfirmedWidget.horizontalHeaderItem(0)
		item.setText(_translate("MainWindow", "Item"))
		item = self.ItemConfirmedWidget.horizontalHeaderItem(1)
		item.setText(_translate("MainWindow", "Quantity"))
		item = self.ItemConfirmedWidget.horizontalHeaderItem(2)
		item.setText(_translate("MainWindow", "Special Note"))

def except_hook(cls, exception, traceback):
	sys.__excepthook__(cls, exception, traceback)

if __name__ == "__main__":
	app = QtWidgets.QApplication(sys.argv)
	app.setStyleSheet('QMainWindow{background-color: darkgray;border: 1px solid black;}')
	MainWindow = QtWidgets.QMainWindow()
	sys.excepthook = except_hook
	ui = Ui_MainWindow()
	ui.setMouseTracking(True)
	MainWindow.setWindowFlags(QtCore.Qt.FramelessWindowHint)
	ui.setupUi(MainWindow)
	MainWindow.show()
	sys.exit(app.exec_())
