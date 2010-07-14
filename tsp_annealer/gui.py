#!/usr/bin/python
#gui.py

import Tkinter as tk
import tkMessageBox
import sys,time
from math import sqrt
import Queue,threading,random

##TODO: combine GuiThread and ThreadedGUI into one

class xGuiThread:
    """
    Helper class to create a gui in its own thread

    Instantiate with a guiClass and any required guiArgs
    """
    def __init__(self,guiClass,*guiArgs,**guiKArgs):
        self.guiClass=guiClass
        self.guiArgs=guiArgs
        self.guiKArgs=guiKArgs

    def start(self):
        """
        Set "start" as the thread target to create the gui
        """
        root=tk.Tk()
        self.gui=self.guiClass(root,*self.guiArgs,**self.guiKArgs)
        root.mainloop()

class ThreadedGUI(tk.Tk):
    def __init__(self,
            width=320,height=240,
            xScale=2.0,yScale=2.0,
            padx=15,pady=15,pointSize=6,lineWidth=2):
        tk.Tk.__init__(self)

        #self.root=root
        self.xScale=xScale
        self.yScale=yScale
        self.width=width*self.xScale
        self.height=height*self.yScale
        self.padx=padx
        self.pady=pady
        self.pointSize=pointSize
        self.lineWidth=lineWidth

        #problem setup variables
        self.problemSource = tk.StringVar()
        self.problemSource.set('random')
        self.numCities = tk.IntVar()
        self.numCities.set(50)
        self.filePath = tk.StringVar()

        self.startTemp = tk.DoubleVar()
        self.endTemp = tk.DoubleVar()
        self.alpha = tk.DoubleVar()
        self.reps = tk.IntVar()
        self.target = tk.DoubleVar()
        self.randomSeed = tk.DoubleVar()

        self.startTemp.set(800.0)
        self.endTemp.set(1.0)
        self.alpha.set(0.975)
        self.reps.set(300)
        self.target.set(0.0)
        self.randomSeed.set(1.0)

        #status label variables
        self.runTime=tk.StringVar()
        self.currentTemp=tk.StringVar()
        self.currentEnergy=tk.StringVar()
        self.bestEnergy=tk.StringVar()
        self.currentReps = tk.StringVar()

        self.iterCount=0 #track the total number of redraws
        self.clickCount=0 #mouse click counter for swapCities

        self.route=[]

        self.ctlQ=Queue.Queue()
        self.drawQ=Queue.Queue()

    def start(self):
        print 'Start GUI'
        self.initGui()
        self.after(10,self.checkQ)
        print 'GUI mainloop'
        self.mainloop()

    def initGui(self):
        print 'Init GUI'

        self.rowconfigure(0,weight=1)
        self.columnconfigure(0,weight=1)
        
        self.mainFrame = tk.Frame(self,padx=2,pady=2)
        self.mainFrame.grid(sticky='nsew')
        self.mainFrame.rowconfigure(1,weight=1)
        self.mainFrame.columnconfigure(1,weight=1)

        #Problem options frame
        self.problemFrame = tk.LabelFrame(self.mainFrame,text='Load Points',
                padx=4,pady=4)
        self.problemFrame.grid(row=0,column=0,columnspan=2,sticky='new',
                padx=2)
        self.problemFrame.columnconfigure(2,weight=1)

        self.canvasFrame=tk.Frame(self.mainFrame,relief='groove',bd=2)
        self.canvasFrame.grid(row=1,column=1,sticky='nsew',padx=2,pady=8)
        self.canvasFrame.grid_rowconfigure(0,weight=1)
        self.canvasFrame.grid_columnconfigure(0,weight=1)
        
        leftPanel = tk.Frame(self.mainFrame)
        leftPanel.grid(row=1,column=0,sticky='nse')
        leftPanel.rowconfigure(2,weight=1)
        
        self.annealingOptionsFrame = tk.LabelFrame(leftPanel,
                text='Annealing Options',padx=4,pady=4)
        self.annealingOptionsFrame.grid(row=1,column=0,sticky='new',
                padx=2)
        #self.annealingOptionsFrame.grid_rowconfigure(8,weight=1)
        self.annealingOptionsFrame.grid_columnconfigure(1,weight=1)

        self.progressFrame = tk.LabelFrame(leftPanel,
                text='Annealing Progress')
        self.progressFrame.grid(row=2,column=0,sticky='new',
                padx=2)
        self.progressFrame.columnconfigure(1,weight=1)

        self.buttonFrame = tk.Frame(leftPanel,pady=3)
        self.buttonFrame.grid(row=3,column=0,sticky='sew',pady=6,padx=4)
        self.buttonFrame.columnconfigure(0,weight=1)
        self.buttonFrame.columnconfigure(1,weight=1)
        self.buttonFrame.columnconfigure(2,weight=2)
        
        self.statusBarFrame = tk.Frame(self.mainFrame)
        self.statusBarFrame.grid(row=2,column=0,columnspan=2,sticky='sew')
        self.statusBarFrame.grid_columnconfigure(0,weight=1)

        #Problem options widgets
        self.optRandom = tk.Radiobutton(self.problemFrame,
                text = 'Random',variable=self.problemSource,
                value = 'random'
                )
        self.optRandom.grid(row=0,column=0,sticky='nw')

        self.entryRandomPointCount = tk.Entry(self.problemFrame,
                textvariable=self.numCities,width=4)
        self.entryRandomPointCount.grid(row=0,column=1,sticky='w',padx=3)

        self.optFromFile = tk.Radiobutton(self.problemFrame,
                text = 'From File',variable=self.problemSource,
                value = 'file'
                )
        self.optFromFile.grid(row=1,column=0,sticky='nw')

        self.entFilePath = tk.Entry(self.problemFrame,
                textvariable=self.filePath)
        self.entFilePath.grid(row=1,column=1,
                columnspan=2,sticky='ew',padx=3)

        self.btnFilePath = tk.Button(self.problemFrame,
                text='Browse',command=self.btnFilePath_click
                )
        self.btnFilePath.grid(row=1,column=3)

        #---Annealing options
        lblStartTemp = tk.Label(self.annealingOptionsFrame,text='Start Temp:',
                anchor='w')
        lblStartTemp.grid(row=0,column=0,sticky='new')
        self.entStartTemp = tk.Entry(self.annealingOptionsFrame,
                textvariable=self.startTemp,width=6)
        self.entStartTemp.grid(row=0,column=1,sticky='sew')

        lblEndTemp = tk.Label(self.annealingOptionsFrame,text='End Temp:',
                anchor='w')
        lblEndTemp.grid(row=1,column=0,sticky='new')
        self.entEndTemp = tk.Entry(self.annealingOptionsFrame,
                textvariable=self.endTemp,width=6)
        self.entEndTemp.grid(row=1,column=1,sticky='sew')

        lblReps = tk.Label(self.annealingOptionsFrame,text='Reps:',
                anchor='w')
        lblReps.grid(row=2,column=0,sticky='new')
        self.entReps = tk.Entry(self.annealingOptionsFrame,
                textvariable=self.reps,width=6)
        self.entReps.grid(row=2,column=1,sticky='sew')

        lblAlpha = tk.Label(self.annealingOptionsFrame,text='Alpha:',
                anchor='w')
        lblAlpha.grid(row=3,column=0,sticky='new')
        self.Alpha = tk.Entry(self.annealingOptionsFrame,
                textvariable=self.alpha,width=6)
        self.Alpha.grid(row=3,column=1,sticky='sew')

        lblTarget = tk.Label(self.annealingOptionsFrame,text='Target:',
                anchor='w')
        lblTarget.grid(row=5,column=0,sticky='new')
        self.Target = tk.Entry(self.annealingOptionsFrame,
                textvariable=self.target,width=6)
        self.Target.grid(row=5,column=1,sticky='sew')
        
        lblSeed = tk.Label(self.annealingOptionsFrame,text='Seed:',
                anchor='w')
        lblSeed.grid(row=6,column=0,sticky='new')
        self.Seed = tk.Entry(self.annealingOptionsFrame,
                textvariable=self.randomSeed,width=6)
        self.Seed.grid(row=6,column=1,sticky='sew')

        #---Progress Widgets
        r=0
        
        lblCurTemp=tk.Label(self.progressFrame,text='Temp:',anchor='e'
                ).grid(row=r,column=0,sticky='w')
        self.lblCurTemp = tk.Label(self.progressFrame,
                textvariable=self.currentTemp)
        self.lblCurTemp.grid(row=r,column=1,sticky='w')

        r+=1
        lblCurEnergy=tk.Label(self.progressFrame,text='Energy:',anchor='e'
                ).grid(row=r,column=0,sticky='w')
        self.lblCurEnergy = tk.Label(self.progressFrame,
                textvariable=self.currentEnergy)
        self.lblCurEnergy.grid(row=r,column=1,sticky='w')
        
        r+=1
        lblBest=tk.Label(self.progressFrame,text='Best:',anchor='e'
                ).grid(row=r,column=0,sticky='w')
        self.lblBestEnergy = tk.Label(self.progressFrame,
                textvariable=self.bestEnergy,)                
        self.lblBestEnergy.grid(row=r,column=1,sticky='w')
        
        r+=1
        lblReps=tk.Label(self.progressFrame,text='Reps:',anchor='e'
                ).grid(row=r,column=0,sticky='w')   
        self.lblCurrentReps = tk.Label(self.progressFrame,
                textvariable=self.currentReps)
        self.lblCurrentReps.grid(row=r,column=1,sticky='w')

        r+=1
        lblRunTime=tk.Label(self.progressFrame,text='Time:',anchor='e'
                ).grid(row=r,column=0,sticky='w')

        self.lblRunTime = tk.Label(self.progressFrame,
                textvariable=self.runTime)
        self.lblRunTime.grid(row=r,column=1,sticky='w')
        
        #---Buttons
        self.btnStart=tk.Button(self.buttonFrame,text='Start',
                command=self.click_start)
        self.btnStart.grid(row=0,column=0,sticky='ew')

        self.btnStep=tk.Button(self.buttonFrame,text='Step',
                command=self.click_step)
        self.btnStep.grid(row=0,column=1,sticky='ew')

        self.btnExit=tk.Button(self.buttonFrame,text='Exit',
                command=self.click_exit)
        self.btnExit.grid(row=0,column=2,sticky='ew')

        #---Canvas
        self.canvas=tk.Canvas(self.canvasFrame,
                width=self.width+self.padx*2,
                height=self.height+self.pady*2,
                bg='white'
                )
        self.canvas.grid(row=0,column=0,sticky='nsew')

        self.canvas.bind("<Button-1>", self.swapSelect)

        #---Status Bar
        self.lblStatus=tk.Label(self.statusBarFrame,anchor='w',
                relief='sunken',)
        self.lblStatus.grid(row=0,column=0,sticky='ew')

        self.protocol("WM_DELETE_WINDOW", self.kill)

    def kill(self):
        self.ctlQ.put(Message('exit'))
        self.after(500,self.destroy)

    def btnFilePath_click(self):
        pass

    def click_start(self):
        data = {
                'beginTemp':self.startTemp.get()
                ,'endTemp':self.endTemp.get()
                ,'alpha':self.alpha.get()
                ,'reps':self.reps.get()
                ,'points':self.numCities.get()
                ,'target':self.target.get()
                }

        self.ctlQ.put(Message('start',data))

    def click_exit(self):
        self.kill()

    def click_step(self):
        self.ctlQ.put(Message('step'))

    def click_continue(self):
        self.ctlQ.put(Message('continue'))

