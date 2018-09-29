import numpy as np
class History:
    def __init__(self):
        self.all_theta = []
        self.all_loss = []
        self.best_thetas = []
        self.best_losses = []
        self.all_best = []
        self.best = np.inf
        self.best_theta = None
        self.loss_trace = []
        self.iters = 0
        
    
    def track(self, theta, loss, force=False):
        self.all_theta.append(theta)
        self.all_loss.append(loss)
        self.iters += 1
        is_best = False
        if loss<self.best or force:
            self.best = loss
            self.best_theta = theta
            self.best_losses.append(self.best)
            self.best_thetas.append(self.best_theta)
            is_best = True
        self.loss_trace.append(self.best)
        self.all_best.append(is_best)
        return is_best
    
    def finalise(self):
        self.all_theta = np.array(self.all_theta)
        self.all_loss = np.array(self.all_loss)
        self.best_losses = np.array(self.best_losses)
        self.best_thetas = np.array(self.best_thetas)
        self.theta = np.array(self.best_theta)
        self.loss = np.array(self.best)
        self.loss_trace = np.array(self.loss_trace)
        return self