import mysql.connector
import csv
import datetime
from datetime import date
mydb = mysql.connector.connect(
  host="0.tcp.in.ngrok.io",
  user="root",
  passwd="<redacted>",
  database="hotelkvs",
  port="<redacted>"
  )
#### Mai dekhraha tha ki kamkarega kya phir sab edit karne wala tha

mycursor = mydb.cursor(buffered=True)
''' ---------- Guest room details --------'''
def GuestRoom():
    room=101
    mycursor.execute("select Serialno,Details,Amount,Date,Time,Email,Phoneno from GData where Room='%s';"%room)
    data=mycursor.fetchall()
    d=data[0]
    print("SerialNo:-",d[0])
    print("Details:-",d[1])
    print("Amount:-",d[2])
    d1=d[3].split('.')
    print("Entry Date:-",d1[0])
    print("Exit Date:-",d1[1])
    d2=d[4].split('.')
    print("Entry Time:-",d2[0])
    print("Exit Time:-",d2[1])
    print("Email:-",d[5])
    print("PhoneNo:-",d[6])
    #for billing Billing()
''' -----------------chechkout date check--------------'''
def CheckoutDate():
    mycursor.execute("select SerialNo from Room where RoomStatus='occupied';")
    data=mycursor.fetchall()
    for i in data:
        mycursor.execute("select Date from GData where SerialNo=%s;"%i)
        data1=mycursor.fetchall()
        p=data1
        p1=p[0]
        p2=p1[0]
        p3=p2.split('.')
        date1=p3[1].split("/")
        date1.reverse()
        ExitDate="-".join(date1)
        TodayDate = str(date.today())
        i2=i[0]
        t="2020-11-09"
        if ExitDate==t:
            print("time for checkout")
            print("SerialNo:%s"%i2,"-----CheckOut date:",ExitDate)
            mycursor.execute("select RoomNO,Details from GData where SerialNo='%s';"%i2)
            data3=mycursor.fetchall()
            data4=data3[0]
            room=data4[0]
            mycursor.execute("select Chargedfor,Amount from R%s;"%data4[0])
            data5=mycursor.fetchall()
            data6=data5[0]
            print("RoomNo:R%s"%data4[0],"-----Details of Guest:",data4[1])
            Billing()
        else:
            continue

def Details():
    room=input("room no")
    x1=input("Name X.Y")#Details
    x2=12
    x3=input("date dd\mm\yy.dd\mm\yy")#date
    x4=input("Entry Time")#Entrytime
    x5=input("Email")#Email
    x6=int(input("Phone No"))#phone no
    Registration(x1,x2,x3,x4,x5,x6,room)
'''------- registration----------'''
def Registration(x1,x2,x3,x4,x5,x6,room):
    mycursor = mydb.cursor(buffered=True)
    mycursor.execute("select Max(SerialNo) from Room where SerialNo is not null;")
    data=mycursor.fetchall()
    d1=data
    d1=d1[0]
    mycursor.execute("select Max(SerialNo) from RoomHis where SerialNo is not null;")
    data=mycursor.fetchall()
    d2=data
    d2=d2[0]
    try:
        d1=int(d1[0])
        try:
            d2=int(d2[0])
            l=[]
            l.append(d1)
            l.append(d2)
            SN=max(l)
            SN=str(SN)
        except:
            SN=str(d1)
    except:
        SN='1'
    mycursor.execute("insert into GData values('%s','%s','%s','%s','%s','%s','%s','%s')",(SN,x1,x2,x3,x4,x5,x6,room))
    dict={101:2000,102:2000,103:2000,104:2000,201:2500,202:2500,203:2500,301:3750,302:3750,301:3750}
    mycursor.execute('insert into R%s(Serialno,Date) select Serialno,Date from GData;"%room')
    amount=dict[room]
    mycursor.execute("update R%s set Amount='%s',Chargedfor='accommodation' where serialno='%s'"%(int(room),amount,SN))
    #Under construction Room
    mycursor.execute("update Room set RoomStatus='occupied',SerialNo='%s' where RoomNo='%s';"%(SN,room))
    mydb.commit()
'''------ vacancy checking --------'''
def vacancy():
    mycursor.execute("select RoomNo,RoomStatus,Details from Room where RoomStatus='unoccupied';")
    data=mycursor.fetchall()
    p=[]
    for i in range (0,10):
        k=data[i]
        k1=k[0]
        k2=k[1]
        k3=k[2]
        print("Room No : R%s"%k1)
        print("Status : %s"%k2)
        print("Room Specification : %s"%k3)
