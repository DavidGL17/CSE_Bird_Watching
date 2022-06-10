# Ce script output l'adresse ip de l'esp, doit boucler tant qu'il le trouve pas

nmap -sn -oG -v 192.168.4.0/24 # inspecter le résultat de ça, grep esp. Si y'a rien, alors on recommence, sinon on print la ligne
# une fois la ligne print python peut récuperer et sauvegarder l'adresse ip
# possible de faire la gestion de la boucle dans python aussi