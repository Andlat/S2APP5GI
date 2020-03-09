#
#  Gabarit pour l'application de traitement des frequences de mots dans les oeuvres d'auteurs divers
#  Le traitement des arguments a ete inclus:
#     Tous les arguments requis sont presents et accessibles dans args
#     Le traitement du mode verbose vous donne un exemple de l'utilisation des arguments
#
#  Frederic Mailhot, 26 fevrier 2018
#    Revise 16 avril 2018
#    Revise 7 janvier 2020

#  Parametres utilises, leur fonction et code a generer
#
#  -d   Deja traite dans le gabarit:  la variable rep_auth contiendra le chemin complet vers le repertoire d'auteurs
#       La liste d'auteurs est extraite de ce repertoire, et est comprise dans la variable authors
#
#  -P   Si utilise, indique au systeme d'utiliser la ponctuation.  Ce qui est considére comme un signe de ponctuation
#       est defini dans la liste PONC
#       Si -P EST utilise, cela indique qu'on désire conserver la ponctuation (chaque signe est alors considere
#       comme un mot.  Par defaut, la ponctuation devrait etre retiree
#
#  -m   mode d'analyse:  -m 1 indique de faire les calculs avec des unigrammes, -m 2 avec des bigrammes.
#
#  -a   Auteur (unique a traiter).  Utile en combinaison avec -g, -G, pour la generation d'un texte aleatoire
#       avec les caracteristiques de l'auteur indique
#
#  -G   Indique qu'on veut generer un texte (voir -a ci-haut), le nombre de mots à generer doit être indique
#
#  -g   Indique qu'on veut generer un texte (voir -a ci-haut), le nom du fichier en sortie est indique
#
#  -F   Indique qu'on desire connaitre le rang d'un certain mot pour un certain auteur.  L'auteur doit etre
#       donné avec le parametre -a, et un mot doit suivre -F:   par exemple:   -a Verne -F Cyrus
#
#  -v   Deja traite dans le gabarit:  mode "verbose",  va imprimer les valeurs données en parametre
#
#
#  Le systeme doit toujours traiter l'ensemble des oeuvres de l'ensemble des auteurs.  Selon la presence et la valeur
#  des autres parametres, le systeme produira differentes sorties:
#
#  avec -a, -g, -G:  generation d'un texte aleatoire avec les caracteristiques de l'auteur identifie
#  avec -a, -F:  imprimer la frequence d'un mot d'un certain auteur.  Format de sortie:  "auteur:  mot  frequence"
#                la frequence doit être un nombre reel entre 0 et 1, qui represente la probabilite de ce mot
#                pour cet auteur
#  avec -f:  indiquer l'auteur le plus probable du texte identifie par le nom de fichier qui suit -f
#            Format de sortie:  "nom du fichier: auteur"
#  avec ou sans -P:  indique que les calculs doivent etre faits avec ou sans ponctuation
#  avec -v:  mode verbose, imprimera l'ensemble des valeurs des paramètres (fait deja partie du gabarit)


import math
import argparse
import glob
import sys
import os
from pathlib import Path
from random import randint
from random import choice

# Ajouter ici les signes de ponctuation à retirer
PONC = ["!", '"', "'", ")", "(", ",", ".", ";", ":", "?", "-", "_"]
TAILLE_TABLEAU = 2**16

#  Vous devriez inclure vos classes et méthodes ici, qui seront appellées à partir du main

class Node:
    def __init__(self, val=None):
        self.val = val
        self.count = 0
        self.next = None

    def __str__(self):
        return "Node{val:" + str(self.val) + ", count:" + str(self.count) + "}->" + str(self.next)


class CountingHashTable:
    def __init__(self, size):
        self.table = [None for i in range(size)]
        self.size = size

    def __getitem__(self, key):
        return self.table[key]

    def __str__(self):
        s = "HashTable:{\n"
        for i in range(self.size):
            s += "\t" + str(self.table[i]) + "\n"

        return s + "}"

    def add(self, obj):
        index = hash(obj) % self.size

        node = self.table[index]
        if node is None: #If no nodes exist at that index, create a new one with the given value
            self.table[index] = Node(obj)
            node = self.table[index]

        elif node.val != obj:  # If something else is at that index
            # Traverse linked list
            foundInList = False

            while node.next is not None:
                node = node.next
                if node.val == obj:
                    foundInList = True
                    break

            if not foundInList:  # If not found value in linked list, create a new node
                node.next = Node(obj)
                node = node.next

        # Increment count of the node/value
        node.count += 1

        return self

    def count(self):
        c = 0

        for i in range(self.size):
            node = self.table[i]
            while node is not None:
                node = node.next
                c += 1

        return c

    def highest(self):
        highestNode = Node(None)  # Starting with an empty node

        for i in range(self.size):
            node = self.table[i]
            while node is not None:
                if node.count > highestNode.count:
                    highestNode = node

                node = node.next

        return highestNode


