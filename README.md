# VFS Shell Emulator (Вариант 6, Этапы 1–3)

Эмулятор командной оболочки с графическим интерфейсом на `tkinter`, поддержкой конфигурации через аргументы командной строки и виртуальной файловой системой (VFS) в памяти на основе JSON.

## Запуск

1. **Обычный запуск (дефолтная VFS в памяти):**
   ```bash
   python shell_emulator.py
   ```
2. **Запуск с подключением JSON-файла VFS:**
   ```bash
   python shell_emulator.py --vfs vfs.json
   ```
3. **Запуск со стартовым скриптом:**
   ```bash
   python shell_emulator.py --vfs vfs.json --script script_ok.txt
   ```
4. **Проверка остановки скрипта при ошибке:**
   ```bash
   python shell_emulator.py --vfs vfs.json --script script_error.txt
   ```
5. **Автоматический прогон всех режимов (Windows):**
   ```cmd
   run_tests.bat
   ```

## Поддерживаемые команды

- `ls [dir]` - список файлов и папок в текущей или указанной директории VFS
- `cd <dir>`, `cd ..`, `cd /` - переход по директориям VFS
- `vfs-init` - сброс VFS в памяти к дефолтному состоянию и перезапись JSON-файла (если передан `--vfs`)
- `exit` - закрытие эмулятора
