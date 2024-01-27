import time


def pad_num(num: int) -> str:
    """
    Pads number out to 2 characters
    """
    return f"{num // 10}{num % 10}"


def timestamp(seconds: int | None = None) -> str:
    """
    Splits a double digit time into components
    """
    if seconds is None:
        seconds = time.time()

    Y, M, mD, h, m, s, wD, yD = time.localtime(seconds)

    return f"{pad_num(h)}:{pad_num(m)}:{pad_num(s)}"


if __name__ == "__main__":

    for i in range(61):
        print(i, pad_num(i))

    print(time.time())
    print(timestamp(time.time()))
    print(timestamp())
