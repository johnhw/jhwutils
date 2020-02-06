# JHW 2019

import timeit
import matplotlib.pyplot as plt
import numpy as np
import scipy.optimize
import scipy.special
import time


complexities = {
    "linear": lambda n: n,
    "constant": lambda n: 1 + n * 0,
    "quadratic": lambda n: n ** 2,
    "cubic": lambda n: n ** 3,
    "log": lambda n: np.log(n),
    "nlogn": lambda n: n * np.log(n),
    "exp": lambda n: 2 ** n,
    "factorial": lambda n: scipy.special.gamma(n),
}

def complexity_fit(x, fn, ns, ts):
    return np.sum((x * fn(ns) - ts) ** 2)


def time_complexity(
    fn, ns, reps=20, number=1000, plot=True, setup="pass", extra_globals={}
):
    ts = []
    for rep in range(reps):
        times = []
        for n in ns:
            times.append(
                timeit.timeit(
                    "fn(n)",
                    setup=setup,
                    globals={**globals(), "fn": fn, "n": n, **extra_globals},
                    number=number,
                )
            )
            time.sleep(0.0001) # important for getting timings reliably!
        print(".", end="", flush=True)

        time.sleep(0.01)
        ts.append(times)

    # compute stats
    ts = np.array(ts).T
    ts = ts / np.mean(ts[0])
    mean_times = np.median(ts, axis=1)
    std_times = np.std(ts, axis=1)
    sem_times = 1.96 * (std_times / np.sqrt(reps))

    # plot complexity curve
    if plot:
        fig, ax = plt.subplots(1, 1, figsize=(12, 4))
        ax.plot(ns, mean_times, "k--", zorder=10)
        ax.fill_between(ns, mean_times - sem_times, mean_times + sem_times, alpha=0.1)
        ax.set_xlabel("N")
        ax.set_ylabel("Time (relative)")
        ax.set_title("Linear scale complexity")
        ax.set_frame_on(False)

    # fit and score complexities
    scores = []
    coeffs = []
    names = []
    fns = []
    ns = np.array(ns)
    ts = np.array(mean_times)
    for c_name, c_fn in complexities.items():
        res = scipy.optimize.minimize_scalar(
            complexity_fit, bracket=[1e-5, 1e5], args=(c_fn, ns, ts)
        )
        scores.append(res.fun)
        coeffs.append(res.x)
        names.append(c_name)
        fns.append(c_fn)

    scores = 1.0 / np.sqrt(np.array(scores))
    tot_score = np.sum(scores)
    scores = scores / tot_score

    
    if plot:
        print()
        print(f"Scores for {fn.__name__}")
        # plot reference curves
        for score, coeff, fn, name in zip(scores, coeffs, fns, names):
            ax.plot(ns, fn(ns) * coeff,  alpha=min(1.0, score+0.1), label=name, lw=1+score*5) # 

    ord_score = np.argsort(-scores)
    score_dict = {}
    for ix in ord_score:
        if plot:
            print(f"  {names[ix].ljust(12)} {scores[ix]*100.0:4.1f}%")
        score_dict[names[ix]] = scores[ix]

    if plot:
        ax.legend()
        ax.set_ylim(0.0, np.max(mean_times) * 1.1)

    return ns, mean_times, score_dict

if __name__=="__main__":
    import random
    # test sorting sequences of random integers
    def quadratic_time(n):
        s = 0
        for i in range(n):
            for j in range(n):
                s = s + 1
            

    time_complexity(quadratic_time, range(1, 800, 20), reps=12, number=5)
    plt.show()