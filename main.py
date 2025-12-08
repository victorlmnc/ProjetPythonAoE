# main.py
import argparse
import sys
import os
from typing import Optional

# --- Import de nos modules de jeu ---
from core.map import Map
from core.army import Army
from engine import Engine
from view.terminal_view import TerminalView
from view.gui_view import PygameView 
from utils.serialization import save_game, load_game
from tournament import Tournament
from utils.loaders import load_map_from_file, load_army_from_file
from core.definitions import GENERAL_CLASS_MAP, UNIT_CLASS_MAP
from scenarios import lanchester_scenario, custom_battle_scenario

# Import du Menu
try:
    from view.menu_view import MenuView
    HAS_MENU = True
except ImportError:
    HAS_MENU = False

def load_game_from_save(filepath: str) -> Engine:
    """
    Charge un moteur de jeu complet depuis une sauvegarde.
    """
    return load_game(filepath)

def save_army_to_text_file(army: Army, filepath: str):
    """
    Saves an Army object to a text file compatible with load_army_from_file.
    """
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            # Write General Class Name
            f.write(f"{type(army.general).__name__}\n")
            
            # Write Units
            for unit in army.units:
                # Assuming unit.pos is a tuple (x, y)
                x, y = unit.pos
                f.write(f"{type(unit).__name__} {x} {y}\n")
        print(f"Army saved to: {filepath}")
    except Exception as e:
        print(f"Error saving army to {filepath}: {e}")

def main(args: Optional[list[str]] = None):
    """
    Point d'entrée principal de la simulation MedievAIl.
    """

    parser = argparse.ArgumentParser(description="MedievAIl - Battle GenerAIl Simulator")
    subparsers = parser.add_subparsers(dest="command")

    # --- Battle Command ---
    battle_parser = subparsers.add_parser("battle", help="Run a single battle")
    battle_parser.add_argument("--map", required=True, type=str, help="Path to the .map file")
    battle_parser.add_argument("--army1", required=True, type=str, help="Path to the army 1 .txt file")
    battle_parser.add_argument("--army2", required=True, type=str, help="Path to the army 2 .txt file")
    battle_parser.add_argument("--load_game", type=str, help="Path to a .sav file to load a game")
    battle_parser.add_argument("--view", type=str, default="terminal", choices=["terminal", "pygame"], help="Choose the view mode")
    battle_parser.add_argument("--max_turns", type=int, default=1000, help="Maximum number of turns")
    battle_parser.add_argument("--save_path", type=str, help="Path to save the final game state")

    # --- GUI Command ---
    gui_parser = subparsers.add_parser("gui", help="Run the configuration GUI")

    # --- Tournament Command ---
    tournament_parser = subparsers.add_parser("tournament", help="Run a tournament")
    tournament_parser.add_argument("--generals", required=True, nargs='+', help="List of general names")
    tournament_parser.add_argument("--maps", required=True, nargs='+', help="List of map paths")
    tournament_parser.add_argument("--armies", required=True, nargs='+', help="List of army paths")
    tournament_parser.add_argument("--rounds", type=int, default=1, help="Number of rounds per matchup")

    # --- Lanchester Command ---
    lanchester_parser = subparsers.add_parser("lanchester", help="Run a Lanchester's Law scenario")
    lanchester_parser.add_argument("--unit", required=True, type=str, help="Unit type to use")
    lanchester_parser.add_argument("--n", required=True, type=int, help="Number of units for the smaller army")
    lanchester_parser.add_argument("--map", required=True, type=str, help="Path to the .map file")
    lanchester_parser.add_argument("--view", type=str, default="terminal", choices=["terminal", "pygame"], help="Choose the view mode")
    lanchester_parser.add_argument("--max_turns", type=int, default=1000, help="Maximum number of turns")

    parsed_args = parser.parse_args(args)

    if parsed_args.command == "battle":
        run_battle(parsed_args)
    elif parsed_args.command == "gui":
        run_gui()
    elif parsed_args.command == "tournament":
        run_tournament(parsed_args)
    elif parsed_args.command == "lanchester":
        run_lanchester(parsed_args)
    else:
        # Default behavior
        parser.print_help()

