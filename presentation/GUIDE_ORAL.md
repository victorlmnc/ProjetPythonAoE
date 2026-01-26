# 🎤 Guide de Préparation Oral - MedievAIl

## ⏱️ Timing (15 minutes max)

| Phase | Durée | Contenu |
|-------|-------|---------|
| **Slides** | ~1min30 | Tableau requirements + Équipe |
| **Démo Live** | ~13min | Démonstration complète |

---

## 📋 SLIDE 1 : Requirements (~1min30)

### Points clés à mentionner :

1. **Architecture MVC** : Séparation claire `core/` (Modèle), `view/` (Vue), `engine.py` (Contrôleur)

2. **3 Niveaux d'IA** :
   - `CaptainBRAINDEAD` : Actions individuelles dans la ligne de vue uniquement
   - `MajorDAFT` : Seek & destroy global
   - `ColonelKAISER` : Stratégies avancées (kiting, formations, focus fire, cohésion)

3. **Points forts** :
   - 13 types d'unités avec stats AoE2
   - Mode headless pour tournois automatiques
   - Reinforcement Learning intégré

4. **Limitation** (mentionner honnêtement) :
   - Pas de pathfinding A* complet, utilise steering + collision sliding

---

## 📋 SLIDE 2 : Équipe (~30s)

> À COMPLÉTER avec vos vraies infos !

- Dire brièvement les contributions principales
- Ne pas s'attarder

---

## 🎮 PLAN DE DÉMONSTRATION LIVE (~13 min)

### Commandes préparées (copier-coller prêts) :

```powershell
# 1. PARTIE RAPIDE - Montrer le jeu de base
python main.py play -ai MajorDAFT ColonelKAISER -n 20 -u Knight Pikeman

# 2. MODE TERMINAL (req 7)
python main.py play -ai MajorDAFT ColonelKAISER -n 10 -t

# 3. SCÉNARIO PERSONNALISÉ (req 8)
python main.py run scenarios/compliance_test.scen MajorDAFT ColonelKAISER

# 4. TEST LANCHESTER (req 8)
python main.py lanchester Knight 15 --general MajorDAFT

# 5. TOURNOI AUTOMATIQUE (req 8)
python main.py tourney -G MajorDAFT ColonelKAISER CaptainBRAINDEAD -S maps/small.map -N 2

# 6. MODE RL (bonus)
python main.py match --map-size 100 --units 30
```

---

### Déroulé minute par minute :

#### ⏱️ 0:00 - 2:00 : Partie Rapide GUI (Req 5, 7)
```powershell
python main.py play -ai MajorDAFT ColonelKAISER -n 25 -u Knight Archer --map-size 100x100
```

