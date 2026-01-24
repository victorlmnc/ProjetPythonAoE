import random
import math
from ai.general import General
from core.unit import Unit, UC_BUILDING
# Import đúng kiến trúc cũ
from extensions.custom_units import GameCastle, House

# Các chiến thuật cấp cao
STRATEGY_ATTACK_BASE = 0  # Ưu tiên phá công trình (Castle > House)
STRATEGY_HUNT_UNITS = 1  # Săn quân địch
STRATEGY_MIXED = 2  # Hỗn hợp


class RLCommander(General):
    def __init__(self, army_id: int, role_config: str = "team1", learning=True):
        super().__init__(army_id)
        self.role_config = role_config

        # State: (Tỉ lệ máu, Castle Status, House Status)
        self.q_table = {}
        self.learning_rate = 0.1
        self.discount_factor = 0.95
        self.epsilon = 0.3 if learning else 0.0

        self.last_state = None
        self.last_action = None
        self.previous_score = 0

    def calculate_weighted_score(self, my_units, enemy_units):
        """
        Tính điểm thưởng step-by-step:
        - GameCastle: 50 điểm (Rất quan trọng)
        - House: 10 điểm (Quan trọng)
        - Lính: 1 điểm
        """
        score = 0
        for u in my_units:
            score += u.current_hp

        for u in enemy_units:
            if isinstance(u, GameCastle):
                score -= u.current_hp * 50
            elif isinstance(u, House):
                score -= u.current_hp * 10
            else:
                score -= u.current_hp
        return score

    def _get_state_key(self, my_units, enemy_units):
        my_hp = sum(u.current_hp for u in my_units)
        en_hp = sum(u.current_hp for u in enemy_units)

        # 1. Tỷ lệ lực lượng
        ratio = my_hp / (en_hp + 1)
        if ratio > 1.2:
            r_state = 2
        elif ratio < 0.8:
            r_state = 0
        else:
            r_state = 1

        # 2. Check trạng thái công trình
        castle_alive = 0
        house_alive = 0

        for u in enemy_units:
            if isinstance(u, GameCastle):
                castle_alive = 1
            if isinstance(u, House):
                house_alive = 1
            if castle_alive and house_alive: break

        return (r_state, castle_alive, house_alive)

    def learn_terminal_result(self, final_reward):
        if self.last_state is not None and self.last_action is not None:
            old_q = self.q_table.get(self.last_state, [0.0] * 3)[self.last_action]
            new_q = old_q + self.learning_rate * (final_reward - old_q)
            if self.last_state not in self.q_table: self.q_table[self.last_state] = [0.0] * 3
            self.q_table[self.last_state][self.last_action] = new_q

    def decide_actions(self, current_map, my_units, enemy_units):
        actions = []
        state_key = self._get_state_key(my_units, enemy_units)

        # Tính Reward
        current_score = self.calculate_weighted_score(my_units, enemy_units)
        reward = (current_score - self.previous_score) - 1  # Phạt thời gian
        self.previous_score = current_score

        # Q-Learning Update
        if self.last_state is not None and self.last_action is not None:
            old_q = self.q_table.get(self.last_state, [0.0] * 3)[self.last_action]
            max_future_q = max(self.q_table.get(state_key, [0.0] * 3))
            new_q = old_q + self.learning_rate * (reward + self.discount_factor * max_future_q - old_q)

            if self.last_state not in self.q_table: self.q_table[self.last_state] = [0.0] * 3
            self.q_table[self.last_state][self.last_action] = new_q

        # Chọn Action
        if random.random() < self.epsilon:
            strategy = random.randint(0, 2)
        else:
            qs = self.q_table.get(state_key, [0.0] * 3)
            strategy = qs.index(max(qs))

        self.last_state = state_key
        self.last_action = strategy

        # --- TÌM MỤC TIÊU ---
        target_castle = None
        target_house = None

        for u in enemy_units:
            if isinstance(u, GameCastle):
                target_castle = u
                break
            elif isinstance(u, House) and target_house is None:
                target_house = u

        # Ưu tiên: Castle > House
        target_building = target_castle if target_castle else target_house

        # Danh sách lính địch (không phải nhà)
        enemy_troops = [u for u in enemy_units if UC_BUILDING not in u.armor_classes]

        # --- THỰC HIỆN ---
        for unit in my_units:
            if not unit.is_alive or UC_BUILDING in unit.armor_classes: continue

            unit_type = unit.__class__.__name__
            target = None

            # Chiến thuật 0: Phá nhà
            if strategy == STRATEGY_ATTACK_BASE:
                target = target_building
                if not target: target = self.find_closest_enemy(unit, enemy_troops)

            # Chiến thuật 1: Săn lính
            elif strategy == STRATEGY_HUNT_UNITS:
                target = self.find_closest_enemy(unit, enemy_troops)
                if not target: target = target_building

            # Chiến thuật 2: Hỗn hợp
            elif strategy == STRATEGY_MIXED:
                if self.role_config == "team1":
                    if unit_type in ["Crossbowman", "Pikeman"]:
                        target = target_building
                    else:
                        target = self.find_closest_enemy(unit, enemy_troops)
                else:
                    if unit_type in ["Crossbowman", "Knight"]:
                        target = target_building
                    else:
                        target = self.find_closest_enemy(unit, enemy_troops)

                if not target: target = target_building if target_building else self.find_closest_enemy(unit,
                                                                                                        enemy_troops)

            # Tạo lệnh di chuyển/tấn công
            if target:
                dist = unit._calculate_distance(target)
                if dist > unit.attack_range + 0.5:
                    # Di chuyển phân tán nhẹ
                    rx = random.uniform(-1.0, 1.0)
                    ry = random.uniform(-1.0, 1.0)
                    move_pos = (target.pos[0] + rx, target.pos[1] + ry)
                    actions.append(("move", unit.unit_id, move_pos))
                else:
                    actions.append(("attack", unit.unit_id, target.unit_id))

            # Hit & Run cho Cung thủ
            if unit_type == "Crossbowman":
                closest = self.find_closest_enemy(unit, enemy_troops)
                if closest and unit._calculate_distance(closest) < 2.5:
                    dx = unit.pos[0] - closest.pos[0]
                    dy = unit.pos[1] - closest.pos[1]
                    mag = math.sqrt(dx * dx + dy * dy)
                    if mag > 0:
                        run_pos = (unit.pos[0] + dx / mag * 3, unit.pos[1] + dy / mag * 3)
                        actions.append(("move", unit.unit_id, run_pos))

        return actions