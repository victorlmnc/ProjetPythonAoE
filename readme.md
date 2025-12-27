# 🏰 MedievAIl - Battle GenerAIl Simulator

> Simulateur de batailles médiévales inspiré d'Age of Empires II, axé sur les tactiques IA.

---

## 🚀 Installation

```bash
pip install pygame pillow matplotlib pytest
```

---

## 🎮 Lancer le Jeu

```bash
# Partie rapide (10v10 Knights, mode Pygame)
python main.py play

# Mode Terminal ASCII
python main.py play -t

# Personnaliser unités/nombre/IA
python main.py play -u Pikeman -n 20 -ai MajorDAFT ColonelKAISER
```

---

## ⌨️ Contrôles en Jeu (Pygame)

### Navigation Caméra

| Contrôle | Action |
|----------|--------|
| **W / ↑** | Haut |
| **A / ←** | Gauche |
| **S / ↓** | Bas |
| **D / →** | Droite |
| **Maj + WASD** | Déplacement rapide (3x) |
| **Clic droit + glisser** | Faire glisser la carte |
| **Molette** | Zoom avant / arrière |

### Affichage (Toggles)

| Touche | Action |
|--------|--------|
| **1** | Toggle infos armée |
| **2** | Toggle barres de vie |
| **3** ou **M** | Toggle minimap |
| **4** | Toggle détails unités |

### Contrôles Jeu

| Touche | Action |
|--------|--------|
| **Espace** | Pause / Reprendre |
| **F11** | Sauvegarde rapide |
| **F12** | Info chargement |
| **Échap** | Quitter |

---

## 📋 Commandes CLI

```bash
# Partie rapide
python main.py play [options]

# Test Lanchester (N vs 2N)
python main.py lanchester Knight 10

# Graphique Lanchester (matplotlib)
python main.py plot MajorDAFT lanchester Knight "range(5, 25, 5)"

# Tournoi automatique
python main.py tourney -G MajorDAFT ColonelKAISER -S maps/small.map -N 10
```

---

## 👥 Généraux (IA)

| Nom | Comportement |
|-----|--------------|
| `CaptainBRAINDEAD` | Passif, n'attaque que si agressé |
| `MajorDAFT` | Agressif, attaque l'ennemi le plus proche |
| `ColonelKAISER` | Avancé : formations, kiting, focus fire |

---

## ⚔️ Unités

| Unité | HP | Attaque | Portée | Spécial |
|-------|-----|---------|--------|---------|
| Knight | 100 | 10 | 0.5 | - |
| Pikeman | 55 | 4 | 0.5 | +22 vs Cavalerie |
| Crossbowman | 35 | 6 | 7.0 | - |
| Onager | 50 | 50 | 8.0 | Splash damage |
| EliteWarElephant | 620 | 20 | 0.5 | Trample damage |
| Monk | 30 | 0 | 9.0 | Heal & Convert |

---

## 🧪 Tests

```bash
pytest tests/test_unit.py -v
```

---

## ⚡ Mécaniques

- **Formule dégâts** : `max(1, Attaque + Bonus - Armure)`
- **Élévation** : +25% dégâts depuis hauteur
- **Victoire** : Destruction armée ou Wonder ennemie