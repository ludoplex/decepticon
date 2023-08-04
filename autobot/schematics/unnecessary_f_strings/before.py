"""...with useless f-string prefixes."""


def func() -> None:
    a = "world"
    b = f"Hello, {a}!"
    c = "Hello world"
    d = f"Hello, " + f"{a}!"
