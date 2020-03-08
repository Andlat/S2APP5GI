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


class Pair:
    """Creates a pair of values."""

    def __init__(self, a, b):
        """Init the pair values."""
        self.a = a
        self.b = b

    def __eq__(self, other):
        return isinstance(other, self.__class__) and other.a == self.a and other.b == self.b

    def __hash__(self):
        return hash((self.a, self.b))

    def __str__(self):
        return "A: " + str(self.a) + " B: " + str(self.b)

class Digramme:
    """Digramme de mots."""

    def __init__(self, a, b):
        self.digramme = Pair(a, b)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and other == self

    def __hash__(self):
        return hash(self.digramme)


count = Pair(0, 0)


class PairedHashTable:
    """Hash table of Pairs"""
    def __init__(self, size):
        self.table = [Pair(None, 0) for i in range(size)]
        self.size = size

    def __getitem__(self, key):
        return self.table[key]

    def add(self, obj):
        _hash = hash(obj)
        index = _hash % self.size
        assert index >= 0, "ERROR ! Index is negative: " + str(index)
        #  assert table[index] is not table[index+1], "IS SAME OBJECT. SHIT"
        count.b += 1
        if self.table[index].a is None:  # If empty pair
            self.table[index].a = obj
            self.table[index].b = 0
        elif self.table[index].a == obj:  # if the object is already being counted
            self.table[index].b += 1
        else:  # Another object is already in that place
            # TODO CREATE A LINKED LIST OR A TREE
            count.a += 1
            #print(index)


def findHighestCount(table):
    """Needs a PairedHashTable, which the second value is the count"""
    high = 0
    index = -1;
    for i in range(table.size):
        if table[i].b > high:
            high = table[i].b
            index = i

    return table[index]


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
    table = PairedHashTable(TAILLE_TABLEAU)

    for file in glob.glob(rep_aut + "/*.txt"):
        print(file)
        with open(file) as stream:
            digramme = Pair(None, None)

            for line in stream:
                line = removePonc(line)

                for word in line.split():
                    if digramme.a is None:
                        digramme.a = word
                    else:
                        digramme.a = digramme.b
                        digramme.b = word

                        table.add(digramme)
        break
    print("COUNT")
    print("DUPLICATES: ", end='')
    print(count.a)
    print("TOTAL: ", end='')
    print(count.b)

    print(str(findHighestCount(table).b) + ", " + str(findHighestCount(table).a))
