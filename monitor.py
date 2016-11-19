#!/usr/bin/python3.5 -W ignore

from container import Server
from pylxd import Client

class Monitor():
    def __init__(self):
        Config.init()
        server = Server()
        print("Monitor Started")

    def findMachine(self, cpu, memory):
        containers = self.server.getAllContainers()


def main():
    monitor = Monitor()

if __name__ == '__main__':
    main()
