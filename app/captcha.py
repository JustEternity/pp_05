import tkinter as tk
from PIL import Image, ImageTk
import random

class CaptchaPuzzle(tk.Frame):
    """Виджет пазла каптчи. Пользователь может перетаскивать фрагменты"""
    def __init__(self, parent, image_paths, cell_size=120):
        super().__init__(parent)
        self.image_paths = image_paths
        self.cell_size = cell_size
        self.correct_order = list(range(4))
        self.current_order = self.correct_order.copy()
        random.shuffle(self.current_order) # перемешивание фрагментов

        self.canvas = tk.Canvas(self, width=2*cell_size, height=2*cell_size, bg='white')
        self.canvas.pack()

        self.photo_images = []
        self.image_ids = []
        self.selected_item = None
        self.start_pos = None # координата начала перемещения фрагмента

        self.load_images()
        self.draw_puzzle()

        self.bind_events()

    def load_images(self):
        for path in self.image_paths:
            img = Image.open(path)
            img = img.resize((self.cell_size, self.cell_size), Image.Resampling.LANCZOS) # масштабирование фрагментов
            photo = ImageTk.PhotoImage(img) # преобразование в формат tkintera
            self.photo_images.append(photo)

    def draw_puzzle(self):
        self.canvas.delete("all")
        self.image_ids = []
        for idx, order_idx in enumerate(self.current_order): # idx номер ячейки, order_idx номер фрагмента
            row = idx // 2
            col = idx % 2

            # Рассчет координат вставки каждого фрагмента в ячейку (левый верхний угол)
            x = col * self.cell_size
            y = row * self.cell_size
            img_id = self.canvas.create_image(x, y, anchor='nw', image=self.photo_images[order_idx])
            self.image_ids.append(img_id) # сохранение идентификаторов фрагментов

    def bind_events(self):
        for img_id in self.image_ids:
            self.canvas.tag_bind(img_id, '<ButtonPress-1>', self.on_press) # Нажатие ЛКМ
            self.canvas.tag_bind(img_id, '<B1-Motion>', self.on_motion) # Перемещение с нажатой ЛКМ
            self.canvas.tag_bind(img_id, '<ButtonRelease-1>', self.on_release) # Отпуск ЛКМ

    def on_press(self, event):
        self.selected_item = self.canvas.find_closest(event.x, event.y)[0] # ближайший фрагмент к точке нажатия
        self.start_pos = (event.x, event.y)
        self.canvas.tag_raise(self.selected_item) # перенос выбранного фрагмента на передний план

    def on_motion(self, event):
        if self.selected_item:
            # Координаты перемещения фрагмента
            dx = event.x - self.start_pos[0]
            dy = event.y - self.start_pos[1]
            self.canvas.move(self.selected_item, dx, dy)
            self.start_pos = (event.x, event.y)

    def on_release(self, event):
        if self.selected_item:
            coords = self.canvas.coords(self.selected_item) # Координаты выбранного фрагмента
            x_center = coords[0] + self.cell_size/2
            y_center = coords[1] + self.cell_size/2

            # Определение целевой ячейки
            col = int(x_center // self.cell_size)
            row = int(y_center // self.cell_size)
            if col >= 2: col = 1
            if row >= 2: row = 1
            target_idx = row * 2 + col

            # Индекс выбранного фрагмента
            selected_idx = self.image_ids.index(self.selected_item)

            if selected_idx != target_idx:
                # Смена фрагментов местами
                self.current_order[selected_idx], self.current_order[target_idx] = \
                    self.current_order[target_idx], self.current_order[selected_idx]
                self.redraw()
            else:
                self.redraw()

            self.selected_item = None

    def redraw(self):
        """Перерисовывает каптчу по текущему расположению фрагментов"""
        self.canvas.delete("all")
        self.image_ids = []
        for idx, order_idx in enumerate(self.current_order):
            row = idx // 2
            col = idx % 2
            x = col * self.cell_size
            y = row * self.cell_size
            img_id = self.canvas.create_image(x, y, anchor='nw', image=self.photo_images[order_idx])
            self.image_ids.append(img_id)
        self.bind_events()

    def is_correct(self):
        return self.current_order == self.correct_order