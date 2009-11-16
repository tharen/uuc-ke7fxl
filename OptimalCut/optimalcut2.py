import random,math

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

        #self.maxTemp = 100000*len(self.cuts)**-1
        #self.minTemp = .0001*self.maxTemp
        self.maxTemp = maxTemp
        self.minTemp = minTemp
        self.alpha = alpha
        #self.tempReps = 5*len(self.cuts)
        self.tempReps = reps
        self.goal = self.cuts.totalLength()

        print self.minTemp,self.maxTemp,self.tempReps

        self.temp = self.maxTemp


        self.keptDeltas=[]
        self.bestSolution = {}
        self.bestDelta = 9e10
        self.currentSolution = {}
        self.currentDelta = 9e10
        self.repsCompleted = 0

##    def _readCutsFile(self):
##        self.cuts = self.__readCutsFile(self.cutsFileName)

    def main(self):
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
        anneal.write('Temp       Best     Current  Test     Prob   Rand   Kept\n')
        while self.temp>=self.minTemp:
            print self.temp
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
                    msg='%-10.4f %-8.2f %-8.2f %-8.2f\n' % (
                            self.temp,self.bestDelta,
                            self.currentDelta,delta
                            )
                    #print msg
                    anneal.write(msg)

                else:
                    p=self.__getProbability(self.currentDelta,delta)
                    r = random.random()
                    if p>r:
                        msg='%-10.4f %-8.2f %-8.2f %-8.2f %-5.4f %-5.4f +\n' % (
                                self.temp,self.bestDelta,
                                self.currentDelta,delta,p,r
                                )
                        #print msg
                        anneal.write(msg)
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
        orderSheet=''

        productItems={}
        cutAssignments = assignments.values()

        #tally the quantity of each product
        for assignment in cutAssignments:
            if not assignment.product in productItems.keys():
                productItems[assignment.product] = 0
            productItems[assignment.product]+=1

        orderSheet += 'Product     Len   Qnt     Ft  $ Each    $ Tot\n'

        #sum all product groups
        sumFt=0
        sumcost=0
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
            cost = product.cost
            totLen = product.length * quantity
            totcost = quantity * cost

            #add to the order totals
            sumFt+=totLen
            sumcost+=totcost

            #write the product order line
            orderSheet += '%9s  %4d  %4d   %4d  %6.2f   %6.2f\n' % (
                    desc,length/12,quantity,totLen/12,cost,totcost)

        orderSheet += '-'*45 + '\n'
        orderSheet += '                 %4d %6d          %7.2f' % (sumQnt,sumFt,sumcost)

        return orderSheet

    def idSort(self,item1,item2):
        if item1.id>item2.id: return 1
        if item2.id>item1.id: return -1
        return 0

    def cutSheet(self,assignments):
        cutAssignments = assignments.values()
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
            waste = assignment.residual()
            if assignment.product.group==9999:
                length = 0
                waste = 0
            rate = product.cost

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
        return sum([assignment.residual()
                for k,assignment in assignments.items()
                if assignment.product.group!=9999
                ])

    def wasteStats(self,assignments):
        #list residuals from all cut assignments
        l=[assignment.residual()
                for k,assignment
                in assignments.items()
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
                prod = random.choice(self.__productGroups[prodGroup])
            except IndexError:
                #print 'No options for product (%s)' % prod
                #Unknown product group
                return self.products[9999]

            # if the random selection is of sufficient length, return
            #   otherwise try again
            if prod.length>=minLen: break

        return prod

    def _assignCuts(self):
        cutAssignments={}
        assignmentId=0
        c=0
        for prodGroup,cuts in self.__cutGroups.items():
            cutIdx=range(0,len(cuts))
            testIdx=cutIdx[:]

            i=random.choice(testIdx)
            cut=cuts[i]

            product = self._getProdOpt(prodGroup,cut.length)
            assignment=self.Assignment(assignmentId,product)

            while 1:
                try:
                    assignment.append(cut)
                    c+=1
                    cutIdx.remove(i)
                    #if all cuts have been assigned, break
                    if len(cutIdx)==0:break

                except:
                    pass

                testIdx.remove(i)

                if len(testIdx)==0:
                    #reset the test indexes to the unassigned cuts
                    testIdx=cutIdx[:]
                    #create a new assignment object
                    assignmentId+=1
                    product = self._getProdOpt(prodGroup,cut.length)
                    assignment=self.Assignment(assignmentId,product)
                    cutAssignments[assignmentId]=assignment

                i=random.choice(testIdx)
                cut = cuts[i]

        #print c
        return cutAssignments

    def x_assignCuts(self):
        """
        Make cut assigments to product items
        """
        cutAssignments = {}
        assignmentId = 0
        #print self.__cutGroups.keys()

        #for each product group assign cuts to a product item
        for prodGroup,cuts in self.__cutGroups.items():
            #print prod,cuts
            #cuts=cuts[:] #clone the product group cuts list so the original is not disturbed
            cutIdx=range(0,len(cuts))

            #pick a random cut item from the product group to start the assignment
            i = random.choice(cutIdx)
            cut = cuts[i]

            cutLen = cut.grossLength()

            #get the id of a product that fits the first cut
            product = self._getProdOpt(prodGroup,cutLen)

            assignment=self.Assignment(assignmentId,product)

            #iteratively add cuts to the assignment until the residual
            #  length is less than all remaining cuts
            while 1:
                if assignment.residual() - cutLen >= 0:
                    #the current cut fits so add it to the assignment
                    if not assignmentId in cutAssignments.keys():
                        cutAssignments[assignmentId]=assignment

                    assignment.append(cut)

                    #remove the cut from the index list
                    cutIdx.remove(i)

                else:
                    #the cut doesn't fit, start a new assignment
                    assignmentId+=1

                    #get a compatible product
                    product = self._getProdOpt(prodGroup,cutLen)
                    #create the assignment
                    assignment = self.Assignment(assignmentId,product)

                    #add the assignment
                    if not assignmentId in cutAssignments.keys():
                        cutAssignments[assignmentId]=assignment

                    #add the cut to the assignment
                    assignment.append(cut)

                    cutIdx.remove(i)

                #continue until all cuts in the group have been assigned
                if len(cutIdx)==0:
                    break

                #pick a random cut from those remaining
                i = random.choice(cutIdx)
                cut = cuts[i]

                cutLen = cut.grossLength()

            assignmentId+=1

        return cutAssignments

    def __readProductsFile(self):
        """
        Read the products text file into groups of products
        """
        lines = open(self.productsFileName).readlines()

        #{id:(prod,availableLen,rate,item),}
        #Id,Group,Material,Length,cost
        for l in lines[1:]:
            x = l.split(',') #split on commas
            id = int(x[0])
            group = int(x[1])
            description = x[2].strip()
            length = float(x[3])
            cost = float(x[4])
            #create a new product object
            product=self.Product(id,group,description,length,cost)
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

        #products array
        self.__products=[]
        prodKeys=self.products.keys()
        for i in range(len(prodKeys)):
            p=self.products[prodKeys[i]]
            self.__products.append([prodKeys[i],p.group,p.length,p.cost])

        #product group array
        self.__prodGroups=[]

        return True

##        products = {}
##
##        for l in lines[1:]:
##            x = l.split(',')
##            id = int(x[0])
##            prod = x[1].strip()
##            length = float(x[2])
##            cost = float(x[3])
##            products[id] = (prod,length,cost)
##
##        products[9999] = ('Unknown',9e10,0)
##
##        return products

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

##    def __groupProducts(self):
##        prodGroups = {}
##        for prod in self.__cutGroups.keys():
##            prodIds = [id for id,v in self.products.items() if v[0]==prod]
##            prodGroups[prod]=prodIds
##        return prodGroups

##    def __groupCuts(self):
##        """
##        Aggregate cuts by product
##        """
##        #list the cut ids by product type
##        #(prodType:[cutId1,cutId2,...],...}
##        productCuts={}
##        for k,c in self.cuts.items():
##            if not c.productGroup in productCuts.keys():
##                productCuts[c.productGroup] = []
##            productCuts[c.productGroup].append(k)
##
##        return productCuts

    class Assignment(list):
        def __init__(self,id,product):
            self.id = id
            self.product = product

        def append(self,cut):
            """
            Add a cut to the assignment list
            """
            if self.sumCutLength() + cut.grossLength() > self.product.length:
                raise "Gross Length Error"
                #return False

            ##TODO: is there a better way to overide append
            self.extend([cut])

        def residual(self):
            """
            Return the difference between assigned cuts and product length
            """
            return self.product.length - self.sumCutLength()

        def sumCutLength(self):
            """
            Total the length of all assigned cuts
            """
            totCut=0
            for c in self:
                totCut+=c.grossLength()

            return totCut

    class Product:
        def __init__(self,id,group,description,length,cost):
            """
            Products belong to groups and may be available
              in various lengths
            """
            self.id=id
            self.group=group
            self.description=description
            self.length=length
            self.cost=cost

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
    #cutter=OptimalCutter(maxTemp=1000,minTemp=1,alpha=.95,reps=200)
    cutter=OptimalCutter(maxTemp=1000,minTemp=5,alpha=.95,reps=250,trim=1.0)
    #cuts = cutter.readCutsFile('cuts.lst')
    #products = cutter.readProductsFile('products.lst')
    cutter.main()

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
