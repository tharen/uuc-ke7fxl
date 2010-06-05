#!/usr/bin/python
#annealer2.py


import time,sys
import Queue,threading

#import psyco
#psyco.full()

#import numpy
#rand=numpy.random.rand
#rint=numpy.random.randint
#shuffle=numpy.random.shuffle

import scipy

rand=scipy.random.rand
rint=scipy.random.randint
shuffle=scipy.random.shuffle
exp=scipy.math.exp

#import array
#array=array.array
#sum=numpy.sum

class AnnealerProfile:
    def __init__(self,*args,**kargs):
        """
        Report the performance stats of an annealer run by executing it
        under the hotshot profiler
        """
        import hotshot
        import hotshot.stats
        self.profile=hotshot.Profile('profile.txt')
        self.annealer=Annealer(*args,**kargs)
        #calibrate the profiler
        #self.profile.bias=self.profile.calibrate(10000)

    def start(self):
        self.profile.runctx('self.annealer.start()',globals(),locals())
        stats=hotshot.stats.load('profile.txt')
        stats=stats.sort_stats('time')
        stats.print_stats()

class Annealer:
    def __init__(self,problem,
            beginTemp=100,endTemp=1,
            alpha=0.95,reps=200,
            log='anneal.txt',**kargs):
        """
        Solve a combinatorial problem using simulated annealing

        Args
        ----
        #controlMessageQueue - Queue for controlling the annealer loop
        #statusCallback - Function for passing annealer status messages

        beginTempemp - Initial annealing tempature
        endTemp - Final anealing tempature
        alpha - Cooling rate between temperature steps
        reps - Number of alternatives to attempt at each temperature step

        log - Log file object
        """
        ##TODO: use the python logger builtin

##        import psyco
##        psyco.full()

        self.problem=problem #kargs['problem'](**kargs)#['problemKArgs'])

        #set optional annealling routine
        self.anneal=self.coolAfterReps

        self.beginTemp=beginTemp #beginning Temp
        self.endTemp=max(endTemp,0.0004) #ending temp
        self.alpha=alpha #cooling schedule
        self.reps=reps #solutions to test per temp cycle

        self.currentTemp=beginTemp

        self.log = open(log,'w')
        self.log.write('\n'.join(map(str,(self.beginTemp,self.endTemp,self.alpha,self.reps))))
        self.log.write('\n')
        self.log.flush()

        self.stepping = False
        self.running = False

        self.statusQueue = Queue.Queue()
        self.controlQueue = Queue.Queue()

    def setup(self,params):
        self.__dict__.update(params)
        self.currentTemp = self.beginTemp
        self.log.write('Parameters reset:\n')
        self.log.write('  %s = %s\n' % ('beginTemp',self.beginTemp))
        self.log.write('  %s = %s\n' % ('endT',self.endTemp))
        self.log.write('  %s = %s\n' % ('alpha',self.alpha))
        self.log.write('  %s = %s\n' % ('reps',self.reps))

    def postMsg(self,log=False,*args):
        """
        print and log a status message
        """
        return

        fmt=''
        for a in args:
            fmt+='%.4e  '
        if log:
            self.log.write(fmt % args+'\n')
        else:
            print fmt % args

    def start(self):

        self.running=True
        self.stepping=False

        #self.profile.runctx('self.start()',globals(),locals())
        self.anneal()

    def _continue(self):
        """
        Check the control queue and return False if there is a stop message

        In stepping mode the annealer loop is blocked until there is a
        message to advance or continue.
        """
        if self.stepping:
            #block until there is a message in the control queue
            msg=self.controlQueue.get()
            return self._handleControlMsg(msg)
        else:
            #return immediately if the control queue is empty
            try:
                msg=self.controlQueue.get_nowait()
                return self._handleControlMsg(msg)
            except Queue.Empty:
                return True

    def _handleControlMsg(self,msg):
        if msg.type=='continue':
            #print 'worker got go'
            self.running=True
            self.stepping=False
            return True

        elif msg.type=='stop':
            #print 'worker got stop'
            self.running = False
            self.stepping = False
            return False

        elif msg.type=='step':
            #print 'worker got step'
            self.stepping=True
            self.running=True
            return True

        else:
            #print 'worker got unknown ctl %s' % ctl
            return True

    def coolAfterReps(self,):
        """
        SA algorithm with proportional cooling after max repetitions
        """
        #get the first solution

        cS=self.problem.solution
        cE=self.problem.fitness
        bE=cE

        sol=self.problem.elaborate()
        #self.statusQ.put((sol,bE,'%.1f (%.1f) %.3f' % (cE,bE,self.currentTemp),self.running))
        self.statusQueue.put((sol,bE,'%.1f (%.1f) %.3f' % (cE,bE,self.currentTemp),True))

        #loop until temp is less than self.endT
        st=time.time()
        reps=0
        #loop until temperature is reduced to endTemp
        while self._continue():
            i=0
            #self.reps repetitions at current temperatur
            while 1:
                if i>=self.reps: break

                #get a new problem solution to test
                tE=self.problem.next()

                #Keep the new solution if it is the same or better
                #   than the current solution
                if tE<=cE:
                    self.postMsg(self.currentTemp,i,cE,tE,bE)
                    best=False
                    cE=tE
                    #if this is the best so far, upgrade it
                    if cE<=bE:
                        bE=cE
                        best=True

