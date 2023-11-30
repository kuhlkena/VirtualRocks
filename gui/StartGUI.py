import tkinter as tk
from tkinter import filedialog as fd
from tkinter import messagebox as mb

class StartGUI(tk.Frame):

    def __init__(self, parent, controller):
        
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Choose Project:", font=controller.font, bg=controller.backcolor)
        label.pack(side="top", fill="x", pady=10)
        self.config(bg=controller.backcolor)

        middleframe = tk.Frame(self, bg=controller.backcolor)
        middleframe.place(anchor="c", relx=.5, rely=.5)

        newBtn = tk.Button(middleframe, height=10, width=20, text="New", bg=controller.buttoncolor, command=lambda: self.new_project())
        openBtn = tk.Button(middleframe, height=10, width=20, text="Open", bg=controller.buttoncolor, command=lambda: self.open_project())
        label = tk.Label(self, text="*paths cannot contain white spaces", bg=controller.backcolor)

        newBtn.pack(padx=20, side='left')
        openBtn.pack(padx=20, side='right')
        label.pack(side='bottom')
  
    # Event handler for the "new project" button
        # Should open a dialogue asking the user to selct a working directory
        # Then call controllers new_project method
    def new_project(self):
        projdir = fd.askdirectory(title='select workspace', initialdir='/home/')
        if not projdir:
            return
        if ' ' in projdir:
            print("Path must not contain white spaces")
            mb.showerror("Paths cannot contain whitespace                           ")
            return
        self.controller.new_project(projdir)

    # Event handler for the "open project" button
        # Should open a dialogue asking the user to selct a project save file
        # Then call controllers open_project method
    def open_project(self):
        projfile = fd.askopenfilename(filetypes=[('Choose a project.pkl file', '*.pkl')])
        if not projfile:
            return
        self.controller.open_project(projfile)


        