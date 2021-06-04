import gym
import numpy as np

class Discretizer(gym.ActionWrapper):
    """
    Wrap a gym environment and make it use discrete actions.

    Args:
        combos: ordered list of lists of valid button combinations

    Based on https://github.com/openai/retro/blob/98fe0d328e1568836a46e5fce55a607f47a0c332/retro/examples/discretizer.py.
    License of https://github.com/openai/retro/blob/98fe0d328e1568836a46e5fce55a607f47a0c332/retro/examples/discretizer.py:
    The MIT License

    Copyright (c) 2017-2018 OpenAI (http://openai.com)

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.
    """

    def __init__(self, env, combos):
        super().__init__(env)
        assert isinstance(env.action_space, gym.spaces.MultiBinary)
        buttons = env.unwrapped.buttons
        self._decode_discrete_action = []
        for combo in combos:
            arr = np.array([False] * env.action_space.n)
            for button in combo:
                arr[buttons.index(button)] = True
            self._decode_discrete_action.append(arr)

        self.action_space = gym.spaces.Discrete(
            len(self._decode_discrete_action))

    def action(self, action):
        if isinstance(action, tuple) or isinstance(action, list):
            number_of_actions = int(self.env.action_space.n / self.env.players)
            return np.concatenate(
                tuple(
                    self.map_discrete_action_to_multi_binary_action(action[index])[0:number_of_actions]
                    for index
                    in range(len(action))
                ),
                axis=None
            )
        else:
            return self.map_discrete_action_to_multi_binary_action(action)

    def map_discrete_action_to_multi_binary_action(self, action):
        return self._decode_discrete_action[action].copy()
