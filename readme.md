# Projet de programmation : MedievAIl BAIttle GenerAIl

Ce projet est un simulateur de batailles médiévales inspiré d'Age of Empires II, axé sur les tactiques militaires IA sans aucun aspect économique.

## Comment utiliser le simulateur

Le programme utilise une interface en ligne de commande. Toutes les commandes commencent par `python main.py`, suivi d'une sous-commande (`battle`, `tournament`, `lanchester`) et de ses options.

### 1. Lancer une bataille simple

Pour lancer une simulation de bataille, utilisez la commande `battle`.

#### Vue Terminal (par défaut)
Vous verrez une représentation textuelle de la bataille directement dans votre terminal.

```bash
python main.py battle --map "maps/small.map" --army1 "armies/armee_test_bleue.txt" --army2 "armies/armee_test_rouge.txt"
```

#### Vue Graphique (Pygame)
Pour une expérience visuelle, vous pouvez utiliser la vue Pygame.

**Prérequis :** Assurez-vous d'avoir installé la bibliothèque Pygame.
```bash
pip install pygame
```

**Commande :**
Ajoutez l'option `--view pygame` pour ouvrir une fenêtre graphique qui affichera la bataille.
```bash
python main.py battle --map "maps/small.map" --army1 "armies/armee_test_bleue.txt" --army2 "armies/armee_test_rouge.txt" --view pygame
```

### 2. Lancer un tournoi automatique

Pour faire s'affronter plusieurs IA sur différentes cartes et obtenir un tableau de scores, utilisez la commande `tournament`. Ce mode est "headless" (sans affichage) pour garantir une exécution rapide.

```bash
python main.py tournament --generals CaptainBRAINDEAD MajorDAFT --maps maps/small.map --armies armies/armee_test_bleue.txt armies/armee_test_rouge.txt
```

### 3. Tester les lois de Lanchester

Pour lancer un scénario généré de manière procédurale basé sur les lois de Lanchester (une petite armée contre une armée deux fois plus grande), utilisez la commande `lanchester`.

```bash
python main.py lanchester --unit Knight --n 10 --map maps/small.map
```
Vous pouvez également lancer ce scénario avec la vue Pygame :
```bash
python main.py lanchester --unit Knight --n 10 --map maps/small.map --view pygame
```

### 4. Sauvegarder et charger une partie

Vous pouvez sauvegarder l'état d'une bataille à la fin de la simulation et le recharger plus tard.

*   **Pour sauvegarder :** Ajoutez l'option `--save_path`.
    ```bash
    python main.py battle --map "maps/small.map" --army1 "armies/armee_test_bleue.txt" --army2 "armies/armee_test_rouge.txt" --max_turns 10 --save_path saves/partie_sauvegardee.sav
    ```

*   **Pour charger :** Utilisez l'option `--load_game` avec la commande `battle`.
    ```bash
    python main.py battle --load_game saves/partie_sauvegardee.sav --max_turns 20
    ```
