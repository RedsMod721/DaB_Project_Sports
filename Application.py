import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv("shots_2023.csv")

# print(data.head())

data = data[(data['awaySkatersOnIce'] == 5) & (data['homeSkatersOnIce'] == 5)]
data = data[data['shotDistance'] <= 89]
data = data[data['shotOnEmptyNet'] == 0]
data = data[data['xCordAdjusted'] <= 89]

print("xGoals Max {:.2f}".format(data['xGoal'].max()))
print("xGoals Mean {:.2f}".format(data['xGoal'].mean()))
print("X Cords: {}, {}".format(data['xCordAdjusted'].min(),data['xCordAdjusted'].max()))
print("Y Cords: {}, {}".format(data['yCordAdjusted'].min(),data['yCordAdjusted'].max()))

