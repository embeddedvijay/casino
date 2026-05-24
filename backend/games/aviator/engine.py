import random


def generate_crash_point():
    r = random.random()

    if r < 0.10:
        return round(random.uniform(1.01, 1.20), 2)

    if r < 0.72:
        return round(random.uniform(1.21, 2.80), 2)

    if r < 0.93:
        return round(random.uniform(2.81, 10.00), 2)

    return round(random.uniform(10.01, 80.00), 2)


def calculate_multiplier(elapsed: float):
    multiplier = 1 + (elapsed * 0.22) + ((elapsed ** 1.7) * 0.045)
    return round(multiplier, 2)


def calculate_cashout(amount: float, multiplier: float):
    return round(float(amount) * float(multiplier), 2)