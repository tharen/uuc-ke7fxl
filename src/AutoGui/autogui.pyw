#autogui.py

import Tkinter as tk
import ImageTk,Image,time
import ConfigParser


class GUI(tk.Tk):
    def __init__(self,parent):
        tk.Tk.__init__(self,parent)#width=800,height=480)
        #store references to loaded applications
        self.apps={}
        #open in an undecorated, borderless window
        self.overrideredirect(1)
        #set the window to a fixed size and position
        self.wm_geometry("800x480+0+0")
        #read in the configuration file
        self.ini=ConfigParser.ConfigParser()
        self.ini.read('config.ini')
        self.fullscreen=False
        
        #set the default background color
        self.bgColor=self.ini.get('colors','background')
        #self.option_add('*Radiobutton*Background',self.bgColor)
        #self.option_add('*Radiobutton*selectcolor','green')
        #set the window background to a contrasting color to expose gui gaps
        self.config(bg='black',bd=2)#self.bgColor,bd=0)
        #make it stretchy so frames fill their space
        self.grid_columnconfigure(1,weight=1)
        self.grid_rowconfigure(0,weight=1)
        #create the left button frame and application frame
        self.leftButtonFrame=tk.Frame(self,highlightthickness=0,bd=0,bg=self.bgColor)
        self.rightButtonFrame=tk.Frame(self,highlightthickness=0,bd=0,bg=self.bgColor)
        self.appFrame=tk.Frame(self,highlightthickness=0,bd=0,bg=self.bgColor)
        self.leftButtonFrame.grid(row=0,column=0,sticky='nsw')
        self.rightButtonFrame.grid(row=0,column=2,sticky='nse')
        self.appFrame.grid(row=0,column=1,sticky='nsew')
        self.appFrame.grid_rowconfigure(0,weight=1)
        self.appFrame.grid_columnconfigure(0,weight=1)
        
        #store the value of the radiobutton option
        self.appOption=tk.StringVar()
        
        frame=tk.Frame(self,bg=self.bgColor,)
        frame.grid(row=1,column=0,columnspan=3,sticky='ew')
        frame.grid_columnconfigure(0,weight=1)
        font=self.ini.get('init','statusfont')
        fsBtn=tk.Button(frame,text='fs',relief='flat',bg=self.bgColor,
                font=font,command=self.toggleFullScreen)
        fsBtn.grid(row=0,column=1)
        self.statusbar=StatusFrame(self,frame)
        self.statusbar.grid(row=0,column=0,sticky='ew')
        self.initApps()
        
        self.bind('<Key>',self.keyEvent)
    
    def keyEvent(self,event):
        print event.keysym
        if event.keysym == 'L1': #F11
            self.toggleFullScreen()
    
    def toggleFullScreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.leftButtonFrame.grid_remove()
            self.rightButtonFrame.grid_remove()
        else:
            self.leftButtonFrame.grid()
            self.rightButtonFrame.grid()
            
    def __gridButtons(self,parent,alignment):#,btnValue='',btnText='',done=False):
        #open the button up/down images
        up_img = Image.open('tabup_90x70.png')
        down_img = Image.open('tabdown_90x70.png')
        #retain reference so PIL doesn't garbage collect it
        #rotate the button for right side
        if alignment=='right':
            sticky='ne'
            upbtn=self.rightBtnUpImage=ImageTk.PhotoImage(up_img.rotate(180))
            downbtn=self.rightBtnDownImage=ImageTk.PhotoImage(down_img.rotate(180))
            apps = self.ini.items('rightapps')
            
        else:
            sticky='nw'
            upbtn=self.leftBtnUpImage=ImageTk.PhotoImage(up_img)
            downbtn=self.leftBtnDownImage=ImageTk.PhotoImage(down_img)
            apps=self.ini.items('leftapps')
        
        #set the font for the radiobuttons
        font=self.ini.get('init','appbuttonfont')
        self.option_add('*Radiobutton*Font',font)
        #load the buttons and initiate the snapins
        for btnValue,appConfigs in apps:
            row,appClassName,btnText,description,options=appConfigs.split(',')
            radio=tk.Radiobutton(parent,text=btnText,
                    compound='center',image=upbtn,selectimage=downbtn,
                    bg=self.bgColor,selectcolor=self.bgColor,
                    bd=0,offrelief='flat',indicatoron=0,highlightthickness=0,
                    variable=self.appOption,value=btnValue,command=self.appSelect)
            radio.grid(row=row,sticky=sticky)
            #config classname must be equal to a class name loaded into globals
            appClass=globals()[appClassName]
            #initialize the snapin
            app=appClass(self,self.appFrame,description,self.bgColor)
            #add it to the snapin reference dict
            self.apps[btnValue]=app
            #tell the app which button controls it
            app.button=radio

    def initApps(self):
        self.__gridButtons(self.leftButtonFrame,'left')
        self.__gridButtons(self.rightButtonFrame,'right')
        defApp=self.ini.get('init','defaultapp')
        self.appOption.set(defApp)
        self.appSelect()
    
    def showApp(self,app):
        for a in self.apps.keys():
            self.statusbar.clearStatus()
            self.apps[a].hide()
        #try: self.apps[app].show()
        #except: pass
        self.apps[app].show()
        
    def appSelect(self):
        app = self.appOption.get()
        print app
        if app == 'exit':
            self.shutdown()
        self.showApp(app)
    
    def shutdown(self):
        self.quit()

