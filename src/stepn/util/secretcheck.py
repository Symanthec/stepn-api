from onetimepass import get_totp


def is_valid_secret(secret):
    try:
        get_totp(secret)
        return True
    except TypeError:
        return False
