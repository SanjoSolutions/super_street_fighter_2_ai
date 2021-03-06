from Runner import Runner
from Scheduler import Scheduler
from model import Player, PlayerHadouken


def main():
    runner = Runner(
        players=(
            Player(0),
        ),
        state='ryu_vs_ken_highest_difficulty'
    )
    scheduler = Scheduler(runner.on_frame, fps=40)
    scheduler.run()


if __name__ == '__main__':
    main()
