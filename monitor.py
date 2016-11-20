#!/usr/bin/python3.5 -W ignore

from container import Server
from cpbo import Config
from cpbo import ServerBO
from cpbo import ContainerBO
from pylxd import Client
from json import load, dump
from constants import Constants
class Monitor():
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
                if not(cbo.isRunning()):
                    continue
                #checking container is underflow or not
                curMem=cbo.getMemoryLimit();
                u=cbo.mem_util;
                uPercent=u/curMem;
                if(uPercent < Constants.MemThresholdPercent):
                    delta=Constants.MemThresholdPercent-Constants.UGPercent;
                    expectedMemSize=u//delta;
                    cbo.expectedMemSize=expectedMemSize;
                    scList.append(cbo);
                    print(cbo.name+"  cur:%d new:%d"%(curMem,expectedMemSize));
            scList.sort(key=lambda obj: obj.expectedMemSize, reverse=False)
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
                if (cbo.sname not in sla) or (cbo.name not in sla[cbo.sname]):
                    continue;
                if not(cbo.isRunning()):
                    continue
                #checking container is overflow or not
                curMem=cbo.getMemoryLimit();
                if curMem >= self.sla[cbo.sname][cbo.name][1]:
                    print(cbo.name, curMem, self.sla[cbo.sname][cbo.name][1])
                    continue
                curUtil=cbo.mem_util;
                oPercent=curUtil/curMem;
                print("oPercent:", oPercent)
                if(oPercent >= Constants.MemThresholdPercent):
                    delta=Constants.MemThresholdPercent-Constants.OGPercent;
                    expectedMemSize=curUtil//delta;
                    cbo.expectedMemSize=expectedMemSize;
                    scList.append(cbo);
                    print(cbo.name+"  cur:%d new:%d"%(curMem,expectedMemSize));
            scList.sort(key=lambda obj: obj.expectedMemSize, reverse=True)
            overList.append(scList);
        return overList;


    def findMachine(self, cpu, memory):
        containers = self.server.getAllContainers()


def main():
    try:
        m = Monitor();
        print("Underloaded")
        for sc in m.getUnderLoadServer(m.cp.containers):
            for cbo in sc:
                print(cbo.name, cbo.expectedMemSize)
        print("Overloaded")
        for sc in m.getUnderLoadServer(m.cp.containers):
            for cbo in sc:
                print(cbo.name, cbo.expectedMemSize)
    except KeyboardInterrupt as e:
        print("\nReceived Keyboard Interrupt")
    finally:
        if Server.SLA != None:
            print("Dumping contents of SLA into file")
            with open('sla.json', 'w') as f:
                dump(Server.SLA, f)


if __name__ == '__main__':
    main()
