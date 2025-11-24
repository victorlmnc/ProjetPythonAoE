# main.py
import argparse
import sys
from typing import Optional

# --- Import de nos modules de jeu ---
# (Nous supposons qu'ils existent et sont prêts)
from core.map import Map
from core.army import Army
from core.unit import Knight, Pikeman, Archer
from ai.general import General
from ai.generals_impl import CaptainBRAINDEAD, MajorDAFT
from engine import Engine

# (Ces fonctions sont des placeholders pour l'instant)
# Nous les implémenterons à l'étape suivante.
def load_map_from_file(filepath: str) -> Map:
    """
    Placeholder: Charge une définition de carte depuis un fichier.
    Pour l'instant, retourne une carte par défaut.
    """
    print(f"Chargement de la carte depuis {filepath}...")
    # Retourne une carte flottante de 100x100
    return Map(width=100.0, height=100.0)

def load_army_from_file(filepath: str, army_id: int) -> Army:
    """
    Placeholder: Charge une définition d'armée depuis un fichier.
    Pour l'instant, retourne une armée par défaut.
    """
    print(f"Chargement de l'armée {army_id} depuis {filepath}...")
    
    # Création d'une armée de test
    units = []
    general = MajorDAFT(army_id=army_id) # IA par défaut
    
    if army_id == 0:
        # Armée 0 (Bleue) : 5 Chevaliers
        units = [Knight(unit_id=i, army_id=army_id, pos=(48.0, float(i * 2))) for i in range(5)]
    else:
        # Armée 1 (Rouge) : 10 Piquiers
        units = [Pikeman(unit_id=i + 5, army_id=army_id, pos=(52.0, float(i * 2))) for i in range(10)]
        
    return Army(army_id=army_id, units=units, general=general)

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
        
        if not parsed_args.headless:
            # Ici, on liera l'affichage (terminal ou Pygame)
            print("Lancement avec affichage (non implémenté)...")
            # view = TerminalView(engine)
            # engine.set_view(view)
        
        # Lancement du moteur de jeu
        engine.run_game(max_turns=parsed_args.max_turns)

# --- Point d'entrée standard en Python ---
if __name__ == "__main__":
    # Permet à argparse de lire les arguments de la ligne de commande
    main()