##                        sol=self.problem.elaborate()
##                        self.statusQ.put((sol,cE,'%.1f (%.1f) %.4f' % (cE,bE,self.currentTemp),self.running))
                    self.problem.keep(best)

                #if test is higher energy, select it by probability proportional to T
                else:
                    #calc the probability of selecting a less optimal solution
                    px=(cE-tE)#/ec*100 #difference in the two costs
                    p=exp(px/self.currentTemp) #Boltzman probability of acceptance
                    r=rand() #random 0-1
                    if r<=p: #probability is greater than some random value
                        self.postMsg(self.currentTemp,i,cE,tE,bE,px,p,r)
                        self.problem.keep()
                        cE=tE

                i+=1
            reps+=i
            #self.statusQ.put((self.cSol,self.cOV,'%.1f (%.1f) %.3f' % (self.cOV,self.bOV,self.currentTemp),self.running))
            sol=self.problem.elaborate()
            self.statusQueue.put((sol,cE,'%.1f (%.1f) %.4f' % (cE,bE,self.currentTemp),True))
            self.currentTemp*=self.alpha
            #exit the loop if endT has been reached
            if self.currentTemp<self.endTemp:break

        et=time.time()
        #self.statusQ.put((self.bSol,self.bOV,'%.1f (%.1f) %.3f' % (self.cOV,self.bOV,self.currentTemp),self.running))
        sol=self.problem.elaborate(True)
        self.statusQueue.put((sol,bE,'%.1f (%.1f) %.4f' % (cE,bE,self.currentTemp),True))

        print 'Annealling Done'
        print 'Best Energy:',bE
        print 'Total Reps:',reps
        print 'Solution Time:',ts(et-st)

        self.log.write(str(sol)+'\n')
        self.log.write(str(bE)+'\n')
        self.log.write(str(reps)+'\n')

        ##TODO: report the distance matrix

class TSP:
    """
    Travelling sales person routing class
    """
    def __init__(self,locations={},targetLength=0,
            writeDistMatrix=True,
            solutionAlgorithm='sequence_reverse',
            **kargs):
        """
        Locations - a dictionary of locations coordinates {id:(x,y),}
        targetLength - incase there is a defined optimal length
                other than 0

        All sequence operations are performed on the indices of locations

        A solution is just a list of location indices to travel to in order.
            The final trip closes the loop from the last list index to the
            first.
        """
