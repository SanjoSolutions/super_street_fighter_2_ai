from enum import IntEnum
from moves_database import moves


# See RyuDiscretizer.py
class Actions(IntEnum):
    IDLE = 0
    LEFT = 1
    RIGHT = 2
    DOWN = 3
    LEFT_DOWN = 5
    RIGHT_DOWN = 6
    LEFT_HEAVY_PUNCH = 23
    RIGHT_HEAVY_PUNCH = 24
    LEFT_DOWN_HEAVY_PUNCH = 33
    RIGHT_DOWN_HEAVY_PUNCH = 34


class Player:
    def __init__(self, player_index):
        self.player_index = player_index
        self.buffered_actions = []

    def choose_action(self, info):
        if len(self.buffered_actions) >= 1:
            action = self.buffered_actions.pop(0)
        else:
            if info['active_p1'] == 0:
                if should_air_defend(info):
                    action = self.air_defend(info)
                elif should_throw(info):
                    action = self.throw(info)
                elif should_block_standing(info):
                    action = self.standing_block(info)
                elif should_crouch_block(info):
                    action = self.crouch_block(info)
                elif should_hadouken(info):
                    action = self.hadouken(info)
                else:
                    action = self.crouch_block(info)
            else:
                action = self.crouch_block(info)

        return action

    def air_defend(self, info):
        if is_character_on_left(info):
            actions = [
                Actions.RIGHT,
                Actions.DOWN,
                Actions.RIGHT_DOWN_HEAVY_PUNCH
            ]
        else:
            actions = [
                Actions.LEFT,
                Actions.DOWN,
                Actions.LEFT_DOWN_HEAVY_PUNCH
            ]
        action = actions.pop(0)
        self.buffered_actions.extend(actions)
        return action

    def throw(self, info):
        if is_character_on_left(info):
            action = Actions.RIGHT_HEAVY_PUNCH
        else:
            action = Actions.LEFT_HEAVY_PUNCH
        return action

    def standing_block(self, info):
        if is_character_on_left(info):
            action = Actions.LEFT
        else:
            action = Actions.RIGHT
        return action

    def crouch_block(self, info):
        if is_character_on_left(info):
            action = Actions.LEFT_DOWN
        else:
            action = Actions.RIGHT_DOWN
        return action

    def hadouken(self, info):
        if is_character_on_left(info):
            actions = [
                Actions.DOWN,
                Actions.RIGHT_DOWN,
                Actions.RIGHT_HEAVY_PUNCH
            ]
        else:
            actions = [
                Actions.DOWN,
                Actions.LEFT_DOWN,
                Actions.LEFT_HEAVY_PUNCH
            ]
        action = actions.pop(0)
        self.buffered_actions.extend(actions)
        return action


def is_character_on_left(info):
    return info['x_p1'] <= info['x_p2']


Y_ON_GROUND = 192


def should_air_defend(info):
    return (
        x_distance(info) <= 32 and
        info['y_p2'] < Y_ON_GROUND and
        is_opponent_jumping(info['sprite_id_next_frame_p2'])
    )


def should_throw(info):
    return is_opponent_in_throw_range(info) and is_opponent_inactive(info)


def is_opponent_in_throw_range(info):
    return 18 < x_distance(info) <= 33 and info['y_p2'] == Y_ON_GROUND


def is_opponent_inactive(info):
    return info['active_p2'] == 0


def should_block_standing(info):
    opponent_sprite_id = info['sprite_id_next_frame_p2']
    return (
        (is_opponent_jumping(opponent_sprite_id) or is_opponent_upper_cutting()) and
        is_opponent_close_by(info)
    )


def should_crouch_block(info):
    return is_opponent_close_by(info)


def should_hadouken(info):
    return (
        info['projectile_active_p1_1'] == 0 and
        x_distance(info) > 145 and
        (
            info['projectile_active_p2_1'] == 0 or
            distance(info['x_projectile_p2'], info['x_p1']) > 104
        )
    )


def determine_jump_sprite_ids(moves):
    jump_sprite_ids = set()
    for character_name, character_moves in moves.items():
        for character_move_name, move_frames in character_moves.items():
            if 'jump' in character_move_name:
                sprite_ids = set(sprite_id for sprite_id, _ in move_frames)
                jump_sprite_ids |= sprite_ids
    return jump_sprite_ids


jump_sprite_ids = determine_jump_sprite_ids(moves)


def is_opponent_jumping(opponent_sprite_id):
    return opponent_sprite_id in jump_sprite_ids


def is_opponent_upper_cutting():
    # Ken seems to have no upper cut
    return False


def is_opponent_close_by(info):
    return x_distance(info) <= 71


def x_distance(info):
    return distance(info['x_p1'], info['x_p2'])


def distance(a, b):
    return abs(b - a)
