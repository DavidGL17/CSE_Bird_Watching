# Main file with the state machine 
import enum
import os
from time import sleep
import json

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
def getPicture():
   pass

# Détecte le nombre d'oiseaux présents sur l'image
# Retourne un bool pour savoir si c'est des oiseaux, un bool pour si c'est des oeufs et le nombre d'oiseaux/oeuf
def birdDetection(image):
   pass

if __name__ == "__main__":
   # General variables
   currentState = CurrentState(States.Init, 0)

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
         saveToFile(currentState.state, currentState.eggNumber)
         pass
      elif currentState.state == States.FirstFall:
         saveToFile(currentState.state, currentState.eggNumber)
         pass
      elif currentState.state == States.SendMail:
         saveToFile(currentState.state, currentState.eggNumber)
         pass
      elif currentState.state == States.WaitForEmpty:
         saveToFile(currentState.state, currentState.eggNumber)
         pass