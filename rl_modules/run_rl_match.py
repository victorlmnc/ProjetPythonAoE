import sys
import os
import pickle
import pygame
import time

# Thêm đường dẫn root
sys.path.append(os.getcwd())

from engine import Engine
from core.army import Army
from extensions.map_builder import create_battle_map, generate_army_composition
from extensions.custom_view import CustomPygameView
from rl_modules.commander import RLCommander
from extensions.custom_units import GameCastle

MODEL_DIR = "ai/rl/models"
REPORT_DIR = "reports"


def load_trained_model(team_id):
    """Hàm hỗ trợ load Q-Table từ file .pkl"""
    filename = f"{MODEL_DIR}/q_table_team{team_id}_final.pkl"
    if os.path.exists(filename):
        try:
            with open(filename, 'rb') as f:
                print(f">>> [LOAD] Đang nạp model cho Team {team_id} từ {filename}...")
                return pickle.load(f)
        except Exception as e:
            print(f">>> [LỖI] Không đọc được file model: {e}")
    return {}


# --- CUSTOM ENGINE: GHI ĐÈ LUẬT THẮNG ---
class RegicideEngine(Engine):
    def _check_game_over(self) -> bool:
        # Kiểm tra Castle
        castle_0_alive = any(isinstance(u, GameCastle) and u.is_alive for u in self.armies[0].units)
        castle_1_alive = any(isinstance(u, GameCastle) and u.is_alive for u in self.armies[1].units)

        # Kiểm tra Lính
        any_0_alive = any(u.is_alive for u in self.armies[0].units)
        any_1_alive = any(u.is_alive for u in self.armies[1].units)

        if not castle_0_alive:
            self.winner = 1
            self.game_over = True
            print(">>> Team 1 mất Castle! Team 2 thắng!")
            return True

        if not castle_1_alive:
            self.winner = 0
            self.game_over = True
            print(">>> Team 2 mất Castle! Team 1 thắng!")
            return True

        if not any_0_alive:
            self.winner = 1
            self.game_over = True
            print(">>> Team 1 bị tiêu diệt hoàn toàn! Team 2 thắng!")
            return True

        if not any_1_alive:
            self.winner = 0
            self.game_over = True
            print(">>> Team 2 bị tiêu diệt hoàn toàn! Team 1 thắng!")
            return True

        return False


# [HÀM MỚI] Đếm số lượng quân ban đầu
def get_initial_composition(army_units):
    """
    Hàm đếm số lượng quân ban đầu trước khi trận đấu diễn ra.
    Trả về dict: {'UnitName': count}
    """
    comp = {}
    for u in army_units:
        u_type = type(u).__name__
        comp[u_type] = comp.get(u_type, 0) + 1
    return comp


# [HÀM MỚI] Đếm số lượng quân còn sống
def count_current_survivors(army_units):
    """
    Hàm đếm số lượng quân còn sống tại thời điểm gọi.
    Trả về dict: {'UnitName': count_alive}
    """
    alive = {}
    for u in army_units:
        if u.is_alive:
            u_type = type(u).__name__
            alive[u_type] = alive.get(u_type, 0) + 1
    return alive


def generate_unit_rows_html(initial_comp, survivor_comp):
    """
    Sinh HTML dựa trên so sánh giữa ban đầu và hiện tại.
    """
    html_rows = ""
    # Sắp xếp theo tên unit
    sorted_keys = sorted(initial_comp.keys())

    for u_type in sorted_keys:
        total = initial_comp[u_type]
        alive = survivor_comp.get(u_type, 0)
        dead = total - alive
        if dead < 0: dead = 0  # Đề phòng lỗi logic

        html_rows += f"""
        <tr>
            <td class="sub-label">{u_type}</td>
            <td style="font-weight:bold; color:#555;">{total}</td>
            <td class="val-alive">{alive}</td>
            <td class="val-dead">{dead}</td>
        </tr>
        """
    return html_rows


