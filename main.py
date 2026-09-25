import tkinter as tk
from views.Interfaz import Interfaz


def main():
    ventana = tk.Tk()
    Interfaz(ventana)
    ventana.mainloop()


if __name__ == "__main__":
    main()