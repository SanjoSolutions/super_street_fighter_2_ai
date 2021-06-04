from Runner import Runner
from Scheduler import Scheduler


def main():
    runner = Runner()
    scheduler = Scheduler(runner.on_frame, fps=40)
    scheduler.run()


if __name__ == '__main__':
    main()
