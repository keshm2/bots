import random

def random_hex():
    return '{0x:06x}'.format(random.randint(0, 0xFFFFFF))