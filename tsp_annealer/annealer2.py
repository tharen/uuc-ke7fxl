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
        import hotshot
        self.profile=hotshot.Profile('profile.txt')
        self.annealer=Annealer(*args,**kargs)
        #calibrate the profiler
        #self.profile.bias=self.profile.calibrate(10000)

    def start(self):
        import hotshot.stats
        self.profile.runctx('self.annealer.start()',globals(),locals())
        stats=hotshot.stats.load('profile.txt')
        stats=stats.sort_stats('time')
        stats.print_stats()

class Annealer:
    """
    Solve a combinatorial problem using simulated annealing
    """
    def __init__(self,ctlQ,statusQ,beginT=0,endT=0,alpha=0,tReps=0,
            log='anneal.txt',**kargs):

##        import psyco
##        psyco.full()

        self.problem=kargs['problem'](**kargs)#['problemKArgs'])

        self.anneal=self.coolAfterReps

        self.beginT=beginT #beginning Temp
        self.endT=max(endT,0.0004) #ending temp
        self.alpha=alpha #cooling schedule
        self.tReps=tReps #solutions to test per temp cycle

        self.log=open(log,'w')
        self.ctlQ=ctlQ
        self.statusQ=statusQ

        self.T=beginT

        self.log.write('\n'.join(map(str,(self.beginT,self.endT,self.alpha,self.tReps))))
        self.log.write('\n')
        self.log.flush()


    def post(self,log=False,*args):
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

        self.running=False
        self.step=False
        #self.profile.runctx('self.start()',globals(),locals())
        self.anneal()
        self.log.close()

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
            print 'worker got go'
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
            print 'pause'
            self.running=False
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
        self.statusQ.put((sol,bE,'%.1f (%.1f) %.3f' % (cE,bE,self.T),self.running))

        #loop until temp is less than self.endT
        st=time.time()
        reps=0
        while self.__workCtl():
            i=0
            while 1:
                if i>=self.tReps: break
                tE=self.problem()
                if tE<=cE:
                    self.post(self.T,i,cE,tE,bE)
                    best=False
                    cE=tE
                    #if this is the best so far, upgrade it
                    if cE<=bE:
                        bE=cE
                        best=True

##                        sol=self.problem.elaborate()
##                        self.statusQ.put((sol,cE,'%.1f (%.1f) %.4f' % (cE,bE,self.T),self.running))
                    self.problem.keep(best)
                #if test is higher energy, select it by probability proportional to T
                else:
                    #calc the probability of selecting a less optimal solution
                    px=(cE-tE)#/ec*100 #difference in the two costs
                    p=exp(px/self.T) #Boltzman probability of acceptance
                    r=rand() #random 0-1
                    if r<=p: #probability is greater than some random value
                        self.post(self.T,i,cE,tE,bE,px,p,r)
                        self.problem.keep()
                        cE=tE

                i+=1
            reps+=i
            #self.statusQ.put((self.cSol,self.cOV,'%.1f (%.1f) %.3f' % (self.cOV,self.bOV,self.T),self.running))
            sol=self.problem.elaborate()
            self.statusQ.put((sol,cE,'%.1f (%.1f) %.4f' % (cE,bE,self.T),self.running))
            self.T*=self.alpha
            #exit the loop if endT has been reached
            if self.T<self.endT:break

        et=time.time()
        #self.statusQ.put((self.bSol,self.bOV,'%.1f (%.1f) %.3f' % (self.cOV,self.bOV,self.T),self.running))
        sol=self.problem.elaborate(True)
        self.statusQ.put((sol,bE,'%.1f (%.1f) %.4f' % (cE,bE,self.T),self.running))

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
            writeDistMatrix=True,**kargs):
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
        self.solutions=self._genSolution_seqrev()
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

    def __call__(self):
        """
        Generate the next solution

        Return the next solution from the generator when the
        class instance is called as a function
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
            l=self.numLocs-1
            #to random points in the current solution
            i=rint(0,l)
            j=rint(0,l)
            while j==i:
                j=rint(0,l)
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
    i=0
    numCities=100
    w=320
    h=240
    locations=scipy.zeros((numCities,2))

    scipy.random.seed(1)

    while 1:
        if i==numCities: break
        x=rint(0,w)
        y=rint(0,h)
        locations[i]=(x,y)
        i+=1

    problemKArgs={'locations':locations,
            'targetLength':0
            }

    wArgs={'problem':TSP,
            'problemKArgs':problemKArgs,
            'beginT':1000,
            'endT':.01,
            'alpha':0.99,
            'tReps':600,
            'annealer':'coolAfterReps',
            'nextSolution':'sequenceReverse',
            }
    wArgs.update(problemKArgs)
    #gui.ControlMain(gui.GuiThread,gui.ThreadedGUI,AnnealerProfile,wArgs,w,h,50)
    gui.ControlMain(gui.GuiThread,gui.ThreadedGUI,Annealer,wArgs,w,h,50)

    #os.system('gnuplot -persist plot.txt')

##    stats=pstats.Stats('profile.txt')
##    stats=stats.sort_stats('time')
##    stats.print_stats()
