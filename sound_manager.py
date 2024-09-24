import pygame
import glob
from threading import Lock

class Sound_manager:
    def __init__(self):
        pygame.mixer.init()  # Inicializa el sistema de audio de pygame
        self._sound_cache = {}
        self._cache_lock = Lock()
        
        self._cache_sound()

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
            print(f"Cached {wav}")

    def play_sound(self, sound_file):
        if sound_file in self._sound_cache:
            sound = self._sound_cache[sound_file]
            sound.play()
        else:
            print(f"El sonido {sound_file} no está en caché.")

    def _add_wav_cache(self, sound_file):
        sound = pygame.mixer.Sound(sound_file)  # Cargar el archivo de sonido
        with self._cache_lock:
            self._sound_cache[sound_file] = sound  # Guardar el sonido en la caché

    def stop_all_sounds(self):
        pygame.mixer.stop()  # Detiene todos los sonidos que estén reproduciéndose
