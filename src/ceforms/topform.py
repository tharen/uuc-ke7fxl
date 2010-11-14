import os
import sys
import time

import Tkinter as tk
import tkFont

def log(msg):
    rt=time.clock()
    sys.stdout.write('%.3f - %s\n' % (rt,msg))

debug=log

class GUI:
    def __init__(self,root):
        self.root=root
        self.root.columnconfigure(
                0,weight=1)
        self.root.rowconfigure(
                0,weight=1)
        self._setWindowSize()
        self.panel=tk.Frame(
                root)
        self.panel.grid(sticky='nsew')
        self.panel.columnconfigure(
                0,weight=1)
        self.panel.rowconfigure(
                0,weight=1)
        self.menu=tk.Frame(self.root
                ,bg='black')
        self.menu.grid(row=1,
                column=0
                ,sticky='nsew')
        self.menu.rowconfigure(0
                ,weight=1)
        self.menu.columnconfigure(
                0,weight=1)
#        self.menu_fm.columnconfigure(
#                1,weight=1)
        self.menu.columnconfigure(2,
                weight=1)

        self.left_menu=None
        self.right_menu=None
        
        self.menu_font=tkFont.Font(
                family='system',
                size=10,
                weight=tkFont.BOLD)

    def addCommand(self,side
            ,label,command):
        if side=='left':
            menu=self.left_menu.menu
        elif side=='right':
            menu=self.right_menu.menu
        menu.add_command(label=label,
                font=self.menu_font,
                command=command)
                
    def addMenu(self,side,label):
        
        menu = tk.Menubutton(
                self.menu
                ,text=label
                ,font=self.menu_font
                ,direction='above'
                ,anchor='center'
                ,bg='black'
                ,fg='white'
                ,activebackground='black'
                ,activeforeground='white')
        
        menu.menu=tk.Menu(
                menu,tearoff=0)
        menu['menu']= menu.menu
        menu.menu.configure(bg='black'
                ,fg='white')

        if not (self.left_menu or
                self.right_menu):
            debug('init divider')
            self.div=tk.Label(
                    self.menu
                    ,width=9
                    ,bg='black')
            self.div.grid(row=0
                    ,column=1
                    ,sticky='nsew')
        if side=='left':
            debug('left menu')
            self.left_menu=menu
            menu.grid(column=0,row=0
                    ,sticky='nsew')
        elif side=='right':
            debug('right menu')
            self.right_menu=menu
            menu.grid(column=2,row=0
                    ,sticky='nsew')
    
    def _setWindowSize(self):
        w = self.root.winfo_screenwidth()
        h = self.root.winfo_screenheight()
        
        debug('(%s wide x %s high)' % (w,h))
        debug('OS = %s' % os.name) 
        if os.name.lower() != 'ce':
            w=640
            h=480

        self.root.wm_geometry(
                '%dx%d+%d+%d' % 
                #(w,h-51,0,52))
                (w,h-51,-4,4))

class LabelOption(tk.Frame):
    def __init__(self,parent
            ,label=''
            ,label_width=7
            ,variable=None
            ,row=None
            ,column=0
            ,sticky='new'
            ,columnspan=1
            ,stacked=False
            ,items=()
            ):
        tk.Frame.__init__(self,parent)
        self.columnconfigure(1
                ,weight=1)
        label=tk.Label(self
                ,text=label
                ,font=parent.font
                ,width=label_width
                ,anchor='e')
        label.grid(row=0
                ,column=0
                ,sticky='new'
                ,padx=2
                )
                
        #div=tk.Label(self,width=1)
        #div.grid(row=0
        #        ,column=1)
        entry=tk.OptionMenu(self
                ,value=variable
                ,font=parent.font
                ,**items
                )
        if stacked:
            er=1
            ec=0
            self.columnconfigure(1
                    ,weight=0)
            self.columnconfigure(0
                    ,weight=1)
            label.configure(
                    anchor='w')
        else:
            er=0
            ec=1
            #es=1
        entry.grid(
                row=er
                ,column=ec
                #,columnspan=es
                ,sticky='new'
                ,padx=2
                )
        
        self.grid(row=row
                ,column=column
                ,sticky=sticky
                ,columnspan=columnspan
                ,pady=2)
                
class LabelEntry(tk.Frame):
    def __init__(self,parent
            ,label=''
            ,label_width=7
            ,textvariable=None
            ,row=None
            ,column=0
            ,sticky='new'
            ,columnspan=1
            ,stacked=False
            ):
        tk.Frame.__init__(self,parent)
        self.columnconfigure(1
                ,weight=1)
        label=tk.Label(self
                ,text=label
                ,font=parent.font
                ,width=label_width
                ,anchor='e')
        label.grid(row=0
                ,column=0
                ,sticky='new'
                ,padx=2
                )
                
        #div=tk.Label(self,width=1)
        #div.grid(row=0
        #        ,column=1)
        entry=tk.Entry(self
                ,textvariable=textvariable
                ,font=parent.font
                )
        if stacked:
            er=1
            ec=0
            self.columnconfigure(1
                    ,weight=0)
            self.columnconfigure(0
                    ,weight=1)
            label.configure(
                    anchor='w')
        else:
            er=0
            ec=1
            #es=1
        entry.grid(
                row=er
                ,column=ec
                #,columnspan=es
                ,sticky='new'
                ,padx=2
                )
        
        self.grid(row=row
                ,column=column
                ,sticky=sticky
                ,columnspan=columnspan
                ,pady=2)

class DataForm(tk.Frame):
    def __init__(self,parent):
        tk.Frame.__init__(self,parent)
        self.columnconfigure(0
                ,weight=1)
        self.columnconfigure(1
                ,weight=1)
        self.rowconfigure(15
                ,weight=1)
        self.vehicle_id=tk.IntVar()
        self.purch_date=tk.StringVar()
        self.station_id=tk.IntVar()
        self.odometer=tk.DoubleVar()
        self.quantity=tk.DoubleVar()
        self.price=tk.DoubleVar()
        self.comment=tk.StringVar()

        self.font=tkFont.Font(
                family='system',
                size=10)

        veh=LabelEntry(self
                ,label='Vehicle:'
                ,textvariable=self.vehicle_id
                ,row=0
                ,columnspan=2
                )
                
        purchdate=LabelEntry(self
                ,label='Date:'
                ,textvariable=self.purch_date
                ,row=1
                ,column=0
                )

        station=LabelOption(self
                ,label='Station:'
                ,variable=self.station_id
                ,row=3
                ,columnspan=2
                ,items=('one','two','three')
                )
                
        odom=LabelEntry(self
                ,label='Odom:'
                ,textvariable=self.odometer
                ,row=1
                ,column=1
                )
                
        gals=LabelEntry(self
                ,label='Quant:'
                ,textvariable=self.quantity
                ,row=2)
                
        price=LabelEntry(self
                ,label='Price:'
                ,textvariable=self.price
                ,row=2,column=1)

        comment=LabelEntry(self
                ,label='Comment:'
                ,textvariable=self.comment
                ,row=4
                ,columnspan=2
                ,stacked=True
                )

if __name__=='__main__':
    debug('init main')
    root=tk.Tk()
    root.title('Fred')
    gui=GUI(root)
    gui.addMenu('left','File')
    gui.addMenu('right','Yada')

    gui.addCommand('left'
            ,'Exit'
            ,root.destroy)

    df=DataForm(gui.panel)
    df.grid(sticky='nsew')
    root.mainloop()