##    def click_pause(self):
##        self.ctlQ.put('pause')

    def drawRoutes(self,pntList,dist,msg,running,drawIDs=False):

        self.pntList=pntList

        lineWidth = self.lineWidth
        pointSize = self.pointSize

        if not running:
            status='%s (")' % msg
            self.lblStatus.configure(text=status)
            return

        else: status='%s (>)' % msg

        if pntList:
            px=self.padx
            py=self.pady
            #keep a running tally of all routes drawn
            self.iterCount+=1
            #convert the points to routes

            self.canvas.delete(tk.ALL)

            for p1,p2 in zip(pntList,pntList[1:] + [pntList[0]]):
                self.canvas.create_line(
                    p1[0]*self.xScale+px,p1[1]*self.yScale+py,
                    p2[0]*self.xScale+px,p2[1]*self.yScale+py,
                    fill="blue", dash=(4, 4),
                    width=lineWidth
                    )

            #draw each vertex and edge in the route
            for i,pnt in enumerate(pntList):
                item=self.canvas.create_oval(
                        (pnt[0]*self.xScale+px-pointSize/2,
                        pnt[1]*self.yScale+py-pointSize/2,
                        pnt[0]*self.xScale+px+pointSize/2,
                        pnt[1]*self.yScale+py+pointSize/2,),
                        fill='red',outline='red',
                        tags=str(i),
                        )
                self.canvas.itemconfig(item, tags=(str(i),))
                #draw the point id
                if drawIDs:
                    self.canvas.create_text(
                            (pnt[0]*self.xScale+px+pointSize+1,
                            pnt[1]*self.yScale+py+pointSize+1),
                            fill='red',text=i,anchor='ne'
                            )
            #place the count and current distance
            #x=self.width
            #y=0
            #self.canvas.create_text((x,y),text='(%d) %.2f' % \
            #        (self.iterCount,dist),anchor='ne')

        #update the status
        #self.lblStatus.configure(text=status)

    def swapSelect(self,event):
        x=self.canvas.canvasx(event.x)
        y=self.canvas.canvasy(event.y)
        #print x,y
        items=self.canvas.find_enclosed(x-5,y-5,x+5,y+5)
        #item=self.canvas.find_closest(x,y)
        if len(items)<1: return
        #print items
        item=items[0]
        for item in items:
            try:
                int(self.canvas.gettags(item)[0])
                break
            except:
                continue
        if not item: return
        if self.clickCount==0:
            #print (self.canvas.gettags(item))
            self.canvas.itemconfig(item,fill='green',outline='green')
            self.i=int(self.canvas.gettags(item)[0])
            self.clickCount+=1
            return
        if self.clickCount==1:
            #print (self.canvas.gettags(item))
            self.canvas.itemconfig(item,fill='blue',outline='blue')
            self.j=int(self.canvas.gettags(item)[0])
            self.clickCount=0


        #print self.i,self.j
        self.pntList[self.i],self.pntList[self.j]=self.pntList[self.j],self.pntList[self.i]

        dist=self.routeDist()

        self.drawRoutes(self.pntList,dist,'',True)

    def routeDist(self):
        dist=0
        for i in xrange(-1,len(self.pntList)-1):
            j=i+1
            dist+=self.calcDist(self.pntList[i],self.pntList[j])
        return dist

    def calcDist(self,a,b):
        dx=a[0]-b[0]
        dy=a[1]-b[1]
        return sqrt(dx*dx+dy*dy)

    def checkQ(self):
        """
        check for something to do in the draw Queue
        """
        try:
            msg=self.drawQ.get_nowait()

        except Queue.Empty:
            #self.update_idletasks()
            time.sleep(.001)
            self.after_idle(self.checkQ)
            return

        rteList=msg.solution
        dist=msg.currentEnergy
        stat='%.1f (%.1f)' % (msg.currentEnergy,msg.bestEnergy)
        running=msg.running

        self.drawRoutes(rteList,dist,stat,running,drawIDs=True)
        
        self.runTime.set('%.1f' % msg.runTime)
        self.currentTemp.set(  '%.2f' % msg.currentTemp)
        self.currentEnergy.set('%.2f' % msg.currentEnergy)
        self.bestEnergy.set(   '%.2f' % msg.bestEnergy)
        self.currentReps.set(  '%d' % msg.reps)

        #time.sleep(.001)
        #self.update_idletasks()
        self.after_idle(self.checkQ)

