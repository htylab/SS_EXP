import matplotlib.pyplot as plt
import numpy as np
import time
import time, random
import math
import serial
from collections import deque



#Display loading 
class PlotData:
    def __init__(self, max_entries=30):
        self.axis_x = deque(maxlen=max_entries)
        self.axis_y = deque(maxlen=max_entries)
    def add(self, x, y):
        self.axis_x.append(x)
        self.axis_y.append(y)


#initial
fig, (ax,ax2) = plt.subplots(2,1)
line,  = ax.plot(np.random.randn(100))
line2, = ax2.plot(np.random.randn(100))
plt.show(block = False)
plt.setp(line2,color = 'r')



PData= PlotData(500)
ax.set_ylim(0,500)
ax2.set_ylim(0,500)



# plot parameters
print ('plotting data...')
# open serial port
strPort='com4'
ser = serial.Serial(strPort, 115200)
ser.flush()

start = time.time()

while True:
    
    for ii in range(10):

        try:
            data = float(ser.readline())
            PData.add(time.time() - start, data)
        except:
            pass

    ax.set_xlim(PData.axis_x[0], PData.axis_x[0]+5)
    ax2.set_xlim(PData.axis_x[0], PData.axis_x[0]+5)
    line.set_xdata(PData.axis_x)
    line.set_ydata(PData.axis_y)
    line2.set_xdata(PData.axis_x)
    line2.set_ydata(PData.axis_y)
    fig.canvas.draw()
    fig.canvas.flush_events()
