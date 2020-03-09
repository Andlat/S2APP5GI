# S2APP5GI

## Fonctionnement du calcul de la fréquence des mots
La structure de données utilisée est une hash table qui contient des linked lists pour gérer les collisions. Le code supporte tous les n-grammes

Chaque node de la linked list contient 3 membres:
- val: Valeur de la node (le n-gramme)
- count: Fréquence de cette valeur
- next: Prochaine node de la liste. Peut aussi être de la valeur None

L'index d'une valeur dans la hash table est calculé avec le hash de l'objet modulo la largeur de la table: hash(objet) % size

#### Alternative pour la structure de la hash table
- Un arbre pourrait être utilisé à la place de la linked list

## Ce qui reste à faire
- Trier les mots selon leur fréquence pour créer la chaine de Markov
- Chaine de Markov
- et autre...
