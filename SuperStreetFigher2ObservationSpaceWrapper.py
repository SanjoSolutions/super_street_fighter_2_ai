import os

import gym
from gym import Wrapper
import numpy as np
import math

projectile_sprite_ids = [
    0, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159,160, 161, 162, 163, 164, 165,  # Ryu
    102, 103,  # Ken
]
projectile_sprite_ids_set = set(projectile_sprite_ids)


def generate_projectile_sprite_ids_dictionary(sprite_ids):
    dictionary = dict()
    for index in range(len(sprite_ids)):
        dictionary[sprite_ids[index]] = index
    return dictionary


projectile_sprite_ids_dictionary = generate_projectile_sprite_ids_dictionary(projectile_sprite_ids)

NUMBER_OF_SPRITES = 200
NUMBER_OF_CHARACTER_INPUTS = NUMBER_OF_SPRITES + 7 + len(projectile_sprite_ids) + 5


class SuperStreetFighter2ObservationSpaceWrapper(Wrapper):
    def __init__(self, env):
        super().__init__(env)
        self.observation_space = gym.spaces.Box(
            low=0,
            high=1,
            shape=(
                2 * NUMBER_OF_CHARACTER_INPUTS +
                5,
            )
        )
        self.env.observation_space = self.observation_space

    def reset(self, **kwargs):
        if self.env.initial_state:
            self.env.em.set_state(self.env.initial_state)
        for p in range(self.env.players):
            self.env.em.set_button_mask(np.zeros([self.env.num_buttons], np.uint8), p)
        self.env.em.step()
        if self.env.movie_path is not None:
            rel_statename = os.path.splitext(os.path.basename(self.env.statename))[0]
            self.record_movie(
                os.path.join(self.env.movie_path, '%s-%s-%06d.bk2' % (self.env.gamename, rel_statename, self.env.movie_id)))
            self.env.movie_id += 1
        if self.env.movie:
            self.env.movie.step()
        self.env.data.reset()
        self.env.data.update_ram()
        return (0,) * self.observation_space.shape[0]

    def step(self, action):
        for p, ap in enumerate(self.env.action_to_array(action)):
            if self.env.movie:
                for i in range(self.env.num_buttons):
                    self.env.movie.set_key(i, ap[i], p)
            self.env.em.set_button_mask(ap, p)

        if self.env.movie:
            self.env.movie.step()
        self.env.em.step()
        self.env.data.update_ram()
        rew, done, info = self.env.compute_step()
        info = dict(info)
        return self.observation(info), rew, bool(done), info

    def observation(self, info):
        observations = np.concatenate(
            (
                generate_character_observations(
                    {
                        'sprite_id_next_frame': info['sprite_id_next_frame_p1'],
                        'hp': info['hp_p1'],
                        'x': info['x_p1'],
                        'y': info['y_p1'],
                        'active': info['active_p1'],
                        'projectile_active_1': info['projectile_active_p1_1'],
                        'projectile_active_2': info['projectile_active_p1_2'],
                        'projectile_active_3': info['projectile_active_p1_3'],
                        'sprite_id_next_frame_projectile': info['sprite_id_next_frame_projectile_p1'],
                        'x_projectile': info['x_projectile_p1'],
                        'y_projectile': info['y_projectile_p1'],
                        'other_character_hp': info['hp_p2'],
                        'other_character_x': info['x_p2'],
                    }
                ),
                generate_character_observations(
                    {
                        'sprite_id_next_frame': info['sprite_id_next_frame_p2'],
                        'hp': info['hp_p2'],
                        'x': info['x_p2'],
                        'y': info['y_p2'],
                        'active': info['active_p1'],
                        'projectile_active_1': info['projectile_active_p2_1'],
                        'projectile_active_2': info['projectile_active_p2_2'],
                        'projectile_active_3': info['projectile_active_p2_3'],
                        'sprite_id_next_frame_projectile': info['sprite_id_next_frame_projectile_p2'],
                        'x_projectile': info['x_projectile_p2'],
                        'y_projectile': info['y_projectile_p2'],
                        'other_character_hp': info['hp_p1'],
                        'other_character_x': info['x_p1'],
                    }
                ),
                (
                    normalize_time_left(info['time_left']),
                    normalize_x_distance(calculate_x_distance(info['x_p1'], info['x_p2'])),
                    normalize_y_distance(calculate_y_distance(info['y_p1'], info['y_p2'])),
                    normalize_distance(calculate_distance(info['x_p1'], info['y_p1'], info['x_p2'], info['y_p2'])),  # distance
                    1 if info['hp_p1'] == info['hp_p2'] else 0,  # both characters have equal hp
                )
            )
        )
        return observations


def generate_character_observations(character_observations):
    return np.concatenate((
        create_sprite_id_embedding(character_observations['sprite_id_next_frame']),
        (
            normalize_hp(character_observations['hp']),
            normalize_x_coordinate(character_observations['x']),
            normalize_y_coordinate(character_observations['y']),
            character_observations['active'],
            1 if character_observations['hp'] > character_observations['other_character_hp'] else 0,  # more hp than other player
            character_observations['x'] < character_observations['other_character_x'],  # is on left
            character_observations['x'] > character_observations['other_character_x'],  # is on right
        ),
        create_projectile_sprite_id_embedding(character_observations['sprite_id_next_frame_projectile']),
        (
            character_observations['projectile_active_1'],
            character_observations['projectile_active_2'],
            character_observations['projectile_active_3'],
            normalize_x_coordinate(character_observations['x_projectile']),
            normalize_y_coordinate(character_observations['y_projectile']),
        )
    ))


def generate_character_observations_p2(character_observations):
    return np.concatenate((
        create_sprite_id_embedding(character_observations['sprite_id_next_frame']),
        (
            normalize_hp(character_observations['hp']),
            normalize_x_coordinate(character_observations['x']),
            normalize_y_coordinate(character_observations['y']),
            character_observations['active']
        )
    ))


def create_sprite_id_embedding(sprite_id):
    embedding = [0] * NUMBER_OF_SPRITES
    if sprite_id >= NUMBER_OF_SPRITES:
        print('sprite_id', sprite_id)
    else:
        embedding[sprite_id] = 1
    return embedding


def create_projectile_sprite_id_embedding(sprite_id):
    embedding = [0] * len(projectile_sprite_ids)
    if sprite_id in projectile_sprite_ids_set:
        embedding[projectile_sprite_ids_dictionary[sprite_id]] = 1
    else:
        print('projectile sprite id outside of embedding:', sprite_id)
    return embedding


def calculate_x_distance(x1, x2):
    return abs(x2 - x1)


def calculate_y_distance(y1, y2):
    return abs(y2 - y1)


def calculate_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def normalize_sprite_id(sprite_id):
    return sprite_id / 200.0


def normalize_hp(hp):
    return hp / 176.0


def normalize_x_coordinate(x):
    return (x - 54) / float(459 - 54)


def normalize_y_coordinate(y):
    return y / 192.0


def normalize_time_left(time_left):
    return time_left / 99.0


def normalize_x_distance(x_distance):
    return x_distance / float(459 - 54)


def normalize_y_distance(y_distance):
    return y_distance / 192.0


def normalize_distance(distance):
    return distance / calculate_distance(54, 0, 459, 192)
