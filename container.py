#!/usr/bin/python3.5 -W ignore

from pylxd import Client
from time import time
from cpbo import Config
from cpbo import ServerBO
from cpbo import ContainerBO
from cpthread import ContainerInfoThread
from json import load, dump
from constants import Constants
'''
----------------------------------------------
    Class: Manage All servers
----------------------------------------------
'''

class Server:
    overloadThreshold=0.8
    SLA = None
    def __init__(self):
        self.servers=self.loadAllServer();
        # get containers SLA from json file
        try:
            with open('sla.json') as f:
                Server.SLA = load(f)
        except Exception as e:
            Server.SLA = dict()
        self.containers=self.getAllContainersStatus()
        #self.loadExistingContainers()

    '''
    ---------------------------------------------
        Desc: Init all server from config file
    ----------------------------------------------
    '''
    def loadAllServer(self):
        server=list();
        for sinfo in Config.server_config :
            try:
                s=ServerBO(sinfo["host"],sinfo["uri"]);
                server.append(s);
            except Exception as e:
                print("Error: Unable to init server host:"+sinfo["host"]+"\t uri:"+sinfo["uri"]);
                #print(Exception.with_traceback());
        return server;

    '''
    -----------------------------------------------
        Desc: Creats a container on specifci server
        with the givien config
    -----------------------------------------------
    '''
    def createContainer(self,server_index,container_bo):
        container_bo.name='cp' + str(int(time()*1000));
        hw={};
        if(container_bo.cpu!=None and container_bo.cpu!=0):
            hw["limits.cpu"]=str(container_bo.cpu);

        if(container_bo.memory!=None and container_bo.memory!=0):
            hw["limits.memory"]=str(container_bo.memory)+"MB";
        config = {'name': container_bo.name,  "config": hw, 'source': {'type': 'image','fingerprint':str(Config.cp_config["defaultFingerprint"])}}
        container = self.servers[server_index].client.containers.create(config, wait=True);
        container.start(wait=False);
        try:
            Server.SLA[self.servers[server_index].host][container_bo.name] = [container_bo.cpu, container_bo.memory * Constants.MBtoKB]
        except KeyError as e:
            Server.SLA[self.servers[server_index].host] = dict()
            Server.SLA[self.servers[server_index].host][container_bo.name] = [container_bo.cpu, container_bo.memory * Constants.MBtoKB]

        return container;

    '''
    -----------------------------------------------
        Desc: Returns list of container
    -----------------------------------------------
    '''
    def getAllContainersStatus(self):
        containers=list();
        for s in self.servers:
            containers.append(s.client.containers.all());
        #process list of containers
        si=0;
        for c_count in range(0,len(containers)):
            clist=containers[c_count];
            cbo_list=list();
            for c in clist:
                cbo=ContainerBO();
                cbo.container=c;
                cbo.name=c.name;
                cbo.sname=self.servers[si].host;
                cbo_list.append(cbo);
            containers[c_count]=cbo_list;
            si+=1;
        containers=ContainerInfoThread.getCurrentRunStatus(containers);
        #self.printContainersDetail(containers);
        return containers;

    def printContainersDetail(self,containers):
        print("------------------[Printing]----------------------------");
        si=0;
        for clist in containers:
            if(len(clist)>0):
                print("_______________________[Server:"+str(si)+"]__________________________________");
            for c in clist:
                print("sname:"+c.sname+"\tcname:"+c.name+"\tRunning:"+str(c.isRunning())+"\t cpu:"+str(c.getCpuLimit())+"\t mem:"+str(c.getMemoryLimit())+"\tcpu_util: "+str(c.cpu_util)+"\tmem_util : "+str(c.mem_util)+"\n\n");
            si+=1;
        print("--------------------------------------------------------------------");

    '''
    -----------------------------------------------
        Desc: Loads existing containers from servers
    -----------------------------------------------
    '''
    def loadExistingContainers(self):
        for sc in self.containers:
            for cbo in sc:
                try:
                    Server.SLA[cbo.sname][cbo.name] = [cbo.getCpuLimit(), cbo.getMemoryLimit()]
                except KeyError as e:
                    Server.SLA[cbo.sname] = dict()
                    Server.SLA[cbo.sname][cbo.name] = [cbo.getCpuLimit(), cbo.getMemoryLimit()]


if (__name__ == "__main__"):
    try:
        Config.init();
        ser=Server();
        print("Monitoring Tool started ...")
        c1=ContainerBO();
        c1.cpu=2;
        c1.memory=1024;
        ser.createContainer(0,c1);
        ser.getAllContainersStatus();
    except KeyboardInterrupt as e:
        print("\nReceived Keyboard Interrupt")
    finally:
        if Server.SLA != None:
            print("Dumping contents of SLA into file")
            with open('sla.json', 'w') as f:
                dump(Server.SLA, f)
