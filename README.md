После скачивани пропишим в консоль
- pip install pyinstaller

- pyinstaller --onefile --windowed --icon=icons-cam-x70x70.ico --name "MotionDetector" index.py
  --onefile — собрать всё в один EXE-файл.
  --windowed — не показывать консоль (актуально для GUI-приложений).
  --icon аналогично (путь до иконки приложения).
  --name название приложение в кавычках.

В папке dist будет .exe файл с программой, все остальное можно удалить.
