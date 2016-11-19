#!/usr/bin/python3.5 -W ignore

from container import Server
from cpbo import Config
from cpbo import ServerBO
from cpbo import ContainerBO
from pylxd import Client
from json import load, dump
from constants import Constants
class Monitor():
    OlG=8;#Olg: Overload Gap
    UlG=5;#Ulg: Underload Gap
    def __init__(self):
        Config.init()
        print("Initialitation done.");
        self.cp = Server()
        self.sla=Server.SLA;            
        print("Monitor Started...");
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
                if (cbo.sname not in sla) or (cbo.name not in sla[cbo.sname]):
                    continue;
                #checking container is underflow or not
                curMem=cbo.getMemoryLimit();
                u=cbo.mem_util;                
                uPercent=u/curMem;
                if(uPercent < Constants.MemThresholdPercent):                                        
                    delta=Constants.MemThresholdPercent-Constants.UGPercent;
                    exceptedMemSize=u//delta;
                    cbo.exceptedMemSize=exceptedMemSize;
                    scList.append(cbo);
                    print(cbo.name+"  cur:%d new:%d"%(curMem,exceptedMemSize));                
            underList.append(scList);
        return underList;
        
    def findMachine(self, cpu, memory):
        containers = self.server.getAllContainers()


def main():
    try:
        m = Monitor();
        m.getUnderLoadServer(m.cp.containers);
    except KeyboardInterrupt as e:
        print("\nReceived Keyboard Interrupt")
    finally:
        if Server.SLA != None:
            print("Dumping contents of SLA into file")
            with open('sla.json', 'w') as f:
                dump(Server.SLA, f)
    
    
if __name__ == '__main__':
    main()
