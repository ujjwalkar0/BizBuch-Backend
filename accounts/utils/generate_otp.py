import random

def generate_otp(length=6):
    low = 10**(length-1)
    return str(random.randint(low, 10**length - 1))