##        import psyco
##        psyco.full()

        self.solutionAlgoritms = {
                'sequence_reverse':self._genSolution_seqrev,
                'single_position':self._genSolution_1PositionChange,
                'swap':self._genSolution_swap,
                'sequence_random':self._genSolution_seqrand
                }

        self.locations=locations
        self.targetLength=targetLength
        self.numLocs=len(self.locations)

        #calculate the distance matrix
        self.distMatrix=self._calcDistMatrix()
        #optionally write out the distance matrix
        if writeDistMatrix:
            distmat=open('distance.dat','w')
            self._writeDistMatrix(distmat)
            distmat.close()

        #prepare the first solution by shuffling the location keys
        self.solution=range(self.numLocs)
        shuffle(self.solution)

        #initialize the route length and fitness
        self.length=self._calcLength(self.solution)
        self.fitness=self._calcFitness()

        #copy the initial solution to the best
        ##Ideally these would converge at the end of the process
        ##making best values pointless and redundant
        self.bestSolution=self.solution[:]
        self.bestLength=self.length
        self.bestFitness=self.fitness

        #initialize the solution generator
        self.solutions=self.solutionAlgoritms[solutionAlgorithm]()

        #self.solutions=self._genSolution_swap()
        #self.solutions=self._genSolution_1PositionChange()
        #self.solutions=self._genSolution_seqrand()

    def _writeDistMatrix(self,outFile=sys.stdout):
        """
        Print a space delimited distance matrix
        """
        l=len(self.locations)

        h=''.join(['%-7s'] * l)
        #print h
        #print range(l)
        h = h % tuple(range(l))
        outFile.write('       %s\n' % h)

        #for x in xrange(0,l):
        for y in xrange(0,l):
            vals = ''.join(['%-7.1f'] * l)
            vals = vals % tuple(self.distMatrix[y])
            r = '%-7d%s\n' % (y,vals)
            outFile.write(r)

    def _calcDistMatrix(self):
        """
        Precalculate a distance matrix between all locations

        Build a distance matrix so that the distance between each location
        can be found either forward or backward.
        """
        l=len(self.locations)
        dm=scipy.zeros((l,l))
        for i in xrange(0,l):
            for j in xrange(0,l):
                dx=self.locations[i][0]-self.locations[j][0]
                dy=self.locations[i][1]-self.locations[j][1]
                d=(dx**2+dy**2)**0.5
                dm[(i,j)]=d
        return dm

    def next(self):
        """
        Return the next solution
        """
        #return self._genSolution_1PositionChange()
        #return self._genSolution_swap()
        #return self._genSolution_seqrev()
        #return self._genSolution_seqrand()
        return self.solutions.next()

    def _calcLength(self,sol):
        """
        Total round trip euclidean distance
        """
        n=self.numLocs-1
        l=self.locations
        dm=self.distMatrix

        return sum([dm[(sol[i],sol[i+1])] for i in xrange(-1,n)])

    def _calcFitness(self,len=0):
        """
        Absolute distance from the target
        """
        if not len:
            len=self.length
        return ((len-self.targetLength)**2)**0.5

    def keep(self,best=False):
        """
        keep the current solution
        """
        self.solution=self.testSolution[:]
        self.length=self.testLength
        self.fitness=self.testFitness
        if best:
            self.bestSolution=self.solution[:]
            self.bestLength=self.length
            self.bestFitness=self.fitness

    def _genSolution_1PositionChange(self):
        """
        Change the position of one location without disrupting
        the rest of the order
        """
        while 1:
            self.testSolution=self.solution[:]
            l=self.numLocs-1
            #two random points in the current solution
            i=rint(0,l)
            j=rint(0,l)
            while j==i:
                j=rint(0,l)
            self.testSolution.insert(j,self.testSolution.pop(i))

            self.testLength=self._calcLength(self.testSolution)
            self.testFitness=self._calcFitness(self.testLength)
            yield self.testFitness

    def _genSolution_swap(self):
        while 1:
            self.testSolution=self.solution[:]
            l=self.numLocs-1
            #to random points in the current solution
            i=rint(0,l)
            j=rint(0,l)
            while j==i:
                j=rint(0,l)
            self.testSolution[i],self.testSolution[j]= \
                self.testSolution[j],self.testSolution[i]

            self.testLength=self._calcLength(self.testSolution)
            self.testFitness=self._calcFitness(self.testLength)
            #yield self.testFitness
            yield self.testFitness

    def _genSolution_seqrev(self):
        """
        Generate solutions using a random sequence reversal method

        Reverses the direction of travel between two random points
            in the solution
        """
        while 1:
            ts=self.solution[:]
            l=self.numLocs
            #to random points in the current solution
            i=rint(0,l)
            j=rint(0,l)

            ##TODO: is this necessary
            #make sure the same index isn't picked
            #while j==i:
            #    j=rint(0,l)

            #order the two points
            if j<i:
                i,j=j,i
            p2=ts[i:j]
            #p2.reverse()
            ts[i:j]=p2[::-1]

            self.testSolution=ts
            l=self._calcLength(ts)
            self.testLength=l
            self.testFitness=self._calcFitness(l)
            yield self.testFitness
            #return self.testFitness

    def _genSolution_seqrand(self):
        """
        Solution generator randomizind a random sequence of locations
        """
        while 1:
            self.testSolution=self.solution[:]
            l=self.numLocs-1
            #to random points in the current solution
            i=rint(0,l)
            j=rint(0,l)
            while j==i:
                j=rint(0,l)
            #order the two points
            if j<i: i,j=j,i
            p2=self.testSolution[i:j]
            shuffle(p2)
            self.testSolution[i:j]=p2

            self.testLength=self._calcLength(self.testSolution)
            self.testFitness=self._calcFitness(self.testLength)
            yield self.testFitness
            #return self.testFitness

    def elaborate(self,best=False):
        """
        expand the solution to a list of locations
        """
        if best:
            sol=self.bestSolution
        else:
            sol=self.solution
        return [self.locations[i] for i in sol]

def randomLocations(numLocs,maxX,maxY,minX=0,minY=0,seed=1):
    """
    Return an array of randomly distributed coordinate pairs
    within
    """
    scipy.random.seed(seed)
    locations=scipy.zeros((numLocs,2))

    for loc in locations:
        loc[0]=rint(minX,maxX)
        loc[1]=rint(minY,maxY)

    return locations

def ts(s):
    """
    build a readable time string from seconds
    """
    tm=s/60
    h=int(tm/60)
    m=tm-h*60
    s=(m-int(m))*60
    return '%d:%d:%.3f' % (h,int(m),s)

if __name__=='__main__':
    import gui,os,pstats

    numCities=31
    w=320
    h=240

    problem = TSP(locations = randomLocations(numCities,w,h),
            targetLength = 0.0,
            writeDistMatrix = True,
            solutionAlgorithm='sequence_reverse')

    wArgs={ 'beginTempemp':800,
            'endTemp':1,
            'alpha':0.975,
            'reps':500,
            'annealer':'coolAfterReps',
            }

    worker = Annealer(problem,**wArgs)
    myGui = gui.ThreadedGUI(w,h)

    #gui.ControlMain(gui.GuiThread,gui.ThreadedGUI,AnnealerProfile,wArgs,w,h,50)
    ctl = gui.ControlMain(myGui,worker)
    ctl.mainLoop()

    #os.system('gnuplot -persist plot.txt')

##    stats=pstats.Stats('profile.txt')
##    stats=stats.sort_stats('time')
##    stats.print_stats()
