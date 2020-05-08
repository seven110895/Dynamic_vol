
import datetime
import pandas as pd
from theoEngine import TheoEngine

from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import griddata
import matplotlib.pyplot as plt
import numpy as np

underlying_pair = "BTC/USD"
underlying_price = 3607
atm_volatility = .6   # decimal, annualized
interest_rate = 0

theo_engine = TheoEngine(
    underlying_pair=underlying_pair,
    underlying_price=underlying_price,
    atm_volatility=atm_volatility,
    interest_rate=interest_rate
)