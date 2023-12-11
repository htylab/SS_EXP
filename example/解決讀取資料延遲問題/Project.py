import sys
import serial
import time
import qdarkstyle
import heartbeat as hb
import numpy as np
import pyqtgraph as pg
import matplotlib.pyplot as plt
from scipy import signal
from PyQt6 import QtWidgets, uic, QtGui, QtCore


#Calculate Average Heart Beat
class HeartbeatThread(QtCore.QThread):
    update_signal = QtCore.pyqtSignal(float)

    def __init__(self, filtered_data, fs, parent=None):
        super(HeartbeatThread, self).__init__(parent)
        self.filtered_data = filtered_data
        self.fs = fs
        self.running = True
        self.pause = False
        
    def run(self):
        while self.running:
            heart_data = hb.get_data(np.real(self.filtered_data))
            hb.process(heart_data, 0.8, self.fs)
            bpm = hb.measures['bpm']
            if not self.pause:
                self.update_signal.emit(bpm)
            QtCore.QThread.msleep(1000)  
    
    def update_data(self, new_data):
        self.filtered_data = new_data
    
    def start_running(self):
        self.pause = False
    
    def stop_running(self):
        self.pause = True
        
#Read Serial Data        
class SerialReader(QtCore.QThread):
    update_signal = QtCore.pyqtSignal(float)
    
    def __init__(self, parent=None):
        super(SerialReader, self).__init__(parent)
        self.ser = serial.Serial('COM3', 9600)
        self.ser.flush()
        self.running = True
        self.pause = False
        self.read_trash = 0.
    def run(self):
        while self.running:
            if self.ser.inWaiting() > 0:
                if not self.pause:
                    read_data = float(self.ser.readline())
                    self.update_signal.emit(read_data)
                else:
                    read_trash = float(self.ser.readline())
            self.msleep(5)

    
    
    def start_running(self):
        self.pause = False
        self.ser.flushInput()
        
    def stop_running(self):
        self.pause = True


        
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        
        
        #Load UI Page by PyQt6
        uic.loadUi('GUI.ui', self)
        pg.setConfigOptions(antialias=True)
        
        
        #Parameters
        self.fs = 100
        self.duration = 10
        self.samples = self.fs * self.duration
        self.time = np.linspace(0, self.duration, self.samples, endpoint=False)
        self.start_run = False
        
        
        #Original Data
        self.original_data = np.zeros(self.samples)
        self.original_data_time = self.time
        self.position = 0
        
        
        #FIR Parameters
        self.cutoff_low = 2
        self.cutoff_high = 0.8
        self.nyquist = 0.5 * self.fs
        self.width = 16.0
        self.num_taps = int(self.fs / self.nyquist * self.width)
        self.taps_low = signal.firwin(self.num_taps, self.cutoff_low / self.nyquist, window='hamming')
        self.taps_high_b, self.taps_high_a = signal.butter(5, self.cutoff_high / self.nyquist, btype='high', analog=False)
        
        #FIR Response
        self.freq_low, self.response_low = signal.freqz(self.taps_low, worN=8000, fs=self.fs)                
        self.freq_high, self.response_high = signal.freqz(self.taps_high_b, self.taps_high_a, worN=8000, fs=self.fs)
        
        #The Data after FIR
        self.data = signal.lfilter(self.taps_low, 1.0, self.original_data)
        self.data = signal.lfilter(self.taps_high_b, self.taps_high_a, self.data)

        
        #Spectrum
        self.spectrum_data = np.fft.fft(self.data)
        self.spectrum_freq = np.fft.fftfreq(self.samples, 1 / self.fs)
        self.sorted_indices = np.argsort(self.spectrum_freq)
        self.sorted_spectrum_freq = self.spectrum_freq[self.sorted_indices]
        self.sorted_spectrum_data = self.spectrum_data[self.sorted_indices]

        
        #Filtered Data
        self.filtered_data = self.data
        self.filtered_data_time = self.time

        
        #Setup Plots
        self.setup_plots()

        
        #Setup Timer
        self.timer = pg.QtCore.QTimer(self)
        self.timer.timeout.connect(self.update)

        
        #Setup HeartbeatThread
        self.heartbeat_thread = HeartbeatThread(filtered_data=self.filtered_data, fs=self.fs)
        self.heartbeat_thread.update_signal.connect(self.update_heartbeat)

        
        #Setup SerialReaderThread
        self.serial_reader = SerialReader()
        self.serial_reader.update_signal.connect(self.update_data)
        
        
        #Setup Buttons
        self.Start.clicked.connect(self.start_update)
        self.Stop.clicked.connect(self.stop_update)

        
    def setup_plots(self):
        #Setup Original Data Plot
        self.plot_original_data = self.Original_Data.addPlot(title='Original Data')
        self.plot_original_data.setLabel('bottom', 'Time (s)')
        self.plot_original_data.setYRange(-4, 4)
        self.display_original_data = self.plot_original_data.plot(
            self.original_data_time, self.original_data, pen=[255, 0, 255]
        )
        
        
        #Setup FIR Response Plot
        self.plot_fir_response = self.FIR_Response.addPlot(title='FIR Response')
        self.plot_fir_response.setLabel('bottom', 'Frequency (Hz)')
        self.display_fir_response = self.plot_fir_response.plot(
            self.freq_low, abs(self.response_low), pen=[255, 255, 0]
        )
        self.display_fir_response = self.plot_fir_response.plot(
            self.freq_high, abs(self.response_high), pen=[0, 255, 100]
        )
        
        
        #Setup Spectrum Plot
        self.plot_spectrum = self.Spectrum.addPlot(title='Spectrum')
        self.plot_spectrum.setLabel('bottom', 'Frequency (Hz)')
        self.plot_spectrum.setYRange(0, 500)
        self.display_spectrum = self.plot_spectrum.plot(
            self.sorted_spectrum_freq, abs(self.sorted_spectrum_data), pen=[125, 200, 255]
        )
        
        
        #Setup Filtered Data Plot
        self.plot_filtered_data = self.Filtered_Data.addPlot(title='Filtered Data')
        self.plot_filtered_data.setLabel('bottom', 'Time (s)')
        self.plot_filtered_data.setYRange(-4, 4)
        self.display_filtered_data = self.plot_filtered_data.plot(
            self.filtered_data, self.filtered_data, pen=[0, 255, 255]
        )

        
    def start_update(self):
        self.timer.start(10)
        if not self.serial_reader.isRunning():
            self.serial_reader.start()
        if not self.heartbeat_thread.isRunning():
            self.heartbeat_thread.start()
        self.serial_reader.start_running()
        self.heartbeat_thread.start_running()

       
    
    def stop_update(self):
        self.timer.stop()
        self.serial_reader.stop_running()
        self.heartbeat_thread.stop_running()
        
        
    def update_data(self,read_data):
        self.original_data[:-1] = self.original_data[1:]
        self.original_data[-1] = read_data
    
    
    def update_heartbeat(self, bpm):
        self.BPM.setText("Average Heart Beat: %.01f bpm" % bpm)

        
    def update(self):

        original_data_fft = np.fft.fft(self.original_data)
        original_data_fft[0] = 0  # Filter out the DC component
        original_data = np.fft.ifft(original_data_fft)
        self.position += 0.01
        self.display_original_data.setData(self.original_data_time, np.real(original_data))
        self.display_original_data.setPos(self.position, 0)
    
        
        data = signal.lfilter(self.taps_low, 1.0, original_data)
        data = signal.lfilter(self.taps_high_b, self.taps_high_a, data)

        
        spectrum_data = np.fft.fft(data)
        sorted_spectrum_data = spectrum_data[self.sorted_indices]
        self.display_spectrum.setData(self.sorted_spectrum_freq, abs(sorted_spectrum_data))

        
        self.heartbeat_thread.update_data(data)
  

        filtered_data = data
        self.display_filtered_data.setData(self.filtered_data_time, np.real(filtered_data))
        self.display_filtered_data.setPos(self.position, 0)

        

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    ui = MainWindow()
    ui.show()
    sys.exit(app.exec())

