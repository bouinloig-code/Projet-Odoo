from pathlib import Path
import tkinter as tk

#====================================================================

class App(tk.Tk):
    """ Application GUI in Tkinter"""
    def __init__(self):
        """ Application constructor (heritage=Tk object) """
        super().__init__()

#====================================================================

if __name__ == "__main__":
    app = App()
    app.mainloop()
