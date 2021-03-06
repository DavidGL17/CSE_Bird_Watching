# Main file with the state machine 
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

# Email constants : modify as needed
SENDER = 'cse.birds@outlook.com'
SENDER_PASSWORD = "apassword" 
SENDER_SMTP_HOST = 'smtp.office365.com'
SENDER_SMTP_PORT = 587
RECEIVERS = ['cse.birds@outlook.com']

# General constants
PICTURE_FOLDER = "caddy/site"
STATE_FILE_NAME = "state.json"
EMPTY_NEST_WAIT_TIME = 1800 # seconds
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
def getPicture(ipAddr): # Si image de taille 0 recommencer
   display = Display(visible=0, size=(800, 600))
   display.start()
   driver = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver')   
   driver.get(ipAddr)
   while True:
      # click on capture
      button_element = driver.find_element_by_id('capture')
      button_element.click()
      # wait 4 sec
      sleep(5)
      # click refresh
      button_element = driver.find_element_by_id('reload')
      button_element.click()
      sleep(4)
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
      file_size = os.path.getsize(os.path.join(PICTURE_FOLDER, realName))
      if file_size == 0:
         print("problem with image trying again")
         continue
      del response
      response = requests.get(ipAddr)
      soup = BeautifulSoup(response.text, "html.parser")
      link = soup.findAll(id='photo')[0] 
      imageSrc = link["src"]
      response = requests.get(ipAddr+"/"+imageSrc, stream=True)
      x = datetime.datetime.now()
      fileName = str(x) + ".jpg"
      file = open(os.path.join(PICTURE_FOLDER,fileName), 'wb')
      response.raw.decode_content = True
      shutil.copyfileobj(response.raw, file)
      file_size = os.path.getsize(os.path.join(PICTURE_FOLDER, fileName))
      if file_size == 0:
         os.remove(os.path.join(PICTURE_FOLDER, fileName))
         print("problem with image trying again")
         continue
      del response
      driver.quit()
      display.stop()
      return os.path.join(PICTURE_FOLDER, fileName)


# Détecte le nombre d'oiseaux présents sur l'image
# Retourne un bool pour savoir si c'est des oiseaux, un bool pour si c'est des oeufs et le nombre d'oiseaux/oeuf
def birdDetection(image): # image est le path vers l'image
   # A modifier avec les bons filtres
   return False, False, 0

# Envoyer le mail de notification
def sendMail():
   #smtp
   subject = "Notification de surveillance du Nid"

   # Add the From: and To: headers at the start!
   message = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n"
         % (SENDER, ", ".join(RECEIVERS), subject))
   message += """Bonjour\r\nVotre premier oiseau est sorti du nid."""

   print (message)

   try:
      smtpObj = smtplib.SMTP(SENDER_SMTP_HOST, SENDER_SMTP_PORT)
      #smtpObj.set_debuglevel(1)
      smtpObj.ehlo()
      smtpObj.starttls()
      smtpObj.ehlo()    
      smtpObj.login(SENDER,SENDER_PASSWORD)
      smtpObj.sendmail(SENDER, RECEIVERS, message)
      smtpObj.quit()
      print ("Successfully sent email")
   except smtplib.SMTPException:
      print ("Error: unable to send email")

def deactivateHotspot():
   subprocess.run(["sh", "hotspot_deactivate.sh"])

def activateHotspot():
   subprocess.run(["sh","hotspot_activate.sh"])

# Fonction pour la demo
def demo(currentState: CurrentState):
   # prendre photo et montrer qu'elle est visible
   # Attendre appui sur enter
   # redemarrer, envoyer mail, et remettre serveur
   # Et attendre ou exit
   if (currentState.state == States.Init):
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
      input("Press a button to start")
      print("Taking picture...")
      getPicture(currentState.espIpAddr)
      input("Waiting to show image... Press button to continue")
      currentState.state = States.SendMail
      saveToFile(currentState)
      deactivateHotspot()
   elif currentState.state == States.SendMail:
      try:
         sendMail()
      except all:
         log = open("log.txt", "w")
         log.write("Error with mail")
         log.close()
      activateHotspot()
      exit(0)
   
if __name__ == "__main__":
   # General variables
   currentState = CurrentState(States.Init, 0, 0)
   
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
         deactivateHotspot()
      elif currentState.state == States.SendMail:
         saveToFile(currentState)
         sendMail()
         activateHotspot()
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