import argparse
import json
import os
import shlex
import tkinter as tk
from tkinter import scrolledtext


class ShellEmulator:
    def __init__(self, root, vfs_path=None, script_path=None):
        self.root = root
        self.vfs_path = vfs_path
        self.script_path = script_path

        self.vfs_name = os.path.basename(vfs_path) if vfs_path else "default_vfs"
        self.root.title(f"VFS Shell Emulator - {self.vfs_name}")
        self.root.geometry("750x500")

        self.vfs = {}
        self.current_path = "/home/user"

        self.output = scrolledtext.ScrolledText(
            root, bg="black", fg="white", font=("Consolas", 11)
        )
        self.output.pack(fill=tk.BOTH, expand=True)

        bottom_frame = tk.Frame(root, bg="black")
        bottom_frame.pack(fill=tk.X)

        self.prompt_label = tk.Label(
            bottom_frame,
            text=f"user@{self.vfs_name}:{self.current_path}$ ",
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
        self.load_vfs()
        self.update_prompt()
        self.print_text("Доступные команды: ls, cd, vfs-init, exit\n")

        if self.script_path:
            self.root.after(200, self.run_startup_script)

    def get_default_vfs(self):
        return {
            "/": ["home", "etc", "readme.txt"],
            "/home": ["user"],
            "/home/user": ["documents", "notes.txt"],
            "/home/user/documents": ["report.txt"],
            "/etc": ["config.cfg"],
        }

    def load_vfs(self):
        if self.vfs_path and os.path.exists(self.vfs_path):
            try:
                with open(self.vfs_path, "r", encoding="utf-8") as f:
                    self.vfs = json.load(f)
                self.print_text(f"[VFS] Загружена из файла: {self.vfs_path}")
            except Exception as e:
                self.print_text(f"[Ошибка VFS] Не удалось прочитать JSON ({e}). Загружена дефолтная VFS.")
                self.vfs = self.get_default_vfs()
        else:
            self.vfs = self.get_default_vfs()
            if self.vfs_path:
                self.print_text(f"[VFS] Файл '{self.vfs_path}' не найден. Создана дефолтная VFS в памяти.")
            else:
                self.print_text("[VFS] Загружена дефолтная VFS в памяти.")

        if self.current_path not in self.vfs:
            self.current_path = "/"

    def print_text(self, text):
        self.output.insert(tk.END, text + "\n")
        self.output.see(tk.END)

    def update_prompt(self):
        self.prompt_label.config(text=f"user@{self.vfs_name}:{self.current_path}$ ")

    def on_enter(self, event=None):
        line = self.entry.get()
        self.entry.delete(0, tk.END)
        self.entry.focus()

        if not line.strip():
            return

        self.execute_command(line)

    def execute_command(self, line):
        self.print_text(f"user@{self.vfs_name}:{self.current_path}$ {line}")

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

            target_path = self.current_path
            if len(args) == 1:
                target_path = self.resolve_path(args[0])
                if target_path not in self.vfs:
                    self.print_text(f"ls: невозможно получить доступ к '{args[0]}': Нет такого каталога")
                    return False

            items = self.vfs.get(target_path, [])
            self.print_text("  ".join(items) if items else "(пусто)")
            return True

        elif cmd == "cd":
            if len(args) == 0:
                self.print_text("cd: отсутствует аргумент (укажите путь)")
                return False
            elif len(args) > 1:
                self.print_text("cd: слишком много аргументов (ожидается 1)")
                return False

            target = args[0]
            if target == ".":
                return True
            elif target == "/":
                self.current_path = "/"
                self.update_prompt()
                return True
            elif target == "..":
                if self.current_path != "/":
                    parent = "/".join(self.current_path.split("/")[:-1])
                    self.current_path = parent if parent else "/"
                    self.update_prompt()
                return True
            else:
                new_path = self.resolve_path(target)
                if new_path in self.vfs:
                    self.current_path = new_path
                    self.update_prompt()
                    return True
                else:
                    self.print_text(f"cd: {target}: Нет такого каталога")
                    return False

        elif cmd == "vfs-init":
            if len(args) > 0:
                self.print_text("vfs-init: команда не принимает аргументов")
                return False

            self.vfs = self.get_default_vfs()
            self.current_path = "/home/user"
            self.update_prompt()

            if self.vfs_path:
                try:
                    with open(self.vfs_path, "w", encoding="utf-8") as f:
                        json.dump(self.vfs, f, ensure_ascii=False, indent=2)
                    self.print_text(f"VFS сброшена на дефолтную. Файл '{self.vfs_path}' перезаписан.")
                except Exception as e:
                    self.print_text(f"Ошибка записи файла VFS: {e}")
                    return False
            else:
                self.print_text("VFS в памяти сброшена на дефолтную.")
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

    def resolve_path(self, target):
        target = target.rstrip("/")
        if not target:
            return "/"
        if target.startswith("/"):
            return target
        if self.current_path == "/":
            return "/" + target
        return self.current_path + "/" + target

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
