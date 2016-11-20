#!/usr/bin/python3.5 -W ignore

from container import Server
from cpbo import Config
from cpbo import ServerBO
from cpbo import ContainerBO
from pylxd import Client
from time import sleep
from json import load, dump
from constants import Constants
class Monitor():
    def __init__(self):
        Config.init()
        print("Initialitation done.");
        self.cp = Server()
        self.sla=Server.SLA;
        print("Monitor Started...");

    def run(self):
        while(True):
            print("-----------------------------------------------------------------------\n");
            self.periodicMonitor();
            sleep(Constants.MonitorDuration);   

    def periodicMonitor(self):
        cp=self.cp;
        containers=cp.getAllContainersStatus();        
        cOverCList=self.getOverLoadServer(containers);
        cUnderList=self.getUnderLoadServer(containers);
        n=len(cp.servers);
        # Trying for container resize
        cToMigrate=list();        
        #soc: server's overload container list
        for i in range(n):
            sContToMigare=self.tryServerContainerResizing(cOverCList[i],cUnderList[i]);
            cToMigrate.append(sContToMigare);
        
    def tryServerContainerResizing(self,scOverCList,scUnderList):                
        #containers to migrate because it can't be resized            
        ocRemaining=self.trySCROneOnOne(scOverCList,scUnderList);        
        ocRemaining=self.trySCROneToMany(ocRemaining,scUnderList);        
        return ocRemaining;
    '''
    -----------------------------------------------------------
           Desc: Try Server Container Resize One-On-One
    ---------------------------------------------------------
    '''
    def trySCROneOnOne(self,scOverList,scUnderList):
        ocRemaining=list(); 
        print("#OneOnOne: Per server overloaded list",len(scOverList));
        for ocbo in scOverList:
            #print("[OneOnOne: Overload Cname %s by amount %s ]"%(ocbo.name,ocbo.expectedMemSize));
            ucbo=self.findSingleContainerToResize(ocbo.expectedMemSize,scUnderList);
            if(ucbo==None):
                print("[OneOnOne: No appropiate container found for (%s,%s) which needs memory %sMB]"%(ocbo.sname,ocbo.name,ocbo.expectedMemSize//Constants.MBtoKB))
                #no container to resize. Going for migration.
                ocRemaining.append(ocbo);
            else:
                #resize;
                print("OneOnOne: Resizing (%s,%s) which needs memory %sMB using container (%s,%s)"%(ocbo.sname,ocbo.name,ocbo.expectedMemSize//Constants.MBtoKB,ucbo.sname,ucbo.name))                                    
                uNewMem=ucbo.getMemoryLimit()-ocbo.expectedMemSize;
                oNewMem=ocbo.getMemoryLimit()+ocbo.expectedMemSize;
                ucbo.setMemoryLimit(uNewMem);
                ocbo.setMemoryLimit(oNewMem);                                
                ucbo.expectedMemSize=ucbo.expectedMemSize-ocbo.expectedMemSize;
                ocbo.expectedMemSize=0;                                                   
        return ocRemaining;

    
    def findSingleContainerToResize(self,expectedMemSize,cUnderList):
        for ucbo in cUnderList:
            if(expectedMemSize<ucbo.expectedMemSize):
                return ucbo;
        return None;

    '''
    -----------------------------------------------------------
           Desc: Try Server Container Resize One-On-Many
    ---------------------------------------------------------
    '''
    def trySCROneToMany(self,scOverList,scUnderList):
        ocRemaining=list();
        print("#OneOnMany: Per server overloaded list",len(scOverList));    
        isResized=False;
        for ocbo in scOverList:
            #print("[OneOnMany: Overload Cname:%s]"%(ocbo.name));
            isResized=False;
            for ucbo in scUnderList:
                if(ucbo.expectedMemSize>1 and ocbo.expectedMemSize>1):
                    #resize;
                    isResized=True;
                    print(">OneOnmany: Resizing (%s,%s) which needs memory %sMB using container (%s,%s)"%(ocbo.sname,ocbo.name,ocbo.expectedMemSize//Constants.MBtoKB,ucbo.sname,ucbo.name))                                                        
                    incMem= ( ucbo.expectedMemSize if ocbo.expectedMemSize >= ucbo.expectedMemSize else ocbo.expectedMemSize);
                    uMaxMem=ucbo.getMemoryLimit();
                    oMaxMem=ocbo.getMemoryLimit();
                    uNewMem=uMaxMem-incMem;
                    oNewMem=oMaxMem+incMem;
                    remainingMem=ocbo.expectedMemSize-incMem;
                    #print("incMem",incMem//Constants.MBtoKB);                                        
                    #print("uMaxMem",uMaxMem//Constants.MBtoKB);
                    #print("ucbo.expectedMemSize",ucbo.expectedMemSize//Constants.MBtoKB);
                    #print("umem",uNewMem//Constants.MBtoKB);
                    #print("oMaxMem",oMaxMem//Constants.MBtoKB);                    
                    #print("ocbo.expectedMemSize",ocbo.expectedMemSize//Constants.MBtoKB);                    
                    #print("oNewMem",oNewMem//Constants.MBtoKB);
                    #print("delta:",remainingMem//Constants.MBtoKB);
                    ucbo.expectedMemSize=0;
                    ocbo.expectedMemSize=remainingMem;                    
                    ucbo.setMemoryLimit(uNewMem);
                    ocbo.setMemoryLimit(oNewMem);
                    
            if(not isResized):
                #no container to resize. Going for nextphase.                
                print("~[OneOnMany: No appropiate containers found for (%s,%s) which needs memory %sMB]"%(ocbo.sname,ocbo.name,ocbo.expectedMemSize//Constants.MBtoKB))                
                ocRemaining.append(ocbo);            
            elif(ocbo.expectedMemSize>0):
                print("~[OneOnMany: Unable to Resize (%s,%s) which needs memory %sMB completely.]"%(ocbo.sname,ocbo.name,ocbo.expectedMemSize//Constants.MBtoKB));                                                        
        return ocRemaining;

    '''
    ------------------------------------------------
           Desc: Under loaded server
    -------------------------------------------------
    '''
    def getUnderLoadServer(self,containers):
        cp=self.cp;
        underList=list();
        sla=self.sla;
        #sc: server's containers
        for sc in containers:
            scList=list();
            for cbo in sc:
                #line to be removed
                if (cbo.sname not in sla):
                    print("~Warning: Server %s is not in SLA."%(cbo.sname ))
                    continue;
                elif(cbo.name not in sla[cbo.sname]):
                    print("~Warning: Container %s of Server %s is not in SLA."%(cbo.name,cbo.sname ));
                    continue;
                if not(cbo.isRunning()):
                    print("~Warning: Container %s of Server %s is not RUNNING."%(cbo.name,cbo.sname ))
                    continue

                #checking container is underflow or not
                curMem=cbo.getMemoryLimit();
                u=cbo.mem_util;
                uPercent=u/curMem;
                if(uPercent < Constants.MemThresholdPercent):
                    delta=Constants.MemThresholdPercent-Constants.UGPercent;
                    expectedMemSize=curMem-u//delta;
                    print("CurMem:", curMem, "U:", u, "Delta:", delta, "U/Delta:", u//delta)
                    expectedMemSize=(0 if expectedMemSize<=0 else expectedMemSize);
                    cbo.expectedMemSize=expectedMemSize;
                    scList.append(cbo);
                    print("Underload: Server "+cbo.sname+" "+cbo.name+"  cur: %d decreaseBy: %d"%(curMem,expectedMemSize//Constants.MBtoKB));
            scList.sort(key=lambda obj: obj.expectedMemSize, reverse=True)
            underList.append(scList);
        return underList;

    '''
    ------------------------------------------------
           Desc: Over loaded server
    -------------------------------------------------
    '''
    def getOverLoadServer(self,containers):
        cp=self.cp;
        overList=list();
        sla=self.sla;
        #sc: server's containers
        for sc in containers:
            scList=list();
            for cbo in sc:
                #line to be removed
                if (cbo.sname not in sla):
                    print("~Warning: Server %s is not in SLA."%(cbo.sname ))
                    continue;
                elif(cbo.name not in sla[cbo.sname]):
                    print("~Warning: Container %s of Server %s is not in SLA."%(cbo.name,cbo.sname ));
                    continue;
                if not(cbo.isRunning()):
                    print("~Warning: Container %s of Server %s is not RUNNING."%(cbo.name,cbo.sname ))
                    continue
                
                #checking container is overflow or not
                curMem=cbo.getMemoryLimit();
                maxMem=self.sla[cbo.sname][cbo.name][1];
                if curMem >= maxMem:
                    continue;
                curUtil=cbo.mem_util;
                oPercent=curUtil/curMem;
                if(oPercent >= Constants.MemThresholdPercent):
                    delta=Constants.MemThresholdPercent-Constants.OGPercent;
                    expectedMemSize=curUtil//delta - curMem;
                    cbo.expectedMemSize= (expectedMemSize if expectedMemSize+curMem < maxMem else maxMem-curMem);
                    scList.append(cbo);
                    print("Overload: Server "+cbo.sname+" "+cbo.name+"  cur: %d increaseBy: %d"%(curMem,cbo.expectedMemSize//Constants.MBtoKB));
            scList.sort(key=lambda obj: obj.expectedMemSize, reverse=False)
            overList.append(scList);
        return overList;


    def findMachine(self, cpu, memory):
        containers = self.server.getAllContainers()


def main():
    try:
        m = Monitor();            
        m.run();
    except KeyboardInterrupt as e:
        print("\nReceived Keyboard Interrupt")
    finally:
        if Server.SLA != None:
            print("Dumping contents of SLA into file")
            with open('sla.json', 'w') as f:
                dump(Server.SLA, f)


if __name__ == '__main__':
    main()
