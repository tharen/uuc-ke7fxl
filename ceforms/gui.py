import os

import Tkinter as tk
import tkFont


class GUI(tk.Toplevel):
    def __init__(self,root):
        self.root = root
        self.root.columnconfigure(0,weight=1)
        self.root.rowconfigure(0,weight=1)
        
        self._setSize()
        
        self.panel = tk.Frame(self.root)
        self.panel.grid(row=0,column=0,sticky='nsew')
        self.panel.columnconfigure(0,weight=0)
        self.panel.rowconfigure(0,weight=1)
        
        self.menu = tk.Frame(self.root)
        self.menu.grid(row=0,column=0,sticky='sew')
        self.menu.columnconfigure(0,weight=1)
        self.menu.columnconfigure(2,weight=1)
        
        self.canvas = tk.Canvas(self.panel,
                width=640,height=480)
        self.canvas.grid(row=0,column=0,sticky='nsew')
        
        self.left_menu = None
        self.div_menu = None
        self.right_menu = None
    
        self.menu_font = tkFont.Font(family='system',
                size=10,
                weight=tkFont.BOLD)
        
    def _setSize(self):
        w = self.root.winfo_screenwidth()
        h = self.root.winfo_screenheight()
        
        if os.name.lower() == 'ce':
            w = 640
            h = 480
            self.root.winfo_geometry('%dx%d+%d+%d' %
                    (w-1,h-51,-3,4))
    
    def addMenuCommand(self,side,label,command):
        
        if side == 'left':
            menu = self.left_menu.menu
        elif side == 'right':
            menu = self.right_menu.menu
        
        menu.add_command(label=label
                ,font=self.menu_font
                ,command=command)
        
    def addMenu(self,side,label):
        if self.div_menu == None:
            self.div_menu = tk.Label(
                    self.menu
                    ,width=9)
            self.div_menu.grid(row=0,column=1
                    ,sticky='sew')
        menu = tk.Menubutton(self.menu
                ,text = label
                ,font = self.menu_font
                ,direction = 'above'
                ,anchor = 'center'
                ,bg = 'black'
                ,fg = 'white'
                ,activebackground = 'black'
                ,activeforeground = 'white'
                )
        
        menu.menu  =tk.Menu(menu,tearoff=0)
        menu['menu'] = menu.menu
        menu.menu.configure(
                bg='black'
                ,fg='white')
        
        if side == 'left':
            menu.grid(row=0,column=0,sticky='sew')
            menu.configure(anchor='center')
            self.left_menu = menu
            
        elif side == 'right':
            menu.grid(row=0,column=2,sticky='sew')
            menu.configure(anchor='center')
            self.right_menu= menu
            
if __name__=='__main__':
    root = tk.Tk()
    root.title('Fred')
    gui=GUI(root)
    gui.addMenu('left' ,'File')
    gui.addMenu('right','Options')
    
    gui.addMenuCommand('left','Exit',root.destroy)
    
    root.mainloop()
    