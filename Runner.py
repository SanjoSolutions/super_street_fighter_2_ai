from create_environment import create_environment
from model import Player, Actions


class Runner:
    def __init__(self):
        self.environment = create_environment(
            state='ryu_vs_ken_highest_difficulty',
            players=1,
        )
        self.players = (
            Player(0),
        )
        self.done = False
        self.info = None
        self.reset()

    def on_frame(self):
        actions = tuple(player.choose_action(self.info) for player in self.players)
        self.step(actions)
        self.render()
        if self.done:
            self.reset()

    def reset(self):
        self.environment.reset()
        # initial match step, so that info is available for the action decision making
        actions = (Actions.IDLE,) * len(self.players)
        self.step(actions)
        self.render()

    def step(self, actions):
        _, _, self.done, self.info = self.environment.step(actions)

    def render(self):
        self.environment.render()
