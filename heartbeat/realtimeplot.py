import time, random
import math
from collections import deque
from matplotlib import pyplot as plt
start = time.time()
def onclick(event):
    exit()

class RealtimePlot:
    def __init__(self, max_entries = 500):
        fig, axes1 = plt.subplots()
        self.axis_x = deque(maxlen=max_entries)
        self.axis_y = deque(maxlen=max_entries)
        self.axes = axes1
        self.max_entries = max_entries
        self.lineplot, = self.axes.plot([], [], "b-")
        self.axes.set_ylim(0,100)
        fig.canvas.mpl_connect('button_press_event', onclick)
        #self.axes.set_autoscaley_on(True)

    def add(self, x, y):
        self.axis_x.append(x)
        self.axis_y.append(y)
        self.lineplot.set_data(self.axis_x, self.axis_y)
        self.axes.set_xlim(self.axis_x[0], self.axis_x[0] + 15)
        #self.axes.relim(); self.axes.autoscale_view() # rescale the y-axis


def main():
    display = RealtimePlot()
    while True:
        display.add(time.time() - start, random.random() * 100)
        plt.pause(0.001)

if __name__ == "__main__": main()
