import shlex
import tkinter as tk
from tkinter import scrolledtext


class ShellEmulator:
    def __init__(self, root):
        self.root = root
        self.vfs_name = "my_vfs"
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
        self.entry.bind("<Return>", self.run_command)
        self.entry.focus()

        self.print_text(f"VFS '{self.vfs_name}' запущена. Доступные команды: ls, cd, exit")

    def print_text(self, text):
        self.output.insert(tk.END, text + "\n")
        self.output.see(tk.END)

    def run_command(self, event=None):
        line = self.entry.get()
        self.entry.delete(0, tk.END)
        self.entry.focus()

        if not line.strip():
            return

        self.print_text(f"user@{self.vfs_name}:~$ {line}")

        try:
            parts = shlex.split(line)
        except ValueError as e:
            self.print_text(f"Ошибка парсера: {e}")
            return

        cmd = parts[0]
        args = parts[1:]

        if cmd == "ls":
            if len(args) > 1:
                self.print_text("ls: слишком много аргументов (ожидается 0 или 1)")
            else:
                self.print_text(f"Команда: {cmd}, аргументы: {args}")

        elif cmd == "cd":
            if len(args) == 0:
                self.print_text("cd: отсутствует аргумент (укажите путь)")
            elif len(args) > 1:
                self.print_text("cd: слишком много аргументов (ожидается 1)")
            else:
                self.print_text(f"Команда: {cmd}, аргументы: {args}")

        elif cmd == "exit":
            if len(args) > 0:
                self.print_text("exit: команда не принимает аргументов")
            else:
                self.root.destroy()

        else:
            self.print_text(f"{cmd}: команда не найдена")


if __name__ == "__main__":
    root = tk.Tk()
    app = ShellEmulator(root)
    root.mainloop()
