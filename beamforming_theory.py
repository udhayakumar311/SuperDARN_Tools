# -*- coding: utf-8 -*-
"""
Created on Fri Jan 13 14:18:38 2017

@author: mguski
"""
# %%
import numpy as np
import matplotlib.pyplot as plt

nAntennas = 16
x_spacing = 15.4
freq = 10e6

nSteps = 360*5

c = 3e8
alphaVec = np.array(range(nSteps)) /nSteps*2* np.pi


# %% how to map anteeas to PCs, if one PC fails

nAntennas = 16
x_spacing = 15.4
R = 1/nAntennas * np.sin(np.pi*x_spacing/c*freq*nAntennas * np.cos(alphaVec)) / np.sin(np.pi*x_spacing/c*freq*np.cos(alphaVec))
plt.polar(alphaVec, 20*np.log10(np.absolute(R))+100, label='normal')

nAntennas = 8
x_spacing = 15.4
R = 1/nAntennas * np.sin(np.pi*x_spacing/c*freq*nAntennas * np.cos(alphaVec)) / np.sin(np.pi*x_spacing/c*freq*np.cos(alphaVec))
plt.polar(alphaVec, 20*np.log10(np.absolute(R))+100, label='one side')

nAntennas = 8
x_spacing = 15.4*2
R = 1/nAntennas * np.sin(np.pi*x_spacing/c*freq*nAntennas * np.cos(alphaVec)) / np.sin(np.pi*x_spacing/c*freq*np.cos(alphaVec))
plt.polar(alphaVec, 20*np.log10(np.absolute(R))+100, label='every second')

plt.legend()

