# tournament.py
import itertools
from collections import defaultdict
import os
from utils.loaders import load_map_from_file, load_army_from_file
from engine import Engine

class Tournament:
    """
    Runs a round-robin tournament between a set of generals on a set of maps.
    Generates an HTML report of the results.
    """
    def __init__(self, general_names: list[str], map_paths: list[str], army_paths: list[str], rounds: int = 1):
        self.general_names = general_names
        self.map_paths = map_paths
        self.army_paths = army_paths
        self.rounds = rounds
        # Store match history: {"map": str, "p1": str, "p2": str, "winner": str|None}
        self.match_history = []

    def run(self):
        """
        Runs the tournament and prints the results.
        """
        army_pairs = list(itertools.combinations(self.army_paths, 2))
        if not army_pairs:
            # If only one army path provided, use it against itself (mirror match capable)
            army_pairs = [(self.army_paths[0], self.army_paths[0])]

        for map_path in self.map_paths:
            print(f"--- Map: {map_path} ---")
            for army_path1, army_path2 in army_pairs:
                # We use product to get all permutations including reflexive (A vs A, A vs B, B vs A, B vs B)
                for general1_name, general2_name in itertools.product(self.general_names, repeat=2):
                    for i in range(self.rounds):
                        print(f"Round {i+1}: {general1_name} vs {general2_name} on {map_path}")

                        # Load map and armies
                        game_map = load_map_from_file(map_path)
                        # We force army_id 0 and 1
                        army1 = load_army_from_file(army_path1, 0, general1_name)
                        army2 = load_army_from_file(army_path2, 1, general2_name)

                        # Run the game
                        engine = Engine(game_map, army1, army2)
                        # Run fast (no view), max turns limited to avoid infinite games
                        engine.run_game(max_turns=500, view=None)

                        # Record the winner
                        winner_name = None
                        if engine.winner is not None:
                            if engine.winner == 0:
                                winner_name = general1_name
                            else:
                                winner_name = general2_name

                        self.match_history.append({
                            "map": map_path,
                            "p1": general1_name,
                            "p2": general2_name,
                            "winner": winner_name # None = Draw
                        })

        self.generate_report()
        self.print_console_summary()

    def print_console_summary(self):
        """Prints a brief summary to console."""
        print("\n--- Tournament Completed ---")
        wins = defaultdict(int)
        total = defaultdict(int)
        for m in self.match_history:
            total[m["p1"]] += 1
            total[m["p2"]] += 1
            if m["winner"]:
                wins[m["winner"]] += 1

        print("Global Win Rates:")
        for g in self.general_names:
            t = total[g]
            w = wins[g]
            if t > 0:
                print(f"{g}: {w}/{t} ({w/t*100:.1f}%)")
            else:
                 print(f"{g}: 0/0 (0%)")

    def generate_report(self, filename="tournament_report.html"):
        """Generates the HTML report."""
        html = ["<html><head><title>Tournament Report</title>",
                "<style>table {border-collapse: collapse; width: 100%; font-family: sans-serif;} th, td {border: 1px solid black; padding: 8px; text-align: center;} th {background-color: #f2f2f2;} h2 {margin-top: 30px;}</style>",
                "</head><body><h1>Tournament Results</h1>"]

        # 1. Global Score
        html.append("<h2>1. Global Score (Win % across all games)</h2>")
        html.append("<table><tr><th>General</th><th>Wins</th><th>Draws</th><th>Losses</th><th>Total Games</th><th>Win Rate</th></tr>")

        global_stats = {g: {'w':0, 'd':0, 'l':0, 't':0} for g in self.general_names}

        for m in self.match_history:
            p1, p2, w = m['p1'], m['p2'], m['winner']

            # P1 stats
            global_stats[p1]['t'] += 1
            if w == p1: global_stats[p1]['w'] += 1
            elif w is None: global_stats[p1]['d'] += 1
            else: global_stats[p1]['l'] += 1

            # P2 stats
            global_stats[p2]['t'] += 1
            if w == p2: global_stats[p2]['w'] += 1
            elif w is None: global_stats[p2]['d'] += 1
            else: global_stats[p2]['l'] += 1

        for g in self.general_names:
            s = global_stats[g]
            rate = (s['w'] / s['t'] * 100) if s['t'] > 0 else 0
            html.append(f"<tr><td>{g}</td><td>{s['w']}</td><td>{s['d']}</td><td>{s['l']}</td><td>{s['t']}</td><td>{rate:.1f}%</td></tr>")
        html.append("</table>")

        # 2. General vs General (Global)
        html.append("<h2>2. General vs General (Win Rates)</h2>")
        html.append("<table><tr><th>vs</th>")
        for g in self.general_names: html.append(f"<th>{g}</th>")
        html.append("</tr>")

        matrix_data = defaultdict(lambda: defaultdict(lambda: {'w':0, 't':0}))

        for m in self.match_history:
            p1, p2, w = m['p1'], m['p2'], m['winner']
            # A vs B
            matrix_data[p1][p2]['t'] += 1
            if w == p1: matrix_data[p1][p2]['w'] += 1
            # B vs A (symmetric)
            matrix_data[p2][p1]['t'] += 1
            if w == p2: matrix_data[p2][p1]['w'] += 1

        for g1 in self.general_names:
            html.append(f"<tr><th>{g1}</th>")
            for g2 in self.general_names:
                stats = matrix_data[g1][g2]
                if stats['t'] > 0:
                    wr = stats['w'] / stats['t'] * 100
                    cell = f"{stats['w']}/{stats['t']}<br>({wr:.0f}%)"
                else:
                    cell = "-"
                html.append(f"<td>{cell}</td>")
            html.append("</tr>")
        html.append("</table>")

        # 3. Per Scenario (Gen vs Gen)
        html.append("<h2>3. Per Scenario (Detailed Matchups)</h2>")
        unique_maps = sorted(list(set(m['map'] for m in self.match_history)))

        for map_name in unique_maps:
            short_map_name = os.path.basename(map_name)
            html.append(f"<h3>Map: {short_map_name}</h3>")
            html.append("<table><tr><th>vs</th>")
            for g in self.general_names: html.append(f"<th>{g}</th>")
            html.append("</tr>")

            map_matches = [m for m in self.match_history if m['map'] == map_name]
            map_matrix = defaultdict(lambda: defaultdict(lambda: {'w':0, 't':0}))

            for m in map_matches:
                p1, p2, w = m['p1'], m['p2'], m['winner']
                map_matrix[p1][p2]['t'] += 1
                if w == p1: map_matrix[p1][p2]['w'] += 1
                map_matrix[p2][p1]['t'] += 1
                if w == p2: map_matrix[p2][p1]['w'] += 1

            for g1 in self.general_names:
                html.append(f"<tr><th>{g1}</th>")
                for g2 in self.general_names:
                    stats = map_matrix[g1][g2]
                    if stats['t'] > 0:
                        wr = stats['w'] / stats['t'] * 100
                        cell = f"{stats['w']}/{stats['t']} ({wr:.0f}%)"
                    else:
                        cell = "-"
                    html.append(f"<td>{cell}</td>")
                html.append("</tr>")
            html.append("</table>")

        # 4. General vs Scenario
        html.append("<h2>4. General vs Scenario (Win Rate per Map)</h2>")
        html.append("<table><tr><th>General</th>")
        for map_name in unique_maps: html.append(f"<th>{os.path.basename(map_name)}</th>")
        html.append("</tr>")

        gen_map_stats = defaultdict(lambda: defaultdict(lambda: {'w':0, 't':0}))
        for m in self.match_history:
            p1, p2, w = m['p1'], m['p2'], m['winner']
            mp = m['map']
            gen_map_stats[p1][mp]['t'] += 1
            if w == p1: gen_map_stats[p1][mp]['w'] += 1
            gen_map_stats[p2][mp]['t'] += 1
            if w == p2: gen_map_stats[p2][mp]['w'] += 1

        for g in self.general_names:
            html.append(f"<tr><th>{g}</th>")
            for map_name in unique_maps:
                stats = gen_map_stats[g][map_name]
                if stats['t'] > 0:
                     wr = stats['w'] / stats['t'] * 100
                     cell = f"{wr:.1f}%"
                else:
                    cell = "-"
                html.append(f"<td>{cell}</td>")
            html.append("</tr>")
        html.append("</table>")

        html.append("</body></html>")

        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write("\n".join(html))
            print(f"Report generated: {os.path.abspath(filename)}")
        except Exception as e:
            print(f"Error generating report: {e}")
