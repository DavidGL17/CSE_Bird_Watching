import smtplib

# TODO mettre les bons parametres encore (message, objets, adresses...)
def sendEmail():

    sender = 'cse.birds@outlook.com'
    receivers = ['cse.birds@outlook.com']

    #smtp
    smtpHost = 'smtp.office365.com'
    smtpPort = 587
    password = "framboise$1234" 
    subject = "outlook email test"

    # Add the From: and To: headers at the start!
    message = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n"
            % (sender, ", ".join(receivers), subject))
    message += """This is a test e-mail message."""

    print (message)

    try:
        smtpObj = smtplib.SMTP(smtpHost, smtpPort)
        #smtpObj.set_debuglevel(1)
        smtpObj.ehlo()
        smtpObj.starttls()
        smtpObj.ehlo()    
        smtpObj.login(sender,password)
        smtpObj.sendmail(sender, receivers, message)
        smtpObj.quit()
        print ("Successfully sent email")
    except SMTPException:
        print ("Error: unable to send email")

if __name__ == "__main__":
    sendEmail()