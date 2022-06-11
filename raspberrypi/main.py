# Main file with the state machine 
from fileinput import filename
from re import sub
import subprocess
import datetime
import enum
import os
from time import sleep
import json
from selenium import webdriver
from bs4 import BeautifulSoup
import requests
from pyvirtualdisplay import Display
import shutil
import smtplib
import cv2

PICTURE_FOLDER = "caddy/site"
STATE_FILE_NAME = "state.json"
EMPTY_NEST_WAIT_TIME = 600 # seconds
EGGS_WAIT_TIME = 300 # seconds
CHICKS_WAIT_TIME = 120 # seconds
WAIT_FOR_EMPTY_WAIT_TIME = 1800 # seconds


class States(enum.Enum):
   Init = 0 # Etat de reset
   EmptyNest = 1
   Eggs = 2
   Chicks = 3
   FirstFall = 4
   SendMail = 5
   WaitForEmpty = 6

class CurrentState:
   def __init__(self, state : States, eggNumber : int, chickNumber : int):
      self.state = state
      self.eggNumber = eggNumber
      self.chickNumber = chickNumber
      self.espIpAddr = ""

# Sauvegarde l'état et autres variables nécessaires dans le fichier d'état
def saveToFile(currentState: CurrentState):
   dict = {"state": currentState.state.value, "eggNumber" : currentState.eggNumber, "chickNumber" : currentState.chickNumber}
   with open(STATE_FILE_NAME, "w") as i:
      json.dump(dict, i)

# Return a current state element
def readFromFile():
   with open(STATE_FILE_NAME, mode="r") as file:
      doc = json.load(file)
   print(type(doc))
   state = CurrentState(States(doc["state"]), doc["eggNumber"], doc["chickNumber"])
   return state

# Récupère l'image du esp
def getPicture(ipAddr):
   display = Display(visible=0, size=(800, 600))
   display.start()
   driver = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver')   
   driver.get(ipAddr)
   # click on capture
   button_element = driver.find_element_by_id('capture')
   button_element.click()
   # wait 4 sec
   sleep(4)
   # click refresh
   button_element = driver.find_element_by_id('reload')
   button_element.click()
   sleep(2)
   # récupérer la photo
   response = requests.get(ipAddr)
   soup = BeautifulSoup(response.text, "html.parser")
   link = soup.findAll(id='photo')[0] 
   imageSrc = link["src"]
   response = requests.get(ipAddr+"/"+imageSrc, stream=True)
   realName = "latest.jpg"
   
   file = open(os.path.join(PICTURE_FOLDER,realName), 'wb')
   response.raw.decode_content = True
   shutil.copyfileobj(response.raw, file)
   x = datetime.datetime.now()
   fileName = str(x)
   file = open(os.path.join(PICTURE_FOLDER,fileName), 'wb')
   shutil.copyfileobj(response.raw, file)
   del response
   driver.quit()
   display.stop()
   return os.path.join(PICTURE_FOLDER, fileName)


# Détecte le nombre d'oiseaux présents sur l'image
# Retourne un bool pour savoir si c'est des oiseaux, un bool pour si c'est des oeufs et le nombre d'oiseaux/oeuf
def birdDetection(image): # image est le path vers l'image
   pass

# Envoyer le mail de notification
def sendMail():
   sender = 'cse.birds@outlook.com'
   receivers = ['cse.birds@outlook.com']

   #smtp
   smtpHost = 'smtp.office365.com'
   smtpPort = 587
   password = "framboise$1234" 
   subject = "Notification de surveillance du Nid"

   # Add the From: and To: headers at the start!
   message = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n"
         % (sender, ", ".join(receivers), subject))
   message += """Bonjour\r\nVotre premier oiseau est sorti du nid."""

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
   except smtplib.SMTPException:
      print ("Error: unable to send email")

if __name__ == "__main__":
   # General variables
   currentState = CurrentState(States.Init, 0)
   

   os.makedirs(PICTURE_FOLDER, exist_ok=True)
   if (os.path.exists(STATE_FILE_NAME)):
      currentState = readFromFile()
      print(currentState)
   if currentState.state != States.Init:
      foundIt = False
      while not foundIt:
         print("Trying to get esp...")
         output = subprocess.check_output(["nmap", "-sn","-v","192.168.4.0/24"])
         ipAddr = ""
         lines = output.decode().splitlines()
         for line in lines:
            if "esp" in line:
               res = line.split('(')[1]
               ipAddr = res[:-1]
               ipAddr = "http://"+ipAddr
               currentState.espIpAddr = ipAddr
               foundIt = True
               break

   while True:
      if currentState.state == States.Init:
         saveToFile(currentState)
         exit(0)
         # Initialiser le reste des composants (thread?)
         currentState.state = States.EmptyNest
      elif currentState.state == States.EmptyNest:
         saveToFile(currentState)
         while True:
            # Analyser les images et attendre qu'on détecte un oeuf
            sleep(EMPTY_NEST_WAIT_TIME)
            image = getPicture(currentState.espIpAddr)
            isBird, isEggs, number = birdDetection(image)
            if (isEggs and number > 0):
               currentState.state = States.Eggs
               currentState.eggNumber = number
               break
      elif currentState.state == States.Eggs:
         saveToFile(currentState)
         while True:
            # Analyser les images et attendre qu'on détecte un oeuf
            sleep(EGGS_WAIT_TIME)
            image = getPicture(currentState.espIpAddr)
            isBird, isEggs, number = birdDetection(image)
            if (isBird & number >1): # Quand un oisillon éclot (> 1 pour éviter de détecter la mère)
               currentState.state = States.Chicks
               break
            elif (number > currentState.eggNumber):
               currentState.eggNumber = number
      elif currentState.state == States.Chicks:
         saveToFile(currentState)
         while True:
            # Analyser les images et attendre qu'on détecte un oeuf
            sleep(CHICKS_WAIT_TIME)
            image = getPicture(currentState.espIpAddr)
            isBird, isEggs, number = birdDetection(image)
            if (isBird & number < currentState.chickNumber): # Quand un oisillon éclot (> 1 pour éviter de détecter la mère)
               currentState.state = States.FirstFall 
               break
            elif (number > currentState.chickNumber):
               currentState.chickNumber = number
      elif currentState.state == States.FirstFall:
         saveToFile(currentState)
         currentState.state = States.SendMail
         saveToFile(currentState)
         subprocess.run("hotspot_deactivate")
      elif currentState.state == States.SendMail:
         saveToFile(currentState)
         sendMail()
         subprocess.run("hotspot_activate")
         currentState.state = States.WaitForEmpty
      elif currentState.state == States.WaitForEmpty:
         saveToFile(currentState)
         while True:
            # Analyser les images et attendre qu'on détecte un oeuf
            sleep(WAIT_FOR_EMPTY_WAIT_TIME)
            image = getPicture(currentState.espIpAddr)
            isBird, isEggs, number = birdDetection(image)
            if (isBird & number == 0): # Quand un oisillon éclot (> 1 pour éviter de détecter la mère)
               currentState.state = States.EmptyNest
               break