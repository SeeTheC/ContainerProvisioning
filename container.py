from pylxd import  Client
import time
from cpbo import Config
from cpbo import ServerBO
from cpbo import ContainerBO
'''
-------------------------------------------
    Class: Manage All servers
----------------------------------------------
'''
class Server:

    def __init__(self):
        self.servers=self.loadAllServer();

    '''
    -------------------------------------------
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
        Desc: Creats a container on specifc server
        with the givie
    ----------------------------------------------
    '''
    def createContainer(self,server_index,container_bo):
        cid=int(time.time()*1000);
        hw={};
        if(container_bo.cpu!=None and container_bo.cpu!=0):
            hw["limits.cpu"]=str(container_bo.cpu);
            
        if(container_bo.memory!=None and container_bo.memory!=0):
            hw["limits.memory"]=str(container_bo.memory)+"MB";
        config = {'name': "cp"+str(cid),  "config": hw, 'source': {'type': 'image','fingerprint':str(Config.cp_config["defaultFingerprint"])}}
        print(config);
        container = self.servers[server_index].client.containers.create(config, wait=True)
        return cid;

if (__name__ == "__main__"):
    Config.init();
    ser=Server();
    c1=ContainerBO();
    c1.cpu=2;
    c1.memory=256;
    ser.createContainer(0,c1);
    print("success");


