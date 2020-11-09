import smtplib

class Recovery:
   def __init__(self,receivers,nombre,link):
      self.sender='karlozgll1506@gmail.com'
      self.clavesender='iame bzmg degh eefv'
      self.receivers=[receivers]
      self.message = """From: StarsProject <correoqueenvia@gmail.com>\nTo: {}\nSubject: RESTAURACION DE CONTRASENA\n
      Hola! {}, para restablecer su contrasena, siga este enlace: """.format(receivers,nombre)+link


   def enviar(self):
      try:
         smtpObj = smtplib.SMTP_SSL('smtp.gmail.com', 465)
         smtpObj.login(self.sender,self.clavesender)
         smtpObj.sendmail(self.sender, self.receivers, self.message)      
         print("Successfully sent email")
      except (OSError, smtplib.SMTPException):
         print("Error: unable to send email")
      smtpObj.quit