**Démo actions pendant le jeu :**
- [ ] Zoom molette (Req 7)
- [ ] Déplacement caméra WASD/Flèches
- [ ] Pause/Reprise (Espace)
- [ ] Vitesse +/- (Req 7)
- [ ] F1/F2/F3 pour les overlays
- [ ] **F11 Quick Save** (très important à montrer!)
- [ ] **F12 Quick Load** (recharger l'état)

**À dire :** "Ici on voit le moteur temps réel (req 5) avec positions flottantes et le système de cooldown. Les animations sont synchronisées avec le reload time des unités."

---

#### ⏱️ 2:00 - 3:00 : Vue Terminal (Req 2, 7)
```powershell
python main.py play -ai MajorDAFT ColonelKAISER -n 8 -t
```

**À dire :** "Le mode headless (req 2) permet d'exécuter sans aucune dépendance graphique. Ici on montre la vue Terminal ASCII pour le debug."

---

#### ⏱️ 3:00 - 5:00 : Comparaison IAs (Req 3)
```powershell
# D'abord BRAINDEAD vs DAFT (DAFT gagne)
python main.py play -ai CaptainBRAINDEAD MajorDAFT -n 15 -u Knight

# Puis DAFT vs KAISER (KAISER gagne toujours)
python main.py play -ai MajorDAFT ColonelKAISER -n 15 -u Knight Crossbowman
```

**À dire :** 
- "CaptainBRAINDEAD n'agit que sur sa ligne de vue, pas de coordination"
- "ColonelKAISER utilise le kiting (les archers fuient les mêlées), le focus fire, et les mêlées attendent les tireurs pour la cohésion"

---

#### ⏱️ 5:00 - 7:00 : Unités Avancées (Req 4, 6)
```powershell
# Montrer le Splash Damage
python main.py play -ai MajorDAFT MajorDAFT -n 5 -u Onager Knight

# Ou montrer les bonus de dégâts (Pikeman vs Cavalry)
python main.py play -ai MajorDAFT MajorDAFT -n 10 -u Pikeman Knight
```

**À dire :** 
- "L'Onager fait des dégâts splash dans un rayon de 1.5 tuiles"
- "Le Pikeman fait +22 de bonus contre la cavalerie (Knight)"

---

#### ⏱️ 7:00 - 9:00 : Mode Lanchester (Req 8)
```powershell
python main.py lanchester Knight 10 --general ColonelKAISER
```

**À dire :** "Ce mode teste la loi de Lanchester : N unités contre 2N. L'armée de 20 Knights devrait gagner avec des pertes réduites."

---

#### ⏱️ 9:00 - 11:00 : Tournoi Automatique (Req 8)
```powershell
python main.py tourney -G MajorDAFT ColonelKAISER CaptainBRAINDEAD -S maps/small.map -N 3
```

**À dire :** "Le tournoi génère un rapport HTML avec matrices de victoires. ColonelKAISER devrait dominer."

*Ouvrir `tournament_report.html` dans le navigateur pour montrer le résultat.*

---

#### ⏱️ 11:00 - 13:00 : Bonus RL + Création (Req bonus)
```powershell
# Mode Match avec modèles RL
python main.py match --map-size 80 --units 20 --maxturn 500

# Montrer la création de contenu (optionnel)
python main.py create map maps/demo.map --width 50 --height 50
```

**À dire :** "Nous avons implémenté un système de Reinforcement Learning. Les agents apprennent à combattre via Q-learning."

---

## 🔑 Points Clés à Retenir

### Requirements Critiques à Démontrer :

| Req | Quoi | Comment le montrer |
|-----|------|-------------------|
| 2 | Mode Headless | `-t` ou tournoi sans GUI |
| 3 | 3 IAs + KAISER > DAFT | Matchs directs |
| 5 | Temps réel + élévation | GUI + mentionner ±25% |
| 7 | Contrôles (pause, speed, save) | F11/F12, +/-, Espace |
| 8 | Formats scénario | `.scen`, `.py`, `.map` |

### Vocabulaire à utiliser :
- "Requirement numéro X"
- "Mode headless"
- "Positions flottantes"
- "Cooldown temps réel"
- "Kiting", "Focus fire", "Cohésion"
- "Splash damage", "Bonus de dégâts"

---

## ⚠️ Checklist Technique (Avant la démo)

- [ ] Tester que Python fonctionne : `python --version`
- [ ] Tester les dépendances : `pip install -r requirements.txt`
- [ ] Vérifier connexion vidéo-projecteur
- [ ] Lancer une fois `python main.py play` pour pré-charger les sprites
- [ ] Avoir les commandes prêtes dans un fichier texte
- [ ] Fermer toutes les applications inutiles
- [ ] Désactiver les notifications Windows

---

## 🎯 Questions Probables du Jury

1. **"Comment ColonelKAISER bat MajorDAFT ?"**
   → Kiting (tireurs fuient), formations, focus fire sur cibles basses HP, cohésion mêlée/tireurs

2. **"Comment fonctionne le système de dégâts ?"**
   → `(Attaque + Bonus) - Armure`, minimum 1 dégât

3. **"Pourquoi pas de pathfinding A* ?"**
   → Complexité + le steering avec sliding fonctionne bien pour notre cas d'usage

4. **"Comment marche le mode RL ?"**
   → Observation de l'état (positions, HP), actions discrètes, reward basé sur HP différentiel

5. **"Que fait le Monk ?"**
   → Soigne alliés (2 HP/tick) + peut convertir ennemis (change `army_id`)

---

## 📦 Fichiers à avoir prêts

1. `slides.html` → Ouvrir dans navigateur → Imprimer en PDF
2. Ce guide (pour réviser)
3. Terminal prêt dans le dossier du projet
4. `tournament_report.html` (pré-généré si possible)

---

**Bonne chance ! 🎉**
