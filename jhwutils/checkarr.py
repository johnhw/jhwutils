import numpy as np
from binascii import crc32


def array_hash(arr):
    arr = np.array(arr)
    shape = arr.shape
    flat = arr.ravel()
    stats = (
        np.nanmax(flat),
        np.nanmin(flat),
        np.nanmean(flat),
        np.nanmedian(flat),
        np.nanstd(flat),
        np.nansum(flat),
        np.nansum(flat * np.arange(len(flat))),
    )
    return shape, np.nansum(stats)


def check_hash(arr, test):
    sh, stats = array_hash(arr)
    ok = sh == test[0] and np.allclose(stats, test[1], rtol=1e-5, atol=1e-5)
    if not ok:
        print(f"Got hash {sh}, {stats} but expected {test[0]}, {test[1]}")
    return ok


def _check_scalar(x, h, tol=5):
    formatting = f"{{x:1.{tol}e}}"
    formatted = formatting.format(x=x)
    print(formatted)
    hash_f = hex(crc32(formatted.encode("ascii")))
    return hash_f


def check_scalar(x, h, tol=5):
    offset = 10 ** (-tol) * x * 0.1
    ctr = _check_scalar(x, h, tol)
    abv = _check_scalar(x + offset, h, tol)
    blw = _check_scalar(x - offset, h, tol)
    if h not in [ctr, abv, blw]:
        print(f"Warning: Got {x:1.5e} -> {ctr}, expected {h}")
        return False
    return True


def check_string(s, h):
    hash_f = hex(crc32(f"{s.lower()}".encode("utf8")))
    if hash_f != h:
        print(f"Warning: Got {x} -> {hash_f}, expected {h}")
    return hash_f == h


if __name__ == "__main__":
    check_scalar(0.01000, "0x5ecf2a74")
