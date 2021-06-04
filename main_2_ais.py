from Runner import Runner
from Scheduler import Scheduler
from model import Player, PlayerHadouken


def main():
    runner = Runner(
        players=(
            Player(0),
            PlayerHadouken(1)
        ),
        state='ryu_vs_ryu_both_controlled'
    )
    scheduler = Scheduler(runner.on_frame, fps=40)
    scheduler.run()


if __name__ == '__main__':
    main()
