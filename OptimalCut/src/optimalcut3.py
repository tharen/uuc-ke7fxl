import numpy

class Project:
    def __init__(self,materialsFile,cutsFile):
        self.materialsFile=materialsFile
        self.cutsFile=cutsFile

        self.materials=[] #list of all available materials
        self.materialTypes={} #list of materials indexes grouped by material type id
        self.materialTypeNames={} #material type names keyed to type id
        self.cuts=[] #list of all project cuts
        self.materialCuts={} #cut indexes keyed to material type id
        self.jobCuts={} #cut indexes keyed to job id
        self.jobNames={} #job names keyed to job id
        
        self._readCuts(self.cutsFile)
        self._readMaterials(self.materialsFile)
    
    def _missingMaterials(self):
        """
        Find cuts with unmatched materials or lengths that exceed available materials
        """
        for materialTypeId,cuts in self.materialCuts.items():
            pass
    
    def __parseMaterialLine(self,l):
        #Id,TypeId,Material,Length,Cost
        ll=l.split(',')
        ll[0]=int(ll[0]) #material id
        ll[1]=int(ll[1]) #material type id
        #ll[2]=str(ll[2]) #material name
        ll[3]=float(ll[3]) #length
        ll[4]=float(ll[4]) #cost
        return ll
        
    def _readMaterials(self,materialsPath):
        materials=[]
        self.materialTypes={}
        self.materialTypeNames={}
        
        f=open(materialsPath)
        f.readline()
        for l in f.readlines():
            if len(l.strip())>0 and l[0] != '#':
                materials.append(self.__parseMaterialLine(l))
        
        #group materials by type id
        for m in range(len(materials)):
            t=materials[m][1]
            if not self.materialTypes.has_key(t):
                self.materialTypes[t]=[]
                self.materialTypeNames[t]=materials[m][2]
            self.materialTypes[t].append(m)
            
        self.materials=numpy.array(self.materials,copy=True)
        
    def __parseCutLine(self,cutLine):
        #CutId,ItemId,Item,PieceIndex,Piece,MaterialGroup,Material,CutLength,Trim,Optimize
        ll=cutLine.split(',')
        ll[0]=int(ll[0]) #cut id
        ll[1]=int(ll[1]) #job id
        #ll[2]=str(ll[2]) #job name
        ll[3]=int(ll[3]) #job cut index
        #ll[4]=str(ll[4]) #cut description
        ll[5]=int(ll[5]) #material type id
        #ll[6]=int(ll[6]) #material description
        ll[7]=float(ll[7]) #cut length
        ll[8]=float(ll[8]) #cut trim allowance
        ll[9]=bool(ll[9]) #include
        return ll

    def _readCuts(self,cutsPath='cuts.lst'):
        cuts=[]
        self.materialCuts={}
        self.jobCuts={}
        self.jobNames={}
        
        #read in the cuts list
        f=open(cutsPath)
        #skip the header
        f.readline()
        for l in f.readlines():
            #skip comments and blank lines
            if len(l.strip())>0 and l[0] != '#':
                cuts.append(self.__parseCutLine(l))
        
        #group cuts by material type
        for c in range(len(cuts)):
            g=cuts[c][5] #material type id
            #add the material group if it's not present already
            if not self.materialCuts.has_key(g):
                self.materialCuts[g]=[]
            self.materialCuts[g].append(c)
        
        #group cuts by job
        for c in range(len(cuts)):
            g=cuts[c][1] #job id
            #add the job group if it's not present already
            if not self.jobCuts.has_key(g):
                self.jobCuts[g]=[]
                self.jobNames[g]=cuts[c][2]
            self.jobCuts[g].append(c)
        
        self.cuts=numpy.array(cuts,copy=True)
        
        print len(self.cuts), 'cuts'
        print len(self.materialCuts),'material types'
        print len(self.jobCuts),'jobs'
        #print self.jobNames.values()
    
if __name__=='__main__':
    project=Project('materials.lst','cuts.lst',)
    
