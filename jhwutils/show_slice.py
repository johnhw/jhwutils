import colorama
import numpy as np


def inslice(i, n, slc):
    if type(slc) == type(0):
        return i == slc
    return (
        (
            slc.start is None
            or (slc.start >= 0 and i >= slc.start)
            or (slc.start < 0 and i >= n + slc.start)
        )
        and (
            slc.stop is None
            or (slc.stop >= 0 and i < slc.stop)
            or (slc.stop < 0 and i < n + slc.stop)
        )
        and (slc.step is None or i % slc.step == 0)
    )


highlight = colorama.Back.YELLOW + colorama.Fore.BLACK + colorama.Style.BRIGHT
normal = colorama.Style.RESET_ALL + colorama.Back.WHITE + colorama.Fore.BLACK


# ideas: show colormap for entries (via HTML?)
# shwo multidimensional arrays, grouped by colour


class show_slice:
    def __init__(self, a):
        self.a = a
        if len(self.a.shape) == 1:
            self.a = self.a[None, :]

    def __getitem__(self, slc):
        for i, row in enumerate(self.a):
            inside_row = inslice(i, self.a.shape[0], slc[0])
            for j, col in enumerate(row):
                inside_col = inslice(j, self.a.shape[1], slc[1])
                if inside_row and inside_col:
                    print(highlight + f" {col:5.1f}", end=" ")
                else:
                    print(normal + f" {col:5.1f}", end=" ")
            print(colorama.Style.RESET_ALL)
        print()

    print(colorama.Style.RESET_ALL)


if __name__ == "__main__":
    colorama.init()  # not in the notebook!
    a = np.zeros((5, 5))
    show_slice(a)[1:2, ::2]
