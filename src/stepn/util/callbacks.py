def prompt(message):
    def prompt_callback():
        return input(message)

    return prompt_callback


def raise_error(message):
    def raise_callback():
        raise RuntimeError(message)

    return raise_callback
