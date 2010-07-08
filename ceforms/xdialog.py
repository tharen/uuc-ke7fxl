import Tkinter as tk
import tkFont
##TODO: list box class
##TODO: clear button
import os

class Dialog(tk.Toplevel):

    def __init__(self,parent
            ,title=None,**args):
        tk.Toplevel.__init__(self
                ,parent)
        
        self.transient(parent)
        
        if title:
            self.title(title)

        self.parent = parent

        self.result = args['defValue']
        
        self.columnconfigure(0
                ,weight=1)
        self.rowconfigure(0
                ,weight=1)
        
        body = tk.Frame(self)
        body.columnconfigure(0
                ,weight=1)
        body.rowconfigure(0
                ,weight=1)
        self.initial_focus = self.body(body,**args)
        body.grid(sticky='nsew')
        
        self.buttonbox()

        self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol(
                "WM_DELETE_WINDOW"
                , self.cancel
                )

        w = self.winfo_screenwidth()
        h = self.winfo_screenheight()
        
        if os.name.lower() != 'ce':
            w=640
            h=480

        self.wm_geometry(
                '%dx%d+%d+%d' % 
                (w,h-51,-4,4))

        self.wait_window(self)

    #
    # construction hooks

    def body(self, master, defValue):
        # create dialog body.  return widget that should have
        # initial focus.  this method should be overridden

        pass

    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons
        
        box = tk.Frame(self
                ,bg='black')
        box.columnconfigure(0
                ,weight=1)
        box.columnconfigure(2
                ,weight=1)

        w = tk.Button(box
                ,text="Cancel"
                ,height=1
                ,command=self.cancel
                )
                
        w.grid(column=2
                ,row=0
                ,sticky='sew'
                )
                
        w = tk.Button(box
                ,text="OK",
                height=1,
                command=self.ok
                ,default=tk.ACTIVE
                )
                
        w.grid(column=0
                ,row=0
                ,sticky='sew'
                )
        
        self.bind("&lt;Return>"
                ,self.ok)
        self.bind("&lt;Escape>"
                ,self.cancel)

        box.grid(column=0
                ,row=1
                ,sticky='sew'
                )
    #
    # standard button semantics

    def ok(self, event=None):
        if not self.validate():
            self.initial_focus.focus_set() # put focus back
            return

        self.withdraw()
        self.update_idletasks()

        self.apply()

        self.cancel()

    def cancel(self, event=None):
        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()
    #
    # command hooks

    def validate(self):
        return 1 # override

    def apply(self):
        pass # override

class InputList(Dialog):
    def body(self
            ,master
            ,defValue=0
            ,items=()
            ,**args
            ):
        self.slideY=0
        self.slideX=0
        
        #if os.name.lower() == 'ce':
        #    x,y = self.wm_maxsize()
        #else:
        #    x,y = 200,300
##        self.width=x*.6
##        self.height=y*37/64+1
        #self.geometry('+%d+%d' % (x/2-x*.6/2,3))
        
        #self.option_add('*Font',None)
        self.font = tkFont.Font(family='system',size=10,weight=tkFont.BOLD)
        self.grid_columnconfigure(0,weight=1)
        self.grid_columnconfigure(1,weight=1)
        self.grid_rowconfigure(1,weight=1)
        self.listbox=tk.Listbox(self,width=20,height=9,relief='flat',font=self.font)
        self.listbox.grid(row=1,column=0,columnspan=2,sticky='ew')
        self.setItems(items)
        
        self.listbox.bind('<Button-1>',self.mouseDown)
        self.listbox.bind('<ButtonRelease-1>',self.mouseUp)
        self.listbox.bind('<Double-Button-1>',self.ok)
        
    def mouseDown(self,event):
        self.slideY=event.y
        self.slideX=event.x
        self.listbox.bind('<Motion>',self.mouseMotion)
        #self.listbox.scan_mark(self.slideX,self.slideY)
        self.listbox.scan_mark(0,self.slideY)
    
    def mouseUp(self,event):
        self.listbox.unbind('<Motion>')
        self.slide=False
        self.listbox.scan_mark(0,self.slideY)
    
    def mouseMotion(self,event):
        #dy=self.slideY-event.y
        sel = self.listbox.curselection()
        x,y=event.x,event.y
        self.listbox.scan_dragto(0,y)
        self.slideY=y
        self.slideX=x
        self.listbox.scan_mark(0,y)
        self.listbox.selection_set(sel)
