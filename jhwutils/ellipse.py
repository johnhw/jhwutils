import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse

def eigsorted(cov):
    vals, vecs = np.linalg.eigh(cov)
    order = vals.argsort()[::-1]
    return vals[order], vecs[:,order]


def  cov_ellipse(ax, x, nstd, **kwargs):        
    cov = np.cov(x.T)
    vals, vecs = eigsorted(cov)    
    theta = np.degrees(np.arctan2(*vecs[:,0][::-1]))
    w, h = 2 * nstd * np.sqrt(vals)
    ell = Ellipse(xy=(np.mean(x[:,0]), np.mean(x[:,1])),
                width=w, height=h,
                angle=theta, **kwargs)
    
    ax.add_artist(ell)
