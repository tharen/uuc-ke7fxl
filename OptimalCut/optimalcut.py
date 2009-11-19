import math
from numpy import random

class OptimalCutter:
    def __init__(self,cutsFile='cuts.lst',
            productsFile='products.lst',
            itemsFile='items.lst',
            trim=1.0,minOpt='waste',
            maxTemp=100,minTemp=.01,
            alpha=.95,reps=500):

        self.cutsFileName = cutsFile
        self.productsFileName = productsFile
        self.itemsFileName = itemsFile
        self.trim = trim
        self.minOpt = minOpt

        self.products={}
        self.__productGroups={}
        self.__readProductsFile()

        self.cuts=self.Cuts()
        self.__cutGroups = {}
        self.__readCutsFile()

        self.random=self.__getRandom()

        #self.maxTemp = 100000*len(self.cuts)**-1
        #self.minTemp = .0001*self.maxTemp
        self.maxTemp = maxTemp
        self.minTemp = minTemp
        self.alpha = alpha
        #self.tempReps = 5*len(self.cuts)
        self.tempReps = reps
        self.goal = self.cuts.totalLength()

        print self.minTemp,self.maxTemp,self.tempReps, self.goal

        self.temp = self.maxTemp


        self.keptDeltas=[]
        self.bestSolution = {}
        self.bestDelta = 9e10
        self.currentSolution = {}
        self.currentDelta = 9e10
        self.repsCompleted = 0

##    def _readCutsFile(self):
##        self.cuts = self.__readCutsFile(self.cutsFileName)

    def __getRandom(self):
        while 1:
            rand=random.random(1000000)
            for r in rand:
                yield r

##        i=0
##        while 1:
##            try:
##                yield rand[i]
##            except:
##                rand=[random.random() for i in range(10000)]
##                i=0
##                yield rand[i]
##            i+=1

    def main(self):
        #self.__productGroups = self.__groupProducts()
        testAssignments = self._assignCuts()
        waste = self.tallyWaste(testAssignments)
        self.bestSolution = testAssignments
        self.bestDelta = waste
        self.currentSolution = testAssignments
        self.currentDelta = waste

        anneal=open('anneal.txt','w')
        i=0
        anneal.write('Temp       Best     Current  Test     Prob   Rand   Kept\n')
        while self.temp>=self.minTemp:
            print '%-9.4f %-8.2f %-8.2f' % (self.temp,self.bestDelta,self.currentDelta)
            ##TODO: the inner rep loop may be parallelized
            ##      The only problem may be that worker threads are not
            ##      privy to the results of each other
            for x in range(self.tempReps):
                testSolution = self._assignCuts(testAssignments)
                ##TODO: generalize tallyWaste to be a delta calculation for each minOpt
                delta = self.tallyWaste(testSolution)
                if delta<=self.currentDelta:
                ##TODO: the goal is the total length of all cuts
                #if waste<self.temp:
                ##!Threshold acceptance method
                ##      http://mathworld.wolfram.com/SimulatedAnnealing.html
                    self.currentSolution = testSolution
                    self.currentDelta = delta
                    self.keptDeltas.append(delta)
                    if delta<self.bestDelta:
                        self.bestDelta = delta
                        self.bestSolution = testAssignments
                    msg='%-10.4f %-8.2f %-8.2f %-8.2f\n' % (
                            self.temp,self.bestDelta,
                            self.currentDelta,delta
                            )
                    #print msg
                    anneal.write(msg)

                else:
                    p=self.__getProbability(self.currentDelta,delta)
                    #r = self.random.next()
                    r = random.random(1)
                    if p>r:
                        msg='%-10.4f %-8.2f %-8.2f %-8.2f %-5.4f %-5.4f +\n' % (
                                self.temp,self.bestDelta,
                                self.currentDelta,delta,p,r
                                )
                        #print msg
                        anneal.write(msg)
                        self.currentSolution = testSolution
                        self.currentDelta = delta
                        self.keptDeltas.append(delta)

                    #else:
                        #anneal.write('%.6f\t%.2f\t%.2f\t%.2f\t%.4f\t%.4f\t-\n' % (self.temp,self.bestDelta,self.currentDelta,delta,p,r))
                i+=1

            self.temp*=self.alpha
            #self.tempReps = int(self.tempReps*1.005)

        self.repsCompleted = i

        #self.bestDelta = self.currentDelta
        #self.bestSolution = self.currentSolution

        anneal.flush()
        anneal.close()

    def __getProbability(self,base,test):
        ##TODO: compute probability based on temp
        #return random.random()*(self.temp/self.maxTemp)
        dTest = test - self.goal
        dBase = base - self.goal
        x=-(dTest-dBase)/self.temp
        return math.exp(x)

