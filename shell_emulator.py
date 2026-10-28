import argparse
import os
import shlex
import tkinter as tk
from tkinter import scrolledtext


class ShellEmulator:
    def __init__(self, root, vfs_path=None, script_path=None):
        self.root = root
        self.vfs_path = vfs_path
        self.script_path = script_path

        self.vfs_name = os.path.basename(vfs_path) if vfs_path else "my_vfs"
        self.root.title(f"VFS Shell Emulator - {self.vfs_name}")
        self.root.geometry("700x450")

        self.output = scrolledtext.ScrolledText(
            root, bg="black", fg="white", font=("Consolas", 11)
        )
        self.output.pack(fill=tk.BOTH, expand=True)

        bottom_frame = tk.Frame(root, bg="black")
        bottom_frame.pack(fill=tk.X)

        self.prompt_label = tk.Label(
            bottom_frame,
            text=f"user@{self.vfs_name}:~$ ",
            bg="black",
            fg="lightgreen",
            font=("Consolas", 11),
        )
        self.prompt_label.pack(side=tk.LEFT)

        self.entry = tk.Entry(
            bottom_frame,
            bg="black",
            fg="white",
            insertbackground="white",
            font=("Consolas", 11),
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry.bind("<Return>", self.on_enter)
        self.entry.focus()

        self.print_text(f"[DEBUG] Параметры запуска: --vfs={self.vfs_path}, --script={self.script_path}")
        self.print_text(f"VFS '{self.vfs_name}' запущена. Доступные команды: ls, cd, exit\n")

        if self.script_path:
            self.root.after(200, self.run_startup_script)

    def print_text(self, text):
        self.output.insert(tk.END, text + "\n")
        self.output.see(tk.END)

    def on_enter(self, event=None):
        line = self.entry.get()
        self.entry.delete(0, tk.END)
        self.entry.focus()

        if not line.strip():
            return

        self.execute_command(line)

    def execute_command(self, line):
        self.print_text(f"user@{self.vfs_name}:~$ {line}")

        try:
            parts = shlex.split(line)
        except ValueError as e:
            self.print_text(f"Ошибка парсера: {e}")
            return False

        if not parts:
            return True

        cmd = parts[0]
        args = parts[1:]

        if cmd == "ls":
            if len(args) > 1:
                self.print_text("ls: слишком много аргументов (ожидается 0 или 1)")
                return False
            self.print_text(f"Команда: {cmd}, аргументы: {args}")
            return True

        elif cmd == "cd":
            if len(args) == 0:
                self.print_text("cd: отсутствует аргумент (укажите путь)")
                return False
            elif len(args) > 1:
                self.print_text("cd: слишком много аргументов (ожидается 1)")
                return False
            self.print_text(f"Команда: {cmd}, аргументы: {args}")
            return True

        elif cmd == "exit":
            if len(args) > 0:
                self.print_text("exit: команда не принимает аргументов")
                return False
            self.root.destroy()
            return True

        else:
            self.print_text(f"{cmd}: команда не найдена")
            return False

    def run_startup_script(self):
        if not os.path.exists(self.script_path):
            self.print_text(f"[Ошибка скрипта] Файл '{self.script_path}' не найден.")
            return

        self.print_text(f"--- Выполнение скрипта: {self.script_path} ---")
        try:
            with open(self.script_path, "r", encoding="utf-8") as f:
                for raw_line in f:
                    line = raw_line.strip()
                    if not line or line.startswith("#"):
                        continue
                    ok = self.execute_command(line)
                    if not ok:
                        self.print_text(f"[Скрипт остановлен] Ошибка в строке: {line}")
                        return
            self.print_text("--- Скрипт успешно выполнен ---\n")
        except Exception as e:
            self.print_text(f"[Ошибка чтения скрипта] {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VFS Shell Emulator")
    parser.add_argument("--vfs", type=str, default=None, help="Путь к JSON-файлу VFS")
    parser.add_argument("--script", type=str, default=None, help="Путь к стартовому скрипту")
    parsed_args = parser.parse_args()

    root = tk.Tk()
    app = ShellEmulator(root, vfs_path=parsed_args.vfs, script_path=parsed_args.script)
    root.mainloop()
