def prompt(message):
    def prompt_callback(*ignore):
        return input(message)

    return prompt_callback


def raise_error(message):
    def raise_callback(*ignore):
        raise RuntimeError(message)

    return raise_callback
