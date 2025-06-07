from pygame.time import get_ticks

class Timer:
    def __init__(self, duration, repeat=False):
        self.duration = duration
        # self.func = func
        self.repeat = repeat
        self.start_time = 0
        self.active = True

    def activate(self):
        self.start_time = get_ticks()
        self.active = True

    def deactivate(self):
        self.active = False
        self.start_time = 0
        if self.repeat:
            self.activate()

    def update(self):
        current_time = get_ticks()
        if current_time - self.start_time >= self.duration:
            # if self.active and self.start_time != 0:
                # self.func()
            self.deactivate()