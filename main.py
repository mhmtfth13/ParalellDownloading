import yt_dlp
import concurrent.futures
import os
from typing import List, Tuple
import time
import sys
from threading import Lock

class DownloadManager:
   def __init__(self, total_downloads):
       self.progress_dict = {}
       self.lock = Lock()
       self.total_downloads = total_downloads
       self.first_print = True

   def update_progress(self, filename: str, percent: str, speed: str):
       with self.lock:
           self.progress_dict[filename] = (percent, speed)
           self.display_progress()

   def display_progress(self):
       if self.first_print:
           # İlk yazdırma için normal yazdır
           for filename, (percent, speed) in sorted(self.progress_dict.items()):
               print(f"{filename}: {percent} - {speed}")
           if len(self.progress_dict) == self.total_downloads:
               self.first_print = False
       else:
           # Cursor'u yukarı taşı
           sys.stdout.write(f"\033[{self.total_downloads}A")
           # Her satırı güncelle
           for filename, (percent, speed) in sorted(self.progress_dict.items()):
               sys.stdout.write(f"\r{filename}: {percent} - {speed}".ljust(50) + "\n")
           sys.stdout.flush()

class DownloadProgress:
   def __init__(self, filename, manager):
       self.filename = filename
       self.manager = manager
       self.last_update = 0

   def progress_hook(self, d):
       if d['status'] == 'downloading':
           current_time = time.time()
           if current_time - self.last_update >= 0.5:
               percent = d.get('_percent_str', 'N/A').rjust(6)
               speed = d.get('_speed_str', 'N/A')
               self.manager.update_progress(self.filename, percent, speed)
               self.last_update = current_time

def download_video(video_info: Tuple[str, str], manager: DownloadManager) -> None:
   url, output_filename = video_info
   progress_tracker = DownloadProgress(output_filename, manager)
   
   ydl_opts = {
       'format': 'best',
       'outtmpl': f'{output_filename}.mp4',
       'quiet': True,
       'progress_hooks': [progress_tracker.progress_hook],
       'concurrent_fragment_downloads': 5,  # Azaltıldı
   }
   
   try:
       with yt_dlp.YoutubeDL(ydl_opts) as ydl:
           ydl.download([url])
   except Exception as e:
       manager.update_progress(output_filename, "HATA", str(e))

def parallel_download(video_list: List[Tuple[str, str]], manager: DownloadManager) -> None:
   max_workers = 2  # Worker sayısını azalttık
   with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
       for video_info in video_list:
           time.sleep(10)  # Her indirme arasına 10 saniyelik bekleme ekledik
           executor.submit(download_video, video_info, manager)

# Video listesi
videos_to_download = [
   ("https://drive.google.com/file/d/1Fp6KtxxwM-lZHqElbq7Dw6LuNGpzrY5v/view?usp=sharing", "2Yil2Ay1Gun"),
   ("https://drive.google.com/file/d/1zdzoGm0qWaAptK0scP5Xx3IU7OzcsVP5/view?usp=sharing", "2Yil2Ay2Gun"),
   ("https://drive.google.com/file/d/1494TzoI-FTRtsGqQ3YDkG2vBILQlyOlL/view?usp=sharing", "2Yil3Ay1Gun"),
   ("https://drive.google.com/file/d/1Bl3H53ky42V4rn1mOha2i101xwapOgYv/view?usp=sharing", "2Yil3Ay2Gun"),
   ("https://drive.google.com/file/d/1rPAHNvo0hlvxGIMOSL9ZDqrr8g2moMFR/view?usp=sharing", "2Yil4Ay1Gun"),
   ("https://drive.google.com/file/d/1M0grVv_duuV1_h3R60aY1K752N9ziAto/view?usp=sharing", "2Yil4Ay2Gun"),
   ("https://drive.google.com/file/d/1kFNJ9Q_sdKE0TuvrKGIEOVBYTVtlOpBx/view?usp=sharing", "2Yil5Ay1Gun"),
   ("https://drive.google.com/file/d/1lr8sE76qE2C29EGU5oWXQiSerap15Rkx/view?usp=sharing", "2Yil5Ay2Gun"),
   ("https://drive.google.com/file/d/1aAbmO-40XPLbA7jcOQPQ6hU1C5PxaF8t/view?usp=sharing", "2Yil6Ay2Gun"),
   ("https://drive.google.com/file/d/1TAp4pLgeZJKObmVyrZ7ugh3bwjc4xYG0/view?usp=sharing", "2Yil8Ay1Gun")
]

if __name__ == "__main__":
   try:
       os.makedirs("downloads", exist_ok=True)
       os.chdir("downloads")
       
       print("[BASLA] Indirmeler baslatiliyor...")
       manager = DownloadManager(len(videos_to_download))
       parallel_download(videos_to_download, manager)
       
       print("\n[BITTI] Tum indirmeler tamamlandi!")
       
   except KeyboardInterrupt:
       print("\n[IPTAL] Indirme islemi durduruldu.")
   except Exception as e:
       print(f"\n[HATA] Beklenmeyen hata: {str(e)}")
