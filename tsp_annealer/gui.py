#!/usr/bin/python
#gui.py

import Tkinter as tk
import tkMessageBox
import sys,time
from math import sqrt
import Queue,threading,random

##TODO: combine GuiThread and ThreadedGUI into one

class GuiThread:
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

class ThreadedGUI:
    def __init__(self,root,ctlQ,drawQ,
            width,height,xScale=2.0,yScale=2.0,
            padx=15,pady=15):
        self.root=root
        self.root.rowconfigure(0,weight=1)
        self.root.columnconfigure(0,weight=1)
        self.frame=tk.Frame(self.root)
        self.frame.grid(sticky='nsew')
        self.frame.grid_rowconfigure(0,weight=1)
        self.frame.grid_columnconfigure(0,weight=1)
        self.ctlQ=ctlQ
        self.drawQ=drawQ
        self.xScale=xScale
        self.yScale=yScale
        self.width=width*self.xScale
        self.height=height*self.yScale
        self.padx=padx
        self.pady=pady
        self.canvas=tk.Canvas(self.frame,
                width=self.width+self.padx*2,
                height=self.height+self.pady*2
                )
        self.canvas.grid()
        self.bottomFrame = tk.Frame(self.frame)
        self.bottomFrame.grid(row=1,column=0,sticky='sew')
        self.bottomFrame.grid_columnconfigure(4,weight=1)
        self.btnStep=tk.Button(self.bottomFrame,text='Step',command=self.click_step)
        self.btnStep.grid(row=0,column=0)
        self.btnGo=tk.Button(self.bottomFrame,text='Go',command=self.click_go)
        self.btnGo.grid(row=0,column=1)
        self.btnPause=tk.Button(self.bottomFrame,text='Pause',command=self.click_pause)
        self.btnPause.grid(row=0,column=2)
        self.btnStop=tk.Button(self.bottomFrame,text='Stop',command=self.click_stop)
        self.btnStop.grid(row=0,column=3)
        self.lblStatus=tk.Label(self.bottomFrame,width=25,anchor=tk.E)
        self.lblStatus.grid(row=0,column=4,sticky='sew')

        self.canvas.bind("<Button-1>", self.swapSelect)

        self.root.protocol("WM_DELETE_WINDOW", self.kill)

        self.iterCount=0 #track the total number of redraws
        self.clickCount=0 #mouse click counter for swapCities

        self.route=[]

        self.checkQ()

    def kill(self):
        self.ctlQ.put('stop')
        self.root.after(500,self.root.destroy)

    def click_stop(self):
        self.ctlQ.put('stop')

    def click_step(self):
        self.ctlQ.put('step')

    def click_go(self):
        self.ctlQ.put('go')

    def click_pause(self):
        self.ctlQ.put('pause')

    def __drawRoutes(self,pntList,dist,msg,running,drawIDs=False):
        self.pntList=pntList
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
            rteList=[]
            n=len(pntList)
            for i in xrange(n-1):
                j=i+1
                rteList.append((pntList[i],pntList[j]))
            #the last edge is [n-1] to [0], back home
            rteList.append((pntList[-1],pntList[0]))

            pWidth=2
            self.canvas.delete(tk.ALL)
            i=0
            #draw each vertex and edge in the route
            for p1,p2 in rteList:
                self.canvas.create_line(
                        p1[0]*self.xScale+px,p1[1]*self.yScale+py,
                        p2[0]*self.xScale+px,p2[1]*self.yScale+py,
                        fill="blue", dash=(4, 4)
                        )
                item=self.canvas.create_oval(
                        (p1[0]*self.xScale+px-pWidth/2,
                        p1[1]*self.yScale+py-pWidth/2,
                        p1[0]*self.xScale+px+pWidth/2,
                        p1[1]*self.yScale+py+pWidth/2,),
                        fill='red',outline='red',
                        tags=str(i),
                        )
                self.canvas.itemconfig(item, tags=(str(i),))
                #draw the point id
                if drawIDs:
                    self.canvas.create_text(
                            (p1[0]*self.xScale+px+pWidth+1,
                            p1[1]*self.yScale+py+pWidth+1),
                            fill='red',text=i,anchor='ne'
                            )
                i+=1
            #draw the last point in the route
            self.canvas.create_polygon(
                        (p2[0]*self.xScale+px-pWidth/2,
                        p2[1]*self.yScale+py-pWidth/2,
                        p2[0]*self.xScale+px+pWidth/2,
                        p2[1]*self.yScale+py+pWidth/2,),
                        fill='red',outline='red',
                        )
            #place the count and current distance
            self.canvas.create_text((px,py),text='(%d) %.2f' % \
                    (self.iterCount,dist),anchor='nw')
        #update the status
        self.lblStatus.configure(text=status)
        #self.lblStatus.update_idletasks()

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

        self.__drawRoutes(self.pntList,dist,'',True)

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
        try: draw=self.drawQ.get_nowait()
        except Queue.Empty:
            self.root.update_idletasks()
            self.root.after(100,self.checkQ)
            return
        rteList=draw[0]
        dist=draw[1]
        msg=draw[2]
        running=draw[3]
        self.__drawRoutes(rteList,dist,msg,running)

        time.sleep(.005)
        self.root.update_idletasks()
        self.root.after_idle(self.checkQ)

