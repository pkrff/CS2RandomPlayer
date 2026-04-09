import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import pytesseract
import random
import os
import sys
import re

# --- Настройка пути к Tesseract для работы внутри EXE ---
def resource_path(relative_path):
    """ Получает абсолютный путь к ресурсу, работает и для dev, и для PyInstaller. """
    try:
        # PyInstaller создает временную папку и хранит путь в _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Указываем pytesseract, где искать tesseract.exe
tesseract_path = resource_path(os.path.join('Tesseract-OCR', 'tesseract.exe'))
pytesseract.pytesseract.tesseract_cmd = tesseract_path

# --- Основной класс приложения ---
class CS2RandomPlayerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CS2 Random Player (Портативная версия)")
        self.root.geometry("700x700")
        self.root.resizable(True, True)

        self.image_path = None
        self.photo = None
        self.players = []

        self.create_widgets()

    def create_widgets(self):
        # --- Элементы интерфейса ---
        title = tk.Label(self.root, text="CS2 Random Player", font=("Arial", 16, "bold"))
        title.pack(pady=10)

        # Кнопка загрузки
        frame_load = tk.Frame(self.root)
        frame_load.pack(pady=5)
        btn_load = tk.Button(frame_load, text="Загрузить скриншот", command=self.load_image,
                             font=("Arial", 12), bg="#4CAF50", fg="white", padx=10, pady=5)
        btn_load.pack()
        self.lbl_image_status = tk.Label(frame_load, text="Изображение не загружено", fg="gray")
        self.lbl_image_status.pack(pady=5)

        # Превью
        self.lbl_preview = tk.Label(self.root, text="Предпросмотр:", font=("Arial", 10))
        self.lbl_preview.pack(anchor="w", padx=20)
        self.canvas_preview = tk.Canvas(self.root, width=300, height=200, bg="#f0f0f0", relief=tk.SUNKEN, bd=2)
        self.canvas_preview.pack(pady=5)

        # Список игроков
        lbl_players = tk.Label(self.root, text="Распознанные игроки (можно редактировать):", font=("Arial", 10))
        lbl_players.pack(anchor="w", padx=20, pady=(10,0))
        frame_list = tk.Frame(self.root)
        frame_list.pack(pady=5)
        scrollbar = tk.Scrollbar(frame_list)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox_players = tk.Listbox(frame_list, width=40, height=8,
                                          yscrollcommand=scrollbar.set,
                                          font=("Courier", 10))
        self.listbox_players.pack(side=tk.LEFT, fill=tk.BOTH)
        scrollbar.config(command=self.listbox_players.yview)

        # Кнопки управления списком
        frame_btns = tk.Frame(self.root)
        frame_btns.pack(pady=5)
        btn_confirm = tk.Button(frame_btns, text="Подтвердить список", command=self.confirm_players,
                                bg="#2196F3", fg="white", padx=10)
        btn_confirm.pack(side=tk.LEFT, padx=5)
        btn_add = tk.Button(frame_btns, text="Добавить игрока", command=self.add_player_manually)
        btn_add.pack(side=tk.LEFT, padx=5)

        # Настройки команд
        frame_settings = tk.Frame(self.root)
        frame_settings.pack(pady=10)
        lbl_teams = tk.Label(frame_settings, text="Количество команд:", font=("Arial", 10))
        lbl_teams.pack(side=tk.LEFT, padx=5)
        self.spin_teams = tk.Spinbox(frame_settings, from_=2, to=10, width=5, font=("Arial", 10))
        self.spin_teams.pack(side=tk.LEFT, padx=5)
        self.spin_teams.delete(0, tk.END)
        self.spin_teams.insert(0, "2")
        btn_shuffle = tk.Button(frame_settings, text="Перемешать!", command=self.shuffle_and_distribute,
                                bg="#FF9800", fg="white", font=("Arial", 10, "bold"), padx=10)
        btn_shuffle.pack(side=tk.LEFT, padx=10)

        # Результат
        lbl_result = tk.Label(self.root, text="Результат:", font=("Arial", 10))
        lbl_result.pack(anchor="w", padx=20, pady=(10,0))
        self.text_result = tk.Text(self.root, height=12, width=70, font=("Courier", 10))
        self.text_result.pack(padx=20, pady=5)
        self.status = tk.Label(self.root, text="Готов", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    # --- Логика работы (OCR, распределение) ---
    def load_image(self):
        # ... (логика загрузки, OCR, отображения в listbox остается без изменений, как в прошлом ответе) ...
        file_path = filedialog.askopenfilename(title="Выберите скриншот лобби CS2", filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")])
        if not file_path: return
        self.image_path = file_path
        self.lbl_image_status.config(text=os.path.basename(file_path), fg="black")
        self.status.config(text="Изображение загружено. Распознавание...")
        self.root.update()
        img = Image.open(file_path)
        img.thumbnail((300, 200))
        self.photo = ImageTk.PhotoImage(img)
        self.canvas_preview.create_image(150, 100, image=self.photo, anchor=tk.CENTER)
        try:
            img_ocr = Image.open(file_path).convert('L')
            width, height = img_ocr.size
            img_ocr = img_ocr.resize((width*2, height*2), Image.Resampling.LANCZOS)
            text = pytesseract.image_to_string(img_ocr, lang='eng', config='--psm 6')
            lines = text.split('\n')
            self.players = []
            for line in lines:
                line = line.strip()
                if not line: continue
                if any(skip in line.lower() for skip in ['invite', 'searching', 'looking', 'connect', 'play', 'friend']): continue
                if re.match(r'^[\w\s\-_.\[\]\(\)]+$', line) and 3 <= len(line) <= 32: self.players.append(line)
            self.players = list(dict.fromkeys(self.players))
            self.listbox_players.delete(0, tk.END)
            for p in self.players: self.listbox_players.insert(tk.END, p)
            self.status.config(text=f"Распознано {len(self.players)} игроков. Проверьте список.")
            if not self.players: messagebox.showinfo("Информация", "Не удалось распознать ни одного игрока. Попробуйте другой скриншот или добавьте вручную.")
        except Exception as e:
            messagebox.showerror("Ошибка распознавания", str(e))
            self.status.config(text="Ошибка распознавания")

    def confirm_players(self):
        self.players = list(self.listbox_players.get(0, tk.END))
        self.players = [p.strip() for p in self.players if p.strip()]
        self.listbox_players.delete(0, tk.END)
        for p in self.players: self.listbox_players.insert(tk.END, p)
        self.status.config(text=f"Список подтверждён: {len(self.players)} игроков.")
        messagebox.showinfo("Готово", "Список игроков подтверждён.")

    def add_player_manually(self):
        # ... (логика добавления игрока остается без изменений) ...
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить игрока")
        dialog.geometry("300x120")
        tk.Label(dialog, text="Введите никнейм:").pack(pady=10)
        entry = tk.Entry(dialog, width=30)
        entry.pack(pady=5)
        entry.focus()
        def add():
            name = entry.get().strip()
            if name:
                self.listbox_players.insert(tk.END, name)
                dialog.destroy()
            else:
                messagebox.showwarning("Внимание", "Имя не может быть пустым.")
        btn_ok = tk.Button(dialog, text="Добавить", command=add, bg="#4CAF50", fg="white")
        btn_ok.pack(pady=5)

    def shuffle_and_distribute(self):
        # ... (логика распределения остается без изменений) ...
        players = list(self.listbox_players.get(0, tk.END))
        players = [p.strip() for p in players if p.strip()]
        if not players:
            messagebox.showwarning("Внимание", "Список игроков пуст.")
            return
        try: num_teams = int(self.spin_teams.get())
        except ValueError: num_teams = 2
        if num_teams < 2: num_teams = 2
        shuffled = players[:]
        random.shuffle(shuffled)
        teams = [[] for _ in range(num_teams)]
        for i, player in enumerate(shuffled):
            teams[i % num_teams].append(player)
        self.text_result.delete(1.0, tk.END)
        for idx, team in enumerate(teams, 1):
            self.text_result.insert(tk.END, f"Команда {idx} ({len(team)} игроков):\n")
            for p in team:
                self.text_result.insert(tk.END, f"  - {p}\n")
            self.text_result.insert(tk.END, "\n")
        self.status.config(text=f"Распределено {len(players)} игроков на {num_teams} команд.")


if __name__ == "__main__":
    root = tk.Tk()
    app = CS2RandomPlayerApp(root)
    root.mainloop()