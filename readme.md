# Projet de programmation : MedievAIl BAIttle GenerAIl
## But : 

```
créer en `Python` un simulateur de batailles médiévales inspiré d’Age of Empires II, 
mais qui se concentre uniquement sur l’aspect militaire 
(pas d’économie, pas de construction de base, pas de production de ressources).
```

### Branche dev : 
  
projet_bataille/  

│── main.py                # Point d'entrée (gestion CLI avec argparse)  
│── battle/  
│   │── __init__.py  
│   │── engine.py          # Boucle de jeu, règles de combat, conditions de victoire  
│   │── scenario.py        # Chargement/définition des scénarios (JSON/YAML)  
│   │── map.py             # Classe Map (grille, cases, obstacles)  
│   │── unit.py            # Classe de base Unit + sous-classes (Knight, Pikeman, etc.)  
│   │── structures.py      # Bâtiments (Castle, Wonder, etc.)  
│   │── damage.py          # Calculs de dégâts (formules AoE)  
│  
│── ai/  
│   │── __init__.py  
│   │── base_general.py    # Classe General (interface commune pour toutes les IA)  
│   │── brain_dead.py      # Implémentation du Capitaine BRAINDEAD  
│   │── daft.py            # Implémentation du Major DAFT  
│   │── smart_general.py   # IA évoluées (formations, contres…)  
│  
│── visuals/  
│   │── __init__.py  
│   │── terminal_view.py   # Affichage en mode terminal (ASCII/couleurs)  
│   │── gui_view.py        # Affichage 2.5D avec PyGame/Arcade  
│  
│── tournament/  
│   │── __init__.py  
│   │── manager.py         # Lancement des tournois automatiques  
│   │── report.py          # Génération du rapport (HTML/PDF avec stats)  
│  
│── data/  
│   │── scenarios/         # Fichiers JSON/YAML de scénarios  
│   │── units.json         # Base de données des unités (HP, attaque, armure…)  
│   │── sprites/           # Images pour affichage 2.5D  
│  
│── tests/  
│   │── test_units.py      # Tests unitaires (dégâts, mouvements…)  
│   │── test_ai.py         # Tests comportement IA  
│   │── test_engine.py     # Tests du moteur de jeu  