'''-------charging---------'''
def Charging():
    room=int(input("Roomno"))
    a=10
    while a>0:
        charged=input("charged for")
        amount=input("ammount")
        mycursor.execute("insert into R%s values('%s','%s','%s',Null);"%(int(room),charged,amount,Date))
        k=input("More???,yes/no")
        mydb.commit()
        if k.lower()=='yes':
            mydb.commit()
            continue
        else:
            break
'''------ billing---------'''
def Billing():
    mycursor.execute("select Chargedfor,Amount from R%s;"%int(room))
    data=mycursor.fetchall()
    print(len(data))
    for i in range(0,len(data)):
        k=data[i]
        print("ChargedFor :",k[0],"--- Amount :",k[1])
    mycursor.execute("select Sum(Amount) from R%s;"%room)
    data=mycursor.fetchall()
    k=data[0]
    k1=k[0]
    print("Total Bill :: ₹%s"%k1)
'''----------check out-------------'''    
def Checkout():
    mycursor.execute("select Sum(Amount) from R%s;"%int(room))
    data=mycursor.fetchall()
    k=data[0]
    k1=k[0]
    mycursor.execute("select SerialNo from R%s where SerialNo is not null;"%int(room))
    data=mycursor.fetchall()
    p=data[0]
    p1=p[0]
    print(p1)
    mycursor.execute("insert into RoomHis(Date,Time,Details,Photo,Email,Serialno,Roomno,Phoneno,Rate) select Date,Time,Details,Photo,Email,Serialno,RoomNo,Phoneno,Rate from GData where SerialNo='%s';"%p1)
    mycursor.execute("update RoomHis set Amount=%s where SerialNo='%s';"%(k1,p1))
    mycursor.execute("Delete from GData where SerialNo='%s';",p1)
    mycursor.execute("Truncate table R%s;"%int(room))
    mydb.commit
'''--------------- Date modification-----------'''
def Modify():
    room=101
    mycursor.execute("select Date from R%s where SerialNo is not null;"%int(room))
    data=mycursor.fetchall()
    p=data
    p1=p[0]
    p2=p1[0]
    p3=p2.split('.')
    p4=input("new date")
    j=[]
    j.append(p3[0])
    j.append(p4)
    j1='.'.join(j)
    mycursor.execute("select SerialNo from R%s where SerialNo is not null;"%int(room))
    data=mycursor.fetchall()
    p=data[0]
    p1=p[0]
    j2=str(j1)
    mycursor.execute("update R%s set Date='%s' where SerialNo is not null"%(int(room),j2))
    mycursor.execute("update GData set Date='%s' where SerialNo='%s'"%(j2,p1))
    mycursor.execute("select Date from GData where SerialNo='%s';"%p1)
    data=mycursor.fetchall()
    mydb.commit()
'''-------------Rating--------------'''
def RateRoom():
    room='101'
    rate=## Rate
    mycursor.execute("update GData set Rate='%s' where Room='%s';"%(rate,room))
''' ----------------NOTIFICATION---------------------'''
'''for food'''
def Food():
    room='101'
    date='09-12-2020'
    item="Panner makhani"
    quantity='2'
    notee='spicy lessoily'
    mycursor.execute("insert into Notify values('Food Order','%s','%s','%s','%s','%s');"%(date,item,quantity,notee,room))
    mydb.commit()
''' service'''
def Service():
    mycursor.execute("insert into Notify values('RoomService','%s',null,null,'%s',%s);"%(date,note,room))
    mydb.commit()
''' dnd'''
def DND():
    mycursor.execute("insert into Notify values('DND On',null,null,null,null,'%s');"%room)
    mydb.commit()
''' date modify request yeha jo date insert hoga to modifying date hoga ok wesse karenge'''
def ModifyDate():
    mycursor.execute("insert into Notify values('Date Mod','%s',null,null,null,'%s');"%room)
    mydb.commit()
'''over for empting table'''
def Over():#after notification is seen
    mycursor.execute("delete from Notify")
    mydb.commit()
'''data extracting from table'''
def Notify():
    mycursor.execute("select Room,Date,Item,Quantity,SpecialNote from Notify where Topic='Food Order';")
    data=mycursor.fetchall()
    for i in data:
        print('Food Orders')
        #food orders
        print(i)
    mycursor.execute("select Room,SpecialNote,Date from Notify where Topic='RoomService';")
    data=mycursor.fetchall()
    for i in data:
        print('Room Service')
        print(i)
    mycursor.execute("select Room from Notify where Topic='DND On';")
    data=mycursor.fetchall()
    for i in data:
        print("DND ON Rooms")
        print(i)
    mycursor.execute("select Room,Date from Notify where Topic='Date mod';")
    data=mycursor.fetchall()
    for i in data:
        print("Date here date of modification")
        print(i)
    
    
    



