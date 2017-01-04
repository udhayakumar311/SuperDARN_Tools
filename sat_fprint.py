# -*- coding: utf-8 -*-
"""
Created on Tue Jan  3 19:33:13 2017

@author: mguski
"""
# %%
import numpy as np



def r(phi):
    r_a = 6378137
    r_p = 6356752.314
    
    eps = np.sqrt(r_a**2-r_p**2) / r_a
    r =r_p / np.sqrt(1-eps**2*np.cos(phi))
    return r
    
phi = 90/180*np.pi

r(phi) / r_a