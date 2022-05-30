# Main file with the state machine 
import enum
import os
from time import sleep

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

# Sauvegarde l'état et autres variables nécessaires dans le fichier d'état
def saveToFile(state, eggNumber):
   pass

# Récupère l'image du esp
def getPicture():
   pass

# Détecte le nombre d'oiseaux présents sur l'image
# Retourne un bool pour savoir si c'est des oiseaux, un bool pour si c'est des oeufs et le nombre d'oiseaux/oeuf
def birdDetection(image):
   pass

if __name__ == "__main__":
   # General variables
   state = States.Init
   eggNumber = 0

   if (os.path.exists(STATE_FILE_NAME)):
      # Lire dans le fichier et prendre l'état actuel
      pass
   
   while True:
      if state == States.Init:
         saveToFile(state, eggNumber)
         # Initialiser le reste des composants (thread?)
         state = States.EmptyNest
      elif state == States.EmptyNest:
         saveToFile(state, eggNumber)
         while True:
            # Analyser les images et attendre qu'on détecte un oeuf
            sleep(EMPTY_NEST_WAIT_TIME)
            image = getPicture()
            isBird, isEggs, number = birdDetection(image)
            if (isEggs and number > 0):
               state = States.Eggs
               eggNumber = number
               break
      elif state == States.Eggs:
         saveToFile(state, eggNumber)
         while True:
            # Analyser les images et attendre qu'on détecte un oeuf
            sleep(EGGS_WAIT_TIME)
            image = getPicture()
            isBird, isEggs, number = birdDetection(image)
            if (isBird & number >1): # Quand un oisillon éclot (> 1 pour éviter de détecter la mère)
               state = States.Chicks
               break
            elif (number > eggNumber):
               eggNumber = number
      elif state == States.Chicks:
         saveToFile(state, eggNumber)
         pass
      elif state == States.FirstFall:
         saveToFile(state, eggNumber)
         pass
      elif state == States.SendMail:
         saveToFile(state, eggNumber)
         pass
      elif state == States.WaitForEmpty:
         saveToFile(state, eggNumber)
         pass