#!/usr/bin/python

import os
import sys
import Tkinter as tk
import tkFont

log = sys.stdout

def debug(msg):
    log.write('%s\n' % (msg,))

class CEFormApp(tk.Tk):
    def __init__(self,
            parent,
            title='Tk Forms'):
        tk.Tk.__init__(self,parent)
        self._parent=parent
        self.title=title

        #self.overrideredirect(True)
        self.resizable(False,False)
        
        #self.bind('<Configure>',self.on_windowConfigure)

        self.forms = {}
        self.activeForm = None

        self.grid_columnconfigure(0,weight=1)
        self.grid_rowconfigure(0,weight=1)
        
        self.winFrame=tk.Frame(self,bg='green',padx=2,pady=2,bd=0)
        self.menuFrame=tk.Frame(self,bg='red',bd=0)

        self.winFrame.grid(row=0,column=0,sticky='nsew')
        self.menuFrame.grid(row=1,column=0,sticky='sew')
        
        #config column/row weights
        self.winFrame.grid_rowconfigure(0,weight=1)
        self.winFrame.grid_columnconfigure(0,weight=1)

        self.menuFrame.grid_rowconfigure(0,weight=1)
        self.menuFrame.grid_columnconfigure(0,weight=1)
        self.menuFrame.grid_columnconfigure(2,weight=1)

        #setup the persistent menu
        self.menuFont=tkFont.Font(family='system',size=10,weight=tkFont.BOLD)

        self.leftMenu = tk.Menubutton(self.menuFrame,text='MenuL',
                font=self.menuFont,direction='above',anchor='center',
                bg='black',fg='white',
                activebackground='black',activeforeground='white')
        self.leftMenu.grid(column=0,row=0,sticky='sew')
        self.leftMenu.menu=tk.Menu(self.leftMenu,tearoff=0)
        self.leftMenu['menu']= self.leftMenu.menu

        self.centerDivider = tk.Label(self.menuFrame,width=9)
        self.centerDivider.grid(column=1,row=0,sticky='sew')

        self.rightMenu = tk.Menubutton(self.menuFrame,text='MenuR',
                font=self.menuFont,direction='above',anchor='center',
                fg='white',bg='black',
                activebackground='black',activeforeground='white')
        self.rightMenu.grid(column=2,row=0,sticky='sew')
        self.rightMenu.menu = tk.Menu(self.rightMenu,tearoff=0)
        self.rightMenu['menu']=self.rightMenu.menu

        self._setWindowSize()
        self.grid()

        self.addMenuItem('right','Exit',self.quit)

    def addMenuItem(self,side,label,command):
        if side == 'left':
            menu = self.leftMenu.menu
        else:
            menu = self.rightMenu.menu

        menu.add_command(label=label,font=self.menuFont,command=command)

    def quit(self):
        self.destroy()
        
    def _setWindowSize(self):
        w = self.winfo_screenwidth()
        h = self.winfo_screenheight()
        
        debug('(%s,%s)' % (w,h))
        
        if os.name.lower() != 'ce':
            w=640
            h=480

        self.wm_geometry(
                '%dx%d+%d+%d' % 
                #(w,h-51,0,52))
                (w,h-51,-2,4))

def _nocmd(*args**kargs):
    pass

if __name__=='__main__':
    main=CEFormApp(None,title='CE Forms')
    main.mainloop()
