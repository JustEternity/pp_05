import tkinter as tk
from tkinter import messagebox
import db
from captcha import CaptchaPuzzle
import adminscreen
import userscreen

class LoginWindow:
    def __init__(self, root, image_paths):
        self.root = root
        self.image_paths = image_paths
        self.window = tk.Toplevel(root)
        self.window.title("Вход")
        self.window.geometry("550x480")
        self.window.minsize(width=550, height=480)

        self.login_var = tk.StringVar()
        self.password_var = tk.StringVar()

        input_frame = tk.Frame(self.window)
        input_frame.pack(pady=20, expand=True)

        tk.Label(input_frame, text="Логин:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        tk.Entry(input_frame, textvariable=self.login_var, width=20).grid(row=0, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="Пароль:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        tk.Entry(input_frame, textvariable=self.password_var, show='*', width=20).grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.window, text="Соберите пазл:").pack()
        self.captcha = CaptchaPuzzle(self.window, image_paths, cell_size=120)
        self.captcha.pack(pady=10)

        tk.Button(self.window, text="Войти", command=self.login, width=15).pack(pady=20)

        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

    def login(self):
        login = self.login_var.get().strip()
        password = self.password_var.get()
        if not login or not password:
            messagebox.showerror("Ошибка", "Заполните все поля.")
            return

        if not self.captcha.is_correct():
            messagebox.showerror("Ошибка", "Пазл собран неверно.")
            self.handle_failed_attempt(login)
            return

        user_data = db.get_user(login)
        if not user_data:
            messagebox.showerror("Ошибка", "Вы ввели неверный логин или пароль. Пожалуйста проверьте ещё раз введенные данные.")
            self.handle_failed_attempt(login)
            return

        if user_data['blocked']:
            messagebox.showerror("Ошибка", "Вы заблокированы. Обратитесь к администратору.")
            return

        if password != user_data['password']:
            messagebox.showerror("Ошибка", "Вы ввели неверный логин или пароль. Пожалуйста проверьте ещё раз введенные данные.")
            self.handle_failed_attempt(login)
            return

        db.reset_failed_attempts(login)
        messagebox.showinfo("Успех", "Вы успешно авторизовались.")
        self.window.destroy()
        if user_data['role'] == 'admin':
            adminscreen.AdminWindow(self.root, login, self.image_paths, self.show_login)
        else:
            userscreen.UserWindow(self.root, login, self.image_paths, self.show_login)

    def show_login(self):
        """Возврат к окну входа"""
        self.window.destroy()
        LoginWindow(self.root, self.image_paths)

    def handle_failed_attempt(self, login):
        user_data = db.get_user(login)
        if user_data and not user_data['blocked']:
            if user_data['role'] == 'admin': # аккаунт администратора не блокируется
                return
            db.increment_failed_attempts(login)
            updated = db.get_user(login)
            if updated and updated['blocked']:
                messagebox.showerror("Блокировка", "Вы заблокированы. Обратитесь к администратору")

    def on_close(self):
        self.root.quit()