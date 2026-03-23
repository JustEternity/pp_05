import tkinter as tk

class UserWindow:
    def __init__(self, root, login, image_paths, logout_callback):
        self.root = root
        self.login = login
        self.image_paths = image_paths
        self.logout_callback = logout_callback # Функция открытия окна авторизации
        self.window = tk.Toplevel(root)
        self.window.title("Пользователь")
        self.window.geometry("300x200")
        self.window.minsize(width=300, height=200)

        tk.Label(self.window, text=f"Добро пожаловать, {login}!", font=('Arial', 14)).pack(pady=50)
        logout_btn = tk.Button(self.window, text="Выйти из аккаунта", command=self.logout)
        logout_btn.pack(pady=20)
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

    def logout(self):
        self.window.destroy()
        self.logout_callback()

    def on_close(self):
        self.window.destroy()
        self.root.quit()