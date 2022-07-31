from onetimepass import get_totp

from stepn.util import Environment
from stepn.util.secretcheck import is_valid_secret


def prompt(message):
    def prompt_callback(*ignore):
        return input(message)

    return prompt_callback


def raise_error(message):
    def raise_callback(*ignore):
        raise RuntimeError(message)

    return raise_callback


def g_auth_callback(secret):
    return lambda *args: get_totp(secret)


def google_auth_dialog(env: Environment = None):
    """ If Environment is provided, will try to load and save secret """
    if env:
        secret = env.get_property("google-secret") or input("Enter your HMAC secret:")
        if is_valid_secret(secret):
            env.set_property("google-secret", secret)
            return g_auth_callback(secret)
        return prompt("Bad HMAC secret. Enter Google Authenticator code")
    # don't save or load secret elsewhere
    return prompt("Enter Google authenticator code:")
