import pyaudio
import wave
from threading import Thread, Lock
import glob

SAMPWIDTH_INDEX = 0
NCHANNELS_INDEX = 1
FRAMERATE_INDEX = 2
DATA_INDEX = 3

class Sound_manager:


    def __init__(self):
        self._sound_cache = {}
        self._cache_lock = Lock()
        self._destroy = False
        self._device = 0

        self._cache_sound()
        self._device_check()


    def setDevice(self, index):
        self._device = index
        print('device change to', self._device)

    def _device_check(self):
        p = pyaudio.PyAudio()
        device_list = []
        
        for i in range(p.get_device_count()):
            dev = p.get_device_info_by_index(i)
            # Almacenar solo dispositivos con canales de entrada disponibles
            #if dev['maxInputChannels'] > 0:
                #device_list.append(dev['name'])
            device_list.append(dev['name'])

        k = pyaudio.PyAudio()
        for i in range(k.get_device_count()):
            info = k.get_device_info_by_index(i)
            print(f"Device {i}: {info['name']}")

        p.terminate()
        return device_list



    def shoot_sound(self):
        sound_file = 'sounds/shoot.wav'
        self.play_sound(sound_file)

    def target_sound(self):
        sound_file = 'sounds/metal_clang.wav'
        self.play_sound(sound_file)


    def _cache_sound(self):
        wavs = glob.glob("sounds/*.wav")
        
        for wav in wavs:
            self._add_wav_cache(wav)
            print(wav)

    def play_sound(self, sound_file):
        # if we don't do this on a nother thread we have to wait until
        # the message has finished being communicated to do anything
        # (i.e. shootoff freezes)  
        self._play_sound_thread = Thread(target=self._play_sound, 
            args=(sound_file,), name="play_sound_thread")
        self._play_sound_thread.start()  

    def _play_sound(self, *args):
        if self._destroy:
            return

        sound_file = args[0]  
        if sound_file not in self._sound_cache:
            pass
            #self._add_wav_cache(sound_file)

        try:
            # initialize the sound file and stream  
            p = pyaudio.PyAudio()  
            stream = p.open(format=p.get_format_from_width(self._sound_cache[sound_file][SAMPWIDTH_INDEX]),
                            channels=self._sound_cache[sound_file][NCHANNELS_INDEX],
                            rate=self._sound_cache[sound_file][FRAMERATE_INDEX],
                            output=True,
                            output_device_index=self._device,
                            frames_per_buffer=1024 )
            
            # play the sound file
            for data in self._sound_cache[sound_file][DATA_INDEX]:
                if self._destroy:
                    break
                stream.write(data) 

            # clean up
            stream.stop_stream()  
            stream.close()  
            p.terminate() 
        except IOError as e:
            print(f"Error al abrir el stream: {e}")
            return
        except Exception as e:
            print(f"Se produjo un error inesperado: {e}")
             

    def _add_wav_cache(self, sound_file):
        chunk = 1024
        f = wave.open(sound_file, "rb")

        self._sound_cache[sound_file] = (
            f.getsampwidth(), 
            f.getnchannels(), 
            f.getframerate(), 
            []
        )

        data = f.readframes(chunk)
        while data != b'':  # Comparar con b''
            self._sound_cache[sound_file][DATA_INDEX].append(data)
            data = f.readframes(chunk)
        
        f.close()  # Cerrar el archivo al final
        
    def _add_wav_cache2(self, sound_file):
        chunk = 1024
        
        f = wave.open(sound_file,"rb")
        
        self._sound_cache[sound_file] = (f.getsampwidth(), f.getnchannels(), 
            f.getframerate(), [])

        data = f.readframes(chunk)   
        while data != '':  
            self._sound_cache[sound_file][DATA_INDEX].append(data)
            data = f.readframes(chunk) 