class Worker:
    """
    Framework for a threaded worker
    """
    def __init__(self,step=False,
            rX=(0,200),rY=(0,200),
            pnts=20):

        self.controlQueue=Queue.Queue()
        self.statusQueue=Queue.Queue()

        self.step=step
        i=0
        self.points=[]
        while i<pnts:
            x=random.randint(rX[0],rX[1])
            y=random.randint(rY[0],rY[1])
            self.points.append((x,y))
            i+=1

    def start(self):
        self.running=True
        self.step=False
        self.__work()

    def __workCtl(self):
        #if not self.running or self.step:
        if self.step:
            #block until there is a contro message
            #then handle it
            msg=self.controlQueue.get()
            return self.__handleCtl(msg)
        else:
            #return immediately
            #only used by __work to
            try:
                msg=self.controlQueue.get_nowait()
            except Queue.Empty:
                return True
            return self.__handleCtl(msg)

    def __handleCtl(self,msg):
        if msg.type=='continue':
            #print 'worker got continue'
            self.running=True
            self.step=False
            return True
        elif msg.type=='stop':
            #print 'worker got stop'
            self.running = False
            return False
        elif msg.type=='step':
            #print 'worker got step'
            self.step=True
            self.running=True
            return True
        else:
            #print 'worker got unknown ctl %s' % ctl
            return True

    def __work(self,):
        #print 'genRandom'
        dist=0
        while self.__workCtl():
            if self.running:
                w=self.getWork()
                dist=self._calcDist(self.points)
            self.statusQueue.put((self.points,dist,"current (best)",self.running))
            #time.sleep(.002)

    def getWork(self):
        w=random.shuffle(self.points)

    def _calcDist(self,pnts):
        dist=0
        for i in xrange(len(pnts)):
            j=i-1

            dx=abs(pnts[j][0]-pnts[i][0])
            dy=abs(pnts[j][1]-pnts[j][1])
            dist+=sqrt(dx**2+dy**2)
        return dist