def run_gui():
    """
    Runs the graphical configuration menu.
    """
    if not HAS_MENU:
        print("Erreur: Impossible de charger le module de menu (Pygame manquant?).")
        return

    print("Lancement du Menu de Configuration...")
    menu = MenuView()
    config = menu.run()

    if config:
        print("\n--- Lancement de la Bataille Personnalisée ---")
        print(f"Map: {config['map']}")
        print(f"General 1: {config['general1']} - Units: {config['comp1']}")
        print(f"General 2: {config['general2']} - Units: {config['comp2']}")

        # Loading resources
        game_map = load_map_from_file(config['map'])
        gen1_class = GENERAL_CLASS_MAP[config['general1']]
        gen2_class = GENERAL_CLASS_MAP[config['general2']]

        # Create armies using the dictionary compositions
        army1, army2 = custom_battle_scenario(
            config['comp1'],
            config['comp2'],
            gen1_class, gen2_class,
            (game_map.width, game_map.height)
        )

        # Save to file for debug/replay
        save_army_to_text_file(army1, "armies/gui_generated_p1.txt")
        save_army_to_text_file(army2, "armies/gui_generated_p2.txt")

        # Run Engine
        engine = Engine(game_map, army1, army2)
        view = PygameView(engine.map) # Force Pygame view for GUI mode
        
        try:
            engine.run_game(max_turns=1000, view=view)
        except KeyboardInterrupt:
            print("\nArrêt.")

def run_battle(args):
    """
    Runs a single battle simulation.
    """
    print("--- Configuration de la Simulation ---")

    engine: Optional[Engine] = None

    if args.load_game:
        if args.map or args.army1 or args.army2:
            print("Avertissement: --load_game ignore les arguments --map et --army.")
        try:
            engine = load_game_from_save(args.load_game)
        except NotImplementedError as e:
            print(f"Erreur: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.map and args.army1 and args.army2:
        print("Mode: Nouvelle Partie")

        game_map = load_map_from_file(args.map)
        army1 = load_army_from_file(args.army1, army_id=0)
        army2 = load_army_from_file(args.army2, army_id=1)

        engine = Engine(game_map, army1, army2)

    else:
        print("Erreur: Vous devez fournir soit --load_game, soit --map, --army1, ET --army2.", file=sys.stderr)
        sys.exit(1)

    if engine:
        print(f"Vue: {args.view}")
        print(f"Tours Max: {args.max_turns}")

        view = None
        if args.view == "terminal":
            print("Initialisation de l'affichage Terminal...")
            view = TerminalView(engine.map)
        elif args.view == "pygame":
            print("Initialisation de l'affichage Pygame...")
            view = PygameView(engine.map)

        try:
            engine.run_game(max_turns=args.max_turns, view=view)
        except KeyboardInterrupt:
            print("\nSimulation interrompue par l'utilisateur.")

        if args.save_path:
            save_game(engine, args.save_path)

def run_tournament(args):
    """
    Runs a tournament.
    """
    tournament = Tournament(args.generals, args.maps, args.armies, args.rounds)
    tournament.run()

def run_lanchester(args):
    """
    Runs a Lanchester's Law scenario.
    """
    unit_class = UNIT_CLASS_MAP.get(args.unit)
    if unit_class is None:
        print(f"Error: Unknown unit type '{args.unit}'")
        sys.exit(1)

    game_map = load_map_from_file(args.map)
    army1, army2 = lanchester_scenario(unit_class, args.n)

    engine = Engine(game_map, army1, army2)

    view = None
    if args.view == "terminal":
        view = TerminalView(engine.map)
    elif args.view == "pygame":
        view = PygameView(engine.map)

    engine.run_game(max_turns=args.max_turns, view=view)

if __name__ == "__main__":
    main()