import random,math

class OptimalCutter:
    def __init__(self,cutsFile='cuts.lst',productsFile='products.lst',
            trim=1.0,minOpt='waste',
            maxTemp=100,minTemp=.01,
            alpha=.95,reps=500):

        self.cutsFileName = cutsFile
        self.productsFileName = productsFile
        self.trim = trim
        self.minOpt = minOpt

        self.products={}
        self.__productGroups={}

        self._readCutsFile()

        self.__readProductsFile()

        #self.maxTemp = 100000*len(self.cuts)**-1
        #self.minTemp = .0001*self.maxTemp
        self.maxTemp = maxTemp
        self.minTemp = minTemp
        self.alpha = alpha
        #self.tempReps = 5*len(self.cuts)
        self.tempReps = reps
        self.goal = len(self.cuts)

        print self.minTemp,self.maxTemp,self.tempReps

        self.temp = self.maxTemp

        self.__cutGroups = {}
        self.keptDeltas=[]
        self.bestSolution = {}
        self.bestDelta = 9e10
        self.currentSolution = {}
        self.currentDelta = 9e10
        self.repsCompleted = 0

    def _readCutsFile(self):
        self.cuts = self.__readCutsFile(self.cutsFileName)

    def main(self):
        self.__cutGroups = self.__groupCuts()
        #self.__productGroups = self.__groupProducts()
        assignments = self._assignCuts()
        waste = self.tallyWaste(assignments)
        self.bestSolution = assignments
        self.bestDelta = waste
        self.currentSolution = assignments
        self.currentDelta = waste

        anneal=open('anneal.txt','w')
        #anneal.write('Temp,Best,Current,Test,Prob.,Rand,NonOptimal\n')
        i=0

        while self.temp>=self.minTemp:
            #print self.temp
            for x in range(self.tempReps):
                assignments = self._assignCuts()
                ##TODO: generalize tallyWaste to be a delta calculation for each minOpt
                delta = self.tallyWaste(assignments)
                if delta<self.currentDelta:
                ##TODO: the goal is the total length of all cuts
                #if waste<self.temp:
                ##!Threshold acceptance method
                ##      http://mathworld.wolfram.com/SimulatedAnnealing.html
                    self.currentSolution = assignments
                    self.currentDelta = delta
                    self.keptDeltas.append(delta)
                    if delta<self.bestDelta:
                        self.bestDelta = delta
                        self.bestSolution = assignments
                    anneal.write('%.6f\t%.2f\t%.2f\t%.2f\t\t\t\n' % (self.temp,self.bestDelta,self.currentDelta,delta))

                else:
                    p=self.__getProbability(self.currentDelta,delta)
                    r = random.random()
                    if p>r:
                        anneal.write('%.6f\t%.2f\t%.2f\t%.2f\t%.4f\t%.4f\t+\n' % (self.temp,self.bestDelta,self.currentDelta,delta,p,r))
                        self.currentSolution = assignments
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
        try:return math.exp(x)
        except:
            print test,base,self.temp,x
            raise

    def orderSummary(self,assignments):
        f = open('order.txt','w')
        items={}
        cuts = assignments.values()
        for c in cuts:
            if not c[0] in items:
                items[c[0]] = 0
            items[c[0]]+=1

        f.write('Product     Len   Qnt     Ft  $ Each    $ Tot\n')
        sumFt=0
        sumPrice=0
        sumQnt=0
        for k,count in items.items():
            sumQnt+=count
            prod = self.products[k][0]
            length = self.products[k][1]
            price = self.products[k][2]
            totLen = self.products[k][1]*count
            sumFt+=totLen
            totPrice = count * price
            sumPrice+=totPrice
            f.write('%9s  %4d  %4d   %4d  %6.2f   %6.2f\n' % (
                    prod,length/12,count,totLen/12,price,totPrice))

        f.write('-'*45 + '\n')
        f.write('                 %4d %6d          %7.2f' % (sumQnt,sumFt,sumPrice))

    def cutSheet(self,assignments):
        cutLists = assignments.values()
        cutLists.sort()
        sheet = ''
        i=1
        for cutList in cutLists:
            prod = self.products[cutList[0]]
            name = prod[0]
            length = prod[1]
            waste = cutList[2]
            if cutList[0]==9999:
                length = 0
                waste = 0
            rate = prod[2]

            sheet += 'Product\tLength\tRate\tWaste\n'
            sheet += '%s\t%d\t%.2f\t%.2f\n\n' % (name,length,rate,waste)

            sheet+='\tCutId\tItemId\tCut\t(Product)\n'
            for cut in cutList[1]:
                item = self.cuts[cut][2]
                length = self.cuts[cut][1]
                prod = self.cuts[cut][0]
                sheet+='\t%d\t%d\t%.3f\t(%s)\n' % (cut,item,length,prod)
            sheet +='\n'

        sheet += '\n\n'
        sheet += 'Waste Stats\n-------\n'
        sheet += 'Min\tMax\tMean\tTotal\n'
        sheet += '%.2f\t%.2f\t%.2f\t%.2f' % (cutter.wasteStats(cutter.bestSolution))

        sheet += '\n\nCompleted in %d reps' % self.repsCompleted

        return sheet.strip()

    def tallyWaste(self,assignments):
        return sum([v[2] for k,v in assignments.items() if v[0]!=9999])

    def wasteStats(self,assignments):
        l=[v[2] for k,v in assignments.items() if v[0]!=9999]
        minWaste = min(l)
        maxWaste = max(l)
        meanWaste = sum(l)/len(l)
        totalWaste = sum(l)
        return minWaste,maxWaste,meanWaste,totalWaste

    def _getProdOpt(self,prod,minLen):
        """
        Return the ID of a product in product group prod which
            is longer than minLen
        """
        print self.__productGroups
        while 1:
            try:
                prodId = random.choice(self.__productGroups[prod])
            except IndexError:
                #print 'No options for product (%s)' % prod
                return False

            prodLen = self.products[prodId][1]
            if prodLen>=minLen: break

        return prodId

    def _assignCuts(self):
        """
        Assigns cuts to product items
        """
        cutAssignments = {}
        assignmentId = 0
        #print self.__cutGroups.keys()

        #for each product group assign cuts to a product item
        for prodGroup,cuts in self.__cutGroups.items():
            #print prod,cuts
            cuts=cuts[:] #clone the cuts list so the original is not disturbed

            #pick a random cut item
            i = random.choice(range(0,len(cuts)))
            cut = cuts[i]

            #
            cutLength = self.cuts[cut][1] + self.trim
            prodId = self._getProdOpt(prodGroup,cutLen)
            residLen = self.products[prodId][1]

            while 1:
                if residLen - cutLen >= 0:
                    if not assignmentId in cutAssignments.keys():
                        cutAssignments[assignmentId]=[prodId,[],0]
                    cutAssignments[assignmentId][1].append(cut)
                    cuts.pop(i)
                    residLen -= cutLen
                    cutAssignments[assignmentId][2]=residLen
                else:
                    assignmentId+=1
                    prodId = self._getProdOpt(prod,cutLen)
                    residLen = self.products[prodId][1]
                    if not assignmentId in cutAssignments.keys():
                        cutAssignments[assignmentId]=[prodId,[],0]
                    cutAssignments[assignmentId][1].append(cut)
                    cuts.pop(i)
                    residLen -= cutLen
                    cutAssignments[assignmentId][2]=residLen

                #continue until all cuts in the group have been assigned
                if len(cuts)==0:
                    break

                i = random.choice(range(0,len(cuts)))
                cut = cuts[i]
                cutLen = self.cuts[cut][1] + self.trim

            assignmentId+=1

        return cutAssignments

