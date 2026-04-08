import random
import tkinter as tk
from tkinter import ttk, messagebox

class TeamDividerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Случайное распределение команд")
        self.root.geometry("500x400")
        self.root.resizable(False, False)

        # Переменные состояния
        self.use_names = tk.BooleanVar(value=False)   # Режим: False = числа, True = ники
        self.team_size = tk.IntVar(value=5)           # Количество игроков в одной команде

        # Загрузка имён из файла (если есть)
        self.names_list = self.load_names_from_file("names.txt")

        # Интерфейс
        self.create_widgets()

        # Первое распределение
        self.divide_teams()

    def create_widgets(self):
        # Рамка настроек
        settings_frame = ttk.LabelFrame(self.root, text="Настройки", padding=5)
        settings_frame.pack(fill="x", padx=10, pady=5)

        # Размер команды
        ttk.Label(settings_frame, text="Размер команды:").grid(row=0, column=0, sticky="w", padx=5)
        spinbox = ttk.Spinbox(settings_frame, from_=1, to=20, textvariable=self.team_size, width=5)
        spinbox.grid(row=0, column=1, padx=5)
        spinbox.bind("<KeyRelease>", lambda e: self.divide_teams())   # обновляем при изменении

        # Режим работы
        self.numbers_radio = ttk.Radiobutton(settings_frame, text="Числа", variable=self.use_names, value=False,
                                             command=self.divide_teams)
        self.numbers_radio.grid(row=1, column=0, sticky="w", padx=5)
        self.names_radio = ttk.Radiobutton(settings_frame, text="Ники из файла (names.txt)", variable=self.use_names,
                                           value=True, command=self.on_names_mode)
        self.names_radio.grid(row=1, column=1, sticky="w", padx=5)

        # Кнопка случайного распределения
        self.shuffle_btn = ttk.Button(self.root, text="Случайное распределение", command=self.divide_teams)
        self.shuffle_btn.pack(pady=10)

        # Рамка для вывода команд
        teams_frame = ttk.Frame(self.root)
        teams_frame.pack(fill="both", expand=True, padx=10, pady=5)

        ttk.Label(teams_frame, text="Команда 1", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=20)
        ttk.Label(teams_frame, text="Команда 2", font=("Arial", 12, "bold")).grid(row=0, column=1, padx=20)

        self.text_left = tk.Text(teams_frame, width=20, height=15, font=("Courier", 10), state=tk.DISABLED)
        self.text_left.grid(row=1, column=0, padx=10, pady=5)

        self.text_right = tk.Text(teams_frame, width=20, height=15, font=("Courier", 10), state=tk.DISABLED)
        self.text_right.grid(row=1, column=1, padx=10, pady=5)

    def load_names_from_file(self, filename):
        """Загружает список имён из текстового файла (построчно). Возвращает список строк."""
        try:
            with open(filename, "r", encoding="utf-8") as f:
                names = [line.strip() for line in f if line.strip()]
            return names
        except FileNotFoundError:
            return []   # Файла нет – пустой список

    def on_names_mode(self):
        """При переключении в режим ников проверяем, хватает ли имён."""
        if self.use_names.get():
            total_needed = self.team_size.get() * 2
            if len(self.names_list) < total_needed:
                messagebox.showerror(
                    "Ошибка",
                    f"В файле names.txt недостаточно имён.\n"
                    f"Нужно: {total_needed}, найдено: {len(self.names_list)}.\n"
                    "Режим остаётся на 'Числа'."
                )
                self.use_names.set(False)
        self.divide_teams()

    def divide_teams(self):
        """Основная логика: перемешивание и разделение на две команды."""
        team_size = self.team_size.get()
        total_players = team_size * 2

        # Режим "Числа"
        if not self.use_names.get():
            numbers = list(range(1, total_players + 1))
            random.shuffle(numbers)
            left = numbers[:team_size]
            right = numbers[team_size:]
            left.sort()
            right.sort()
            self.update_text(self.text_left, left)
            self.update_text(self.text_right, right)
        else:
            # Режим "Ники"
            if len(self.names_list) < total_players:
                messagebox.showerror(
                    "Ошибка",
                    f"В файле names.txt недостаточно имён.\n"
                    f"Нужно: {total_players}, есть: {len(self.names_list)}.\n"
                    "Переключитесь на режим 'Числа'."
                )
                self.use_names.set(False)
                self.divide_teams()   # рекурсивный вызов для чисел
                return

            # Берём первых total_players имён (или можно случайную выборку – сделаем случайную выборку)
            # По условию "сам txt файл не меняется", но мы можем выбрать случайное подмножество имён.
            # Логично: перемешать весь список имён и взять нужное количество.
            selected_names = random.sample(self.names_list, total_players)
            random.shuffle(selected_names)
            left = selected_names[:team_size]
            right = selected_names[team_size:]
            left.sort()
            right.sort()
            self.update_text(self.text_left, left)
            self.update_text(self.text_right, right)

    def update_text(self, text_widget, data):
        """Обновляет содержимое текстового поля."""
        text_widget.config(state=tk.NORMAL)
        text_widget.delete(1.0, tk.END)
        for item in data:
            text_widget.insert(tk.END, f"{item}\n")
        text_widget.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = TeamDividerApp(root)
    root.mainloop()