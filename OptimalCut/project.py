import random,time

l1Tot=0
l2Tot=0
l3Tot=0

class Project:
    def __init__(self,cutsPath,materialsPath):
        self.cuts=Cuts(cutsPath)
        self.materials=Materials(materialsPath)
        
        ##TODO: compare cut materials to available materials
        
        ##TODO: grouping by material group should be a method of the cuts and materials classes
        self.__cutsByMaterialGroup={}
        for mg in self.cuts.materialGroups:
            cuts=self.cuts.cutsByMaterialGroup(mg)
            self.__cutsByMaterialGroup[mg]=[]
            for i,c in cuts.items():
                l=c.totalLength()
                self.__cutsByMaterialGroup[mg].append([i,l])
        
        self.__materialsByMaterialGroup={}
        for mg in self.materials.materialGroups:
            materials=self.materials.materialsByMaterialGroup(mg)
            self.__materialsByMaterialGroup[mg]=[]
            for i,m in materials.items():
                l=m.length
                c=m.cost
                self.__materialsByMaterialGroup[mg].append([i,l,c])

    def assignCuts(self,base=None):
##        if base==None:
        assignments={}
        totWaste=0
        totCost=0
        cutsByMaterial=self.__cutsByMaterialGroup
##        else:
##            assignments={}
##            cutsByMaterial={}
##            for mg,assign in base.items():
##                j=len(cuts)/2
                 
        for mg,materialLengths in self.__materialsByMaterialGroup.items():
            #cutLengths=[l[1] for l in cutsByMaterial[mg]]
            cutLengths=cutsByMaterial[mg]
            materialLengths,materialCuts,waste,cost=self.pack(cutLengths,materialLengths)
            totWaste+=waste
            totCost+=cost
            assignments[mg]=(materialLengths,materialCuts)

        return assignments,totWaste,totCost
    
    def pack(self,cuts,materials):
        """
        cutLengths - list of cut lengths
        materials - list of tuples of materials (length,cost)
        """
        random.shuffle(materials)
        cuts.sort(cmp=sortCuts,reverse=True)
        materialAssignments=[(0,0.0,0.0)]*len(cuts)
        #materialCosts=[0.0]*len(cuts)
        materialResiduals=[0.0]*len(cuts)

        m=materials[0] #random.choice(materials)
        materialAssignments[0]=m
        materialResiduals[0]=m[1]
        materialCuts=[[None]*10]*len(cuts)
        cutCounts=[0]*len(cuts)
        materialIndex=0

        totCutLen=0.0
        totMaterLen=m[1]
        totCost=m[2]
        
        #global l1Tot,l2Tot,l3Tot
        
        #l1Enter=time.clock()
        for cut in cuts:
            cutLen=cut[1]
            
            fit=False
            
            #l2Enter=time.clock()
            ##TODO: test for minimum cut length first to avoid this loop if it's of no use
            #try to fit the cut in the current assignments
            for i in xrange(materialIndex+1): #len(materialResiduals)):
                if cutLen<=materialResiduals[i]:
                    try:
                        materialCuts[i][cutCounts[i]-1]=cut
                    except:
                        materialCuts[i].append(cut)
                    materialResiduals[i]-=cutLen
                    cutCounts[i]+=1
                    fit=True
                    totCutLen+=cutLen
                    break
            #l2Tot+=time.clock()-l2Enter
            
            #the cut doesn't fit in the current material options, add another
            if not fit:
                
                #l3Enter=time.clock()
                for m in materials:
                    #m=random.choice(materials)
                    if cutLen<=m[1]:
                        try:materialAssignments[materialIndex+1]=m
                        except:
                            #print len(materialAssignments)
                            #print materialIndex
                            #print materialAssignments
                            raise
                        materialResiduals[materialIndex+1]=m[0]-cutLen
                        materialCuts[materialIndex+1]=[cut,] + [None]*9
                        cutCounts[materialIndex+1]=0
                        materialIndex+=1
                        totCutLen+=cutLen
                        totMaterLen+=m[1]
                        totCost+=m[2]
                        break
                #l3Tot+=time.clock()-l3Enter
        
        #l1Tot+=time.clock()-l1Enter
        
        #cost=sum([m[2] for m in materialAssignments])

        #totCuts=sum([sum([c[1] for c in cl if c!=None]) for cl in materialCuts if cl!=None])
        waste=totMaterLen-totCutLen

        return materialAssignments,materialCuts,waste,totCost
    
