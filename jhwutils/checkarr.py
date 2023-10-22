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


def moment_hash(arr):
    arr = np.array(arr)
    shape = arr.shape
    flat = arr.ravel()
    m = np.arange(len(flat))

    stats = []
    for i in range(3):
        f = flat * m ** i
        m_stats = (
            np.nanmax(f),
            np.nanmin(f),
            np.nanmean(f),
            np.nanmedian(f),
            np.nanstd(f),
            np.nansum(f),
        )
        stats.append(m_stats)

    shape_hash = hex(crc32(f"{shape}".encode("utf8")))
    return shape_hash[2:] + _check_scalar(np.nansum(stats))[2:]


def strict_array_hash(arr):
    ix = np.meshgrid(*[np.arange(i) for i in arr.shape], indexing="ij")
    return array_hash(np.mean([i*arr for i in ix], axis=0))

def check_hash(arr, test, strict=False):
    if strict:
        sh, stats = strict_array_hash(arr)
    else:
        sh, stats = array_hash(arr)
    ok = sh == test[0] and np.allclose(stats, test[1], rtol=1e-5, atol=1e-5)

    if not ok:
        print(f"Got hash {sh}, {stats} but expected {test[0]}, {test[1]}")
    return ok

def check_moment(arr, hash):
    hash = moment_hash(arr)
    print(hash)
    return hash == moment_hash

def _check_scalar(x, tol=5):
    formatting = f"{{x:1.{tol}e}}"
    formatted = formatting.format(x=x)
    hash_f = hex(crc32(formatted.encode("ascii")))
    return hash_f

def check_scalar(x, h, tol=5):
    offset = 10 ** (-tol) * x * 0.1
    ctr = _check_scalar(x, tol)
    abv = _check_scalar(x + offset, tol)
    blw = _check_scalar(x - offset, tol)
    if h not in [ctr, abv, blw]:
        print(f"Warning: Got {x:1.5e} -> {ctr}, expected {h}")
        return False
    return True

def check_string(s, h):
    hash_f = hex(crc32(f"{s.lower()}".encode("utf8")))
    if hash_f != h:
        print(f"Warning: Got {s} -> {hash_f}, expected {h}")
    return hash_f == h

def check_anagram(l):
    return check_string("".join(sorted(l)))

def check_list(l):
    return check_string("".join(l))

if __name__ == "__main__":
    check_scalar(0.01000, "0x5ecf2a74")
    print(moment_hash(np.ones((5, 5))))