#xxx

    def setItems(self,items):
        for item in items:
            self.listbox.insert(tk.END,item)
    
    def apply(self):
        i = self.listbox.curselection()
        if len(i):
            val = self.listbox.get(i[0])
            self.result = val
        print self.result
        
class InputPad(Dialog):
    def body(self,master,defValue=0,dType='date',optKey='.',**args):
        
        self.dType = dType
        if os.name.lower() == 'ce':
            x,y = self.wm_maxsize()
        else:
            x,y = 200,300
        self.width=x*.6
        self.height=y*37/64+1
        self.geometry('%dx%d+%d+%d' % (self.width,self.height,x/2-x*.6/2,3))
        
        bodyFrame=tk.Frame(self,relief='flat',width=self.width,height=self.height)
        bodyFrame.grid(row=1,column=0,sticky='nsew')

        bodyFrame.grid_columnconfigure(0,weight=1)
        bodyFrame.grid_rowconfigure(1,weight=1)
        
        self.font = tkFont.Font(family='system',size=12,weight=tkFont.BOLD)
        self.option_add('*Font',self.font)
        
        self.myValue = tk.StringVar()
        #self.myValue.trace('w',self.validate)
        self.valEntry = tk.Entry(bodyFrame,textvariable=self.myValue,
                justify='right',relief='flat',
                )#validate='key',validatecommand=self.validate)#font=font)
        self.valEntry.grid(column=0,row=0,columnspan=1,sticky='ew')
        self.myValue.set(defValue)
        
        btnFrame = tk.Frame(bodyFrame)
        btnFrame.grid(row=1,column=0,columnspan=1,sticky='nsew')
        
        btnList=[[1,2,3],[4,5,6],[7,8,9],[optKey,0,'<']]
        
        r=0
        for row in btnList:
            btnFrame.grid_rowconfigure(r,weight=1)
            c=0
            for col in row:
                btnFrame.grid_columnconfigure(c,weight=1)
                btn=tk.Button(btnFrame,text=str(col))
                btn.bind('<Button-1>',self.btnClick)
                btn.grid(column=c,row=r,sticky='nsew')
                c+=1
            r+=1
        
        self.valEntry.select_range(0,tk.END)
    
    def validate(self,*args):
        if self.dType=='date':
            vals = self.myValue.get().split('/')
            if len(vals)<3: return False
            if int(vals[0])>12:
                f = 0
                l = len(vals[0])
                self.valEntry.focus()
                self.valEntry.select_range(f,l)
                return False
            if int(vals[1])>31:
                f = len(vals[0])+1
                l = len(vals[1])+f
                self.valEntry.focus()
                self.valEntry.select_range(f,l)
                return False
            if int(vals[2])>2008 or int(vals[2])<2007:
                f = len(vals[0])+len(vals[1])+2
                l = len(vals[2])+f
                self.valEntry.focus()
                self.valEntry.select_range(f,l)
                return False
            return True
        else:
            return True
            
    def btnClick(self,event):
        val=event.widget.cget('text')
        if val=='<':
            s=self.myValue.get()
            self.myValue.set(s[:-1])
            ##TODO: mod this for selections
            return
        if self.valEntry.select_present():
            f = self.valEntry.index(tk.SEL_FIRST)
            l = self.valEntry.index(tk.SEL_LAST)
            v = self.myValue.get()
            v = v[:f] + val + v[l:]
            self.myValue.set(v)
            i = self.valEntry.index(len(v[:f]+val))
            self.valEntry.select_clear()
            l = len(self.myValue.get())
            self.valEntry.icursor(i)
        else:
            self.valEntry.insert(tk.INSERT,val)
##            i = self.valEntry.index(tk.INSERT) + 1
##            self.valEntry.icursor(i)

    def apply(self,):
        self.result = self.myValue.get()
        print 'result',self.result

