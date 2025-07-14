import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from tqdm import tqdm
import tkinter as tk
from tkinter import simpledialog, messagebox
import subprocess

def get_folder_name_from_url(url):
    parsed_url = urlparse(url)
    path = parsed_url.path
    folder_name = path.split('/download/')[1].replace('.html', '')
    return folder_name

def download_all_chapters(manga_page_url, cookies, start=1, end=None):
    manga_name = get_folder_name_from_url(manga_page_url)
    save_dir = os.path.join(os.getcwd(), manga_name)
    os.makedirs(save_dir, exist_ok=True)

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": manga_page_url,
        "Origin": "https://im.manga-chan.me",
    }

    response = requests.get(manga_page_url, cookies=cookies, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    download_links = []

    for a in soup.find_all("a", href=True):
        if "/engine/download.php?id=" in a["href"]:
            download_links.append(urljoin(manga_page_url, a["href"]))

    total_chapters = len(download_links)
    download_links = list(reversed(download_links))

    if end is None:
        end = total_chapters

    start_idx = (start - 1) if start else 0
    end_idx = end if end else len(download_links)
    selected_links = download_links[start_idx:end_idx]

    for index, link in enumerate(selected_links, start=start):
        try:
            res = requests.get(link, cookies=cookies, headers=headers, allow_redirects=False)
            real_url = res.headers.get("Location")

            if not real_url:
                print(f"⚠️ Пропуск главы {index}")
                continue

            extension = os.path.splitext(real_url.split("?")[0])[1]
            new_filename = f"{index}{extension}"
            filepath = os.path.join(save_dir, new_filename)

            r = requests.get(real_url, stream=True, cookies=cookies, headers=headers)
            total_size = int(r.headers.get('content-length', 0))
            chunk_size = 8192

            with open(filepath, "wb") as f, tqdm(
                desc=f"Глава {index}",
                total=total_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024
            ) as bar:
                for chunk in r.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        bar.update(len(chunk))

            print(f"✓ Глава {index} сохранена")

        except Exception as e:
            print(f"- Ошибка при скачивании главы {index}: {e}")

    return save_dir

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    url = simpledialog.askstring("Ссылка", "Введите ссылку на страницу манги:")
    if not url:
        messagebox.showerror("Ошибка", "URL обязателен!")
        exit(1)

    cookies_input = simpledialog.askstring("PHPSESSID", "Введите PHPSESSID (или оставьте пустым):")
    start = simpledialog.askinteger("Начало", "С какой главы начать?", initialvalue=1)
    end = simpledialog.askinteger("Конец", "На какой главе закончить?", initialvalue=None)

    cookies = None
    if cookies_input:
        cookies = {
            "PHPSESSID": cookies_input.strip(),
            "dle_user_id": "1234529",
            "dle_password": "8b7771b3b58820fde60f6496f1558529",
            "dle_newpm": "0"
        }

    save_path = download_all_chapters(url, cookies, start, end)

    converter_script = os.path.join(os.getcwd(), "Converter_avif_jpg.bat")

    subprocess.run([converter_script], cwd=save_path, shell=True)

    messagebox.showinfo("Готово", "Скачивание и конвертация завершены!")