class Cuts(list):
    def __init__(self,cutsPath):
        f=open(cutsPath)
        self.columns=f.readline().strip().split(',')
        self.materialGroups=set()
        mi=self.columns.index('MaterialGroup')
        for l in f.readlines():
            ll=l.strip()
            if len(ll)==0 or ll[0]=='#': continue
            ll=ll.split(',')
            self.append(Cut(self.columns,ll))
            self.materialGroups.add(ll[mi])
        f.close()
        
    def cutsByMaterialGroup(self,materialGroup):
        cuts={}
        for c in range(len(self)):
            if self[c].materialgroup==materialGroup:
                cuts[c]=self[c]
        return cuts

class Materials(list):
    def __init__(self,materialsPath):
        f=open(materialsPath)
        self.columns=f.readline().strip().split(',')
        self.materialGroups=set()
        mi=self.columns.index('MaterialGroup')
        for l in f.readlines():
            ll=l.strip()
            if len(ll)==0 or ll[0]=='#': continue
            ll=ll.split(',')
            self.append(Material(self.columns,ll))
            self.materialGroups.add(ll[mi])

    def materialsByMaterialGroup(self,materialGroup):
        materials={}
        for m in range(len(self)):
            if self[m].materialGroup==materialGroup:
                materials[m]=self[m]
        return materials
    
class Material(dict):
    def __init__(self,columns,data):
        self.columns=columns
        self.data=data
        for i in range(len(columns)):
            self[columns[i].lower()]=data[i]
        
        self.length=float(self.length)
        self.cost=float(self.cost)
            
    def __getattr__(self,attr):
        if self.__dict__.has_key(attr):
            return self.__dict__[attr]
        return self.__getitem__(attr.lower())

    def keys(self):
        return self.columns
    
    def items(self):
        return [(self.columns[i],self.data[i]) for i in range(len(self.columns))]
    
class Cut(dict):
    def __init__(self,columns,data):
        self.columns=columns
        self.data=data
        for i in range(len(columns)):
            self[columns[i].lower()]=data[i]
        
        self.cutlength=float(self.cutlength)
        self.trim=float(self.trim)
        
    def __getattr__(self,attr):
        
        if self.__dict__.has_key(attr):
            return self.__dict__[attr]
        return self.__getitem__(attr.lower())
    
    def keys(self):
        return self.columns
    
    def items(self):
        return [(self.columns[i],self.data[i]) for i in range(len(self.columns))]
    
    def totalLength(self):
        return float(self.cutlength) + float(self.trim)


class Test:
    def __init__(self,func,iters=1000):
        self.func=func
        self.iters=iters
        
    def run(self):
        min=9e10
        assignments=None
        for i in xrange(self.iters):
            assignments,waste,cost=self.func(assignments)
            if cost<=min:
                min=cost
                ba=assignments
                bw=waste
        
        print
        print 'Minimum cost',min
        print 'Minimum waste',bw
        print

def sortCuts(c1,c2):
    if c1[1]>c2[1]:
        return 1
    return 0

if __name__=='__main__':
    
    cutsPath=r'C:\Users\Tod\projects\uuc-ke7fxl\OptimalCut\cuts.lst'
    materialsPath=r'C:\Users\Tod\projects\uuc-ke7fxl\OptimalCut\materials.lst'
    #cuts=Cuts(cutsPath)
    #materials=Materials(materialsPath)
    
    project=Project(cutsPath,materialsPath)
    
    test=Test(project.assignCuts,1000)
    
##    import time
##    st=time.clock()
##    test.run()
##    et=time.clock()
##    print et-st
    
    import cProfile
    cProfile.run('test.run()','profile.txt')
    
    import pstats
    s=pstats.Stats('profile.txt')
    s=s.strip_dirs()
    s.sort_stats('time')
    s.print_stats()
    s.dump_stats('stats.txt')
    
    #print l1Tot,l2Tot,l3Tot