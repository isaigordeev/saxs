import numpy as np
import pandas as pd
import os 
from settings import *
# import datetime


# now = datetime.datetime.now()
# filename_directory = analyse_directory + filename + str(now.time())[:8]

filename_directory = analyse_directory + filename
if not os.path.exists(filename_directory):
    os.mkdir(analyse_directory + filename)