import mysql.connector
import csv
import datetime
from datetime import date
mydb = mysql.connector.connect(
  host="0.tcp.in.ngrok.io",
  user="root",
  passwd="toor",
  database="hotelkvs",
  port='12657'
  )
#### Mai dekhraha tha ki kamkarega kya phir sab edit karne wala tha

mycursor = mydb.cursor(buffered=True)
''' ---------- Guest room details --------'''
def GuestRoom():
    room=101
    mycursor.execute("select Serialno,Details,Amount,Date,Time,Email,Phoneno from GData where Room='%s';"%room)
    data=mycursor.fetchall()
    d=data[0]
    print("SerialNo:-",d[0])
    print("Details:-",d[1])
    print("Amount:-",d[2])
    d1=d[3].split('.')
    print("Entry Date:-",d1[0])
    print("Exit Date:-",d1[1])
    d2=d[4].split('.')
    print("Entry Time:-",d2[0])
    print("Exit Time:-",d2[1])
    print("Email:-",d[5])
    print("PhoneNo:-",d[6])
    #for billing Billing()
''' -----------------chechkout date check--------------'''
def CheckoutDate():
    mycursor.execute("select SerialNo from Room where RoomStatus='occupied';")
    data=mycursor.fetchall()
    for i in data:
        mycursor.execute("select Date from GData where SerialNo=%s;"%i)
        data1=mycursor.fetchall()
        p=data1
        p1=p[0]
        p2=p1[0]
        p3=p2.split('.')
        date1=p3[1].split("/")
        date1.reverse()
        ExitDate="-".join(date1)
        TodayDate = str(date.today())
        i2=i[0]
        t="2020-11-09"
        if ExitDate==t:
            print("time for checkout")
            print("SerialNo:%s"%i2,"-----CheckOut date:",ExitDate)
            mycursor.execute("select RoomNO,Details from GData where SerialNo='%s';"%i2)
            data3=mycursor.fetchall()
            data4=data3[0]
            room=data4[0]
            mycursor.execute("select Chargedfor,Amount from R%s;"%data4[0])
            data5=mycursor.fetchall()
            data6=data5[0]
            print("RoomNo:R%s"%data4[0],"-----Details of Guest:",data4[1])
            Billing()
        else:
            continue

def Details():
    room=input("room no")
    x1=input("Name X.Y")#Details
    x2=12
    x3=input("date dd\mm\yy.dd\mm\yy")#date
    x4=input("Entry Time")#Entrytime
    x5=input("Email")#Email
    x6=int(input("Phone No"))#phone no
    Registration(x1,x2,x3,x4,x5,x6,room)
'''------- registration----------'''
def Registration(x1,x2,x3,x4,x5,x6,room):
    mycursor = mydb.cursor(buffered=True)
    mycursor.execute("select Max(SerialNo) from Room where SerialNo is not null;")
    data=mycursor.fetchall()
    d1=data
    d1=d1[0]
    mycursor.execute("select Max(SerialNo) from RoomHis where SerialNo is not null;")
    data=mycursor.fetchall()
    d2=data
    d2=d2[0]
    try:
        d1=int(d1[0])
        try:
            d2=int(d2[0])
            l=[]
            l.append(d1)
            l.append(d2)
            SN=max(l)
            SN=str(SN)
        except:
            SN=str(d1)
    except:
        SN='1'
    mycursor.execute("insert into GData values('%s','%s','%s','%s','%s','%s','%s','%s')",(SN,x1,x2,x3,x4,x5,x6,room))
    dict={101:2000,102:2000,103:2000,104:2000,201:2500,202:2500,203:2500,301:3750,302:3750,301:3750}
    mycursor.execute('insert into R%s(Serialno,Date) select Serialno,Date from GData;"%room')
    amount=dict[room]
    mycursor.execute("update R%s set Amount='%s',Chargedfor='accommodation' where serialno='%s'"%(int(room),amount,SN))
    #Under construction Room
    mycursor.execute("update Room set RoomStatus='occupied',SerialNo='%s' where RoomNo='%s';"%(SN,room))
    mydb.commit()
'''------ vacancy checking --------'''
def vacancy():
    mycursor.execute("select RoomNo,RoomStatus,Details from Room where RoomStatus='unoccupied';")
    data=mycursor.fetchall()
    p=[]
    for i in range (0,10):
        k=data[i]
        k1=k[0]
        k2=k[1]
        k3=k[2]
        print("Room No : R%s"%k1)
        print("Status : %s"%k2)
        print("Room Specification : %s"%k3)
