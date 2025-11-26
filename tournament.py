# tournament.py
import itertools
from collections import defaultdict
from utils.loaders import load_map_from_file, load_army_from_file
from engine import Engine

class Tournament:
    """
    Runs a round-robin tournament between a set of generals on a set of maps.
    """
    def __init__(self, general_names: list[str], map_paths: list[str], army_paths: list[str], rounds: int = 1):
        self.general_names = general_names
        self.map_paths = map_paths
        self.army_paths = army_paths
        self.rounds = rounds
        self.results = defaultdict(lambda: defaultdict(int))

    def run(self):
        """
        Runs the tournament and prints the results.
        """
        army_pairs = list(itertools.combinations(self.army_paths, 2))
        if not army_pairs:
            army_pairs = [(self.army_paths[0], self.army_paths[0])]

        for map_path in self.map_paths:
            print(f"--- Map: {map_path} ---")
            for army_path1, army_path2 in army_pairs:
                for general1_name, general2_name in itertools.permutations(self.general_names, 2):
                    for i in range(self.rounds):
                        print(f"Round {i+1}: {general1_name} vs {general2_name} on {map_path}")

                        # Load map and armies
                        game_map = load_map_from_file(map_path)
                        army1 = load_army_from_file(army_path1, 0, general1_name)
                        army2 = load_army_from_file(army_path2, 1, general2_name)

                        # Run the game
                        engine = Engine(game_map, army1, army2)
                        engine.run_game(max_turns=500, view=None)

                        # Record the winner
                        if engine.winner is not None:
                            if engine.winner == 0:
                                self.results[general1_name][general2_name] += 1
                            else:
                                self.results[general2_name][general1_name] += 1
                        else:
                            self.results[general1_name]["draw"] += 1
                            self.results[general2_name]["draw"] += 1
        self.print_results()

    def print_results(self):
        """
        Prints the tournament results in a markdown table.
        """
        print("\n--- Tournament Results ---")

        # Header
        header = "| General |"
        for general_name in self.general_names:
            header += f" {general_name} |"
        header += " Draws | Total Wins |"
        print(header)

        # Separator
        separator = "|---|"
        for _ in self.general_names:
            separator += "---|"
        separator += "---|"
        print(separator)

        # Body
        for general1_name in self.general_names:
            row = f"| {general1_name} |"
            total_wins = 0
            for general2_name in self.general_names:
                wins = self.results[general1_name][general2_name]
                total_wins += wins
                row += f" {wins} |"

            draws = self.results[general1_name]["draw"]
            row += f" {draws} | {total_wins} |"
            print(row)