class AlphaPad(Dialog):
    def body(self,master,defValue='',**args):
        self.caps=False
        self.myValue=tk.StringVar()
        self.myValue.set(defValue)
        if os.name.lower() == 'ce':
            x,y = self.wm_maxsize()
        else:
            x,y = 200,300
        self.width=x
        self.height=y*37/64+1
        self.geometry('%dx%d+%d+%d' % (self.width,self.height,0,3))

        font = tkFont.Font(family='system',size=8,weight=tkFont.BOLD)
        self.option_add('*Font',font)

        frm=tk.Frame(self,relief='flat')
        frm.grid(row=1,column=0,sticky='new')
        frm.grid_columnconfigure(0,weight=1)

        self.valEntry=tk.Entry(frm,relief='flat',justify='left',textvariable=self.myValue)
        self.valEntry.grid(row=0,column=0,sticky='new')

        bodyFrame=tk.Frame(frm,relief='flat',width=self.width,height=self.height,bg='blue')
        bodyFrame.grid(row=1,column=0,sticky='new')
        
        #bodyFrame.grid_columnconfigure(15,weight=1)
        #bodyFrame.grid_rowconfigure(5,weight=1)
        keys=[['1','2','3','4','5','6','7','8','9','0'],
              ['q','w','e','r','t','y','u','i','o','p'],
              ['a','s','d','f','g','h','j','k','l','-'],
              ['z','x','c','v','b','n','m',',','(',')']]
        self.buttons=[]
        for r in range(len(keys)):
            row=keys[r]
            bodyFrame.grid_rowconfigure(r,weight=1)
            for c in range(len(row)):
                keyText=row[c]
                bodyFrame.grid_columnconfigure(c,weight=1)
                btn=tk.Button(bodyFrame,text=keyText,)
                self.buttons.append(btn)
                btn.grid(row=r,column=c,sticky='nsew')
                btn.bind('<Button-1>',self.btnClick)
        btn=tk.Button(bodyFrame,text='back')
        btn.grid(row=r+1,column=0,sticky='ew',columnspan=3)
        btn.bind('<Button-1>',self.btnClick)
        btn=tk.Button(bodyFrame,text='space')
        btn.grid(row=r+1,column=3,sticky='ew',columnspan=c-5)
        btn.bind('<Button-1>',self.btnClick)
        btn=tk.Button(bodyFrame,text='shift')
        btn.grid(row=r+1,column=c-2,sticky='ew',columnspan=3)
        btn.bind('<Button-1>',self.btnClick)
    def btnClick(self,event):
        val=event.widget.cget('text')
        if val=='back':
            s=self.myValue.get()
            self.myValue.set(s[:-1])
            ##TODO: mod this for selections
            return
        if val=='space':
            val=' '
        if val=='shift':
            self.caps=not self.caps
            #for b in self.buttons:
            #    if self.caps:
            #        b.configure(text=b.cget('text').upper())
            #    else:
            #        b.configure(text=b.cget('text').lower())
            return
        if self.caps:
            val=val.upper()
            #self.myValue.set('upper')
            self.caps=False
        if self.valEntry.select_present():
            f = self.valEntry.index(tk.SEL_FIRST)
            l = self.valEntry.index(tk.SEL_LAST)
            v = self.myValue.get()
            v = v[:f] + val + v[l:]
            self.myValue.set(v)
            i = self.valEntry.index(len(v[:f]+val))
            self.valEntry.select_clear()
            l = len(self.myValue.get())
            self.valEntry.icursor(i)
        else:
            self.valEntry.insert(tk.INSERT,val)
##            i = self.valEntry.index(tk.INSERT) + 1
##            self.valEntry.icursor(i)

    def apply(self,):
        self.result = self.myValue.get()
        print 'result',self.result

if __name__=='__main__':
    import sys
    app = tk.Tk()
    #test InputList
    stationList = []
    for i in range(50):
        stationList.append('%d - %d Station Really Really Long' % (i,i))
    root = InputList(app,defValue='test x - x',title='Testing',items=stationList)
    #test InputPad
#    root = InputPad(app,dType='date',defValue='1/5/07',format='dd/dd/dd',title='Testing',optKey='/')
#    app.mainloop()
    #test alphapad
#   root = AlphaPad(app,defValue='Some text',title='Testing')
    app.withdraw()
    app.mainloop()
    sys.exit()
