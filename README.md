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

**Outcome**: 

  - Shots data is filtered for 5v5 play, shot distance, and other criteria.
  - Fiest draft of player's stats


## 2. Data Visualization (Initial Plot)
**Tools **: matplotlib & numpy (& SciPy’s griddata ?)

**Rules** : xGoal <= 0 set to 0

**Recomandation** : Adjust plot size and color scheme for clarity

**Outcome:** Initial shot map showing xGoals at each coordinate, highlighting areas with higher chance of scoring.


## 3. Data Smoothing
Tools: SciPy’s gaussian_filter, NumPy, matplotlib

**Rules: **

  - Apply Gaussian smoothing to reduce choppiness in the initial xGoal data.
  - Fine-tune the sigma value for smoothing; a higher sigma value results in more smoothing but may lose some detail.

**Recommendation:**

  - Experiment with different sigma values to balance the smoothing effect and retain meaningful patterns in the data.
  - The smoothed xGoal map should better represent the overall distribution of scoring chances.

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

**Outcome:**

  - A smooth, visual representation of the player’s xGoals on the ice surface.
  - This analysis allows you to see where the player has better (or worse) scoring chances compared to the league average.


## 5. Difference map (player vs league comparison)
**Tools:** numpy, matplotlib

**Rules:**

  - Subtract the league-wide smoothed xGoal data from the player's smoothed xGoal data.
  - This will highlight areas where the player outperforms or underperforms relative to the league average.
  - Use a color gradient to clearly visualize areas where the player has a higher or lower chance of scoring.

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

**Outcome:**

  - A final, clear, and detailed visualization that shows the player’s xGoal performance compared to the league average on an actual NHL rink. This makes it easier to understand where the player is most effective and where they may need to improve their shot selection or positioning.
  - The rink overlay provides spatial context to the heatmap, helping to connect the numerical data to the player's real-world shot locations.


