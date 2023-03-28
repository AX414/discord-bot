import requests
import json
import random

url = "https://dbd.tricky.lol/api/"

<<<<<<< HEAD

nomes = ['dwight', 'claudette','meg']
=======
>>>>>>> refs/remotes/origin/main
r1 = requests.get(url+"characterinfo?character="+random.choice(nomes))
r2 = requests.get(url+"randomperks?(role=survivor&pretty)/")

print(f"Response R1: {r1.json()}\n\n")

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
    print(p1n+"\n"+p1i)
