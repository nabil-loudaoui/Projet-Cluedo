 # 21805105 : Yann KIBAMBA
 # 22109168 : Fatima Ezzahrae GOUARAB
 # 22210566 : Nabil LOUDAOUI

# Imports
from datetime import datetime
from datetime import date
from pprint import pprint
import requests
import json
import csv
import pandas as pd
from graphh import GraphHopper

# Chargement de la clé d'API
def lecture_fichier_json(nom_fic):
    with open(nom_fic, 'rt', encoding='utf8') as obj_fic:
        return json.load(obj_fic)

credentials = lecture_fichier_json("credentials.json")
gh_client = GraphHopper(api_key=credentials['clef_GH'])

# Chargement des données Twitter et Snapchat
url = "https://my-json-server.typicode.com/rtavenar/fake_api/twitter_posts"
reponse_tweet = requests.get(url)
print(reponse_tweet) # Bon importation

twitter = reponse_tweet.json()
# pprint(twitter)
# len(twitter) # de longueur 13


url = "https://my-json-server.typicode.com/rtavenar/fake_api/snapchat_posts"
reponse_snap = requests.get(url)
print(reponse_snap)

snapchat= reponse_snap.json()
# pprint(snapchat)
# len(snapchat) # de longueur 8

# Chargement du fichier csv 
suspects = pd.read_csv('suspects.csv', sep=";")
suspects

id_twitter={}
for i in suspects.index:
    id_twitter[suspects['IDENTIFIANT_TWITTER'][i]]=[suspects['NOM'][i],suspects['PRENOM'][i]]
print(id_twitter)

id_snapchat={}
for i in suspects.index:
    id_snapchat[suspects['IDENTIFIANT_SNAPCHAT'][i]]=[suspects['NOM'][i],suspects['PRENOM'][i]]
print(id_snapchat)

# Création de variables correspondant à la date du crime et au lieu du crime
date_crime = datetime(2022,10,8,16,23,0) # Au format datetime.datetime
lieu_crime = gh_client.address_to_latlong("Rennes, UFR Sciences Sociales Université Rennes2")# Latitude et Longitude
lieu_crime

# Etant donné que certains posts ne disposent pas de coordonnées.
# Nous allons supprimer l'information est garder uniquement ceux permettant d'innocenter de manière formelle un individu
# Modification de la liste de dictionnaires twitter et snapchat

new_twitter = []
for dico in twitter:
    for key,value in dico.items():
        if key == "coordinates":
            new_twitter.append(dico)
    for tweet in new_twitter:
        tweet['lat']=tweet['coordinates'][0]
        tweet['lon']=tweet['coordinates'][1]

# pprint(new_twitter)
# len(new_twitter) # Passage de 13 à 8 tweets


new_snapchat = []
for dico in snapchat:
    for key,value in dico.items():
        if key == "loc":
            new_snapchat.append(dico)
    for snap in new_snapchat:
        snap['lat']=snap['loc']['lat']
        snap['lon']=snap['loc']['lng'] 
# pprint(new_snapchat)
# len(new_snapchat) # De 8 à 7 posts

# Désormais nous allons créer un dictionnaire pour chacun des réseaux sociaux.
# Avec comme clé l'identifiant du suspect et comme valeurs la liste de ses posts contenant la date (et heure) et la coordonnée.

def twitter_suspect(dataset):
    dictionnaire ={}
    for identifiant in id_twitter: # parcours par défaut par clé
        liste=[]
        for dico in dataset:
            if dico['author'] == identifiant:
                tweet = [abs(datetime.fromisoformat(dico['iso_date'])-date_crime).total_seconds(),(dico['lat'],dico['lon'])]             
                liste.append(tweet)       
        dictionnaire.update({identifiant:liste})
    return dictionnaire


twitter2 = twitter_suspect(new_twitter)
twitter2

# De même pour snapchat

def snapchat_suspect(dataset):
    dictionnaire ={}
    for identifiant in id_snapchat:
        liste=[]
        for dico in dataset:
            if dico['author'] == identifiant:
                snap = [abs(datetime.fromisoformat(dico['iso_date'])-date_crime).total_seconds(),(dico['lat'],dico['lon'])]             
                liste.append(snap)       
        dictionnaire.update({identifiant:liste})
    return dictionnaire

snapchat2 = snapchat_suspect(new_snapchat)
snapchat2


def alibi_twitter(dataset):
    for identifiant,identite in id_twitter.items():
        k=0
        for valeur in dataset[identifiant]:
            foot = gh_client.duration([valeur[1], lieu_crime],vehicle='foot', unit='s')
            bike =gh_client.duration([valeur[1], lieu_crime],vehicle='bike', unit='s')
            car = gh_client.duration([valeur[1], lieu_crime],vehicle='car', unit='s')
            trajet = min(foot,bike,car)
            if trajet > valeur[0]:
                k += 1
        if k!= 0:
                print(identite[0],identite[1],"a un alibi grâce à son activité sur twitter")
                
        else:
                print(identite[0],identite[1],"n'a pas d'alibi par rapport à son activité sur twitter")


alibi_twitter(twitter2)


def alibi_snapchat(dataset):
    for identifiant,identite in id_snapchat.items():
        k=0
        for valeur in dataset[identifiant]:
            foot = gh_client.duration([valeur[1], lieu_crime],vehicle='foot', unit='s')
            bike =gh_client.duration([valeur[1], lieu_crime],vehicle='bike', unit='s')
            car = gh_client.duration([valeur[1], lieu_crime],vehicle='car', unit='s')
            trajet = min(foot,bike,car)
            if trajet > valeur[0]:
                k += 1
        if k!= 0:
            print(identite[0],identite[1],"a un alibi grâce à son activité sur snapchat")
        else:
            print(identite[0],identite[1],"n'a pas alibi par rapport à son activité sur snapchat")  


alibi_snapchat(snapchat2)


# Au vue des résultats trouver:
# - Le Deuxième Georges dispose d'alibi sur les deux réseaux sociaux. On peut affirmer qu'il n'a pas pu commettre le meurtre
# - Le Troisième Robert dispose uniquement d'un alibi sur snapchat. Toutesfois, cette alibi l'innocente
# - Le Premier Jean-Michel ne dispose d'aucun alibi sur les deux réseaux sociaux malgré ses posts. 
# On peut supposer qu'il est à l'origine du meurtre étant donné qu'il est le seul suspect restant n'ayant pas d'alibi