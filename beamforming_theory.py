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
freq = 8.1e6

nSteps = 360*5

c = 3e8
alphaVec = np.array(range(nSteps)) /nSteps*2* np.pi
# %%
import numpy as np

nBeams = 16
x_spacing = 15.4
beam_sep = 3.24
c = 3e8

center_beam = (nBeams -1)/2
delay_list = []

for iBeam in range(nBeams):
 azm = (iBeam - center_beam) * beam_sep /180 * np.pi
 delta_time = np.sin(azm) * x_spacing / c
 delay_list.append(delta_time*1e9)
 

print("Theory Values for:")
print("  {} beams, {} deg beam sep, {} m antenna spacing".format(nBeams, beam_sep,x_spacing))

for iBeam in range(nBeams):
    print("  beam {: >3d} / {} :   time diff {: >7.3f} ns".format(iBeam, nBeams, delay_list[iBeam]))
    



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

