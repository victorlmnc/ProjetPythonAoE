# main.py
"""
MedievAIl - Battle GenerAIl Simulator
Point d'entrée CLI conforme au cahier des charges PDF.

Usage:
    battle run <scenario> <AI1> <AI2> [-t] [-d DATAFILE]
    battle tourney -G <AI1> <AI2> ... -S <SCEN1> <SCEN2> ... [-N=10]
    battle plot <AI> <plotter> <scenario> <range>
    battle lanchester <unit_type> <N> [-t]
"""
import argparse
import sys
import os
from typing import Optional
import importlib.util

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
from utils.generators import generate_map_file, generate_army_file


def load_game_from_save(filepath: str) -> Engine:
    """Charge un moteur de jeu complet depuis une sauvegarde."""
    return load_game(filepath)


def main(args: Optional[list[str]] = None):
    """
    Point d'entrée principal de la simulation MedievAIl.
    CLI conforme au format du PDF (Req 1).
    """
    parser = argparse.ArgumentParser(
        prog="battle",
        description="MedievAIl - Battle GenerAIl Simulator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  battle run scenarios/1v1.py MajorDAFT ColonelKAISER -t
  battle tourney -G MajorDAFT ColonelKAISER -S scenarios/1v1.py -N 10
  battle lanchester Knight 10 -t
  battle plot MajorDAFT win_rate scenarios/1v1.py "range(5, 50, 5)"
        """
    )
    subparsers = parser.add_subparsers(dest="command", help="Commandes disponibles")

    # =========================================================================
    # Commande: play [-t] [-u UNIT COUNT] [-ai AI1 AI2] -- RACCOURCI SIMPLE
    # =========================================================================
    play_parser = subparsers.add_parser("play", help="🎮 Lancer une partie rapidement (raccourci)")
    play_parser.add_argument("-t", "--terminal", action="store_true",
                            help="Mode terminal ASCII")
    play_parser.add_argument("-u", "--units", nargs='+', default=["Knight"],
                            help="Type d'unité ou liste d'unités (ex: Knight Pikeman)")
    play_parser.add_argument("-n", "--count", type=int, default=10,
                            help="Nombre d'unités par camp (défaut: 10)")
    play_parser.add_argument("-ai", "--generals", nargs=2, default=["MajorDAFT", "MajorDAFT"],
                            help="IA des deux camps (défaut: MajorDAFT MajorDAFT)")
    play_parser.add_argument("--max_turns", type=int, default=2000,
                            help="Nombre max de tours")

    # =========================================================================
    # Commande: battle run <scenario> <AI1> <AI2> [-t] [-d DATAFILE]
    # =========================================================================
    run_parser = subparsers.add_parser("run", help="Lancer une bataille unique")
    run_parser.add_argument("scenario", type=str, 
                           help="Chemin vers le scénario (.py ou .map + armées)")
    run_parser.add_argument("AI1", type=str, 
                           help="Nom du général de l'armée 1 (ex: MajorDAFT)")
    run_parser.add_argument("AI2", type=str, 
                           help="Nom du général de l'armée 2 (ex: ColonelKAISER)")
    run_parser.add_argument("-t", "--terminal", action="store_true",
                           help="Mode terminal ASCII (défaut: mode 2.5D Pygame)")
    run_parser.add_argument("-d", "--datafile", type=str, default=None,
                           help="Fichier de sauvegarde à charger ou sauvegarder")
    run_parser.add_argument("--army1", type=str, default=None,
                           help="Fichier armée 1 (optionnel si scénario .py)")
    run_parser.add_argument("--army2", type=str, default=None,
                           help="Fichier armée 2 (optionnel si scénario .py)")
    run_parser.add_argument("--max_turns", type=int, default=1000,
                           help="Nombre maximum de tours (défaut: 1000)")

    # =========================================================================
    # Commande: battle tourney -G <AI1> <AI2>... -S <SCEN1>... [-N=10]
    # =========================================================================
    tourney_parser = subparsers.add_parser("tourney", help="Lancer un tournoi automatique")
    tourney_parser.add_argument("-G", "--generals", nargs='+', required=True,
                               help="Liste des généraux à faire combattre")
    tourney_parser.add_argument("-S", "--scenarios", nargs='+', required=True,
                               help="Liste des scénarios (fichiers .map)")
    tourney_parser.add_argument("-A", "--armies", nargs='+', default=None,
                               help="Liste des fichiers d'armées")
    tourney_parser.add_argument("-N", "--rounds", type=int, default=10,
                               help="Nombre de rounds par matchup (défaut: 10)")
    tourney_parser.add_argument("--na", action="store_true",
                               help="No-animation: mode headless sans affichage")

    # =========================================================================
    # Commande: battle plot <AI> <plotter> <scenario> <range>
    # =========================================================================
    plot_parser = subparsers.add_parser("plot", help="Générer des graphiques de performance")
    plot_parser.add_argument("AI", type=str, help="Nom du général à tester")
    plot_parser.add_argument("plotter", type=str, 
                            help="Type de graphique (win_rate, damage, survival)")
    plot_parser.add_argument("scenario", type=str, help="Scénario de base")
    plot_parser.add_argument("range", type=str, 
                            help="Range Python (ex: 'range(5, 50, 5)') - utilise eval()")
    plot_parser.add_argument("--opponent", type=str, default="MajorDAFT",
                            help="Adversaire pour les tests (défaut: MajorDAFT)")

    # =========================================================================
    # Commande: battle lanchester <unit_type> <N> [-t]
    # =========================================================================
    lanchester_parser = subparsers.add_parser("lanchester", 
                                              help="Scénario Lanchester (N vs 2N)")
    lanchester_parser.add_argument("unit_type", type=str,
                                  help="Type d'unité (Knight, Pikeman, etc.)")
    lanchester_parser.add_argument("N", type=int,
                                  help="Taille de la petite armée (l'autre = 2N)")
    lanchester_parser.add_argument("-t", "--terminal", action="store_true",
                                  help="Mode terminal ASCII")
    lanchester_parser.add_argument("--general", type=str, default="MajorDAFT",
                                  help="Général à utiliser (défaut: MajorDAFT)")
    lanchester_parser.add_argument("--max_turns", type=int, default=1000,
                                  help="Nombre maximum de tours")

    # =========================================================================
    # Commande legacy: battle (ancien format avec --map, --army1, etc.)
    # =========================================================================
    legacy_parser = subparsers.add_parser("legacy", 
                                          help="Mode legacy (ancien format CLI)")
    legacy_parser.add_argument("--map", required=True, type=str)
    legacy_parser.add_argument("--army1", required=True, type=str)
    legacy_parser.add_argument("--army2", required=True, type=str)
    legacy_parser.add_argument("--load_game", type=str, default=None)
    legacy_parser.add_argument("--view", type=str, default="terminal", 
                              choices=["terminal", "pygame"])
    legacy_parser.add_argument("--max_turns", type=int, default=1000)
    legacy_parser.add_argument("--save_path", type=str, default=None)

    # =========================================================================
    # Commande: battle create <type> <filename> [options]
    # =========================================================================
    create_parser = subparsers.add_parser("create", help="Créer des fichiers de carte ou d'armée")
    create_subparsers = create_parser.add_subparsers(dest="create_type", help="Type de fichier à créer")

    # battle create map
    map_parser = create_subparsers.add_parser("map", help="Créer une carte")
    map_parser.add_argument("filename", type=str, help="Nom du fichier .map")
    map_parser.add_argument("--width", type=int, default=60, help="Largeur de la carte")
    map_parser.add_argument("--height", type=int, default=60, help="Hauteur de la carte")
    map_parser.add_argument("--noise", type=float, default=0.1, help="Niveau de bruit (0.0 - 1.0)")

    # battle create army
    army_parser = create_subparsers.add_parser("army", help="Créer une armée")
    army_parser.add_argument("filename", type=str, help="Nom du fichier armée (.txt)")
    army_parser.add_argument("--general", type=str, default="MajorDAFT", help="Nom du général")
    army_parser.add_argument("--units", type=str, default="Knight:10", help="Unités (ex: 'Knight:10,Pikeman:5')")
    army_parser.add_argument("--map_size", type=str, default="60x60", help="Taille de la carte (ex: '60x60')")
    army_parser.add_argument("--id", type=int, default=0, help="ID de l'armée (0=Haut/Gauche, 1=Bas/Droite)")

    # Parse arguments
    parsed_args = parser.parse_args(args)

    # Dispatch vers la bonne fonction
    if parsed_args.command == "play":
        run_play(parsed_args)
    elif parsed_args.command == "run":
        run_battle(parsed_args)
    elif parsed_args.command == "tourney":
        run_tourney(parsed_args)
    elif parsed_args.command == "plot":
        run_plot(parsed_args)
    elif parsed_args.command == "lanchester":
        run_lanchester(parsed_args)
    elif parsed_args.command == "create":
        run_create(parsed_args)
    elif parsed_args.command == "legacy":
        run_legacy_battle(parsed_args)
    else:
        parser.print_help()


def run_battle(args):
    """
    Exécute une bataille unique.
    Format: battle run <scenario> <AI1> <AI2> [-t] [-d DATAFILE]
    """
    print("--- MedievAIl: Bataille ---")
    print(f"Scénario: {args.scenario}")
    print(f"Général 1: {args.AI1}")
    print(f"Général 2: {args.AI2}")
    print(f"Mode: {'Terminal' if args.terminal else 'Pygame 2.5D'}")
    
    # Vérifier les généraux
    if args.AI1 not in GENERAL_CLASS_MAP:
        print(f"Erreur: Général inconnu '{args.AI1}'")
        print(f"Généraux disponibles: {list(GENERAL_CLASS_MAP.keys())}")
        sys.exit(1)
    if args.AI2 not in GENERAL_CLASS_MAP:
        print(f"Erreur: Général inconnu '{args.AI2}'")
        sys.exit(1)
    
    gen1_class = GENERAL_CLASS_MAP[args.AI1]
    gen2_class = GENERAL_CLASS_MAP[args.AI2]
    
    # Charger le scénario
    # Si c'est un fichier .map, on a besoin des armées
    if args.scenario.endswith('.map'):
        if not args.army1 or not args.army2:
            # Utiliser des armées par défaut
            print("Utilisation d'armées par défaut (10 Knights chacun)")
            game_map = load_map_from_file(args.scenario)
            army1, army2 = custom_battle_scenario(
                {"Knight": 10}, {"Knight": 10},
                gen1_class, gen2_class,
                (game_map.width, game_map.height)
            )
        else:
            game_map = load_map_from_file(args.scenario)
            army1 = load_army_from_file(args.army1, army_id=0, general_name=args.AI1)
            army2 = load_army_from_file(args.army2, army_id=1, general_name=args.AI2)
    else:
        # Scénario Python (.py) - Implémentation Req 3
        print(f"Chargement du scénario Python: {args.scenario}")
        try:
            # Chargement dynamique du module
            spec = importlib.util.spec_from_file_location("scenario_module", args.scenario)
            if spec is None or spec.loader is None:
                raise ImportError(f"Impossible de charger le fichier {args.scenario}")
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Vérifier la présence de la fonction 'create_scenario'
            if not hasattr(module, "create_scenario"):
                raise AttributeError("Le fichier .py doit contenir une fonction 'create_scenario(gen1_class, gen2_class)'.")
            
            # Exécuter la fonction
            result = module.create_scenario(gen1_class, gen2_class)
            
            # Gestion des retours (Army1, Army2) ou (Army1, Army2, Map)
            if len(result) == 3:
                army1, army2, game_map = result
            elif len(result) == 2:
                army1, army2 = result
                # Créer une map par défaut si non fournie (taille basée sur positions max ?)
                game_map = Map(120, 120) 
            else:
                 raise ValueError("create_scenario doit renvoyer (army1, army2) ou (army1, army2, map)")

            # Réassigner la map aux armées et au moteur
            # (Au cas où le scénario ne l'a pas fait explicitement)
            # Pas nécessaire car Engine prend Map + Armies
            
        except Exception as e:
            print(f"Erreur lors du chargement du scénario Python: {e}")
            sys.exit(1)
    
    engine = Engine(game_map, army1, army2)
    
    # Choix de la vue
    view = None
    if args.terminal:
        view = TerminalView(engine.map)
    else:
        view = PygameView(engine.map)
    
    try:
        engine.run_game(max_turns=args.max_turns, view=view)
    except KeyboardInterrupt:
        print("\nSimulation interrompue.")
    
    # Sauvegarde si demandé
    if args.datafile and args.datafile.endswith('.sav'):
        save_game(engine, args.datafile)


def run_tourney(args):
    """
    Exécute un tournoi automatique.
    Format: battle tourney -G <AI1> <AI2>... -S <SCEN1>... [-N=10]
    """
    print("--- MedievAIl: Tournoi ---")
    print(f"Généraux: {args.generals}")
    print(f"Scénarios: {args.scenarios}")
    print(f"Rounds: {args.rounds}")
    
    # Les armées sont gérées par le Tournament
    # Si pas d'armées spécifiées, utiliser des armées par défaut
    if args.armies is None:
        # Créer des fichiers d'armées temporaires ou utiliser des défauts
        args.armies = ["armies/armee_bleue.txt", "armies/armee_rouge.txt"]
        print(f"Armées par défaut: {args.armies}")
    
    tournament = Tournament(args.generals, args.scenarios, args.armies, args.rounds)
    tournament.run()


def run_plot(args):
    """
    Génère des graphiques de performance Lanchester.
    Format: battle plot <AI> <plotter> <scenario> <range>
    Utilise eval() pour parser le range (conforme au PDF).
    """
    print("=" * 60)
    print("📊 MedievAIl: Génération de Graphiques Lanchester")
    print("=" * 60)
    print(f"IA testée     : {args.AI}")
    print(f"Type de plot  : {args.plotter}")
    print(f"Scénario      : {args.scenario}")
    print(f"Range         : {args.range}")
    print(f"Adversaire    : {args.opponent}")
    
    # Vérifier matplotlib
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("Erreur: matplotlib n'est pas installé.")
        print("Installez-le avec: pip install matplotlib")
        sys.exit(1)
    
    # Évaluation sécurisée du range
    try:
        safe_dict = {"range": range, "__builtins__": {}}
        test_range = eval(args.range, safe_dict)
        values = list(test_range)
        print(f"Valeurs N     : {values}")
    except Exception as e:
        print(f"Erreur: Impossible de parser le range '{args.range}'")
        print(f"Exemple valide: 'range(5, 50, 5)'")
        sys.exit(1)
    
    # Vérifier les généraux
    ai_class = GENERAL_CLASS_MAP.get(args.AI)
    opponent_class = GENERAL_CLASS_MAP.get(args.opponent)
    if not ai_class or not opponent_class:
        print(f"Erreur: Général inconnu")
        print(f"Disponibles: {list(GENERAL_CLASS_MAP.keys())}")
        sys.exit(1)
    
    # Déterminer le type d'unité depuis le scénario
    unit_type = "Knight"  # Par défaut
    if "Knight" in args.scenario:
        unit_type = "Knight"
    elif "Pikeman" in args.scenario:
        unit_type = "Pikeman"
    elif "Crossbow" in args.scenario:
        unit_type = "Crossbowman"
    
    unit_class = UNIT_CLASS_MAP.get(unit_type)
    
    print(f"Unité         : {unit_type}")
    print("-" * 60)
    
    # Collecter les données
    results = {
        'N': values,
        'winner_casualties': [],  # Pertes du gagnant (armée 2N)
        'loser_casualties': [],   # Pertes du perdant (armée N) = toujours N
    }
    
    for N in values:
        print(f"  Test N={N} ({N} vs {2*N})...", end=" ", flush=True)
        
        # Créer le scénario Lanchester
        army1, army2 = lanchester_scenario(unit_class, N, ai_class)
        game_map = Map(60, 60)
        engine = Engine(game_map, army1, army2)
        
        # Exécuter sans vue (headless) -> Vitesse maximale
        engine.run_game(max_turns=2000, view=None, logic_speed=1)
        
        # Calculer les pertes
        army1_alive = sum(1 for u in army1.units if u.is_alive)
        army2_alive = sum(1 for u in army2.units if u.is_alive)
        
        # L'armée 2 (2N unités) devrait gagner
        winner_lost = (2 * N) - army2_alive
        
        results['winner_casualties'].append(winner_lost)
        results['loser_casualties'].append(N)  # Le perdant perd toutes ses unités
        
        print(f"Gagnant perd {winner_lost}/{2*N}")
    
    print("-" * 60)
    
    # Générer le graphique
    plt.figure(figsize=(10, 6))
    plt.plot(results['N'], results['winner_casualties'], 'b-o', label='Pertes du gagnant (2N)')
    plt.plot(results['N'], results['loser_casualties'], 'r--', label='Pertes du perdant (N)')
    
    plt.xlabel('Taille de la petite armée (N)')
    plt.ylabel('Nombre de pertes')
    plt.title(f"Loi de Lanchester - {unit_type} (N vs 2N)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Sauvegarder le graphique
    output_path = f"lanchester_{unit_type.lower()}.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\n✅ Graphique sauvegardé: {output_path}")
    
    # Afficher le graphique
    plt.show()


def run_lanchester(args):
    """
    Exécute un scénario de loi de Lanchester.
    Format: battle lanchester <unit_type> <N> [-t]
    """
    print("--- MedievAIl: Test de Lanchester ---")
    print(f"Unité: {args.unit_type}")
    print(f"Configuration: {args.N} vs {2 * args.N}")
    
    unit_class = UNIT_CLASS_MAP.get(args.unit_type)
    if unit_class is None:
        print(f"Erreur: Type d'unité inconnu '{args.unit_type}'")
        print(f"Unités disponibles: {list(UNIT_CLASS_MAP.keys())}")
        sys.exit(1)
    
    general_class = GENERAL_CLASS_MAP.get(args.general)
    if general_class is None:
        print(f"Erreur: Général inconnu '{args.general}'")
        sys.exit(1)
    
    # Créer le scénario Lanchester
    army1, army2 = lanchester_scenario(unit_class, args.N, general_class)
    
    # Créer une map par défaut
    game_map = Map(40, 40)
    engine = Engine(game_map, army1, army2)
    
    # Choix de la vue
    view = None
    if args.terminal:
        view = TerminalView(engine.map)
    else:
        view = PygameView(engine.map)
    
    speed = 1 if args.terminal else 2
    engine.run_game(max_turns=args.max_turns, view=view, logic_speed=speed)


def run_legacy_battle(args):
    """
    Mode legacy pour rétrocompatibilité.
    Format: battle legacy --map X --army1 Y --army2 Z
    """
    print("--- Mode Legacy ---")
    
    engine = None
    
    if args.load_game:
        engine = load_game_from_save(args.load_game)
    else:
        game_map = load_map_from_file(args.map)
        army1 = load_army_from_file(args.army1, army_id=0)
        army2 = load_army_from_file(args.army2, army_id=1)
        engine = Engine(game_map, army1, army2)
    
    view = None
    if args.view == "terminal":
        view = TerminalView(engine.map)
    elif args.view == "pygame":
        view = PygameView(engine.map)
    
    try:
        speed = 1 if args.view == "terminal" else 2
        engine.run_game(max_turns=args.max_turns, view=view, logic_speed=speed)
    except KeyboardInterrupt:
        print("\nSimulation interrompue.")
    
    if args.save_path:
        save_game(engine, args.save_path)


def run_play(args):
    """
    🎮 Commande simplifiée pour lancer une partie rapidement.
    Format: python main.py play [-t] [-u Knight] [-n 10] [-ai DAFT KAISER]
    """
    print("=" * 50)
    print("🏰 MedievAIl - Partie Rapide")
    print("=" * 50)
    print(f"Unités   : {args.count}x {args.units} par camp")
    print(f"IAs      : {args.generals[0]} vs {args.generals[1]}")
    print(f"Mode     : {'Terminal' if args.terminal else 'Pygame 2.5D'}")
    print("=" * 50)
    
    # Vérifier tous les types d'unités
    units_list = args.units if isinstance(args.units, list) else [args.units]
    for u_type in units_list:
        if u_type not in UNIT_CLASS_MAP:
            print(f"Erreur: Type d'unité inconnu '{u_type}'")
            print(f"Disponibles: {list(UNIT_CLASS_MAP.keys())}")
            sys.exit(1)
    
    # Vérifier les généraux
    gen1_class = GENERAL_CLASS_MAP.get(args.generals[0])
    gen2_class = GENERAL_CLASS_MAP.get(args.generals[1])
    if not gen1_class or not gen2_class:
        print(f"Erreur: Général inconnu")
        print(f"Disponibles: {list(GENERAL_CLASS_MAP.keys())}")
        sys.exit(1)
    
    # Créer une carte par défaut
    game_map = Map(60, 60)
    
    # Créer les armées avec les unités choisies (composition mixte)
    # Si plusieurs types, on divise le nombre total par le nombre de types
    # ou on met args.count de chaque type (plus simple pour le test)
    composition = {}
    for u_type in units_list:
        composition[u_type] = args.count  # args.count de CHAQUE type
        
    army1, army2 = custom_battle_scenario(
        composition, composition,
        gen1_class, gen2_class,
        (game_map.width, game_map.height)
    )
    
    engine = Engine(game_map, army1, army2)
    
    # Choisir la vue
    if args.terminal:
        view = TerminalView(engine.map)
    else:
        view = PygameView(engine.map)
    
    try:
        speed = 1 if args.terminal else 2
        engine.run_game(max_turns=args.max_turns, view=view, logic_speed=speed)
    except KeyboardInterrupt:
        print("\nPartie interrompue.")


def run_create(args):
    """
    Gère la commande 'battle create'.
    """
    if args.create_type == "map":
        generate_map_file(args.filename, args.width, args.height, args.noise)
    
    elif args.create_type == "army":
        # Parse map size "WxH"
        try:
            w, h = map(int, args.map_size.lower().split('x'))
        except ValueError:
            print("Erreur: Format map_size incorrect (utiliser '60x60')")
            sys.exit(1)
            
        # Parse units "Type:Count,Type:Count"
        units_config = {}
        try:
            parts = args.units.split(',')
            for p in parts:
                u_type, count = p.split(':')
                units_config[u_type.strip()] = int(count)
        except ValueError:
             print("Erreur: Format units incorrect (utiliser 'Knight:10,Pikeman:5')")
             sys.exit(1)
             
        # Verify general
        if args.general not in GENERAL_CLASS_MAP:
             print(f"Erreur: Général '{args.general}' inconnu. Disponibles: {list(GENERAL_CLASS_MAP.keys())}")
             sys.exit(1)
             
        generate_army_file(args.filename, args.general, units_config, (w, h), args.id)
    
    else:
        print("Spécifiez 'map' ou 'army'.")


if __name__ == "__main__":
    main()