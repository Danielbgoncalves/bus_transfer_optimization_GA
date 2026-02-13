import random

def weighted_choice(items, weights):
    total = sum(weights)
    if total <= 0:
        return None

    r = random.uniform(0, total)
    acc = 0.0
    for item, w in zip(items, weights):
        acc += w
        if acc >= r:
            return item
