import matplotlib.pyplot as plt
import matplotlib.animation as animation 
import numpy as np
import Tkinter as tk
import time
import time, random
import math
import serial
from collections import deque
from matplotlib.widgets import Button, RadioButtons,Slider
#value initial
y_base = 500
y_bound = 100
#Heartbeat value
Heart = '999'
Heart_number = 0
#ax1 ylim
y_max = 1000
y_min = 0

#Display loading 
class RealtimePlot:
    def __init__(self, max_entries = 30):
        self.axis_x = deque(maxlen=max_entries)
        self.axis_y = deque(maxlen=max_entries)
        self.axis_z = deque(maxlen=max_entries)
        self.max_entries = max_entries
    def add(self, x, y):
        self.axis_x.append(x)
        self.axis_y.append(y)
        y2 =np.abs(abs(np.fft.fft(self.axis_y)))
        self.axis_z = y2
def button1_press(event):
    global display
    f = open('Store.txt','w')
    for i in display.axis_y:
        f.write(i)
def button2_press(event):
    y = []
    global display
    fig1, ax = plt.subplots()
    line,  = ax.plot(np.random.randn(100))
    for i in open('Store.txt'):
        y.append(i)
    ax.set_ylim(0,300)
    ax.set_xlim(0,5)
    line.set_xdata(display.axis_x)
    line.set_ydata(np.abs(np.fft.fft(y)))
    fig1.canvas.draw()
    fig1.canvas.flush_events()
def button3_press(event):
    global y_base
    global y_bound
    ax.set_ylim(y_base-y_bound, y_base+y_bound)
    fig.canvas.draw()
    fig.canvas.flush_events()
def button4_press(event):
    exit()
def radio_press(label):
    plt.setp(line,color = label)
def slider_updata(val):
     global y_base
     global y_bound
     y_bound = slider1.val
     y_base = slider2.val


#Tkinter
def clickenter():
    global Heart
    Heart = Control_Entry.get()
def Restart():
    global Heart_number
    Heart_number = 0
def setting_ylim():
    global y_max
    global y_min
    y_max = int(Control_ymax.get())
    y_min = int(Control_ymin.get())
    ax.set_ylim(y_min, y_max)
def Reset():
    global y_max
    global y_min
    y_max = 1000
    y_min = 0
def Exit():
    exit()
def onclick(event):
    a=0

#initial
fig, (ax,ax2) = plt.subplots(2,1)
line,  = ax.plot(np.random.randn(100))
line2, = ax2.plot(np.random.randn(100))
plt.show(block = False)
plt.setp(line2,color = 'r')
start = time.time()


#Button_setting
#x,y,lengh,wegh
#button1
Button1_ax = plt.axes([0.1, 0.02, 0.1, 0.03])
Button1 = Button(Button1_ax, 'Store')
Button1.on_clicked(button1_press)
#button2
Button2_ax = plt.axes([0.2, 0.02, 0.1, 0.03])
Button2 = Button(Button2_ax, 'Display')
Button2.on_clicked(button2_press)
#button3
Button3_ax = plt.axes([0.3, 0.02, 0.1, 0.03])
Button3 = Button(Button3_ax, 'Change')
Button3.on_clicked(button3_press)
#button4
Button4_ax = plt.axes([0.4, 0.02, 0.1, 0.03])
Button4 = Button(Button4_ax, 'Exit')
Button4.on_clicked(button4_press)
#radio1
axcolor = 'lightgoldenrodyellow'
Rax = plt.axes([0.01, 0.01, 0.08, 0.06], axisbg=axcolor)
Radio = RadioButtons(Rax, ('Red', 'Blue', 'Green'))
Radio.on_clicked(radio_press)
#slider1
slider1_ax = plt.axes([0.55 , 0.01, 0.3, 0.02], axisbg=axcolor)
slider1 = Slider(slider1_ax, 'Bound', 0.1, 200, valinit=100)
slider1.on_changed(slider_updata)
#slider2
slider2_ax = plt.axes([0.55, 0.03, 0.3, 0.02], axisbg=axcolor)
slider2 = Slider(slider2_ax, 'Base', 0.1, 1000, valinit=500)
slider2.on_changed(slider_updata)
#Tk 
Control = tk.Tk()
Control.title('Control')
#Restart_button
Control_Restart = tk.Button(Control,text = 'Restart',command = Restart)
Control_Restart.grid(column=2,row=1)
#Heart_base number input
Control_Entry = tk.Entry(Control, bd =5)
Control_Entry.grid(column=1,row=0)
Control_Button = tk.Button(Control,text = 'enter',command = clickenter)
Control_Button.grid(column=2,row=0)
#ylim_set
#y_max
Contoal_ymaxlabel =tk.Label(Control, text = 'set_Max')
Contoal_ymaxlabel.grid(column=0,row=3)
Control_ymax = tk.Entry(Control, bd =5)
Control_ymax.grid(column=1,row=3)
Control_set_ylim = tk.Button(Control,text = 'Enter',command = setting_ylim)
Control_set_ylim.grid(column=2,row=3)
#y_min
Contoal_yminlabel =tk.Label(Control, text = 'set_Min')
Contoal_yminlabel.grid(column=0,row=4)
Control_ymin = tk.Entry(Control, bd =5)
Control_ymin.grid(column=1,row=4)
Control_reset = tk.Button(Control,text = 'Reset',command = Reset)
Control_reset.grid(column=2,row=4)
#Exit_Button
Control_Exit = tk.Button(Control,text = 'Exit',command = Exit)
Control_Exit.grid(column=2,row=5)


display = RealtimePlot()
ax.set_ylim(y_min,y_max)
ax2.set_ylim(0,300)



# plot parameters
print ('plotting data...')
# open serial port
strPort='com9'
ser = serial.Serial(strPort, 9600)



def intit():
    line.set_data([],[])
    return line,line2
def animate (i):
    global Heart
    global Heart_number
    data = ser.readline()
    if data > Heart:
        Heart_number = Heart_number+1
    display.add(time.time() - start, data)
    ax.set_xlim(display.axis_x[0], display.axis_x[0] + 5)
    ax.set_ylim(y_min, y_max)
    ax2.set_xlim(display.axis_x[0], display.axis_x[0] + 5)
    line.set_xdata(display.axis_x)
    line.set_ydata(display.axis_y)
    line2.set_xdata(display.axis_x)
    line2.set_ydata(display.axis_z)
    fig.canvas.draw()
    fig.canvas.flush_events()
    heartbeat =tk.Label(Control, text = Heart_number/2)
    heartbeat.grid(column=0,row=0)
    return line,line2
fig.canvas.mpl_connect('button_press_event', onclick)
anim = animation.FuncAnimation(fig,animate,init_func = intit,interval = 1, blit = True)
plt.show()


