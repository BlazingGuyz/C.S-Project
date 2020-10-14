import mysql.connector
mydb = mysql.connector.connect(
  host="www.db4free.net",
  user="hotelkvs",
  passwd="<redacted>",
  database="hotelkvs",
  )

mycursor = mydb.cursor(buffered=True)
print("Connected to DB")
y=1
#variables
fileloc=r"C:\\Users\\vishnu\\Desktop\\PHENOL.jpg" 
x1="vishnu"
with open(fileloc,"rb") as f:##file directly variable me store nahi kar sakte pehele oprn karna hoga
  x2=f.read()
### koi apna photo daldena primary key use kiya hai
x3="7/11/2020.9/11/2020"
x4="4:45pm"
x5="@gmail.com"
x6=72734
room=101
#### Mai dekhraha tha ki kamkarega kya phir sab edit karne wala tha

#mycursor.execute("insert into hotelkvs values(%s,%s,%s)",(val1,val2,val3))
def Registration(x1,x2,x3,x4,x5,x6,room):
    global y
    #mycursor.execute("set innodb_lock_wait_timeout=180;")#abb nahi chaahiye yeh
    mycursor.execute("insert into GData values(%s,%s,%s,%s,%s,%s,%s)",(y,x1,x2,x3,x4,x5,x6))
    mycursor.execute("insert into R101(Details,Date,Time,Email,Serialno,Phoneno) select Details,Date,EntryTime,Email,Serialno,Phoneno from Guest;")
    dict={101:2000,102:2000,103:2000,104:2000,201:2500,202:2500,203:2500,301:3750,302:3750,301:3750}
    x=y
    y+=1
    amount=dict[room]
    mycursor.execute("update R101 set Amount=%s,Chargefor='accommodation' where serialno=%s",(amount)),

Registration(x1,x2,x3,x4,x5,x6,room)
