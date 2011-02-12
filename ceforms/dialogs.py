import os
import datetime
import Tkinter as tk
import tkFont

MIN_YEAR = 2005
MAX_YEAR = 2011

class Dialog(tk.Toplevel):
    def __init__(self,master
        ,title=None
        ):
        tk.Toplevel.__init__(self
              ,master
              ,relief='flat'
              ,bd=0
              )
        if title:
            self.title(title)

        self.transient(master)
        self.grab_set()

        self.master=master

        self._value=tk.StringVar()
        self.result=None

        w = self.winfo_screenwidth()
        h = self.winfo_screenheight()

        if os.name.lower() != 'ce':
            w=320
            h=240

        self.wm_geometry(
                '%dx%d+%d+%d' %
                (w,h-52,-4,4))

        self.columnconfigure(
                0,weight=1)
        self.rowconfigure(
                0,weight=1)

        self.panel=tk.Frame(self
                ,bd=0
                ,bg='yellow'
                )
        self.panel.grid(
                row=0
                ,column=0
                ,sticky='nsew')
        self.panel.columnconfigure(
                0,weight=1)
        self.panel.rowconfigure(
                0,weight=1)

        #draw the menu/buttons
        self.menu()

        #draw the dialog body, return
        #  the initial focus widget
        self.initial_focus=self.body(
                self.panel
                )

        if not self.initial_focus:
            self.initial_focus=self.panel

        self.protocol(
                'WM_DELETE_WINDOW'
                ,self.cancel
                )
        #force this window to be modal
        #self.wait_window(self)

    def menu(self):
        self.menu=tk.Frame(self
                ,bg='gray25'
                ,bd=2
                ,relief='flat'
                )
        self.menu.grid(row=1,
                column=0
                ,sticky='sew')
        self.menu.rowconfigure(0
                ,weight=1)
        self.menu.columnconfigure(
                0,weight=1)
        self.menu.columnconfigure(
                1,weight=1)
        self.menu.columnconfigure(2,
                weight=1)

        self.menu_font=tkFont.Font(
                family='system',
                size=8,
                weight=tkFont.BOLD
                )

        self.left_menu=tk.Button(
                self.menu
                ,text='OK'
                ,command=self.ok
                ,bg='gray25'
                ,fg='white'
                ,font=self.menu_font
                ,relief='flat'
                )
        self.left_menu.grid(
                row=0,column=0
                ,sticky='sew')

        self.right_menu=tk.Button(
                self.menu
                ,text='Cancel'
                ,command=self.cancel
                ,bg='gray25'
                ,fg='white'
                ,font=self.menu_font
                ,relief='flat'
                )

        self.right_menu.grid(
                row=0,column=2
                ,sticky='sew')

        self.bind('<Return>'
                ,self.ok)
        self.bind('<Escape>'
                ,self.cancel)

    def body(self,master):
        pass

    def show(self):
        self.deiconify()
        self.initial_focus.focus_set()
        self.wait_window(self)

    def validate(self):
        self.result=self._value.get()
        return True

    def apply(self):
        pass

    def ok(self
            ,e=None):
        if not self.validate():
            self.initial_focus.focus_set()
            return

        self.withdraw()
        self.update_idletasks()

        self.apply()

        self.cancel()

    def cancel(self
            ,e=None):
        self.destroy()