##    def __groupProducts(self):
##        prodGroups = {}
##        for prod in self.__cutGroups.keys():
##            prodIds = [id for id,v in self.products.items() if v[0]==prod]
##            prodGroups[prod]=prodIds
##        return prodGroups

    def __groupCuts(self):
        """
        Aggregate cuts by product
        """
        #list the cut ids by product type
        #(prodType:[cutId1,cutId2,...],...}
        productCuts={}
        for k,v in self.cuts.items():
            if not v[0] in productCuts.keys():
                productCuts[v[0]] = []
            productCuts[v[0]].append(k)

        return productCuts

    class Product:
        def __init__(self,id,prodGroup,length,price):
            """
            Products belong to groups and may be available
              in various lengths
            """
            self.id=id
            self.prodGroup=prodGroup
            self.length=length
            self.price=price

    def __readProductsFile(self):
        """
        Read the products text file into groups of products
        """
        lines = open(self.productsFileName).readlines()

        #id,prod,len
        #{id:(prod,availableLen,rate,item),}

        for l in lines[1:]:
            x = l.split(',') #split on commas
            id = int(x[0])
            prodGroup = x[1].strip()
            length = float(x[2])
            price = float(x[3])
            #create a new product object
            product=self.Product(id,prodGroup,length,price)
            #instantiate the group if it hasn't been already
            if not self.__productGroups.has_key(prodGroup):
                self.__productGroups[prodGroup]=[]
            #add the product to the main list and it's group list
            self.products[id]=product
            self.__productGroups[prodGroup].append(product)

        #Add an 'unkown' product group
        product = self.Product(9999,'Unknown',9e10,0)
        self.products[9999]=product
        self.__productGroups[9999]=[product,]

        return True

##        products = {}
##
##        for l in lines[1:]:
##            x = l.split(',')
##            id = int(x[0])
##            prod = x[1].strip()
##            length = float(x[2])
##            price = float(x[3])
##            products[id] = (prod,length,price)
##
##        products[9999] = ('Unknown',9e10,0)
##
##        return products

    def __readCutsFile(self,fName):
        ##TODO: warn if product/length not in products
        lines = open(fName).readlines()
        #id,prod,len
        #{id:(prod,cutLen),}
        cuts = {}
        for line in lines[1:]:
            if line.startswith('#'): continue
            if len(line.strip()) == 0: continue
            x = line.split(',')
            id = int(x[0])
            prod = x[1].strip()
            length = float(x[2])
            item = int(x[3])
            cuts[id] = (prod,length,item)

        print "Read %d cuts" % len(cuts)
        return cuts

if __name__=='__main__':
    cutter=OptimalCutter()
    #cuts = cutter.readCutsFile('cuts.lst')
    #products = cutter.readProductsFile('products.lst')
    cutter.main()

    #import pprint
    #pprint.pprint(cutter.bestSolution)
    #print cutter.cutSheet(cutter.bestSolution)
    print cutter.wasteStats(cutter.bestSolution),cutter.repsCompleted

    print cutter.orderSummary(cutter.bestSolution)

    f = open('cutsheet.txt','w')
    f.write(cutter.cutSheet(cutter.bestSolution))
    f.close()