def removePonc(str):
    for p in PONC:
        str = str.replace(p, '')
    return str

# Main: lecture des paramètres et appel des méthodes appropriées
#
#       argparse permet de lire les paramètres sur la ligne de commande
#             Certains paramètres sont obligatoires ("required=True")
#             Ces paramètres doivent êtres fournis à python lorsque l'application est exécutée

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='markov_zeln2901.py')
    parser.add_argument('-d', required=True, help='Repertoire contenant les sous-repertoires des auteurs')
    parser.add_argument('-a', help='Auteur a traiter')
    parser.add_argument('-f', help='Fichier inconnu a comparer')
    parser.add_argument('-m', required=True, type=int, choices=range(1, 3),
                        help='Mode (1 ou 2) - unigrammes ou digrammes')
    parser.add_argument('-F', type=int, help='Indication du rang (en frequence) du mot (ou bigramme) a imprimer')
    parser.add_argument('-G', type=int, help='Taille du texte a generer')
    parser.add_argument('-g', help='Nom de base du fichier de texte a generer')
    parser.add_argument('-v', action='store_true', help='Mode verbose')
    parser.add_argument('-P', action='store_true', help='Retirer la ponctuation')
    args = parser.parse_args()

    # Lecture du répertoire des auteurs, obtenir la liste des auteurs
    # Note:  args.d est obligatoire
    # auteurs devrait comprendre la liste des répertoires d'auteurs, peu importe le système d'exploitation
    cwd = os.getcwd()
    if os.path.isabs(args.d):
        rep_aut = args.d
    else:
        rep_aut = os.path.join(cwd, args.d)

    rep_aut = os.path.normpath(rep_aut)
    authors = os.listdir(rep_aut)

    # Enlever les signes de ponctuation (ou non) - Définis dans la liste PONC
    if args.P:
        remove_ponc = True
    else:
        remove_ponc = False

    # Si mode verbose, refléter les valeurs des paramètres passés sur la ligne de commande
    if args.v:
        print("Mode verbose:")
        print("Calcul avec les auteurs du repertoire: " + args.d)
        if args.f:
            print("Fichier inconnu a,"
                  " etudier: " + args.f)

        print("Calcul avec des " + str(args.m) + "-grammes")
        if args.F:
            print(str(args.F) + "e mot (ou digramme) le plus frequent sera calcule")

        if args.a:
            print("Auteur etudie: " + args.a)

        if args.P:
            print("Retirer les signes de ponctuation suivants: {0}".format(" ".join(str(i) for i in PONC)))

        if args.G:
            print("Generation d'un texte de " + str(args.G) + " mots")

        if args.g:
            print("Nom de base du fichier de texte genere: " + args.g)

        print("Repertoire des auteurs: " + rep_aut)
        print("Liste des auteurs: ")
        for a in authors:
            aut = a.split("/")
            print("    " + aut[-1])

# ### À partir d'ici, vous devriez inclure les appels à votre code
    table = CountingHashTable(TAILLE_TABLEAU)
    _str = ""
    count_init_ngramme = 0

    for file in glob.glob(rep_aut + "/*.txt"):
        print(file)
        with open(file) as stream:
            for line in stream:
                line = removePonc(line)

                for word in line.split():
                    word = word.lower()  # Ajuster tous les mots en lettres miniscules

                    # Ajustement initial pour n-grammes§
                    if count_init_ngramme < args.m:
                        _str += " " + word
                        count_init_ngramme += 1

                        # Si le premier n-gramme est cree, l'ajouter dans la hashtable
                        if count_init_ngramme == args.m:

                            table.add(_str.strip())

                    else:
                        # Creer le prochain n-gramme (Retirer le premier mot et ajouter le nouveau a la fin)
                        ngramme = _str.split()
                        ngramme.pop(0)
                        ngramme.append(word)
                        _str = ' '.join(str(w) for w in ngramme)

                        table.add(_str.strip())

    print(str(table.count()))
    print(str(table.highest()))
