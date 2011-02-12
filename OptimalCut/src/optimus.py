

class optimus:
    def __init__(self,cuts,products):
        self.cutsFile=cuts
        self.productsFile=products

        self.__readProducts(self)
        self.__readCuts(self)

    def __readProducts(self):
        f=open(self.productsFile)
        lines=f.readlines()[1:]
        self.products=[]
        for line in lines:
            l=line.split(',')
            id=int(l[0])
            group=int(l[1])
            desc=l[2]
            length=float(l[3])
            cost=float(l[4])
            self.products.append(id,group,desc,length,cost)

    def __readCuts(self):
        f=open(self.cutsFile)
        lines=f.readlines()[1:]
        self.cuts=[]
        for line in lines:
            l=line.split(',')
            id=int(l[0])
            jobItem=int([1])
            desc=l[2]
            jobItemIdx=int(l[3])
            jobStr=l[4]
            prodId=l[[5]]
            prodDesc=l[0]

