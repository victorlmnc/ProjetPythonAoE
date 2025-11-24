# main.py
import argparse
import sys
from typing import Optional

# --- Import de nos modules de jeu ---
# (Nous supposons qu'ils existent et sont prêts)
from core.map import Map
from core.army import Army
from core.unit import Unit, Knight, Pikeman, Crossbowman
from ai.general import General
from ai.generals_impl_IA import CaptainBRAINDEAD, MajorDAFT, ColonelKAISER
from engine import Engine
from view.terminal_view import TerminalView
from utils.serialization import save_game, load_game

GENERAL_CLASS_MAP = {
    "CaptainBRAINDEAD": CaptainBRAINDEAD,
    "MajorDAFT": MajorDAFT,
    #"ColonelKAISER": ColonelKAISER, # Ajoutez votre IA ici quand elle sera prête
}

UNIT_CLASS_MAP = {
    "Knight": Knight,
    "Pikeman": Pikeman,
    "Crossbowman": Crossbowman,
}

GENERAL_CLASS_MAP = {
    "CaptainBRAINDEAD": CaptainBRAINDEAD,
    "MajorDAFT": MajorDAFT,
    "ColonelKAISER": ColonelKAISER, # <-- Elle est maintenant disponible !
}

def load_map_from_file(filepath: str) -> Map:
    """
    Charge une carte (taille + obstacles) depuis un fichier .map.
    """
    print(f"Chargement de la carte depuis {filepath}...")
    
    width, height = 100.0, 100.0 # Valeurs par défaut de sécurité
    obstacles_to_add = []
    
    try:
        with open(filepath, 'r') as f:
            for line_number, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # 1. Lecture de la taille "SIZE: W H"
                if line.startswith("SIZE:"):
                    parts = line.split(":", 1)[1].strip().split()
                    if len(parts) != 2:
                        raise ValueError(f"Ligne {line_number}: Format SIZE invalide. Attendu: W H")
                    width = float(parts[0])
                    height = float(parts[1])
                
                # 2. Lecture des obstacles "Type, X, Y"
                else:
                    parts = line.split(',')
                    if len(parts) == 3:
                        obs_type = parts[0].strip()
                        x = float(parts[1].strip())
                        y = float(parts[2].strip())
                        obstacles_to_add.append((obs_type, x, y))
                        
    except FileNotFoundError:
        print(f"Erreur: Fichier carte introuvable '{filepath}'", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Erreur dans le fichier carte '{filepath}': {e}", file=sys.stderr)
        sys.exit(1)

    # Création de l'objet Map
    game_map = Map(width, height)
    
    # Ajout des obstacles
    for obs in obstacles_to_add:
        game_map.add_obstacle(*obs)
        
    print(f"Carte chargée: {width}x{height} avec {len(obstacles_to_add)} obstacles.")
    return game_map

def load_army_from_file(filepath: str, army_id: int) -> Army:
    """
    Charge une définition d'armée depuis un fichier .txt
    """
    print(f"Chargement de l'armée {army_id} depuis {filepath}...")
    
    general_class: Optional[type[General]] = None
    units_to_create: list[tuple[type[Unit], tuple[float, float]]] = []
    
    try:
        # 'with open' est la méthode recommandée (sec 26.1)
        with open(filepath, 'r') as f:
            for line_number, line in enumerate(f, 1):
                line = line.strip() # Nettoie les espaces et les sauts de ligne
                
                # Ignore les commentaires et les lignes vides
                if not line or line.startswith('#'):
                    continue
                
                # --- 1. Cherche la déclaration du Général ---
                if line.startswith("GENERAL:"):
                    general_name = line.split(":", 1)[1].strip()
                    general_class = GENERAL_CLASS_MAP.get(general_name)
                    
                    if general_class is None:
                        raise ValueError(f"Ligne {line_number}: Général inconnu '{general_name}'.")
                
                # --- 2. Cherche les déclarations d'unités ---
                else:
                    parts = line.split(',')
                    if len(parts) != 3:
                        raise ValueError(f"Ligne {line_number}: Format invalide. Attendu: Type, X, Y")
                    
                    unit_type_name = parts[0].strip()
                    unit_class = UNIT_CLASS_MAP.get(unit_type_name)
                    
                    if unit_class is None:
                        raise ValueError(f"Ligne {line_number}: Type d'unité inconnu '{unit_type_name}'.")
                    
                    # Conversion en flottants (sec 22.2)
                    pos = (float(parts[1].strip()), float(parts[2].strip()))
                    units_to_create.append((unit_class, pos))
    
    except FileNotFoundError:
        print(f"Erreur: Fichier armée introuvable '{filepath}'", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Erreur dans le fichier '{filepath}': {e}", file=sys.stderr)
        sys.exit(1)

    # --- 3. Validation et Création ---
    if general_class is None:
        print(f"Erreur: Le fichier '{filepath}' ne définit aucun 'GENERAL:'.", file=sys.stderr)
        sys.exit(1)
        
    # Instancie le Général
    general_instance = general_class(army_id=army_id)
    
    # Instancie les Unités
    created_units: list[Unit] = []
    
    # Crée un ID de base unique pour cette armée
    # (par ex: Armée 0 -> ID 0-999, Armée 1 -> ID 1000-1999)
    # Assure des unit_id uniques globalement.
    unit_id_base = army_id * 1000 
    
    for i, (unit_class, pos) in enumerate(units_to_create):
        unit_id = unit_id_base + i
        unit = unit_class(unit_id=unit_id, army_id=army_id, pos=pos)
        created_units.append(unit)
        
    print(f"Armée {army_id} chargée: {general_instance.__class__.__name__} avec {len(created_units)} unités.")
    return Army(army_id=army_id, units=created_units, general=general_instance)
def load_game_from_save(filepath: str) -> Engine:
    """
    Placeholder: Charge un moteur de jeu complet depuis une sauvegarde (req 12).
    """
    print(f"Chargement de la partie sauvegardée depuis {filepath}...")
    # Logique de désérialisation (pickle ou json, sec 26) à venir
    raise NotImplementedError("Le chargement de sauvegarde n'est pas encore implémenté.")


def main(args: Optional[list[str]] = None):
    """
    Point d'entrée principal de la simulation MedievAIl.
    """
    
    # 1. Configuration de argparse (Req 10)
    parser = argparse.ArgumentParser(description="MedievAIl - Battle GenerAIl Simulator")
    
    # --- Arguments pour une NOUVELLE partie ---
    parser.add_argument(
        "--map", 
        type=str, 
        help="Chemin vers le fichier .map définissant la carte."
    )
    parser.add_argument(
        "--army1", 
        type=str, 
        help="Chemin vers le fichier .txt définissant l'armée 1 (Bleue)."
    )
    parser.add_argument(
        "--army2", 
        type=str, 
        help="Chemin vers le fichier .txt définissant l'armée 2 (Rouge)."
    )
    
    # --- Argument pour CHARGER une partie ---
    parser.add_argument(
        "--load_game", 
        type=str, 
        help="Chemin vers un fichier de sauvegarde .sav pour reprendre une partie (req 12)."
    )
    
    # --- Arguments Optionnels ---
    parser.add_argument(
        "--headless",
        action="store_true",  # Crée un booléen (True si présent, False sinon)
        help="Lance la simulation sans affichage (pour les tournois, req 11)."
    )
    parser.add_argument(
        "--max_turns",
        type=int,
        default=5,
        help="Nombre maximum de tours avant de déclarer une égalité."
    )

    # 2. Parsing des arguments
    # Si 'args' est None, argparse utilise automatiquement sys.argv[1:]
    parsed_args = parser.parse_args(args)

    print("--- Configuration de la Simulation ---")
    
    engine: Optional[Engine] = None

    # 3. Logique de démarrage : Nouvelle partie OU Chargement
    
    if parsed_args.load_game:
        # Cas 1: On charge une partie sauvegardée
        if parsed_args.map or parsed_args.army1 or parsed_args.army2:
            print("Avertissement: --load_game ignore les arguments --map et --army.")
        try:
            engine = load_game_from_save(parsed_args.load_game)
        except NotImplementedError as e:
            print(f"Erreur: {e}", file=sys.stderr)
            sys.exit(1)
    
    elif parsed_args.map and parsed_args.army1 and parsed_args.army2:
        # Cas 2: On crée une nouvelle partie
        print("Mode: Nouvelle Partie")
        
        # (Ici, nous utilisons nos fonctions placeholder)
        game_map = load_map_from_file(parsed_args.map)
        army1 = load_army_from_file(parsed_args.army1, army_id=0)
        army2 = load_army_from_file(parsed_args.army2, army_id=1)
        
        engine = Engine(game_map, army1, army2)
        
    else:
        # Cas 3: Commande invalide
        print("Erreur: Vous devez fournir soit --load_game, soit --map, --army1, ET --army2.", file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    # 4. Lancement de la simulation
    if engine:
        print(f"Mode Headless: {parsed_args.headless}")
        print(f"Tours Max: {parsed_args.max_turns}")
        
        view = None
        
        if not parsed_args.headless:
            print("Initialisation de l'affichage Terminal...")
            view = TerminalView(engine.map)
        
        # Lancement du moteur de jeu
        engine.run_game(max_turns=parsed_args.max_turns, view=view)

# --- Point d'entrée standard en Python ---
if __name__ == "__main__":
    # Permet à argparse de lire les arguments de la ligne de commande
    main()