class Message:
    def __init__(self,msgType,data=None):
        self.type = msgType
        self.data = data

    def __str__(self):
        return '%s\n%s' % (self.type,self.data)

class ControlMain:
    def __init__(self,
            gui,
            worker,
            problemClass):

        ##TODO: can the gui draw q be pipelined direct to the worker?

        self.gui = gui
        self.worker = worker
        self.problemClass = problemClass

        self.running = False
        self.step = False

        #start the gui and worker in seperate threads
        self.guiThread=threading.Thread(target=self.gui.start)
        self.workerThread=threading.Thread(target=self.worker.start)

        print 'Start threads'
        self.guiThread.start()
        time.sleep(.05)
        self.workerThread.start()

    def end(self):
        """
        Terminate the Q loop and stop the worker
        The gui handles its own termination
        """
        self.running=False
        #self.workerCtlQ.put('stop')
        #wait while the worker gets the message to stop
        while self.workerThread.isAlive():
            time.sleep(.1)
        print 'Worker Stopped'

    def mainLoop(self):
        ##TODO: simplify Qs
        """
        mainLoop functions as the translator between the worker and the gui
        status updates from the worker are converted into drawing requests for
        the gui.  The gui's control outputs are passed to the worker.
        """
        print 'Enter control mainLoop'
        #if running manage the Qs

        self.running = True
        #self.worker.controlQueue.put(Message('go'))

        while self.running:
            #relay messages between the gui and worker threads
            try:
                #check the jobQ without blocking
                msg=self.worker.statusQueue.get_nowait() #(0,.1)
                ##TODO: process the job results
                #if there is something to do, pass it to the gui
                ##TODO: from the job, prepare the gui package
                self.gui.drawQ.put(msg)

                #clear the status Queue
                while 1:
                    self.worker.statusQueue.get_nowait()

            except Queue.Empty:
                pass

            try:
                #check the gui ctlQ without blocking
                msg=self.gui.ctlQ.get_nowait() #(0,.1)
                ##TODO: process the control message
                #if there is a control message, pass it to the worker
                #if the message is "stop" call the end command first
                #if msg=='stop':
                #    self.end()
                if msg.type == 'start':
                    ##TODO: this import is too awkward
                    import annealer2
                    locations = annealer2.randomLocations(
                            msg.data['points'],
                            320,240)
                    problem = self.problemClass(locations)
                    msg.data['problem'] = problem

                elif msg.type == 'exit':
                    self.running = False

                self.worker.controlQueue.put(msg)

            except Queue.Empty:
                pass

            #wait and loop recursively
            time.sleep(.001)

        print 'exit control mainloop'
        #We're done

if __name__=='__main__':

    import annealer2
    annealer2.test()

##    wArgs={'rX':(0,180),'rY':(0,90),'pnts':20}
##    worker = Worker(wArgs)
##
##    gui = ThreadedGUI()
##
##    test=ControlMain(gui,worker)
##    test.mainLoop()
    #sys.exit()

##    root=tk.Tk()
##    gui=ThreadedGUI(root,Queue.Queue(),Queue.Queue(),100,100)
##    root.mainloop()
