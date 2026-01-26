# Visualisation Carte en Terminal - Guide d'Utilisation

## Vue d'ensemble

La visualisation en terminal permet de suivre en temps réel l'évolution du jeu sur une petite carte. Elle utilise des symboles et des couleurs pour représenter les unités et les obstacles.

## Contrôles

### Mouvements et Scroll
- **Z** : Scroll haut
- **S** : Scroll bas
- **Q** : Scroll gauche
- **D** : Scroll droite
- **Flèches directionnelles** : Alternative au ZQSD

### Commandes principales
- **P** : Pause/Reprendre le jeu
- **TAB** : Ouvrir la page HTML avec tous les détails (unités, stats, IA)
- **Esc** : Quitter le jeu
- **F9** : Changer la vue
- **F11** : Sauvegarde rapide
- **F12** : Chargement rapide

## Symboles et Couleurs

### Couleurs
- **(Bleu)** : Armée 1
- **(Rouge)** : Armée 2

### Types d'unités (Symboles)
| Symbole | Type |
|---------|------|
| **K** | Knight (Chevalier) |
| **P** | Pikeman (Pikier) |
| **X** | Crossbowman (Arbalétrier) |
| **S** | LongSwordsman (Épéiste) |
| **E** | EliteSkirmisher (Skirmisher élite) |
| **A** | CavalryArcher (Archer à cheval) |
| **O** | Onager (Catapulte) |
| **C** | LightCavalry (Cavalerie légère) |
| **R** | Scorpion (Scorpion) |
| **M** | CappedRam (Bélier) |
| **T** | Trebuchet (Trébuchet) |
| **W** | EliteWarElephant (Éléphant de guerre élite) |
| **\*** | Monk (Moine) |
| **#** | Castle (Château) |
| **\*** | Wonder (Merveille) |

### Obstacles
- **T** (vert) : Arbre
- **R** (gris) : Rocher
- **·** (gris) : Terrain vide

## Page de détails (TAB)

En appuyant sur TAB, une page HTML s'ouvre automatiquement avec :

### Informations par armée
- **Nombre d'unités** : Vivantes et totales
- **Pourcentage de survie** : Ratio des unités vivantes
- **Santé globale** : Points de vie totaux avec barre de progression

### Détails pour chaque unité
- **Type** : Classe de l'unité
- **ID** : Identifiant unique
- **Santé** : Points de vie avec barre visuelle (code couleur)
- **Position** : Coordonnées X,Y
- **Attaque** : Puissance et type (mêlée/perçant)
- **Armure** : Résistances mêlée et perçante
- **Tâche actuelle** : État actuel (marche, attaque, inactif, etc.)
- **Statut** : Vivant ou mort

### État de l'IA
Les fichiers HTML contiennent aussi des données sur l'état des généraux et leurs stratégies.

## Conseils d'utilisation

1. **Petites cartes** : La vue terminal est idéale pour des cartes <= 80x25
2. **Scroll** : Utilisez ZQSD pour explorer les zones non affichées
3. **Pause** : Appuyez sur P pour pause le jeu et prendre du temps pour analyser
4. **Détails** : TAB vous permet d'inspecter tous les dégâts et positions exactes
5. **Couleurs** : Les couleurs ANSI permettent de distinguer rapidement les deux armées

## Limitations

- Affichage limité à 80 caractères de largeur (terminal standard)
- Affichage limité à 25 lignes de hauteur
- Les unités se superposant dans la même case affichent seulement la dernière
- Nécessite un terminal supportant les codes couleurs ANSI

## Fichiers générés

À chaque appui sur TAB, un nouveau fichier HTML est créé dans le dossier `saves/` :
```
saves/snapshot_time_Xs_YYYYMMDD_HHMMSS.html
```

Où X est le temps écoulé en secondes depuis le début du jeu.