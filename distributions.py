import numpy as np
from scipy.special import logit
from scipy.stats import norm

class LogitNormal:
    def _pdf(self, x, **kwargs):
        return norm.pdf(logit(x), **kwargs)/(x*(1-x))