##        try:return math.exp(x)
##        except:
##            print test,base,self.temp,x
##            raise

    def orderSummary(self,cutAssignments):
        orderSheet=''

        productItems={}
        #cutAssignments = assignments.values()

        #tally the quantity of each product
        for assignment in cutAssignments:
            if not assignment.product in productItems.keys():
                productItems[assignment.product] = 0
            productItems[assignment.product]+=1

        orderSheet += 'Product     Len   Qnt     Ft  $ Each    $ Tot\n'

        #sum all product groups
        sumFt=0
        sumPrice=0
        sumQnt=0

        #sort the products
        products=productItems.keys()
        products.sort()

        #report the total for each product
        for product in products:
            quantity=productItems[product]
            sumQnt+=quantity
            desc = product.description
            length = product.length
            price = product.price
            totLen = product.length * quantity
            totPrice = quantity * price

            #add to the order totals
            sumFt+=totLen
            sumPrice+=totPrice

            #write the product order line
            orderSheet += '%9s  %4d  %4d   %4d  %6.2f   %6.2f\n' % (
                    desc,length/12,quantity,totLen/12,price,totPrice)

        orderSheet += '-'*45 + '\n'
        orderSheet += '                 %4d %6d          %7.2f' % (sumQnt,sumFt,sumPrice)

        return orderSheet

    def idSort(self,item1,item2):
        if item1.id>item2.id: return 1
        if item2.id>item1.id: return -1
        return 0

    def cutSheet(self,cutAssignments):
        #cutAssignments = assignments.values()
        cutAssignments.sort(cmp=self.idSort)

        cutCount=0
        cutTotLen=0

        sheet = ''
        i=1
        for assignment in cutAssignments:
            id=assignment.id
            product = assignment.product
            desc = product.description
            length = product.length
            waste = assignment.residual
            if assignment.product.group==9999:
                length = 0
                waste = 0
            rate = product.price

            sheet += 'ID     Product     Length  Rate    Waste\n'
            sheet += '%-6d %-10s  %-6d  %-6.2f  %-6.2f\n' % (id,desc,length,rate,waste)

            sheet+='    CutId  Job Item             Length   (Product)\n'
            for cut in assignment:
                id = cut.id
                item = cut.itemDesc
                length = cut.length
                prod = cut.productDesc
                sheet+='    %-5d  %-20s %-6.3f   (%s)\n' % (id,item,length,prod)
                cutCount+=1
                cutTotLen+=length
            sheet +='\n'

        sheet += '\n'
        sheet += '%d cuts\n' % cutCount
        sheet += '%.4f total length\n\n' % cutTotLen
        sheet += 'Waste Stats\n-------\n'
        sheet += 'Min    Max    Mean   Total\n'
        sheet += '%-6.2f %-6.2f %-6.2f %-.2f' % (cutter.wasteStats(cutter.bestSolution))

        sheet += '\n\nCompleted in %d reps' % self.repsCompleted

        return sheet.strip()

    def tallyWaste(self,assignments):
        return sum([assignment.residual
                for assignment in assignments
                if assignment.product.group!=9999
                ])

    def wasteStats(self,assignments):
        #list residuals from all cut assignments
        l=[assignment.residual
                for assignment
                in assignments
                if assignment.product.group!=9999
                ]
        minWaste = min(l)
        maxWaste = max(l)
        meanWaste = sum(l)/len(l)
        totalWaste = sum(l)
        return minWaste,maxWaste,meanWaste,totalWaste

    def _getProdOpt(self,prodGroup,minLen):
        """
        Return the ID of a product in product group prod which
            is longer than minLen
        """
        #print self.__productGroups
        while 1:
            try:
                r=int(self.random.next() * len(self.__productGroups[prodGroup]))
                #prod = random.choice(self.__productGroups[prodGroup])
                prod = self.__productGroups[prodGroup][r]
            except IndexError:
                #print 'No options for product (%s)' % prod
                #Unknown product group
                return self.products[9999]

            # if the random selection is of sufficient length, return
            #   otherwise try again
            if prod.length>=minLen: break

        return prod

    def splitAssignments(self,baseAssignments):

        #randomly slice the current assignments
        l=0
        r=len(baseAssignments)
        m=(r-l)/2
        s=r/6
        j = random.randint(0,s,1)

        l=m-j
        r=m+10-j

        cutAssignments=baseAssignments[0:l]
        cutAssignments.extend(baseAssignments[r:])

        #j=len(baseAssignments)/10
        #j=int(round(len(baseAssignments) * self.random.next(),0))
        #cutAssignments=baseAssignments[j:]

        leftovers = []
        for assignment in baseAssignments[l:r]:
            leftovers.extend(assignment)

        #group one side of the slice by product group
        cutGroups={}
        for cut in leftovers:
            if not cutGroups.has_key(cut.productGroup):
                cutGroups[cut.productGroup]=[]
            cutGroups[cut.productGroup].append(cut)

        return cutAssignments,cutGroups

    def _assignCuts(self,baseAssignments=None):
        if baseAssignments==None:
            cutAssignments=[]

            #group all cuts
            cutGroups={}
            for cut in self.cuts.values():
                if not cutGroups.has_key(cut.productGroup):
                    cutGroups[cut.productGroup]=[]
                cutGroups[cut.productGroup].append(cut)

        else:
            cutAssignments,cutGroups=self.splitAssignments(baseAssignments)

        c=0
        g=0
        for prodGroup,cuts in cutGroups.items():
            g+=1
            cutIdx=range(0,len(cuts))
            testIdx=cutIdx[:]

            idx=testIdx.pop(0)
            cut=cuts[idx]

            #get random option from the product group
            product = self._getProdOpt(prodGroup,cut.length)

            #instantiate an assignment
            assignment=self.Assignment(len(cutAssignments),product)

            #sequentially attempt to add each cut to the assignment
            while 1:
                if assignment.addCut(cut):
                    #cut fits within the product option, remove it from the cutIdx list
                    c+=1
                    cutIdx.remove(idx)

                    #if all cuts have been assigned, break
                    if len(cutIdx)==0:
                        #add the assignment to the completed list
                        cutAssignments.append(assignment)
                        break

                r=len(testIdx)
                minCut=9e10
                if r!=0:
                    minCut=min([cuts[i].grossLength() for i in testIdx])

                #if all remaining cuts have been tested, start a new assignment
                if minCut>assignment.residual or r==0:
                    if len(assignment)>0:
                        #sometimes an assignment will be empty when no cuts fit the selected product option
                        cutAssignments.append(assignment)

                    #reset the test indexes to the unassigned cuts
                    testIdx=cutIdx[:]

                    #create a new assignment object
                    product = self._getProdOpt(prodGroup,cut.length)
                    assignment=self.Assignment(len(cutAssignments),product)



                idx=testIdx.pop(0)
                cut = cuts[idx]

