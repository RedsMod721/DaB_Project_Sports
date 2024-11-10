# DaB_Project_Sports


# Process steps

## 1. Data Import and Cleaning
**Tools** : pandas
**Data Source** : moneypuck.com
**Data cleansing rules**: 
  - 5 v 5 plays (No Power plays)
  - No shots taking place across the ice
  - No empty-net shots
  - No shots from behing the net

    **Maybe** :
"""
data = data[(data['awaySkatersOnIce'] == 5) & (data['homeSkatersOnIce'] == 5)]data = data[data['shotDistance'] <= 89]
data = data[data['shotOnEmptyNet'] == 0]
data = data[data['xCordAdjusted'] <= 89]
"""

**Outcome**: 
  - Shots data is filtered for 5v5 play, shot distance, and other criteria.
  - Fiest draft of player's stats


## 2. Data Visualization (Initial Plot)
**Tools **: matplotlib & numpy (& SciPy’s griddata ?)

**Rules** : xGoal <= 0 set to 0
**Recomandation** : Adjust plot size and color scheme for clarity

  **Maybe** :
"""
import numpy as np
from scipy.interpolate import griddata
import matplotlib.pyplot as plt

[x,y] = np.round(np.meshgrid(np.linspace(0,100,100),np.linspace(-42.5,42.5,85)))
xgoals = griddata((data['xCordAdjusted'],data['yCordAdjusted']),data['xGoal'],(x,y),method='cubic',fill_value=0)
xgoals = np.where(xgoals < 0,0,xgoals)

fig = plt.figure(figsize=(10,12), facecolor='w', edgecolor='k')
plt.imshow(xgoals,origin = 'lower')
plt.colorbar(orientation = 'horizontal', pad = 0.05)
plt.title('xGoal Array',fontdict={'fontsize': 15})
plt.show()
"""

**Outcome:** Initial shot map showing xGoals at each coordinate, highlighting areas with higher chance of scoring.


## 3. Data Smoothing
Tools: SciPy’s gaussian_filter, NumPy, matplotlib

**Rules: **
  - Apply Gaussian smoothing to reduce choppiness in the initial xGoal data.
  - Fine-tune the sigma value for smoothing; a higher sigma value results in more smoothing but may lose some detail.

**Recommendation:**
  - Experiment with different sigma values to balance the smoothing effect and retain meaningful patterns in the data.
  - The smoothed xGoal map should better represent the overall distribution of scoring chances.
Maybe:


  **Maybe** :
"""
xgoals_smooth = gaussian_filter(xgoals, sigma=3)

fig = plt.figure(figsize=(10,12), facecolor='w', edgecolor='k')
plt.imshow(xgoals_smooth, origin='lower')
plt.colorbar(orientation='horizontal', pad=0.05)
plt.title('xGoal Smoothed Array', fontdict={'fontsize': 15})
plt.show()
"""

**Outcome:**
  - A smoother xGoal grid for the entire NHL, which highlights broader trends in shot location efficiency (e.g., higher chances of scoring near the net).
  - The smoothing reduces the sharp fluctuations in the original data, providing a more interpretable visualization.

## 4. Individual player analysis 
**Tools:** pandas, numpy, matplotlib, SciPy’s griddata, Gaussian smoothing

**Rules:**
  - Filter the data for a specific player’s shots, using the player’s name as a filter.
  - Apply the same steps as the previous analysis (data cleaning, grid interpolation, and Gaussian smoothing) but focusing on the selected player’s shot data.

**Recommendation:**
  - After isolating the player’s shots, visualize their xGoals and compare with the league-wide averages.
  - By using the same smoothing method and grid interpolation, you can visually assess where the player has higher or lower chances of scoring compared to the league.

  **Maybe:**
"""
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
"""

**Outcome:**
  - A smooth, visual representation of the player’s xGoals on the ice surface.
  - This analysis allows you to see where the player has better (or worse) scoring chances compared to the league average.


## 5. Difference map (player vs league comparison)
**Tools:** numpy, matplotlib

**Rules:**
  - Subtract the league-wide smoothed xGoal data from the player's smoothed xGoal data.
  - This will highlight areas where the player outperforms or underperforms relative to the league average.
  - Use a color gradient to clearly visualize areas where the player has a higher or lower chance of scoring.

  **Maybe** : 
  difference = player_shots_smooth - xgoals_smooth
"""
fig = plt.figure(figsize=(10,12), facecolor='w', edgecolor='k')
plt.imshow(difference,origin = 'lower')
plt.colorbar(orientation = 'horizontal', pad = 0.05)
plt.title(player_name + ' vs Leage xGoal',fontdict={'fontsize': 15})
plt.show()
"""

**Outcome:**
  - A heatmap showing the areas where the player’s scoring chances are better or worse than the league average.
  - This gives a more detailed and intuitive understanding of the player's shot locations compared to other NHL players, highlighting their strengths and weaknesses on the ice.


## 6. Rink Overlay and Final Visualization
**Tools:** matplotlib, custom rink plotting function (create_rink)

**Rules:**
  - Overlay the rink lines on the difference map to add context to the data.
  - Ensure that the map is scaled appropriately to fit the NHL rink dimensions (e.g., the length and width of the ice rink).
  - Adjust the transparency of the rink lines and the background to ensure that the data visualization remains the focal point while still providing context.

**Recommendation:**
  - Use the create_rink function or an equivalent method to draw an accurate representation of an NHL rink, including the blue lines, faceoff circles, goal crease, and net locations.

    **Maybe **:
"""
import matplotlib as mpl
difference = difference[:,:90]

fig, ax = plt.subplots(1,1, figsize=(10,12), facecolor='w', edgecolor='k')
create_rink(ax, plot_half=True, board_radius= 25, alpha = .9)
ax = ax.imshow(difference, extent = (0,89,-42.5,42.5),cmap='bwr', origin = 'lower', norm = mpl.colors.Normalize(vmin=-0.05, vmax=0.05))
fig.colorbar(ax, orientation="horizontal",pad = 0.05)
plt.title(player_name + ' vs Leage xGoal',fontdict={'fontsize': 15})
plt.axis('off')
plt.show()
"""

**Outcome:**
  - A final, clear, and detailed visualization that shows the player’s xGoal performance compared to the league average on an actual NHL rink. This makes it easier to understand where the player is most effective and where they may need to improve their shot selection or positioning.
  - The rink overlay provides spatial context to the heatmap, helping to connect the numerical data to the player's real-world shot locations.


