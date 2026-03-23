import tkinter as tk
from tkinter import ttk, messagebox
import db

class AdminWindow:
    def __init__(self, root, admin_login, image_paths, logout_callback):
        self.root = root
        self.admin_login = admin_login
        self.image_paths = image_paths
        self.logout_callback = logout_callback # Функция открытия окна авторизации
        self.window = tk.Toplevel(root)
        self.window.title("Панель администратора")
        self.window.geometry("600x500")
        self.window.minsize(width=600, height=500)
        self.create_widgets()
        self.refresh_user_list()
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_widgets(self):
        tk.Label(self.window, text="Управление пользователями", font=('Arial', 14)).pack(pady=10)

        # Таблица аккаунтов
        columns = ('login', 'role', 'blocked')
        self.tree = ttk.Treeview(self.window, columns=columns, show='headings')
        self.tree.heading('login', text='Логин')
        self.tree.heading('role', text='Роль')
        self.tree.heading('blocked', text='Заблокирован')
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Фрейм для кнопок управления списком
        btn_frame = tk.Frame(self.window)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Добавить", command=self.add_user_dialog).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Редактировать", command=self.edit_user_dialog).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Удалить", command=self.delete_user).pack(side=tk.LEFT, padx=5)
        tk.Button(self.window, text="Выйти из аккаунта", command=self.logout).pack(pady=10, side=tk.BOTTOM)

    def logout(self):
        self.window.destroy()
        self.logout_callback()

    def on_close(self):
        self.window.destroy()
        self.root.quit()

    def refresh_user_list(self):
        # Очистка таблицы
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Заполнение таблицы
        users = db.get_all_users()
        for username, role, blocked in users:
            blocked_text = "Да" if blocked else "Нет"
            self.tree.insert('', tk.END, values=(username, role, blocked_text))

    def add_user_dialog(self):
        """Окно создания аккаунта пользователя"""
        dialog = tk.Toplevel(self.window)
        dialog.title("Добавить пользователя")
        dialog.geometry("300x200")
        dialog.minsize(width=250, height=150)
        dialog.maxsize(width=250, height=150)

        tk.Label(dialog, text="Логин:").grid(row=0, column=0, padx=5, pady=5)
        login_entry = tk.Entry(dialog)
        login_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(dialog, text="Пароль:").grid(row=1, column=0, padx=5, pady=5)
        password_entry = tk.Entry(dialog, show='*')
        password_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(dialog, text="Роль:").grid(row=2, column=0, padx=5, pady=5)
        role_combo = ttk.Combobox(dialog, values=['user', 'admin'], state='readonly')
        role_combo.set('user')
        role_combo.grid(row=2, column=1, padx=5, pady=5)

        def add():
            login = login_entry.get().strip()
            password = password_entry.get()
            role = role_combo.get()
            if not login or not password:
                messagebox.showerror("Ошибка", "Заполните все поля.")
                return
            if not db.get_user(login) and db.add_user(login, password, role):
                messagebox.showinfo("Успех", "Пользователь добавлен.")
                dialog.destroy()
                self.refresh_user_list()
            else:
                messagebox.showerror("Ошибка", "Пользователь с таким логином уже существует.")

        tk.Button(dialog, text="Добавить", command=add).grid(row=3, columnspan=2, pady=10)

    def edit_user_dialog(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите пользователя для редактирования.")
            return
        item = self.tree.item(selected[0])
        login = item['values'][0]
        role = item['values'][1]
        blocked = (item['values'][2] == 'Да')

        dialog = tk.Toplevel(self.window)
        dialog.title("Редактирование пользователя")
        dialog.geometry("300x250")
        dialog.minsize(width=250, height=200)
        dialog.maxsize(width=250, height=200)

        tk.Label(dialog, text="Логин:").grid(row=0, column=0, padx=5, pady=5)
        tk.Label(dialog, text=login).grid(row=0, column=1, padx=5, pady=5, sticky='w')

        tk.Label(dialog, text="Новый пароль:").grid(row=1, column=0, padx=5, pady=5)
        password_entry = tk.Entry(dialog, show='*')
        password_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(dialog, text="Роль:").grid(row=2, column=0, padx=5, pady=5)
        role_combo = ttk.Combobox(dialog, values=['user', 'admin'], state='readonly')
        role_combo.set(role)
        role_combo.grid(row=2, column=1, padx=5, pady=5)

        blocked_var = tk.IntVar(value=1 if blocked else 0)
        tk.Checkbutton(dialog, text="Заблокирован", variable=blocked_var).grid(row=3, columnspan=2, pady=5)

        def save():
            update_data = {}
            new_password = password_entry.get()
            if new_password:
                update_data['password'] = new_password
            update_data['role'] = role_combo.get()
            update_data['blocked'] = bool(blocked_var.get())
            db.update_user(login, **update_data)
            messagebox.showinfo("Успешно", "Данные обновлены.")
            dialog.destroy()
            self.refresh_user_list()

        tk.Button(dialog, text="Сохранить", command=save).grid(row=4, columnspan=2, pady=10)

    def delete_user(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите пользователя для удаления.")
            return
        item = self.tree.item(selected[0])
        login = item['values'][0]
        if login == self.admin_login:
            messagebox.showerror("Ошибка", "Нельзя удалить самого себя.")
            return
        if messagebox.askyesno("Подтверждение", f"Удалить пользователя {login}?"):
            db.delete_user(login)
            self.refresh_user_list()