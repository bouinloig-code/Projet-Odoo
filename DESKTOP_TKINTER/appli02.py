from tkinter import ttk
import tkinter as tk

def initWidgets(self):
    """ Init all widget of the main window """
    self.message = ttk.Label(self, text="Hello Tkinter")
    self.message.pack()
    self.btn1 = ttk.Button(self, text="Production", command=self.onBtn1Click)
    self.btn1.pack()
    self.btn2 = ttk.Button(self, text="Bom", command=self.onBtn2Click)
    self.btn2.bind("<Return>", self.onBtn2Click)
    self.btn2.focus()  
    self.btn2.pack()
def onBtn1Click(self):
    """ Callback Btn1 pressed """
    self.message['text']="mrp.production"
def onBtn2Click(self, event=None):
    """ Callback Btn2 pressed """
    self.message.config(text="mrp.bom")
