import time


def pad_num(num: int) -> str:
    return f"{num // 10}{num % 10}"


def timestamp():
    Y, M, mD, h, m, s, wD, yD = time.localtime()

    return f"{pad_num(h)}:{pad_num(m)}:{pad_num(s)}"


if __name__ == "__main__":
    for i in range(61):
        print(i, pad_num(i))

    print(timestamp())
