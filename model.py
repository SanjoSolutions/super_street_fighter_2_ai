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


Y_ON_GROUND = 192


class Player:
    def __init__(self, player_index):
        self.player_index = player_index
        self.queued_actions = []

    def choose_action(self, info):
        if len(self.queued_actions) >= 1:
            action = self.dequeue_action()
        else:
            action = self._choose_action(info)

        return action

    def _choose_action(self, info):
        if self.can_do_move(info):
            if self.should_air_defend(info):
                action = self.air_defend(info)
            elif self.should_throw(info):
                action = self.throw(info)
            elif self.should_block_standing(info):
                action = self.standing_block(info)
            elif self.should_crouch_block(info):
                action = self.crouch_block(info)
            elif self.should_hadouken(info):
                action = self.hadouken(info)
            else:
                action = self.crouch_block(info)
        else:
            action = self.crouch_block(info)
        return action

    def can_do_move(self, info):
        return (
            info[self.suffix_player_name('active')] == 0 and
            info[self.suffix_player_name('disabled_time_left')] == 0
        )

    def queue_actions(self, actions):
        self.queued_actions.extend(actions)

    def dequeue_action(self):
        return self.queued_actions.pop(0)

    def is_character_on_left(self, info):
        return info[self.suffix_player_name('x')] <= info[self.suffix_other_player_name('x')]

    def should_air_defend(self, info):
        return (
                self.x_distance(info) <= 32 and
                info[self.suffix_other_player_name('y')] < Y_ON_GROUND and
                is_opponent_jumping(info[self.suffix_other_player_name('sprite_id_next_frame')])
        )

    def should_throw(self, info):
        return self.is_opponent_in_throw_range(info) and self.is_opponent_inactive(info)

    def is_opponent_in_throw_range(self, info):
        return 18 < self.x_distance(info) <= 33 and info[self.suffix_other_player_name('y')] == Y_ON_GROUND

    def is_opponent_inactive(self, info):
        return info[self.suffix_other_player_name('active')] == 0

    def should_block_standing(self, info):
        opponent_sprite_id = info[self.suffix_other_player_name('sprite_id_next_frame')]
        return (
                (is_opponent_jumping(opponent_sprite_id) or is_opponent_upper_cutting()) and
                self.is_opponent_close_by(info)
        )

    def should_crouch_block(self, info):
        return self.is_opponent_close_by(info)

    def should_hadouken(self, info):
        return (
            self.can_hadouken(info) and
            self.x_distance(info) > 145 and
            (
                    info[self.suffix_other_player_name('projectile_active') + '_1'] == 0 or
                    distance(
                        info[self.suffix_other_player_name('x_projectile')],
                        info[self.suffix_player_name('x')]
                    ) > 104
            )
        )

    def can_hadouken(self, info):
        return (
            info[self.suffix_player_name('projectile_active') + '_1'] == 0 and
            info[self.suffix_player_name('hit')] == 0
        )

    def is_opponent_close_by(self, info):
        return self.x_distance(info) <= 71

    def x_distance(self, info):
        return distance(info[self.suffix_player_name('x')], info[self.suffix_other_player_name('x')])

    def air_defend(self, info):
        if self.is_character_on_left(info):
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
        self.queue_actions(actions)
        action = self.dequeue_action()
        return action

    def throw(self, info):
        if self.is_character_on_left(info):
            action = Actions.RIGHT_HEAVY_PUNCH
        else:
            action = Actions.LEFT_HEAVY_PUNCH
        return action

    def standing_block(self, info):
        if self.is_character_on_left(info):
            action = Actions.LEFT
        else:
            action = Actions.RIGHT
        return action

    def crouch_block(self, info):
        if self.is_character_on_left(info):
            action = Actions.LEFT_DOWN
        else:
            action = Actions.RIGHT_DOWN
        return action

    def hadouken(self, info):
        if self.is_character_on_left(info):
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
        self.queue_actions(actions)
        action = self.dequeue_action()
        return action

    def suffix_player_name(self, string):
        return suffix_player_name(string, generate_player_name(self.player_index))

    def suffix_other_player_name(self, string):
        return suffix_player_name(string, generate_player_name(self.determine_other_player_index()))

    def determine_other_player_index(self):
        return (self.player_index + 1) % 2


def suffix_player_name(string, player_name):
    return string + '_' + player_name


def generate_player_name(player_index):
    return 'p' + str(player_index + 1)


class PlayerHadouken(Player):
    def _choose_action(self, info):
        if self.can_do_move(info):
            if self.can_hadouken(info):
                action = self.hadouken(info)
            else:
                action = Actions.IDLE
        else:
            action = Actions.IDLE
        return action


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


def distance(a, b):
    return abs(b - a)
