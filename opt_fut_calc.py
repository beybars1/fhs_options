import os
import numpy as np
import math
from scipy.stats import norm


class Calc:

    def __init__(self, strike_price, vol_rate, r, rf, stock_size, basis):
        self.strike_price = strike_price
        self.vol_rate = vol_rate
        self.r = r
        self.rf = rf
        self.stock_size = stock_size
        self.basis = basis

    def fwd_price(self, stock_price, period):
        return round((stock_price*math.exp((self.r-self.rf)*period/self.basis)), 2)

    def d_one(self, fwd_price, period):
        return round((math.log(fwd_price/self.strike_price) + math.pow(self.vol_rate, 2)*period/self.basis/2) / \
               (self.vol_rate*math.sqrt(period/self.basis)), 4)

    def d_two(self, d_one, period):
        return round(d_one-self.vol_rate*math.sqrt(period/self.basis), 4)

    @staticmethod
    def normal_d(d):
        return round(norm.cdf(d, loc=0, scale=1), 4)

    def option_call(self, period, fwd_price, n_d_one, n_d_two):
        return round(math.exp(-self.r*period/self.basis)*(fwd_price*n_d_one-self.strike_price*n_d_two), 4)

    def option_put(self, period, fwd_price, n_d_one, n_d_two):
        return round(math.exp(-self.r * period / self.basis) * (self.strike_price * n_d_two - fwd_price * n_d_one), 4)

    def sbs(self, d1, d2):
        return np.round((d2-d1)*self.stock_size, 4)

    @staticmethod
    def sbm(sbs, stock_price):
        return np.round(sbs*stock_price, 4)

    @staticmethod
    def accum(sbm1, sbm2):
        return np.round(sbm1+sbm2, 4)

