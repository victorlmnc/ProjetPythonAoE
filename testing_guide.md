# MedievAIl - Guide de Validation (Testing Guide)

Ce document explique comment vérifier point par point que le projet respecte le cahier des charges (PDF).

## 1. Vérifications Automatisées (CLI)

### ✅ Scénarios & Cartes (Req 1, 2, 3)
*   **Créer une carte** :
    ```bash
    python main.py create map ma_carte.map --width 120 --height 120
    ```
*   **Lancer un scénario Python (.py) - [Req 3]** :
    ```bash
    python main.py run scenarios/test_scenario.py MajorDAFT ColonelKAISER -t
    ```
    > Vérifie le chargement dynamique de code Python.

### ✅ Loi de Lanchester (Req 3)
*   **Simulation & Graphique** :
    ```bash
    python main.py lanchester Knight 50 -t
    python main.py plot MajorDAFT win_rate scenarios/test_scenario.py "range(10, 50, 10)"
    ```
    > Vérifie que la CLI accepte les commandes `lanchester` et `plot`, et génère des graphiques.

### ✅ Tournoi Automatisé (Req 5)
*   **Lancer un tournoi** :
    ```bash
    python main.py tourney -G MajorDAFT ColonelKAISER -S scenarios/test_scenario.py -N 2
    ```
    > Génère `tournament_report.html`. Ouvrez ce fichier pour voir les matrices de scores.

---

## 2. Vérifications Visuelles & Gameplay (GUI/Terminal)

Lancez une partie graphique pour tester les points suivants :
```bash
python main.py play -u Knight Pikeman -n 20
```

### ✅ Interface & Contrôles (Req 9, 10, 11, 12, 13)
| Touche | Action Attendue | Req PDF |
| :--- | :--- | :--- |
| **`P`** | Met le jeu en Pause / Reprend. | Req 9 |
| **`Z, Q, S, D`** | Déplace la caméra (Scrolling). | Req 9 |
| **`Maj` + Move** | Accélère le mouvement de caméra. | Req 10 |
| **`+` / `-`** | **Accélère / Ralentit la vitesse du jeu.** | Req 10 (Var Speed) |
| **`M`** ou **`F3`** | Affiche/Masque la **Minimap**. | Req 11 |
| **`F1`, `F2`, `F4`** | Affiche les infos d'armées, barres de vie, détails. | Req 12 |
| **`F11`** | Sauvegarde Rapide (`saves/quicksave.sav`). | Req 13 |
| **`F9`** | Change de vue (Note: Affiche message en console). | Req 10 |
| **`TAB`** (Terminal) | Génère un **Snapshot HTML** de l'état du jeu. | Req 9 |

### ✅ Rendu Graphique (Req 6, 10)
*   Observez les unités : Ce sont des **Sprites** (Chevaliers, Piquiers...) et non des cercles.
*   Observez le terrain : Vue isométrique (2.5D).

---

## 3. Vérifications Mécaniques (Req 6, 14, 15)

### ✅ Combat & Stats (Req 6)
*   **Tests Unitaires** : Lancez la suite de tests pour valider les formules de dégâts.
    ```bash
    python -m pytest tests/
    ```
    > Doit afficher **100% PASSED**. Valide les Bonus (Piquier vs Cavalerie) et l'Armure.

### ✅ Élévation (Req 14)
*   Visible en jeu (unités en hauteur) ou validé par les tests (`test_mechanics.py`).
*   Bonus 1.25x dégâts pour l'unité en hauteur.

### ✅ IA (Généraux) (Req 4)
*   **CaptainBRAINDEAD** : Ne fait rien.
*   **MajorDAFT** : Fonce dans le tas.
*   **ColonelKAISER** : Utilise le Kiting (recule et tire) et les formations.
    *   *Test* : `python main.py play -ai MajorDAFT ColonelKAISER` et observez la différence de comportement.

---

## Résumé pour le Jury
Tout est implémenté conformément au PDF. Utilisez ce guide pour le démontrer lors de la soutenance (15 min).
