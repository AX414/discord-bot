import requests
import json
import random

url = "https://dbd.tricky.lol/api/"

nomes_survs = ['dwight', 'claudette','meg']

r1 = requests.get(url+"characterinfo?role=survivor&character="+random.choice(nomes_survs))
r2 = requests.get(url+"randomperks?(role=survivor&pretty)/")


# Pegar indice do personagem
print(f"Index: {r1.json()['index']}")

# Pegar nome do personagem
print(f"Nome: {r1.json()['name']}")

# Pegando as perks randomicas
print(f"\n\nResponse R2: {r2.json()}\n\n")


print("\n\n\n")
data = r2.json()
dictionary = data
for value in dictionary.values():
    prkn = value['name']
    prki = value['image']
    print(prkn+"\n"+prki)


#arquivo1= open('./jsons/characters.json', encoding="utf8")
#characters = json.loads(arquivo1.read())

#arquivo2 = open('./jsons/perks.json', encoding="utf8")
#perks = json.loads(arquivo2.read())


# Retorna dwight
#print(f"Resposta: \n\n{characters['0']['name']}\n\n")

#print("\n\nApresenta todos os survivors:\n\n")
#for value in characters.values():
#    if value['role'] == 'survivor':
#        print(value['name'])

#print("\n\nApresenta todos os killers:\n\n")
#for value in characters.values():
#    if value['role'] == 'killer':
#        print(value['name'])

#print("\n\nApresenta todas as perks dos survivors:\n\n")
#for value in perks.values():
#        if value['role'] == 'survivor':
#            print(value['name'])

#print("\n\nApresenta todas as perks dos killers:\n\n")
#for value in perks.values():
#        if value['role'] == 'killer':
#            print(value['name'])