def generate_battle_report(engine, winner, init_s1, init_s2, army1, army2):
    if not os.path.exists(REPORT_DIR):
        os.makedirs(REPORT_DIR)

    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"{REPORT_DIR}/match_report_{timestamp}.html"

    # Xác định người thắng
    winner_text = "DRAW"
    winner_bg = "#95a5a6"  # Gray
    if winner == 0:
        winner_text = "TEAM 1 (BLUE) WINS"
        winner_bg = "#3498db"  # Blue
    elif winner == 1:
        winner_text = "TEAM 2 (RED) WINS"
        winner_bg = "#e74c3c"  # Red

    # Đếm số quân còn sống hiện tại
    current_s1 = count_current_survivors(army1.units)
    current_s2 = count_current_survivors(army2.units)

    # Tạo các dòng HTML
    rows_team1 = generate_unit_rows_html(init_s1, current_s1)
    rows_team2 = generate_unit_rows_html(init_s2, current_s2)

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Battle Report</title>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; background-color: #f4f6f8; color: #333; margin: 0; padding: 20px; }}
            .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .header {{ text-align: center; margin-bottom: 30px; border-bottom: 2px solid #eee; padding-bottom: 20px; }}
            .header h1 {{ margin: 0; color: #2c3e50; font-size: 32px; }}
            .header .meta {{ color: #7f8c8d; font-size: 14px; margin-top: 5px; }}
            .winner-banner {{ 
                background-color: {winner_bg}; color: white; 
                text-align: center; padding: 15px; font-size: 24px; font-weight: bold; 
                border-radius: 6px; margin-bottom: 30px; 
            }}
            .stats-container {{ display: flex; gap: 30px; }}
            .team-card {{ flex: 1; border: 1px solid #e1e4e8; border-radius: 8px; overflow: hidden; }}
            .team-header {{ padding: 15px; text-align: center; font-weight: bold; font-size: 18px; color: white; }}
            .team-blue {{ background-color: #3498db; }}
            .team-red {{ background-color: #e74c3c; }}
            .stat-table {{ width: 100%; border-collapse: collapse; }}
            .stat-table th, .stat-table td {{ padding: 10px 15px; border-bottom: 1px solid #eee; text-align: center; }}
            .stat-table th {{ background-color: #f8f9fa; font-size: 12px; text-transform: uppercase; color: #555; }}
            .sub-label {{ text-align: left !important; padding-left: 20px !important; font-weight: 500; color: #444; }}
            .val-alive {{ color: #27ae60; font-weight: bold; }}
            .val-dead {{ color: #c0392b; }}
            .footer {{ text-align: center; margin-top: 40px; font-size: 12px; color: #999; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Battle Report</h1>
                <div class="meta">Match ID: {timestamp} &bull; Duration: {engine.turn_count} Turns</div>
            </div>

            <div class="winner-banner">
                {winner_text}
            </div>

            <div class="stats-container">
                <div class="team-card">
                    <div class="team-header team-blue">Team 1 (Blue)</div>
                    <table class="stat-table">
                        <tr><th>Unit Type</th><th>Total</th><th>Alive</th><th>Dead</th></tr>
                        {rows_team1}
                    </table>
                </div>

                <div class="team-card">
                    <div class="team-header team-red">Team 2 (Red)</div>
                    <table class="stat-table">
                        <tr><th>Unit Type</th><th>Total</th><th>Alive</th><th>Dead</th></tr>
                        {rows_team2}
                    </table>
                </div>
            </div>

            <div class="footer">
                Battle Simulator Report
            </div>
        </div>
    </body>
    </html>
    """
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"\n>>> 📝 Report chi tiết đã lưu: {filename}")


# --- HÀM CHÍNH ---
def run_gui_match(map_size=120, units_per_team=50, max_turns=2000):
    print(f"\n>>> KHỞI TẠO TRẬN ĐẤU DEMO (Match Mode)")
    print(
        f"    Map: {map_size}x{map_size} | Units: {units_per_team} | Max Turns: {max_turns if max_turns != -1 else 'INFINITE'}")

    # 1. Init Map
    game_map, tree_units = create_battle_map(width=map_size, height=map_size)

    # 2. Setup AI (Load Model)
    ai_1 = RLCommander(army_id=0, role_config="team1", learning=False)
    ai_1.q_table = load_trained_model(1)

    ai_2 = RLCommander(army_id=1, role_config="team2", learning=False)
    ai_2.q_table = load_trained_model(2)

    # 3. Spawn Armies
    margin = 15
    spawn_1 = (margin, margin)
    spawn_2 = (map_size - margin, map_size - margin)

    units_1 = generate_army_composition(0, spawn_1[0], spawn_1[1], units_per_team)
    army_1 = Army(0, units_1, ai_1)

    units_2 = generate_army_composition(1, spawn_2[0], spawn_2[1], units_per_team)
    army_2 = Army(1, units_2, ai_2)

    # --- [GHI NHẬN SỐ LƯỢNG QUÂN BAN ĐẦU] ---
    init_stats_1 = get_initial_composition(units_1)
    init_stats_2 = get_initial_composition(units_2)
    print(f">>> Initial Stats T1: {init_stats_1}")
    print(f">>> Initial Stats T2: {init_stats_2}")

    # 4. Engine & View
    engine = RegicideEngine(game_map, army_1, army_2)
    view = CustomPygameView(game_map, engine.armies)
    view.set_nature_units(tree_units)

    # 5. Xử lý max_turns
    if max_turns == -1:
        run_turns = sys.maxsize
    else:
        run_turns = max_turns

    print("\n>>> BẮT ĐẦU TRẬN ĐẤU...")
    print(">>> Phím SPACE: Pause | S: Step | +/-: Speed")

    try:
        engine.run_game(max_turns=run_turns, view=view, logic_speed=2)
    except KeyboardInterrupt:
        print("\n>>> Dừng trận đấu.")

    # 6. Báo cáo (Truyền thống kê ban đầu vào)
    generate_battle_report(engine, engine.winner, init_stats_1, init_stats_2, army_1, army_2)


if __name__ == "__main__":
    run_gui_match()