##        print g,c
##        #print c,g
##        x=0
##        for a in cutAssignments:
##            for c in a:
##                x+=1
##        print x

##        l=range(len(cutAssignments))
##        random.shuffle(l)
##        a=[]
##        for i in l:
##            a.append(cutAssignments[i])
##        return a

        return cutAssignments

    def __readProductsFile(self):
        """
        Read the products text file into groups of products
        """
        lines = open(self.productsFileName).readlines()

        #{id:(prod,availableLen,rate,item),}
        #Id,Group,Material,Length,Price
        for l in lines[1:]:
            x = l.split(',') #split on commas
            id = int(x[0])
            group = int(x[1])
            description = x[2].strip()
            length = float(x[3])
            price = float(x[4])
            #create a new product object
            product=self.Product(id,group,description,length,price)
            #instantiate the group if it hasn't been already
            if not self.__productGroups.has_key(group):
                self.__productGroups[group]=[]
            #add the product to the main list and it's group list
            self.products[id]=product
            self.__productGroups[group].append(product)

        #Add an 'unkown' product group
        product = self.Product(9999,9999,'Unknown',9e10,0)
        self.products[9999]=product
        self.__productGroups[9999]=[product,]

        return True

    def __readCutsFile(self):
        ##TODO: warn if product/length not in products
        lines = open(self.cutsFileName).readlines()

        #CutId,ItemId,Item,PieceIndex,Piece,MaterialGroup,Material,CutLength
        #{id:(prod,cutLen),}

        i=0
        for line in lines[1:]:
            if line.startswith('#'): continue
            if len(line.strip()) == 0: continue
            x = line.split(',')
            cutId = int(x[0])
            itemId = int(x[1])
            itemDesc = x[2].strip()
            pieceIdx = int(x[3])
            pieceDesc = x[4].strip()
            prodGroup = int(x[5])
            prodDesc = x[6].strip()
            cutLength = float(x[7])

            cut = self.Cut(cutId,itemId,itemDesc,pieceIdx,
                    pieceDesc,prodGroup,prodDesc,cutLength,
                    self.trim)

            #group cuts by product type
            if not prodGroup in self.__cutGroups.keys():
                self.__cutGroups[prodGroup]=[]
            self.__cutGroups[prodGroup].append(cut)

            #add the cut to the cuts object
            self.cuts[cutId]=cut

            i+=1

        print "Read %d cuts" % i
        return True

    class Assignment(list):
        def __init__(self,id,product):
            self.id = id
            self.product = product
            self.cumulativeLength=0
            self.residual=self.product.length

        def addCut(self,cut):
            """
            Add a cut to the assignment list
            """
            if self.cumulativeLength + cut.grossLength() <= self.product.length:
                self.cumulativeLength+=cut.grossLength()
                self.residual=self.product.length-self.cumulativeLength
                self.append(cut)
                return True
            else:
                return False

    class Product:
        def __init__(self,id,group,description,length,price):
            """
            Products belong to groups and may be available
              in various lengths
            """
            self.id=id
            self.group=group
            self.description=description
            self.length=length
            self.price=price

    class Cuts(dict):
        def __init__(self):
            pass

        def totalLength(self):
            l=0
            for k,c in self.items():
                l+=c.length
            return l

        def __str__(self):
            s = ''
            for k,c in self.items():
                s+='%s\n' % c.__str__()
            return s

    class Cut:
        def __init__(self,id,itemId,itemDesc,
                pieceIdx,pieceDesc,
                prodGroup,prodDesc,
                length,trim=0.0):
            """
            Cuts
            """
            self.id = id
            self.itemId = itemId
            self.itemDesc = itemDesc
            self.pieceIdx = pieceIdx
            self.pieceDesc = pieceDesc
            self.productGroup = prodGroup
            self.productDesc = prodDesc
            self.length = length
            self.trim = trim

        def grossLength(self):
            return self.length + self.trim

        def __repr__(self):
            return self.__str__()

        def __str__(self):
            s='%d,' % self.id
            s+='%d,' % self.itemId
            s+='%s,' % self.itemDesc
            s+='%d,' % self.pieceIdx
            s+='%s,' % self.pieceDesc
            s+='%d,' % self.productGroup
            s+='%s,' % self.productDesc
            s+='%.4f' % self.length
            return s

if __name__=='__main__':
    import cProfile

    #cutter=OptimalCutter(maxTemp=10000,minTemp=1000,alpha=.95,reps=500)
    cutter=OptimalCutter(maxTemp=500,minTemp=10,alpha=.9,reps=300)

    cProfile.run('cutter.main()','profile.txt')
    #cutter.main()

    #import pprint
    #pprint.pprint(cutter.bestSolution)
    #print cutter.cutSheet(cutter.bestSolution)
    print cutter.wasteStats(cutter.bestSolution),cutter.repsCompleted

    order = cutter.orderSummary(cutter.bestSolution)
    f = open('order.txt','w')
    f.write(order)
    f.close()

    cuts=cutter.cutSheet(cutter.bestSolution)
    f = open('cutsheet.txt','w')
    f.write(cuts)
    f.close()

    import pstats
    s=pstats.Stats('profile.txt')
    s=s.strip_dirs()
    s.sort_stats('cumulative')
    s.print_stats()
    #s.dump_stats('stats.txt')
##    f = open('stats.txt','wb')
##    import sys
##    sys.stdout=f
##    s.print_stats()
##    f.close()