class Numpad(Dialog):
    def __init__(self,master
            ,initValue=0
            ,title=None
            ):
        #self.initValue=initValue
        Dialog.__init__(self
                ,master
                ,title)
        self._value.set(initValue)

    def body(self,master):
        main_frame=tk.Frame(
                #self.panel
                master
                )
        main_frame.grid(
                row=0
                ,column=0
                ,sticky='nsew'
                )

        main_frame.rowconfigure(
                1
                ,weight=1
                )
        main_frame.columnconfigure(
                0
                ,weight=1
                )

        display_font=tkFont.Font(
                family='system'
                ,size=12
                )
        button_font=tkFont.Font(
                family='system'
                ,size=12
                )

        self.display=tk.Entry(
                main_frame
                ,textvariable=self._value
                ,relief='flat'
                ,font=display_font
                ,justify='right'
                )

        self.display.grid(
                row=0
                ,column=0
                ,sticky='new'
                )

        numpad=tk.Frame(
                main_frame
                ,relief='flat'
                )
        numpad.grid(
                row=1
                ,column=0
                ,sticky='nsew'
                )

        w=numpad.winfo_width()
        h=numpad.winfo_height()

        i=1
        for r in range(3):
            numpad.rowconfigure(
                r
                ,weight=1
                )
            for c in range(3):
                numpad.columnconfigure(
                        c
                        ,weight=1
                        )
                btn=tk.Button(
                        numpad
                        ,text=str(i)
                        ,font=button_font
                        #,relief='flat'
                        )
                btn.grid(
                        row=r
                        ,column=c
                        ,sticky='nsew'
                        )
                btn.bind('<Button-1>'
                        ,self.num_click)
                i+=1

        numpad.rowconfigure(
                3
                ,weight=1
                )
        dec=tk.Button(numpad
                ,text='.'
                ,font=button_font
                )
        dec.grid(row=3
                ,column=0
                ,sticky='nsew'
                )
        dec.bind('<Button-1>'
                ,self.dec_click)
        zero=tk.Button(numpad
                ,text='0'
                ,font=button_font
                )
        zero.grid(row=3
                ,column=1
                ,sticky='nsew'
                )
        zero.bind('<Button-1>'
                ,self.num_click)
        back=tk.Button(numpad
                ,text='<-'
                ,font=button_font
                )
        back.grid(row=3
                ,column=2
                ,sticky='nsew'
                )

        back.bind('<Button-1>'
                ,self.back_click
                )

        self.display.bind('<Key>'
                ,self.key_dispatch
                )

        self.update_idletasks()

        self.display.icursor(tk.END)

        return self.display

    def key_dispatch(self,e):
        x=self._value.get()
        if e.char in '1234567890':
            self._value.set(x+e.char)
            self.display.icursor(tk.END)

        elif e.char=='.':
            if not '.' in x:
                self._value.set(
                        x+e.char
                        )
            self.display.icursor(tk.END)

        elif e.keycode == 8:
            self._value.set(x[:-1])
            self.display.icursor(tk.END)

        elif e.keycode==13:
            self.ok()

        else:
            print e.char,e.keycode

        return 'break'

    def validate(self):
        self.result=self._value.get()
        return True

    def num_click(self,e):
        x=e.widget.cget('text')
        y=self._value.get()
        self._value.set(y+x)
        self.display.icursor(tk.END)

    def back_click(self,e):
        val=self._value.get()
        self._value.set(0)
        self._value.set(val[:-1])
        self.display.icursor(tk.END)

    def dec_click(self,e):
        val=self._value.get()
        if not '.' in val:
            self._value.set(val+'.')
        self.display.icursor(tk.END)

