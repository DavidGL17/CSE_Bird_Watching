# Main file with the state machine 
import enum
from http.client import LineTooLong
import os
from time import sleep
import json
from selenium import webdriver
from bs4 import BeautifulSoup
import requests
from pyvirtualdisplay import Display
import urllib.request
import shutil

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
   def __init__(self, state : States, eggNumber : int):
      self.state = state
      self.eggNumber = eggNumber

# Sauvegarde l'état et autres variables nécessaires dans le fichier d'état
def saveToFile(currentState):
   jsonStr = json.dumps(currentState.__dict__)
   with open(STATE_FILE_NAME, "w") as i:
      json.dump(jsonStr, i)

# Return a current state element
def readFromFile():
   with open("text_data.json", mode="r") as file:
      doc = json.load(file)
   state = CurrentState(doc["state"], doc["eggNumber"])
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
   imageSrc = link[0]["src"]
   response = requests.get(ipAddr+"/"+imageSrc, stream=True)
   realName = "latest.jpg"
   
   file = open(realName, 'wb')
   response.raw.decode_content = True
   shutil.copyfileobj(response.raw, file)
   del response
   driver.quit()
   display.stop()

# Détecte le nombre d'oiseaux présents sur l'image
# Retourne un bool pour savoir si c'est des oiseaux, un bool pour si c'est des oeufs et le nombre d'oiseaux/oeuf
def birdDetection(image):
   pass

# Envoyer le mail de prévention
def sendMail():
   pass

if __name__ == "__main__":
   # General variables
   currentState = CurrentState(States.Init, 0)

   getPicture("http://192.168.4.7")
   exit(0)
   if (os.path.exists(STATE_FILE_NAME)):
      currentState = readFromFile()
   if currentState.state != States.SendMail:
      pass
      # get ip address of esp


   while True:
      if currentState.state == States.Init:
         saveToFile(currentState)
         # Initialiser le reste des composants (thread?)
         currentState.state = States.EmptyNest
      elif currentState.state == States.EmptyNest:
         saveToFile(currentState)
         while True:
            # Analyser les images et attendre qu'on détecte un oeuf
            sleep(EMPTY_NEST_WAIT_TIME)
            image = getPicture()
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
            image = getPicture()
            isBird, isEggs, number = birdDetection(image)
            if (isBird & number >1): # Quand un oisillon éclot (> 1 pour éviter de détecter la mère)
               currentState.state = States.Chicks
               break
            elif (number > currentState.eggNumber):
               currentState.eggNumber = number
      elif currentState.state == States.Chicks:
         saveToFile(currentState)
         pass
      elif currentState.state == States.FirstFall:
         saveToFile(currentState)
         pass
      elif currentState.state == States.SendMail:
         saveToFile(currentState)
         pass
      elif currentState.state == States.WaitForEmpty:
         saveToFile(currentState)
         pass