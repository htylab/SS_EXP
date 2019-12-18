import matplotlib.pyplot as plt
import numpy as np
import time
import time, random
import math
from collections import deque
import serial

fig, ax = plt.subplots()
line, = ax.plot(np.random.randn(100))
plt.show(block=False)
start = time.time()
def onclick(event):
    exit()

class RealtimePlot:
    def __init__(self, max_entries = 500):
        self.axis_x = deque(maxlen=max_entries)
        self.axis_y = deque(maxlen=max_entries)
        self.max_entries = max_entries

    def add(self, x, y):
        self.axis_x.append(x)
        self.axis_y.append(y)

tstart = time.time()
display = RealtimePlot()
plt.show(block=False)
fig.canvas.mpl_connect('button_press_event', onclick)
ax.set_ylim(0,1000)
ptime = time.time()
#please check your arduino port 
strPort='com3'
# plot parameters
print ('plotting data...')
# open serial port
ser = serial.Serial(strPort, 115200)

while True:
    linex = ser.readline()
    data = float(linex.split()[0])
    print(data)

    display.add(time.time() - start, data)
    line.set_xdata(display.axis_x)
    line.set_ydata(display.axis_y)
    ax.set_xlim(display.axis_x[0], display.axis_x[0] + 5)
    ax.draw_artist(ax.patch)
    ax.draw_artist(line)
    #fig.canvas.update()
    fig.canvas.draw()
    fig.canvas.flush_events()
    delta = time.time()-ptime
    ptime = time.time()
