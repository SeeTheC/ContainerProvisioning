#!/usr/bin/python3.5 -W ignore

from container import Server
from cpbo import Config
from cpbo import ServerBO
from cpbo import ContainerBO
from pylxd import Client
from json import load, dump

class Monitor():
    a=10;
    def __init__(self):
        Config.init()
        print("Initialitation done.");
        self.cp = Server()
        print("Monitor Started...");
    def getUnderLoadServer(self):
        cp=self.cp;
        sla=Server.SLA;
    def findMachine(self, cpu, memory):
        containers = self.server.getAllContainers()


def main():
    try:
        monitor = Monitor();
    except KeyboardInterrupt as e:
        print("\nReceived Keyboard Interrupt")
    finally:
        if Server.SLA != None:
            print("Dumping contents of SLA into file")
            with open('sla.json', 'w') as f:
                dump(Server.SLA, f)


if __name__ == '__main__':
    main()
