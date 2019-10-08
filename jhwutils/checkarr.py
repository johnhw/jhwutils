import numpy as np


def array_hash(arr):
    arr = np.array(arr)
    shape = arr.shape
    flat = arr.ravel()
    stats = np.nanmax(flat), np.nanmin(flat), np.nanmean(flat), np.nanmedian(flat), np.nanstd(flat), np.nansum(flat), np.nansum(flat * np.arange(len(flat)))
    return shape, np.nansum(stats)
    
def check_hash(arr, test):
    sh,stats = array_hash(arr)
    ok = sh==test[0] and np.allclose(stats, test[1], rtol=1e-2, atol=1e-3)
    if not ok:
        print(f"Got hash {sh}, {stats} but expected {test[0]}, {test[1]}")
    return ok