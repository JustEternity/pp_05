import tkinter as tk
from auth_screen import LoginWindow

def main():
    images = [
        "images/1.png",
        "images/2.png",
        "images/3.png",
        "images/4.png"
    ]

    root = tk.Tk()
    root.withdraw()
    LoginWindow(root, images)
    root.mainloop()

if __name__ == "__main__":
    main()