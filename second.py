import gdown
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

   def update_progress(self, filename: str, status: str):
       with self.lock:
           self.progress_dict[filename] = status
           self.display_progress()

   def display_progress(self):
       if self.first_print:
           for filename, status in sorted(self.progress_dict.items()):
               print(f"{filename}: {status}")
           if len(self.progress_dict) == self.total_downloads:
               self.first_print = False
       else:
           sys.stdout.write(f"\033[{self.total_downloads}A")
           for filename, status in sorted(self.progress_dict.items()):
               sys.stdout.write(f"\r{filename}: {status}".ljust(50) + "\n")
           sys.stdout.flush()

def get_file_id(url: str) -> str:
   """Google Drive URL'inden file ID'yi çıkarır"""
   file_id = url.split('/')[5]
   return file_id

def download_video(video_info: Tuple[str, str], manager: DownloadManager) -> None:
   url, output_filename = video_info
   file_id = get_file_id(url)
   output_path = f'downloads/{output_filename}.mp4'
   
   try:
       manager.update_progress(output_filename, "Indiriliyor...")
       gdown.download(
           f"https://drive.google.com/uc?id={file_id}",
           output_path,
           quiet=True
       )
       manager.update_progress(output_filename, "Tamamlandi")
   except Exception as e:
       manager.update_progress(output_filename, f"Hata: {str(e)}")

def parallel_download(video_list: List[Tuple[str, str]], manager: DownloadManager) -> None:
   max_workers = 2
   with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
       for video_info in video_list:
           time.sleep(15)  # Bekleme süresini 15 saniyeye çıkardık
           executor.submit(download_video, video_info, manager)

# Video listesi
videos_to_download = [
   # 2. YIL 2. AY
   ("https://drive.google.com/file/d/1Fp6KtxxwM-lZHqElbq7Dw6LuNGpzrY5v/view?usp=sharing", "2Yil2Ay1Gun"),
   ("https://drive.google.com/file/d/1zdzoGm0qWaAptK0scP5Xx3IU7OzcsVP5/view?usp=sharing", "2Yil2Ay2Gun"),
   
   # 2. YIL 3. AY
   ("https://drive.google.com/file/d/1494TzoI-FTRtsGqQ3YDkG2vBILQlyOlL/view?usp=sharing", "2Yil3Ay1Gun"),
   ("https://drive.google.com/file/d/1Bl3H53ky42V4rn1mOha2i101xwapOgYv/view?usp=sharing", "2Yil3Ay2Gun"),
   
   # 2. YIL 4. AY
   ("https://drive.google.com/file/d/1rPAHNvo0hlvxGIMOSL9ZDqrr8g2moMFR/view?usp=sharing", "2Yil4Ay1Gun"),
   ("https://drive.google.com/file/d/1M0grVv_duuV1_h3R60aY1K752N9ziAto/view?usp=sharing", "2Yil4Ay2Gun"),
   
   # 2. YIL 5. AY
   ("https://drive.google.com/file/d/1kFNJ9Q_sdKE0TuvrKGIEOVBYTVtlOpBx/view?usp=sharing", "2Yil5Ay1Gun"),
   ("https://drive.google.com/file/d/1lr8sE76qE2C29EGU5oWXQiSerap15Rkx/view?usp=sharing", "2Yil5Ay2Gun"),
   
   # 2. YIL 6. AY
   ("https://drive.google.com/file/d/1aAbmO-40XPLbA7jcOQPQ6hU1C5PxaF8t/view?usp=sharing", "2Yil6Ay2Gun"),
   
   # 2. YIL 8. AY
   ("https://drive.google.com/file/d/1TAp4pLgeZJKObmVyrZ7ugh3bwjc4xYG0/view?usp=sharing", "2Yil8Ay1Gun")
]

if __name__ == "__main__":
   try:
       os.makedirs("downloads", exist_ok=True)
       
       print("[BASLA] Indirmeler baslatiliyor...")
       start_time = time.time()
       
       manager = DownloadManager(len(videos_to_download))
       parallel_download(videos_to_download, manager)
       
       end_time = time.time()
       duration = end_time - start_time
       print(f"\n[BITTI] Toplam sure: {duration:.2f} saniye")
       
   except KeyboardInterrupt:
       print("\n[IPTAL] Indirme islemi durduruldu.")
   except Exception as e:
       print(f"\n[HATA] Beklenmeyen hata: {str(e)}")
