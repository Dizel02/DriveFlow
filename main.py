import tkinter as tk
from tkinter import messagebox
from database import Database
from ui import LoginWindow


def main():
    db = Database()

    try:
        db.init_tables()
    except Exception as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Ошибка подключения к серверу БД",
            f"Не удалось соединиться с MySQL.\nУбедитесь, что в XAMPP запущен MySQL!\n\nДетали: {e}"
        )
        return

    app = LoginWindow(db)
    app.mainloop()


if __name__ == "__main__":
    main()