class AppFrame(tk.Frame):
    def __init__(self,root,parent,description,bgColor):
        tk.Frame.__init__(self,parent,bg=bgColor,bd=0,relief='flat')
        self.grid(row=0,column=0,sticky='nsew')
        self.grid_rowconfigure(0,weight=1)
        self.grid_columnconfigure(0,weight=1)
        self.parent=parent
        self.root=root
        self.button=None
        self.description=description
        #self.buttonText=''
        
    def hide(self):
        try:self.button.deselect()
        finally:self.grid_remove()
        
    def show(self):
        self.root.statusbar.setStatus(0,self.description)
        try:self.button.select()
        finally:self.grid()

##TODO: these would be seperate modules in the future
class MapApp(AppFrame):
    def __init__(self,root,parent,description,bgColor):
        AppFrame.__init__(self,root,parent,description,bgColor)
        self.canvas=tk.Canvas(self,bg='yellow',bd=0,highlightthickness=0,relief='flat')
        self.canvas.grid(row=0,column=0,sticky='nsew')

class TunesApp(AppFrame):
    def __init__(self,root,parent,description,bgColor):
        AppFrame.__init__(self,root,parent,description,bgColor)
        self.canvas=tk.Canvas(self,bg='gray',bd=0,relief='flat')
        self.canvas.grid(row=0,column=0,sticky='nsew')

class EmptyApp(AppFrame):
    """Generic class for non existent snapins"""
    def __init__(self,root,parent,description,bgColor):
        AppFrame.__init__(self,root,parent,description,bgColor)

class StatusFrame(tk.Frame):
    """Status bar at the bottom of the window
    Use instance.statusString<0-2>.set('status string') to modify the contents"""
    def __init__(self,root,parent,):
        tk.Frame.__init__(self,parent)
        self.parent=parent
        self.root=root
        bg=self.root.bgColor
        self.configure(background=bg)
        font=self.root.ini.get('init','statusfont')
        self.option_add('*Label*Font',font)
        self.statusString0=tk.StringVar()
        self.statusString1=tk.StringVar()
        self.statusString2=tk.StringVar()
        self.statusString0.set('Status1')
        self.statusString1.set('Status2')
        self.statusString2.set('Status3')
        self.configure(bg=bg)
        self.status1=tk.Label(self,textvariable=self.statusString0,
                bg=bg,anchor='w',relief='flat',bd=1,width=17).grid(row=0,column=0)
        self.status2=tk.Label(self,textvariable=self.statusString1,
                bg=bg,relief='flat',bd=1,anchor='center').grid(
                    row=0,column=1,sticky='ew')
        self.status3=tk.Label(self,textvariable=self.statusString2,
                bg=bg,relief='flat',bd=1,anchor='e',width=17).grid(row=0,column=2)
        self.grid_columnconfigure(1,weight=1)
    
    def setStatus(self,field,text):
        self.__dict__['statusString'+str(field)].set(text)

    def clearStatus(self,field=None):
        if field==None:
            for i in range(3):
                self.__dict__['statusString'+str(i)].set('')
        else: self.__dict__['statusString'+str(field)].set('')
        
if __name__=='__main__':
    app = GUI(None)
    app.mainloop()
    