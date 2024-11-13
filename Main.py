import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from scipy.ndimage import gaussian_filter 
import HockeyRink

data = pd.read_csv("shots_2023.csv")

# print(data.head())

data = data[(data['awaySkatersOnIce'] == 5) & (data['homeSkatersOnIce'] == 5)]
data = data[data['shotDistance'] <= 89]
data = data[data['shotOnEmptyNet'] == 0]
data = data[data['xCordAdjusted'] <= 89]

# Prints the max % that a shot would be a goal, 
#   avg % that a shot would be a goal (xGoal),
#   Cordinates have been adjusted to show as if they happened in the offensive zone

# print("xGoals Max {:.2f}".format(data['xGoal'].max()))
# print("xGoals Mean {:.2f}".format(data['xGoal'].mean()))
# print("X Cords: {}, {}".format(data['xCordAdjusted'].min(),data['xCordAdjusted'].max()))
# print("Y Cords: {}, {}".format(data['yCordAdjusted'].min(),data['yCordAdjusted'].max()))


# Creating an array of the xGoal values from the data
#  "gridData" allows us to fill the missing gaps in the data, and we fill the negative 
#   values with 0 because negative 'Xgoals' are not possible in reality (every shot has some probability of going in)
[x,y] = np.round(np.meshgrid(np.linspace(0, 100, 100), np.linspace(-42.5, 42.5, 85)))
xgoals = griddata((data['xCordAdjusted'],data['yCordAdjusted']),
    data['xGoal'],(x,y),method='cubic',fill_value=0)
xgoals = np.where(xgoals < 0,0,xgoals)

# fig = plt.figure(figsize=(10,12), facecolor='w', edgecolor='k')
# plt.imshow(xgoals,origin = 'lower')
# plt.colorbar(orientation = 'horizontal', pad = 0.05)
# plt.title('xGoal Array',fontdict={'fontsize': 15})
# plt.show()

# Using the 'gaussian filter' function, we are smoothing the data to 
#   make it more viusally appealing; Smoothing the data allows for much easier analysis
# Also drops the maximum from 0.79 to ~0.23 

xgoals_smooth = gaussian_filter(xgoals,sigma = 3)

fig = plt.figure(figsize=(10,12), facecolor='w', edgecolor='k')
plt.imshow(xgoals_smooth,origin = 'lower')
plt.colorbar(orientation = 'horizontal', pad = 0.05)
plt.title('xGoal Smoothed Array',fontdict={'fontsize': 15})
plt.show()

# Template for individual players e.g. Conor McDavid

player_name = 'Connor McDavid'
player_shots = data[data['shooterName'] == player_name]

[x,y] = np.round(np.meshgrid(np.linspace(0,100,100),np.linspace(-42.5,42.5,85)))
xgoals_player = griddata((player_shots['xCordAdjusted'],player_shots['yCordAdjusted']),player_shots['xGoal'],(x,y),method='cubic',fill_value=0)
xgoals_player = np.where(xgoals_player < 0,0,xgoals_player)

player_shots_smooth = gaussian_filter(xgoals_player,sigma = 3)

fig = plt.figure(figsize=(10,12), facecolor='w', edgecolor='k')
plt.imshow(player_shots_smooth,origin = 'lower')
plt.colorbar(orientation = 'horizontal', pad = 0.05)
plt.title(player_name + ' xGoal Smoothed Array',fontdict={'fontsize': 15})
plt.show()

# Taking the Difference of the two arrays to see where Players perform better
difference = player_shots_smooth - xgoals_smooth

fig = plt.figure(figsize=(10,12), facecolor='w', edgecolor='k')
plt.imshow(difference,origin = 'lower')
plt.colorbar(orientation = 'horizontal', pad = 0.05)
plt.title(player_name + ' vs Leage xGoal',fontdict={'fontsize': 15})
plt.show()

difference = difference[:,:90]

fig, ax = plt.subplots(1,1, figsize=(10,12), facecolor='w', edgecolor='k')
rink = HockeyRink.HockeyRink(board_radius=28, alpha=1)
rink.draw(ax, plot_half=True)

# Currently having issue with 'extent' that shows the heatmap extending past the rink
img = ax.imshow(difference, extent=(0,89,-42.5,42.5), vmin= -0.05, vmax= 0.05, cmap='bwr', origin='lower', alpha = 0.4)
fig.colorbar(img, orientation="horizontal", pad=0.05)

plt.title(player_name + ' vs League xGoal', fontdict={'fontsize': 15})
plt.axis('off')

plt.show()



# difference = difference[:,:90]

# fig, ax = plt.subplots(1,1, figsize=(10,12), facecolor='w', edgecolor='k')
# rink = HockeyRink.HockeyRink(board_radius=28, alpha=1)
# ax = ax.imshow(difference, extent = (0,89,-42.5,42.5),cmap='bwr', origin = 'lower', norm = mpl.color.Normalize(vmin=-0.05, vmax=0.05))
# fig.colorbar(ax, orientation="horizontal",pad = 0.05)
# plt.title(player_name + ' vs Leage xGoal',fontdict={'fontsize': 15})
# plt.axis('off')
# rink.draw(ax, plot_half=True)
# plt.show()

# rink = HockeyRink.HockeyRink(board_radius=28, alpha=1)
# fig, ax = plt.subplots(1, 1, figsize=(10, 12), facecolor='w', edgecolor='k')
# rink.draw(ax, plot_half=True)
# plt.show()