class Worker:
    """
    Framework for a threaded worker
    """
    def __init__(self,ctlQ,jobQ,step=False,rX=0,rY=0,pnts=0):
        self.ctlQ=ctlQ
        self.jobQ=jobQ
        self.step=step
        i=0
        self.points=[]
        while i<pnts:
            x=random.randint(rX[0],rX[1])
            y=random.randint(rY[0],rY[1])
            self.points.append((x,y))
            i+=1

    def start(self):
        self.running=False
        self.step=False
        self.__work()

    def __workCtl(self):
        #if not self.running or self.step:
        if self.step:
            #block until there is a contro message
            #then handle it
            ctl=self.ctlQ.get()
            return self.__handleCtl(ctl)
        else:
            #return immediately
            #only used by __work to
            try: ctl=self.ctlQ.get_nowait()
            except Queue.Empty:
                return True
            return self.__handleCtl(ctl)

    def __handleCtl(self,ctl):
        if ctl=='go':
            #print 'worker got go'
            self.running=True
            self.step=False
            return True
        elif ctl=='stop':
            #print 'worker got stop'
            return False
        elif ctl=='step':
            #print 'worker got step'
            self.step=True
            self.running=True
            return True
        elif ctl=='pause':
            self.running=False
            return True
        else:
            #print 'worker got unknown ctl %s' % ctl
            return True

    def __work(self,):
        #print 'genRandom'
        dist=0
        while self.__workCtl():
            if self.running:
                #print 'working'
                w=self.getWork()
                dist=self._calcDist(self.points)
            self.jobQ.put((self.points,dist,"current (best)",self.running))
            time.sleep(.001)
##        while self.running:
##            w=self.getWork()
##            dist=self._calcDist(self.points)
##            self.jobQ.put((self.points,dist,"current (best)",self.running))
##            time.sleep(.1)
##            self.__workCtl()
##        self.__workCtl()

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

class ControlMain:
    def __init__(self,guiClass,threadedGUI,workerClass,workerKArgs,guiWidth,guiHeight,pnts):
        self.pnts=pnts
        self.workerCtlQ=Queue.Queue()
        self.workerJobQ=Queue.Queue()
        self.guiDrawQ=Queue.Queue()
        self.guiCtlQ=Queue.Queue()

        #start the gui in its own thread
        self.gui=guiClass(threadedGUI,self.guiCtlQ,self.guiDrawQ,
                guiWidth,guiHeight)

        self.guiThread=threading.Thread(target=self.gui.start)
        self.guiThread.start()

        #start the worker in it's own thread
        self.worker=workerClass(self.workerCtlQ,self.workerJobQ,**workerKArgs)

        self.thread1=threading.Thread(target=self.worker.start)
        self.thread1.start()

        self.running=True
        self.workerCtlQ.put('go')
        self.mainLoop()

    def end(self):
        """
        Terminate the Q loop and stop the worker
        The gui handles its own termination
        """
        self.running=False
        self.workerCtlQ.put('stop')
        #wait while the worker gets the message to stop
        while self.thread1.isAlive():
            time.sleep(.1)
        print 'Worker Stopped'

    def mainLoop(self):
        ##TODO: simplify Qs
        """
        mainLoop functions as the translator between the worker and the gui
        status updates from the worker are converted into drawing requests for
        the gui.  The gui's control outputs are passed to the worker.
        """
        #if running manage the Qs
        while self.running:
            try:
                #check the jobQ without blocking
                job=self.workerJobQ.get_nowait() #(0,.1)
                ##TODO: process the job results
                #if there is something to do, pass it to the gui
                ##TODO: from the job, prepare the gui package
                self.guiDrawQ.put(job)
            except Queue.Empty:
                pass
            try:
                #check the gui ctlQ without blocking
                ctl=self.guiCtlQ.get_nowait() #(0,.1)
                ##TODO: process the control message
                #if there is a control message, pass it to the worker
                #if the message is "stop" call the end command first
                if ctl=='stop': self.end()
                self.workerCtlQ.put(ctl)
            except Queue.Empty:
                pass
            #wait and loop recursively
            time.sleep(.001)

        print 'exit mainloop'
        #We're done

if __name__=='__main__':

    wArgs={'rX':(0,180),'rY':(0,90),'pnts':20}
    test=ControlMain(GuiThread,ThreadedGUI,Worker,wArgs,200,100,50)
    #sys.exit()

##    root=tk.Tk()
##    gui=ThreadedGUI(root,Queue.Queue(),Queue.Queue(),100,100)
##    root.mainloop()
