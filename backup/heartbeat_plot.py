# -*- coding: utf-8 -*-
"""
Created on Mon Nov 09 12:58:58 2015

@author: clark
"""
import sys, serial
import numpy as np
from time import sleep
from collections import deque
from matplotlib import pyplot as plt


# class that holds analog data for N samples
class AnalogData:

  # constr
  def __init__(self, maxLen):
    self.ax = deque([0.0]*maxLen)
    self.ay = deque([0.0]*maxLen)
    self.maxLen = maxLen

  # ring buffer
  def addToBuf(self, buf, val):
    if len(buf) < self.maxLen:
      buf.append(val)
    else:
      buf.pop()
      buf.appendleft(val)

  # add data
  def add(self, data):
    assert(len(data) == 1)
    self.addToBuf(self.ax, data[0])
    

    
# plot class
class AnalogPlot:
  count = 0  
  # constr
  def __init__(self, analogData):
    # set plot to animated
    plt.ion() 
    self.axline, = plt.plot(analogData.ax)
    
    plt.ylim([np.min(list(analogData.ax)[0:200]), np.max(list(analogData.ax)[0:200])])
    #plt.ylim([-500, 2023])

  # update plot
  def update(self, analogData):

    #print("min %s" % np.min(analogData.ax))
    self.count +=1
    if self.count % 5 == 0 :
      
      self.axline.set_ydata(analogData.ax)
      
      plt.ylim([np.min(list(analogData.ax)[0:500])-10, np.max(list(analogData.ax)[0:500])+10])
      
      plt.draw()

# main() function
def main():
# expects 1 arg - serial port string
#  if(len(sys.argv) != 2):
#    print 'Example usage: python showdata.py "/dev/tty.usbmodem411"'
#    exit(1)

 #strPort = '/dev/tty.usbserial-A7006Yqh'
  #strPort = sys.argv[1];
  strPort='com3'
  # plot parameters
  analogData = AnalogData(1000)
  analogPlot = AnalogPlot(analogData)

  print ('plotting data...')

  # open serial port
  ser = serial.Serial(strPort, 115200)
  print (ser)
  while True:
    try:
      line = ser.readline()
      #print(line)
      '''
      hp = np.roll(hp, 1)
      hp[0] = float(line)
      print(np.mean(hp))
      '''
      for val in line.split():
          #print (float(val))
          
          data = [float(val)]
      
          #print (data)
      
      if(len(data) == 1):
        analogData.add(data)
        analogPlot.update(analogData)
    except KeyboardInterrupt:
      print ('exiting')
      break
  # close serial
  ser.flush()
  ser.close()

# call main
if __name__ == '__main__':
  main()