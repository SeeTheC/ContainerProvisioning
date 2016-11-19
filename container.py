#!/usr/bin/python3.5 -W ignore

from pylxd import Client
from time import time
from cpbo import Config
from cpbo import ServerBO
from cpbo import ContainerBO
from cpthread import ContainerInfoThread
'''
----------------------------------------------
    Class: Manage All servers
----------------------------------------------
'''
class Server:
    overloadThreshold=0.8

    def __init__(self):
        self.servers=self.loadAllServer();
        # get containers SLA from json file
        self.SLA=None
        self.containers=self.getAllContainersStatus()

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
        cid=int(time()*1000);
        hw={};
        if(container_bo.cpu!=None and container_bo.cpu!=0):
            hw["limits.cpu"]=str(container_bo.cpu);

        if(container_bo.memory!=None and container_bo.memory!=0):
            hw["limits.memory"]=str(container_bo.memory)+"MB";
        config = {'name': "cp"+str(cid),  "config": hw, 'source': {'type': 'image','fingerprint':str(Config.cp_config["defaultFingerprint"])}}
        container = self.servers[server_index].client.containers.create(config, wait=True);
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
        for c_count in range(0,len(containers)):
            clist=containers[c_count];
            cbo_list=list();
            for c in clist:
                cbo=ContainerBO();
                cbo.container=c;
                cbo.name=c.name;
                cbo_list.append(cbo);
            containers[c_count]=cbo_list;
        containers=ContainerInfoThread.getCurrentRunStatus(containers);

        for clist in containers:
            print("----------")
            for c in clist:
                print(str(c.isRunning())+"\t cpu:"+str(c.getCpuLimit())+"\t mem:"+str(c.getMemoryLimit()));
                print("cpu_util: "+str(c.cpu_util)+"\tmem_util : "+str(c.mem_util)+"\n\n");

        return containers;

        def getOverloadedContainers(self):
            pass


if (__name__ == "__main__"):
    Config.init();
    ser=Server();
    print("Monitoring Tool started ...")
    c1=ContainerBO();
    c1.cpu=2;
    c1.memory=256;
    ser.createContainer(0,c1);
    ser.getAllContainersStatus();
    print("success");
