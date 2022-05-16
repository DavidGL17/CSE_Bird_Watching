pip install -r requirements.txt
# Run the script to download negatives
python3 neg_creator.py
# on passe au positives maintenant
mkdir info # Pour les images positives
mkdir data # Pour le résultat final
# La il faudra faire un create samples. Lui le fait qu'avec une image, je pense que y'a moyens qu'on le fasse avec plusieurs
# Comment ça marche : ça va prendre nos negatives, et insérer notre oiseau dedans. Donc les négatives doivent être des images d'arbre,...
# bg est l'images des négatives qu'on a crée, info.lst est le fichier qui va être crée par createsamples
opencv_createsamples -img bird5050.jpg -bg bg.txt -info info/info.lst -pngoutput info -maxxangle 0.5 -maxyangle -0.5 -maxzangle 0.5 -num 500
opencv_createsamples -info info/info.lst -num 500 -w 20 -h 20 -vec positives.vec
opencv_traincascade -data data -vec positives.vec -bg bg.txt -numPos 480 -numNeg 240 -numStages 10 -w 20 -h 20