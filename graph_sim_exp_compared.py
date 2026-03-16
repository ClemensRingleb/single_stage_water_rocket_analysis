import math
import numpy as np

import pygame as pg
from pygame.locals import *

import matplotlib.pyplot as plt

# -------------------------------------------

# Angabe der Daten

fill_levels = [20, 30, 40, 50, 80]

h_max_list_sim = [19.68, 26.24, 27.57, 23.43, 1.24]
h_max_list_exp = [16.05, 25.31, 28.22, 21.61, 0.67]

v_max_list_sim = [15.48, 17.11, 17.36, 15.02, 2.13]
v_max_list_exp = [19.13, 20.86, 21.04, 15.58, 1.13]

# plotten

plt.figure(figsize=(16, 9))

plt.plot(fill_levels, h_max_list_sim, linestyle = "dashed", linewidth=2, label="Simulation", marker = "x", markersize = 8, markeredgecolor = "black")
plt.plot(fill_levels, h_max_list_exp, linestyle= "solid", linewidth=2, label="Experiment", marker = "x", markersize = 8, markeredgecolor = "black")
plt.xlabel("Volumenanteil Wasser $V_w$ [ % ]", fontsize = 18) 
plt.ylabel("maximale Höhe $h$ [ m ]", fontsize = 18)
plt.axvline(0, color="black")
plt.axhline(0, color="black")
plt.legend(loc = "upper right", fontsize = 19)
plt.grid(linestyle='-', linewidth=1)
plt.savefig('diff_height_sim_exp_plot.png')
plt.show()



plt.figure(figsize=(16, 9))

plt.plot(fill_levels, v_max_list_sim, linestyle = "dashed", linewidth=2, label="Simulation", marker = "x", markersize = 8, markeredgecolor = "black")
plt.plot(fill_levels, v_max_list_exp, linestyle= "solid", linewidth=2, label="Experiment", marker = "x", markersize = 8, markeredgecolor = "black")
plt.xlabel("Volumenanteil Wasser $V_w$ [ % ]", fontsize = 18) 
plt.ylabel("maximale Geschwindigkeit $v$ [ m/s ]", fontsize = 18)
plt.axvline(0, color="black")
plt.axhline(0, color="black")
plt.legend(loc = "upper right", fontsize = 19)
plt.grid(linestyle='-', linewidth=1)
plt.savefig('diff_velocity_sim_exp_plot.png')
plt.show()