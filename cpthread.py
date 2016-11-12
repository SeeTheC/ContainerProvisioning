#!/usr/bin/python3.5

import threading
import time
from cpbo import ContainerBO

'''
-----------------------------------------------
        Class: Real time status fetching
-----------------------------------------------
'''
class ContainerInfoThread (threading.Thread):

    '''
    -----------------------------------------------
        Desc: Constructor
    -----------------------------------------------
    '''
    def __init__(self, threadId,servers_containers,server_index,container_index):
        threading.Thread.__init__(self)
        self.threadId = threadId
        self.containers=servers_containers;
        self.s_index=server_index;
        self.c_index=container_index;

    '''
    -----------------------------------------------
        Desc: Thread Run method
    -----------------------------------------------
    '''

    def run(self):
        c=self.containers[self.s_index][self.c_index];
        status=c.getRunningStatus();
        c.cpu_util=status["cpu"] if status != None else None;
        c.mem_util=status["mem"] if status != None else None;
        self.containers[self.s_index][self.c_index]=c;

    '''
    -----------------------------------------------
        Desc: Static Method for getting status
    -----------------------------------------------
    '''
    @staticmethod
    def getCurrentRunStatus(containers):
        threads = [];
        t_count=0;
        for s_count in range(0,len(containers)):
            clist=containers[s_count];
            for c_count in range(0,len(clist)):
                c=clist[c_count];
                c_thread=ContainerInfoThread(t_count,containers,s_count,c_count);
                threads.append(c_thread);
                c_thread.start();
                t_count+=1;
        for t in threads:
            t.join();
        return containers;