class Datepad(Dialog):
    def __init__(self,master
            ,initValue=None
            ,title=None
            ):
        #self.initValue=initValue
        Dialog.__init__(self
                ,master
                ,title)
        try:
            d=datetime.datetime.strptime(
                    initValue
                    ,'%Y/%m/%d'
                    )

            self._value.set(initValue)

        except:
            pass

    def body(self,master):
        main_frame=tk.Frame(
                #self.panel
                master
                )
        main_frame.grid(
                row=0
                ,column=0
                ,sticky='nsew'
                )

        main_frame.rowconfigure(
                1
                ,weight=1
                )
        main_frame.columnconfigure(
                0
                ,weight=1
                )

        display_font=tkFont.Font(
                family='system'
                ,size=12
                )
        button_font=tkFont.Font(
                family='system'
                ,size=12
                )

        self.display=tk.Entry(
                main_frame
                ,textvariable=self._value
                ,relief='flat'
                ,font=display_font
                ,justify='right'
                )

        self.display.grid(
                row=0
                ,column=0
                ,sticky='new'
                )

        numpad=tk.Frame(
                main_frame
                ,relief='flat'
                )
        numpad.grid(
                row=1
                ,column=0
                ,sticky='nsew'
                )

        w=numpad.winfo_width()
        h=numpad.winfo_height()

        i=1
        for r in range(3):
            numpad.rowconfigure(
                r
                ,weight=1
                )
            for c in range(3):
                numpad.columnconfigure(
                        c
                        ,weight=1
                        )
                btn=tk.Button(
                        numpad
                        ,text=str(i)
                        ,font=button_font
                        #,relief='flat'
                        )
                btn.grid(
                        row=r
                        ,column=c
                        ,sticky='nsew'
                        )
                btn.bind('<Button-1>'
                        ,self.num_click)
                i+=1

        numpad.rowconfigure(
                3
                ,weight=1
                )
        slash=tk.Button(numpad
                ,text='/'
                ,font=button_font
                )
        slash.grid(row=3
                ,column=0
                ,sticky='nsew'
                )
        slash.bind('<Button-1>'
                ,self.slash_click)
        zero=tk.Button(numpad
                ,text='0'
                ,font=button_font
                )
        zero.grid(row=3
                ,column=1
                ,sticky='nsew'
                )
        zero.bind('<Button-1>'
                ,self.num_click)
        back=tk.Button(numpad
                ,text='<-'
                ,font=button_font
                )
        back.grid(row=3
                ,column=2
                ,sticky='nsew'
                )

        back.bind('<Button-1>'
                ,self.back_click
                )

        self.display.bind('<Key>'
                ,self.key_dispatch
                )
        self.update_idletasks()

        self.display.icursor(tk.END)

        return self.display

    def validDateParts(self,ds):
        ##TODO: ?find a cleaner way to
        ##      validate partial dates
        ymd=ds.split('/')
        print ymd

        if len(ymd[-1])==0:
            return True

        if len(ymd)==3:
            if ((MIN_YEAR <= int(ymd[0]) <= MAX_YEAR) and
                    (1 <= int(ymd[1]) <= 12) and
                    (1 <= int(ymd[2]) <= 31)  or
                    (len(ymd[2])==1 and ymd[2]=='0')
                ):
                return True
            else:
                return False

        elif len(ymd)==2:
            if ((MIN_YEAR <= int(ymd[0]) <= MAX_YEAR) and
                    (1 <= int(ymd[1]) <= 12) or
                    (len(ymd[1])==1 and ymd[1]=='0')
                ):
                return True
            else:
                return False

        elif len(ymd)==1:
            if (len(ymd[0])<4 or
                    (MIN_YEAR <= int(ymd[0]) <= MAX_YEAR)
                ):
                return True
            else:
                return False

        return True

    def key_dispatch(self,e):
        x=self._value.get()
        if e.char in '1234567890':
            if self.validDateParts(x+e.char):
                self._value.set(x+e.char)
                self.display.icursor(tk.END)

        elif e.char=='/':
            if x.count('/')<2:
                if self.validDateParts(x):
                        self._value.set(
                        x+e.char
                        )
            self.display.icursor(tk.END)

        elif e.keycode == 8:
            self._value.set(x[:-1])
            self.display.icursor(tk.END)

        elif e.keycode==13:
            self.ok()

        else:
            print e.char,e.keycode

        return 'break'

    def validate(self):
        d=self._value.get()
        try:
            r=datetime.datetime.strptime(
                    d
                    ,'%Y/%m/%d'
                    )
            self.result=r.strftime(
                    '%Y/%m/%d'
                    )

            return True

        except:
            self.result=None
            return False

    def num_click(self,e):
        x=e.widget.cget('text')
        y=self._value.get()
        if self.validDateParts(y+x):
            self._value.set(y+x)
            self.display.icursor(tk.END)

    def back_click(self,e):
        val=self._value.get()
        self._value.set(0)
        self._value.set(val[:-1])
        self.display.icursor(tk.END)

    def slash_click(self,e):
        val=self._value.get()
        if val.count('/')<2:
            if self.validDateParts(val):
                self._value.set(val+'/')
                self.display.icursor(tk.END)


if __name__=='__main__':
    def set_ent(e):
        v=e.widget.get()
        numpad=Datepad(root,v
                ,title='Fred')
        numpad.show()
        #root.wait_window(numpad)
        if numpad.result:
            e.widget.delete(
                0
                ,tk.END
                )
            e.widget.insert(
                0
                ,numpad.result
                )
        numpad = None

    def printkey(e):
        print e.char,
        print ',',e.keysym,
        print ',',e.keycode

    def destroy(e):
        root.destroy()

    root=tk.Tk()
    entry=tk.Entry(root)
    entry.grid()
    entry.insert(0,'2009/11/30')
    entry.bind('<Button-1>',set_ent)
    root.bind('<Key>'
            ,destroy)
    entry.focus_set()
    root.mainloop()
