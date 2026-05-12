# import sounddevice as sd
# import numpy as np
# import threading
# import time


# class AudioService:

#     def __init__(self):

#         self.sample_rate = 16000
#         self.duration = 1

#         # تم تخفيض العتبة لتكون واقعية أكثر
#         self.noise_threshold = 0.08

#         self.running = False
#         self.last_event = None

#         self.thread = None

#         # 🔴 تحديد المايك الصحيح (Cirrus Logic WASAPI)
#         self.device = 9


#     def start(self):

#         self.running = True

#         self.thread = threading.Thread(target=self._monitor_audio)
#         self.thread.daemon = True
#         self.thread.start()

#         print("🎤 تم تشغيل مراقبة الصوت")


#     def stop(self):

#         self.running = False

#         if self.thread:
#             self.thread.join()


#     def _monitor_audio(self):

#         while self.running:

#             try:

#                 recording = sd.rec(
#                     int(self.duration * self.sample_rate),
#                     samplerate=None
#                     channels=1,
#                     device=self.device
#                 )

#                 sd.wait()

#                 volume = np.linalg.norm(recording) / len(recording)
#                 print("volume:", volume)

#                 if volume > self.noise_threshold:

#                     self.last_event = {
#                         "cheating_type_id": 6,
#                         "type_ar": "ضوضاء أو صوت مرتفع",
#                         "type_en": "Loud Noise",
#                         "confidence": float(volume)
#                     }

#                     print("🚨 صوت مرتفع مكتشف")

#                 else:
#                     self.last_event = None

#             except Exception as e:
#                 print("Audio Error:", e)

#             time.sleep(0.2)


#     def detect_noise(self):
#     return self.last_event
# # -------------------------------------------------
import sounddevice as sd
import numpy as np
import threading
import time


class AudioService:

    def __init__(self):

        self.sample_rate = 16000
        self.duration = 1
        self.noise_threshold = 0.0008
        # self.noise_threshold = 0.8

        self.running = False
        self.last_event = None

        self.thread = None


    def start(self):

        self.running = True

        self.thread = threading.Thread(target=self._monitor_audio)
        self.thread.daemon = True
        self.thread.start()

        print("🎤 تم تشغيل مراقبة الصوت")


    def stop(self):

        self.running = False

        if self.thread:
            self.thread.join()


    def _monitor_audio(self):

        while self.running:

            try:

                recording = sd.rec(
                    int(self.duration * self.sample_rate),
                    samplerate=self.sample_rate,
                    channels=1
                )

                sd.wait()

                volume = np.linalg.norm(recording) / len(recording)
                print("volume:", volume)

                if volume > self.noise_threshold:

                    self.last_event = {
                        "cheating_type_id": 6,
                        "type_ar": "ضوضاء أو صوت مرتفع",
                        "type_en": "Loud Noise",
                        "confidence": float(volume)
                    }

                    print("🚨 صوت مرتفع مكتشف")

                else:

                    self.last_event = None

            except Exception as e:

                print("Audio Error:", e)

            time.sleep(0.2)


    def detect_noise(self):

        return self.last_event
            






# class AudioService:

#     def __init__(self):
#         print("🎤 AudioService Disabled (Test Mode)")
#         self.last_event = None

#     def start(self):
#         print("🎤 الصوت معطّل حالياً (Test Mode)")

#     def stop(self):
#         pass

#     def detect_noise(self):
#         return None