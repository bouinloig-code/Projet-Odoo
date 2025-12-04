from pathlib import Path
import tkinter as tk
 
#====================================================================
 
class App(tk.Tk):
    """ Application GUI in Tkinter"""
    def __init__(self):
        """ Application constructor (heritage=Tk object) """
        super().__init__()
        self.screen_h = 880 #self.winfo_screenheight()
        self.screen_v = self.winfo_screenheight()
        self.screen_x = 50
        self.screen_y = 0
        geometry = str(self.screen_h) + "x" + str(self.screen_v) + "+" + str(self.screen_x) + "+" + str(self.screen_y)
        self.geometry(geometry)
        self.resizable(True, True) # (width, height)
        self.minsize(100, 100)
        self.maxsize(self.winfo_screenwidth(), self.winfo_screenheight())
        self.attributes('-alpha', 0.9) #window transparency
        # self.iconbitmap(Path("image/logo.png"))
        self.title("Happy Cactus")
#====================================================================
 
if __name__ == "__main__":
    app = App()
    app.mainloop()