import tkinter as tk
from tkinter import ttk

def initWidget(self):
    """ Init all widget of the main window """
    self.img = tk.PhotoImage(file="image/logo.png")
    self.image = ttk.Label(self, image=self.img, text ="Happy Cactus", compound="top")
    self.image.pack()
    self.message = ttk.Label(self, text="Hello, MSIR5!", font=("Courier", 18), foreground="white", background="blue")
    self.message.pack()
    self.btn1 = ttk.Button(self, text="Production", command=self.onBtn1Click)
    self.btn1.pack(pady=10)
    self.btn2 = ttk.Button(self, text="Bom", command=self.onBtn2Click)
    self.btn2.bind("<Return>", self.onBtn2Click)
    self.btn2.focus()  
    self.btn2.pack()