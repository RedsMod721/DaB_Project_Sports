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
**Tools **: matplotlib
