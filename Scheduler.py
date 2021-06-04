from time import time, sleep


class Scheduler:
    def __init__(self, on_frame, fps):
        self.on_frame = on_frame
        self.fps = fps
        self.last_render_time = None

    def run(self):
        while True:
            self.schedule_next_frame()

    def schedule_next_frame(self):
        if self.last_render_time is None:
            self.render_frame()
        else:
            self.sleep_until_next_frame()
            self.render_frame()

    def render_frame(self):
        self.on_frame()
        self.last_render_time = time()

    def sleep_until_next_frame(self):
        time_to_sleep = (1 / self.fps) - (time() - self.last_render_time)
        if time_to_sleep > 0:
            sleep(time_to_sleep)
