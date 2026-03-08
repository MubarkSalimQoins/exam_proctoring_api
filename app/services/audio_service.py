# import sounddevice as sd
# import numpy as np


# class AudioService:

#     def _init_(self):

#         # مستوى الصوت المسموح
#         self.noise_threshold = 0.08

#         # مدة التسجيل (ثانية)
#         self.duration = 1

#         # معدل العينة
#         self.sample_rate = 16000


#     def detect_noise(self):

#         try:

#             # تسجيل الصوت من الميكروفون
#             recording = sd.rec(
#                 int(self.duration * self.sample_rate),
#                 samplerate=self.sample_rate,
#                 channels=1
#             )

#             sd.wait()

#             # حساب مستوى الصوت
#             volume = np.linalg.norm(recording) / len(recording)

#             # إذا الصوت مرتفع
#             if volume > self.noise_threshold:

#                 return {
#                     "cheating_type_id": 6,
#                     "type_ar": "ضوضاء أو صوت مرتفع",
#                     "type_en": "Loud Noise",
#                     "confidence": float(volume)
#                 }

#             return None

#         except Exception as e:

#             print("Audio Error:", e)

#             return None
# -------------------------------------------------
import sounddevice as sd
import numpy as np
import threading
import time


class AudioService:

    def __init__(self):

        self.sample_rate = 16000
        self.duration = 1
        self.noise_threshold = 0.0008

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
            