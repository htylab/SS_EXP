import matplotlib.pyplot as plt
import numpy as np
import time
import time, random
import math
from collections import deque
import scipy.misc as misc
import serial
from matplotlib.widgets import Slider
from matplotlib.widgets import Button
from matplotlib.widgets import RadioButtons
fig, ax = plt.subplots()
tag=0.0   #須手動改變模式
plt.title('The Heartbeat value')

plt.subplots_adjust(left=0.25, bottom=0.25)
plt.show(block=False)
line, = ax.plot(np.random.randn(100),'blue')
plt.axis()
start = time.time()

number=[]
def onclick(event):
    exit()
class RealtimePlot:
    def __init__(self, max_entries = 150):
        self.axis_x = deque(maxlen=max_entries)
        self.axis_y = deque(maxlen=max_entries)
        self.max_entries = max_entries

    def add(self, x, y):
        self.axis_x.append(x)
        self.axis_y.append(y)

tstart = time.time()
display = RealtimePlot()
plt.show(block=False)
ptime = time.time()
strPort='com11'  #更改com的聯接阜
# plot parameters
print ('plotting data...')
# open serial port
ser = serial.Serial(strPort, 9600)

axcolor = 'lightgoldenrodyellow'
#宣告多重按鈕物件
rax = plt.axes([0.025, 0.5, 0.15, 0.15], axisbg=axcolor)
radio = RadioButtons(rax, ( 'blue','red', 'green'), active=0)
#宣告拉霸物件(Slider)
axzoom = plt.axes([0.25, 0.1, 0.65, 0.03], axisbg=axcolor)
szoom = Slider(axzoom, 'ZOOM', 0.7, 1.25, valinit=1.1)
#宣告按鈕
resetax = plt.axes([0.8, 0.025, 0.1, 0.04])
button = Button(resetax, 'Reset', color=axcolor, hovercolor='0.975')

counter=0
maximum=0.0
#Y軸上下限設置
ax.set_ylim(200,800)
def reset(event):
    szoom.reset()
def colorfunc(label):
    line.set_color(label)
    #需克服的點 tag 直無法輸出
    if(label=='blue'):
        tag=0.0
    if(label=='red'):
        tag=1.0
    if(label=='green'):
        tag=2.0
    return tag
    #
def update(val):
    zoom = szoom.val
    if(tag==0.0):
        up=800 * zoom
        down=200 / zoom
    if(tag==1.0):
        up=800 * zoom
        down=200 / zoom
    if(tag==2.0):
        up=800 * zoom
        down=200 / zoom
    ax.set_ylim(down,up)
    #需等上述功能完成才能實現
while True:
    if(tag==0.0):       
        #啟動物件的條件
        szoom.on_changed(update)
        button.on_clicked(reset)
        radio.on_clicked(colorfunc)
        #
        #老師所給的條件
        linex = ser.readline()
        data = float(linex.split()[0])
        print(data)
        display.add(time.time() - start, data)
        line.set_xdata(display.axis_x)
        line.set_ydata(display.axis_y)
        ax.set_xlim(display.axis_x[0], display.axis_x[0] + 15)
        ax.draw_artist(ax.patch)    
        ax.draw_artist(line)
        fig.canvas.draw()
        fig.canvas.flush_events()
        delta = time.time()-ptime
        ptime = time.time()
        #
    if(tag==1.0):#取每10個數字的平均直       
        szoom.on_changed(update)
        button.on_clicked(reset)
        radio.on_clicked(colorfunc)
        linex = ser.readline()
        data = float(linex.split()[0])
        for i in range(0,10,1):
            number.append(data)
            print(number)
            display.add(time.time() - start, data)
            line.set_xdata(display.axis_x)
            line.set_ydata(display.axis_y)
            ax.set_xlim(display.axis_x[0], display.axis_x[0] + 15)
            ax.draw_artist(ax.patch)    
            ax.draw_artist(line)
            fig.canvas.draw()
            fig.canvas.flush_events()
            delta = time.time()-ptime
            ptime = time.time()      
        #print(number)
        

    if(tag==2.0):       #取最大值並數字化
        szoom.on_changed(update)
        button.on_clicked(reset)
        radio.on_clicked(colorfunc)
        linex = ser.readline()
        data = float(linex.split()[0])
        if(data>maximum):
            maximum=data
        print(tag)
        print(maximum)
        display.add(time.time() - start, maximum)
        line.set_xdata(display.axis_x)
        line.set_ydata(display.axis_y)
        ax.set_xlim(display.axis_x[0], display.axis_x[0] + 15)
        ax.draw_artist(ax.patch)    
        ax.draw_artist(line)
        fig.canvas.draw()
        fig.canvas.flush_events()
        delta = time.time()-ptime
        ptime = time.time()