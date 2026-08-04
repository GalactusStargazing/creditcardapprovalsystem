import random


def generate_card_number() -> str:
    """
    Generates a 15-digit card number starting with the fixed prefix 3579,
    followed by 11 random digits.
    """
    prefix = "3579"
    remaining_digits = "".join(str(random.randint(0, 9)) for _ in range(11))
    return prefix + remaining_digits
