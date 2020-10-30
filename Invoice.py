# -*- coding: utf-8 -*-
import subprocess
GuestBill=[]
GuestInfo=[]
def PrepareHTML(GuestInfo,GuestBill):
	#Invoice.py
	GuestInfo=GuestInfo
	GuestBill=GuestBill
	Header=f"""
<h1 style="text-align: center;">
  <span style="font-family: georgia, palatino, serif; font-size: 24pt;">
	<span style="text-decoration: underline;">KVS HOTEL GROUPS</span> 
	<br>
  </span> 
  <img style="border-style: none;" src="icons\\LogoHead.png" alt="" width="64" height="64">
</h1>
<div style="text-align: right;">Hotel Address 1 
  <br>Hotel Address 2 
  <br>Hotel Address 3 
</div>
<br>INFORMATION INVOICE 
<br>
<br>Payee: {GuestInfo[0]}
<br>
<br>
<div style="text-align: right;">Room No.       {GuestInfo[1]}
  <br>Check-In Date  {GuestInfo[2]}
  <br>Check-Out Date {GuestInfo[3]}
</div>
<br>Confirmation Number: {GuestInfo[4]}
<br>
<br>
<div style="text-align: center;">
  <table style="border-collapse: collapse; width: 100%; height: 41px;" border="1">
	<tbody>
	  <tr style="height: 15px;">
		<td style="width: 15%; height: 15px;">Date</td>
		<td style="width: 67%; height: 15px;">Description</td>
		<td style="width: 18%; height: 15px;">Amount(in INR)</td>
	  </tr>
	</tbody>
  </table>
</div>
<div style="text-align: center;">
  <table style="border-collapse: collapse; width: 100%;" border="1">
	<tbody>
	  <tr>
"""

	Date=""
	Desc=""
	Amount=""
	
	for i in range(len(GuestBill)):
		tempDate=GuestBill[i][0]
		tempDesc=GuestBill[i][1]
		tempAmount=GuestBill[i][2]
		if i!=0:
			Date+="<br>"+tempDate+"\n"
			Desc+="<br>"+tempDesc+"\n"
			Amount+="<br>"+str(tempAmount)+"\n"
		else:
			Date+=tempDate+"\n"
			Desc+=tempDesc+"\n"
			Amount+=str(tempAmount)+"\n"
	
	
	DateColumn=f"""
			<td style="width: 15%;">
			  {Date}
			</td>
	"""
	DescColumn=f'''
			<td style="width: 67%;">
			  {Desc}
			</td>
	'''
	AmountColumn=f'''
			<td style="width: 18%;">
			  {Amount}
			</td>
	'''
	
	Footer="""
</tr>
    </tbody>
  </table>
</div>
<div style="text-align: center;">
  <br>
</div>
<div style="padding-left: 520px; text-align: right;">Total (GST-Inclusive)&nbsp; &nbsp; &nbsp; %s &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;&nbsp;</div>
<div style="padding-left: 760px; text-align: right;">_____________________________________</div>
<div style="text-align: left;">------------------------------------------------------------ 
  <br>&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Guest's Signature 
  <br>
  <br>I agree that my 
  <span class="LI ng" data-ddnwab="PR_15_0" aria-invalid="spelling">liablity</span> for this 
  <br>bill not waived and I agree to be 
  <br>held personally liable in the event 
  <br>that the indicated person, company 
  <br>or association fails to pay the&nbsp; 
  <br>full amount of these charges
</div>
<div style="text-align: center;">
  <br>WE HOPE YOU ENJOYED YOUR STAY WITH US! 
  <br>Thank you for choosing KVS Hotel. Your Feedback is important to us. 
  <br>For inquiries concerning your bill please contact HOTELPHONENO
</div>
	"""%str(GuestInfo[5])
	FinalHTML=Header+DateColumn+DescColumn+AmountColumn+Footer
	with open(GuestInfo[4]+".html",'w') as file:
		file.write(FinalHTML)
	subprocess.call("wkhtmltopdf --enable-local-file-access %s.html %s.pdf"%(GuestInfo[4],GuestInfo[4]),shell=True)
	subprocess.call("del %s.html"%GuestInfo[4],shell=True)