import numpy as np


def array_hash(arr):
    arr = np.array(arr)
    shape = arr.shape
    flat = arr.ravel()
    stats = np.max(flat), np.min(flat), np.mean(flat), np.median(flat), np.std(flat), np.sum(flat), np.sum(flat * np.arange(len(flat)))
    return shape, np.sum(stats)
    
def check_hash(arr, test):
    sh,stats = array_hash(arr)
    return sh==test[0] and np.allclose(stats, test[1], rtol=1e-2, atol=1e-3)