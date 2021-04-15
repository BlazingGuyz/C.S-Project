import mysql.connector
import time

PASSWORD="<redacted>"
PORT=3306
print("[SYSTEM] Connecting to Database. Please Wait!")
try:
	mydb = mysql.connector.connect(
		host="localhost",
		user="root",
		passwd=PASSWORD,
		port=PORT
		)
	print("[SYSTEM] Connected!")
except Exception as ERROR1:
	print("[SYSTEM | CRITICAL] Could Connect to Database | (ERROR LOG) ",ERROR1)
	time.sleep(5)	
cursor=mydb.cursor(buffered=True)
print("[SYSTEM] Initialising Database Creation Procedure!")
print("[SYSTEM] Procedure Started. Please Wait!")
try:
	cursor.execute("CREATE DATABASE hotelkvs")
	mydb.commit()
	cursor.execute("USE hotelkvs")
	mydb.commit()
	cursor.execute("CREATE TABLE GData(Serialno char(255) primary key,Details varchar(255), Photo longblob, Date varchar(255), Time varchar(255), Email varchar(255), Phoneno char(12), Room Char(4), Rate varchar(255))")
	cursor.execute("CREATE TABLE notify(Topic longtext, Date varchar(255), Item longtext, Quantity varchar(255), SpecialNote longtext, Room varchar(255))")
	cursor.execute("CREATE TABLE r101(ChargedFor varchar(255), Amount int, Date varchar(255), Serialno varchar(255));")
	cursor.execute("CREATE TABLE r102(ChargedFor varchar(255), Amount int, Date varchar(255), Serialno varchar(255));")
	cursor.execute("CREATE TABLE r103(ChargedFor varchar(255), Amount int, Date varchar(255), Serialno varchar(255));")
	cursor.execute("CREATE TABLE r104(ChargedFor varchar(255), Amount int, Date varchar(255), Serialno varchar(255));")
	cursor.execute("CREATE TABLE r201(ChargedFor varchar(255), Amount int, Date varchar(255), Serialno varchar(255));")
	cursor.execute("CREATE TABLE r202(ChargedFor varchar(255), Amount int, Date varchar(255), Serialno varchar(255));")
	cursor.execute("CREATE TABLE r203(ChargedFor varchar(255), Amount int, Date varchar(255), Serialno varchar(255));")
	cursor.execute("CREATE TABLE r301(ChargedFor varchar(255), Amount int, Date varchar(255), Serialno varchar(255));")
	cursor.execute("CREATE TABLE r302(ChargedFor varchar(255), Amount int, Date varchar(255), Serialno varchar(255));")
	cursor.execute("CREATE TABLE r303(ChargedFor varchar(255), Amount int, Date varchar(255), Serialno varchar(255));")
	cursor.execute("CREATE TABLE room(RoomNo int, Details varchar(255), RoomStatus varchar(255) DEFAULT 'unoccupied', Serialno int);")
	cursor.execute("CREATE TABLE roomhis(Date varchar(255), Time varchar(255), Details varchar(255), Photo longblob, TotalAmount varchar(255), Email varchar(255),Serialno char(4) primary key, RoomNo varchar(255), Phoneno char(12), Rate varchar(255))")
	for i in range(101,105):
		cursor.execute(f"INSERT INTO room(RoomNo,RoomStatus) values({i},'unoccupied');")
	for i in range(201,204):
		cursor.execute(f"INSERT INTO room(RoomNo,RoomStatus) values({i},'unoccupied');")
	for i in range(301,304):
		cursor.execute(f"INSERT INTO room(RoomNo,RoomStatus) values({i},'unoccupied');")
	mydb.commit()
	print("[SYSTEM] Procedure Completed Successfully!")	
	time.sleep(5)
except Exception as ERROR2:
	print("[SYSTEM | CRITICAL] Failed Creation Process | (ERROR LOG) ",ERROR2)
	time.sleep(5)
mydb.close()