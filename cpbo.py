from pylxd import  Client
import json
'''
-------------------------------------------
    Class: Loads the Configuration class
----------------------------------------------
'''
class Config:
    server_config=None;
    cp_config=None;
    
    @staticmethod
    def init():
        Config.loadCpJson();
        Config.loadServerJson();        
        
    @staticmethod     
    def loadCpJson():
        cp_file=open("cp.config","r")
        Config.cp_config=json.load(cp_file);        

    @staticmethod     
    def loadServerJson():
        s_file=open("server.config","r");
        Config.server_config=json.load(s_file);        


'''
-------------------------------------------
    Class: Class obj will info about the server
----------------------------------------------
'''

class ServerBO:
    '''
    -------------------------------------------
        Desc: Constructor
    ----------------------------------------------
    '''
    def __init__(self,_host,_uri):
        self.host=_host;
        self.uri=_uri;
        self.client=self.creatClient();

    '''
    -------------------------------------------
        Desc: Creates the lxd client obj
        return : Obj is successfull else None
    ----------------------------------------------
    '''        
    def creatClient(self):
        client= Client(endpoint=self.uri, cert=(Config.cp_config["cert"],Config.cp_config["key"]),verify=False);
        client.authenticate(Config.cp_config["trustPassword"]);
        if(client.trusted):
            return client;
        else:
            return None;

'''
-------------------------------------------
    Class: Class obj will info about the server
----------------------------------------------
'''
class ContainerBO:
    '''
    -------------------------------------------
        Desc: Constructor
    ----------------------------------------------
    '''
    def __init__(self):
        self.cpu=None;
        self.memory=None;
