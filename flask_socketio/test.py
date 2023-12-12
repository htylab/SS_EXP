from flask import Flask, render_template
from flask_socketio import SocketIO
from collections import deque
import serial
import time
import numpy as np
from scipy.signal import butter, lfilter

async_mode = None
thread = None

app = Flask(__name__)
socketio = SocketIO (app, async_mode = async_mode)

class Data:
    def __init__(self, max_entries=5):
        self.axis_x = deque(maxlen=max_entries)
        self.axis_y = deque(maxlen=max_entries)

    def add(self, x, y):
        self.axis_x.append(x)
        self.axis_y.append(y)
        
def butter_lowpass_filter(data, cutoff_freq, sampling_freq, order=4):
    nyquist = 0.5 * sampling_freq
    normal_cutoff = cutoff_freq / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    y = lfilter(b, a, data)
    return y

def label_peaks(lamb,waveform):
    nz=[]
    peaks = np.ones(waveform.shape).astype(np.bool_)
    for i in range(1,lamb):
        peaks = (waveform >= np.roll(waveform, i)) & (waveform >= np.roll(waveform, -i)) & peaks
    for j in range(len(peaks)):
        if peaks[j] != False:
            nz.append(j)
    nzp=np.array(nz)
    return peaks.astype(np.int16).tolist(),np.mean(np.diff(nzp))

heart = Data(500)
out = Data(400)

def background_thread():
    strPort='com3'
    ser = serial.Serial(strPort, 115200)
    ser.flush()
    start = time.time()
    while True :
        # socketio.sleep(0.5)
        for ii in range(10):
            try:
                data = float(ser.readline())
                heart.add(time.time() - start, data)
                out.add(time.time() - start, data)
            except:
                pass
        if len(heart.axis_x)>=500:
            fs=1/(np.mean(np.diff(heart.axis_x)))
            y2 = np.fft.fft(heart.axis_y)
            x2 = np.fft.fftfreq(y2.size, d=1/fs)

            filtered_data = butter_lowpass_filter(heart.axis_y, 3, fs)
            
            ft = np.fft.fft(filtered_data[101:501])
            x3 = np.fft.fftfreq(ft.size, d=1/fs)

            y3 = ft.copy()
            y3[0] = 0
            output = np.fft.ifft(y3)
            
            y4=abs(output)*100
            peaks,hr=label_peaks(50,y4)
            heart_rate=round(hr/fs*60,1)
            
            time_1 = list(heart.axis_x)
            time_2 = [round(num, 1) for num in time_1]
            x2_1 = list(x2)
            x2_2 = [round(num, 1) for num in x2_1]
            x3_1 = list(x3)
            x3_2 = [round(num, 1) for num in x3_1]
            socketio.emit('update_data', {'time':time_2, 'heartin':list(heart.axis_y),'peaks': peaks,'hr': heart_rate, 'x2':list(x2_2), 'y2':list(abs(y2)), 'x3':list(x3_2), 'y3':list(abs(y3)), 'x4':time_2[101:501], 'y4':list(abs(y4))})
            

@app.route("/")
def index():
    return render_template('index.html', async_mode = socketio.async_mode)

@socketio.on('connect')
def connect():
    global  thread
    if thread is None:
        thread = socketio.start_background_task(target=background_thread)

if __name__ == '__main__':
    app.run(debug=True)