import random

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
        
    def assignCuts(self,baseAssignments=None):
        if baseAssignments!=None:
            #print len(baseAssignments)
            random.shuffle(baseAssignments)
            l=len(baseAssignments)/2
            assignments=baseAssignments[:l]
            #print len(assignments)
            
            cutsGrouped={}
            for assignment in baseAssignments[l:]:
                m=assignment[0]
                g=self.materials[m].materialGroup
                if not cutsGrouped.has_key(g):
                    cutsGrouped[g]=[]
                for cut in assignment[1]:
                    l=self.cuts[cut].totalLength()
                    cutsGrouped[g].append((cut,l))
        
        else:
            cutsGrouped=self.__cutsByMaterialGroup
            print cutsGrouped
            assignments=[]
        
        totalCost=0.0
        totalLength=0.0
        totalWaste=0.0
        
        for mg,cuts in cutsGrouped.items():
            materialOptions=self.__materialsByMaterialGroup[mg]
            cuts=cuts[:]
            testCuts=cuts[:]
            random.shuffle(testCuts)
            materialIndex,residualLength,cost=random.choice(materialOptions)
            while 1:
                assignment=[-1,[-1]*5]
                ai=0
                for cut in testCuts:
                    if cut[1]<=residualLength:
                        
                        if assignment[0]==-1:
                            assignment[0]=materialIndex
                            totalCost+=cost
                            totalLength+=residualLength
                            
                        residualLength-=cut[1]
                        try:
                            assignment[1][ai]=cut[0] #.append(cut[0])
                            ai+=1
                        except:
                            assignment[1].append(cut[0])
                            ai+=1
                        
                        print assignment
                        
                        cuts.remove(cut)
                
                totalWaste+=residualLength
                assignments.append(assignment)

                if len(cuts)==0:
                    break
                
                testCuts=cuts[:]
                materialIndex,residualLength,cost=random.choice(materialOptions)
                
        return assignments,totalLength,totalWaste,totalCost
        
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
            assignments,length,waste,cost=self.func()
            if cost<=min:
                min=cost
                ba=assignments
                bl=length
                bw=waste
        
        print min,bl,bw
            
            
if __name__=='__main__':
    import cProfile
    
    cutsPath=r'C:\Users\Tod\projects\uuc-ke7fxl\OptimalCut\cuts.lst'
    materialsPath=r'C:\Users\Tod\projects\uuc-ke7fxl\OptimalCut\materials.lst'
    #cuts=Cuts(cutsPath)
    #materials=Materials(materialsPath)
    
    project=Project(cutsPath,materialsPath)
    
    test=Test(project.assignCuts,1)
    
    cProfile.run('test.run()','profile.txt')
    
    import pstats
    s=pstats.Stats('profile.txt')
    s=s.strip_dirs()
    s.sort_stats('time')
    s.print_stats()
    s.dump_stats('stats.txt')
    