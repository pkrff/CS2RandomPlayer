import tkinter as tk
from tkinter import messagebox
import webbrowser
import random
import re

class CS2RandomPlayerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CS2 Random Player (Yandex OCR)")
        self.root.geometry("700x700")
        self.root.resizable(True, True)

        self.players = []
        self.create_widgets()

    def create_widgets(self):
        # Заголовок
        title = tk.Label(self.root, text="CS2 Random Player", font=("Arial", 16, "bold"))
        title.pack(pady=10)

        # Инструкция
        instr = tk.Label(self.root, 
                         text="1. Нажмите «Открыть Яндекс.Картинки» → загрузите скриншот → скопируйте текст.\n"
                              "2. Вставьте скопированный текст в поле ниже.\n"
                              "3. Нажмите «Разобрать список» → проверьте игроков.\n"
                              "4. Выберите количество команд и нажмите «Перемешать».",
                         font=("Arial", 10), justify=tk.LEFT)
        instr.pack(pady=10)

        # Кнопка открытия Яндекс.Картинок (OCR)
        btn_yandex = tk.Button(self.root, text="🌐 Открыть Яндекс.Картинки (OCR)",
                               command=self.open_yandex_ocr,
                               font=("Arial", 12), bg="#FFCC00", fg="black", padx=10, pady=5)
        btn_yandex.pack(pady=5)

        # Поле для вставки текста
        lbl_paste = tk.Label(self.root, text="Вставьте скопированный текст сюда:", font=("Arial", 10))
        lbl_paste.pack(anchor="w", padx=20, pady=(10,0))

        self.text_input = tk.Text(self.root, height=6, width=70, font=("Courier", 10))
        self.text_input.pack(padx=20, pady=5)

        # Кнопка разбора текста
        btn_parse = tk.Button(self.root, text="📋 Разобрать список",
                              command=self.parse_text,
                              bg="#2196F3", fg="white", padx=10, pady=5)
        btn_parse.pack(pady=5)

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

        btn_confirm = tk.Button(frame_btns, text="✅ Подтвердить список", command=self.confirm_players,
                                bg="#4CAF50", fg="white", padx=10)
        btn_confirm.pack(side=tk.LEFT, padx=5)

        btn_add = tk.Button(frame_btns, text="➕ Добавить игрока", command=self.add_player_manually)
        btn_add.pack(side=tk.LEFT, padx=5)

        btn_delete = tk.Button(frame_btns, text="❌ Удалить выбранного", command=self.delete_selected)
        btn_delete.pack(side=tk.LEFT, padx=5)

        # Настройки команд
        frame_settings = tk.Frame(self.root)
        frame_settings.pack(pady=10)

        lbl_teams = tk.Label(frame_settings, text="Количество команд:", font=("Arial", 10))
        lbl_teams.pack(side=tk.LEFT, padx=5)

        self.spin_teams = tk.Spinbox(frame_settings, from_=2, to=10, width=5, font=("Arial", 10))
        self.spin_teams.pack(side=tk.LEFT, padx=5)
        self.spin_teams.delete(0, tk.END)
        self.spin_teams.insert(0, "2")

        btn_shuffle = tk.Button(frame_settings, text="🎲 Перемешать и распределить",
                                command=self.shuffle_and_distribute,
                                bg="#FF9800", fg="white", font=("Arial", 10, "bold"), padx=10)
        btn_shuffle.pack(side=tk.LEFT, padx=10)

        # Результат
        lbl_result = tk.Label(self.root, text="Результат распределения:", font=("Arial", 10))
        lbl_result.pack(anchor="w", padx=20, pady=(10,0))

        self.text_result = tk.Text(self.root, height=12, width=70, font=("Courier", 10))
        self.text_result.pack(padx=20, pady=5)

        # Статус-бар
        self.status = tk.Label(self.root, text="Готов", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    def open_yandex_ocr(self):
        """Открывает Яндекс.Картинки с функцией распознавания текста."""
        url = "https://translate.yandex.ru/ocr"
        webbrowser.open(url)
        self.status.config(text="Яндекс.Картинки открыты в браузере. Загрузите скриншот и скопируйте текст.")

    def parse_text(self):
        """Разбирает вставленный текст и извлекает никнеймы."""
        raw_text = self.text_input.get("1.0", tk.END)
        lines = raw_text.split('\n')
        players = []

        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Игнорируем типичные системные надписи
            if any(skip in line.lower() for skip in
                   ['invite', 'searching', 'looking', 'connect', 'play', 'friend', 'queue', 'leader']):
                continue
            # Допустимые символы в никах
            if re.match(r'^[\w\s\-_.\[\]\(\)]+$', line) and 3 <= len(line) <= 32:
                players.append(line)

        # Удаляем дубликаты
        players = list(dict.fromkeys(players))

        # Обновляем Listbox
        self.listbox_players.delete(0, tk.END)
        for p in players:
            self.listbox_players.insert(tk.END, p)

        self.status.config(text=f"Извлечено {len(players)} игроков. Проверьте список.")
        if not players:
            messagebox.showinfo("Информация", "Не найдено подходящих строк. Проверьте формат текста.")

    def confirm_players(self):
        """Фиксирует список."""
        self.players = list(self.listbox_players.get(0, tk.END))
        self.players = [p.strip() for p in self.players if p.strip()]
        self.listbox_players.delete(0, tk.END)
        for p in self.players:
            self.listbox_players.insert(tk.END, p)
        self.status.config(text=f"Список подтверждён: {len(self.players)} игроков.")
        messagebox.showinfo("Готово", "Список игроков подтверждён.")

    def add_player_manually(self):
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

    def delete_selected(self):
        selected = self.listbox_players.curselection()
        if selected:
            self.listbox_players.delete(selected[0])

    def shuffle_and_distribute(self):
        players = list(self.listbox_players.get(0, tk.END))
        players = [p.strip() for p in players if p.strip()]

        if not players:
            messagebox.showwarning("Внимание", "Список игроков пуст.")
            return

        try:
            num_teams = int(self.spin_teams.get())
        except ValueError:
            num_teams = 2

        if num_teams < 2:
            num_teams = 2

        shuffled = players[:]
        random.shuffle(shuffled)

        teams = [[] for _ in range(num_teams)]
        for i, player in enumerate(shuffled):
            teams[i % num_teams].append(player)

        self.text_result.delete(1.0, tk.END)
        
        # Настройка тегов с отступами
        self.text_result.tag_configure("team", lmargin1=20, lmargin2=20)
        self.text_result.tag_configure("player", lmargin1=40, lmargin2=40)
        
        for idx, team in enumerate(teams, 1):
            self.text_result.insert(tk.END, f"Команда {idx} ({len(team)} игроков):\n", "team")
            for p in team:
                self.text_result.insert(tk.END, f"- {p}\n", "player")
            self.text_result.insert(tk.END, "\n")

        self.status.config(text=f"Распределено {len(players)} игроков на {num_teams} команд.")


if __name__ == "__main__":
    root = tk.Tk()
    app = CS2RandomPlayerApp(root)
    root.mainloop()