import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse


def eigsorted(cov):
    vals, vecs = np.linalg.eigh(cov)
    order = vals.argsort()[::-1]
    return vals[order], vecs[:, order]


def cov_ellipse(ax, x, nstd, **kwargs):
    cov = np.cov(x.T)
    mu = np.mean(x, axis=0)
    _cov_ellipse(ax, mu, cov, nstd=nstd, **kwargs)


def _cov_ellipse(ax, mu, sigma, nstd=1, **kwargs):
    vals, vecs = eigsorted(sigma)
    theta = np.degrees(np.arctan2(*vecs[:, 0][::-1]))
    w, h = 2 * nstd * np.sqrt(vals)
    ell = Ellipse(xy=(mu[0], mu[1]), width=w, height=h, angle=theta, **kwargs)

    ax.add_artist(ell)

