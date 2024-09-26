import time

class SimulationEngine:
    def __init__(self, environment):
        self.environment = environment
        self.time_step = 0.1  # seconds
        self.simulation_speed = 1.0  # 1.0 is real-time

    def update(self, generate_food=True, allow_merge=False):
        self.environment.update(self.time_step, generate_food, allow_merge)

    def run_for_duration(self, duration, generate_food=True, allow_merge=False):
        steps = int(duration / self.time_step)
        for _ in range(steps):
            self.update(generate_food, allow_merge)
            time.sleep(self.time_step / self.simulation_speed)

    def fast_forward(self, speed_factor):
        self.simulation_speed = speed_factor

    def slow_motion(self, speed_factor):
        self.simulation_speed = 1 / speed_factor

    def reset_speed(self):
        self.simulation_speed = 1.0