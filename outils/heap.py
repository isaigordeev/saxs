from outils import *
import os


EXTENSION = '.csv'
FILENAME = '075904_treated_xye'
data_dir = 'data_test'

EXTENSION1 = '.txt'
data_dir1 = ''
FILENAME1 = 'data_break_peak:4'

current_dir = os.getcwd()
print(current_dir)

data_dir = os.path.join(current_dir, '..', data_dir, FILENAME)

data = read_data(data_dir, EXTENSION)
background_plot(data[0], data[1])

# data_dir = os.path.join(current_dir, '..', FILENAME1)
# print(data_dir)
#
# data = read_data(data_dir, EXTENSION)
# background_plot(data[0], data[1])