'''-------charging---------'''
def Charging():
    room=int(input("Roomno"))
    a=10
    while a>0:
        charged=input("charged for")
        amount=input("ammount")
        mycursor.execute("insert into R%s values('%s','%s','%s',Null);"%(int(room),charged,amount,Date))
        k=input("More???,yes/no")
        mydb.commit()
        if k.lower()=='yes':
            mydb.commit()
            continue
        else:
            break
'''------ billing---------'''
def Billing():
    mycursor.execute("select Chargedfor,Amount from R%s;"%int(room))
    data=mycursor.fetchall()
    print(len(data))
    for i in range(0,len(data)):
        k=data[i]
        print("ChargedFor :",k[0],"--- Amount :",k[1])
    mycursor.execute("select Sum(Amount) from R%s;"%room)
    data=mycursor.fetchall()
    k=data[0]
    k1=k[0]
    print("Total Bill :: ₹%s"%k1)
'''----------check out-------------'''    
def Checkout():
    mycursor.execute("select Sum(Amount) from R%s;"%int(room))
    data=mycursor.fetchall()
    k=data[0]
    k1=k[0]
    mycursor.execute("select SerialNo from R%s where SerialNo is not null;"%int(room))
    data=mycursor.fetchall()
    p=data[0]
    p1=p[0]
    print(p1)
    mycursor.execute("insert into RoomHis(Date,Time,Details,Photo,Email,Serialno,Roomno,Phoneno,Rate) select Date,Time,Details,Photo,Email,Serialno,RoomNo,Phoneno,Rate from GData where SerialNo='%s';"%p1)
    mycursor.execute("update RoomHis set Amount=%s where SerialNo='%s';"%(k1,p1))
    mycursor.execute("Delete from GData where SerialNo='%s';",p1)
    mycursor.execute("Truncate table R%s;"%int(room))
    mydb.commit
'''--------------- Date modification-----------'''
def Modify():
    room=101
    mycursor.execute("select Date from R%s where SerialNo is not null;"%int(room))
    data=mycursor.fetchall()
    p=data
    p1=p[0]
    p2=p1[0]
    p3=p2.split('.')
    p4=input("new date")
    j=[]
    j.append(p3[0])
    j.append(p4)
    j1='.'.join(j)
    mycursor.execute("select SerialNo from R%s where SerialNo is not null;"%int(room))
    data=mycursor.fetchall()
    p=data[0]
    p1=p[0]
    j2=str(j1)
    mycursor.execute("update R%s set Date='%s' where SerialNo is not null"%(int(room),j2))
    mycursor.execute("update GData set Date='%s' where SerialNo='%s'"%(j2,p1))
    mycursor.execute("select Date from GData where SerialNo='%s';"%p1)
    data=mycursor.fetchall()
    mydb.commit()
'''-------------Rating--------------'''
def RateRoom():
    room='101'
    rate=## Rate
    mycursor.execute("update GData set Rate='%s' where Room='%s';"%(rate,room))
''' ----------------NOTIFICATION---------------------'''
'''for food'''
def Food():
    room='101'
    date='09-12-2020'
    item="Panner makhani"
    quantity='2'
    notee='spicy lessoily'
    mycursor.execute("insert into Notify values('Food Order','%s','%s','%s','%s','%s');"%(date,item,quantity,notee,room))
    mydb.commit()
''' service'''
def Service():
    mycursor.execute("insert into Notify values('RoomService','%s',null,null,'%s',%s);"%(date,note,room))
    mydb.commit()
''' dnd'''
def DND():
    mycursor.execute("insert into Notify values('DND On',null,null,null,null,'%s');"%room)
    mydb.commit()
''' date modify request yeha jo date insert hoga to modifying date hoga ok wesse karenge'''
def ModifyDate():
    mycursor.execute("insert into Notify values('Date Mod','%s',null,null,null,'%s');"%room)
    mydb.commit()
'''over for empting table'''
def Over():#after notification is seen
    mycursor.execute("delete from Notify")
    mydb.commit()
'''data extracting from table'''
def Notify():
    mycursor.execute("select Room,Date,Item,Quantity,SpecialNote from Notify where Topic='Food Order';")
    data=mycursor.fetchall()
    for i in data:
        print('Food Orders')
        #food orders
        print(i)
    mycursor.execute("select Room,SpecialNote,Date from Notify where Topic='RoomService';")
    data=mycursor.fetchall()
    for i in data:
        print('Room Service')
        print(i)
    mycursor.execute("select Room from Notify where Topic='DND On';")
    data=mycursor.fetchall()
    for i in data:
        print("DND ON Rooms")
        print(i)
    mycursor.execute("select Room,Date from Notify where Topic='Date mod';")
    data=mycursor.fetchall()
    for i in data:
        print("Date here date of modification")
        print(i)
    
    
    



