#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch, OVSSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call
from functools import partial

def MyTopo():
    switch = partial( OVSSwitch, protocols='OpenFlow13' )
    net = Mininet( topo=None,
                   build=False,
                   ipBase='10.0.0.0/24',switch=switch)

    info( '*** Adding controller\n' )
    c1=net.addController(name='c1',
                      controller=RemoteController,
                      ip='127.0.0.1',
                      protocol='tcp',
                      port=6633)

    info( '*** Add switches\n')
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch, protocols='OpenFlow13', dpid='1')
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch, protocols='OpenFlow13', dpid='2')
    s3 = net.addSwitch('s3', cls=OVSKernelSwitch, protocols='OpenFlow13', dpid='3')
    s4 = net.addSwitch('s4', cls=OVSKernelSwitch, protocols='OpenFlow13', dpid='4')

    
    info( '*** Add hosts\n')
    cdn   = net.addHost('h1', cls=Host, ip='10.0.0.1/24', mac='00:00:00:00:00:01', defaultRoute=None)
    user2 = net.addHost('h2', cls=Host, ip='10.0.0.2/24', mac='00:00:00:00:00:02', defaultRoute=None)
    user3 = net.addHost('h3', cls=Host, ip='10.0.0.3/24', mac='00:00:00:00:00:03', defaultRoute=None)
    user4 = net.addHost('h4', cls=Host, ip='10.0.0.4/24', mac='00:00:00:00:00:04', defaultRoute=None)
    user6 = net.addHost('h6', cls=Host, ip='10.0.0.6/24', mac='00:00:00:00:00:06', defaultRoute=None)

    info( '*** Add links\n')
    
    # Switch 1
    net.addLink(s1, s2, port1 = 1, port2 = 1)
    net.addLink(s1, s3, port1 = 2, port2 = 2)    
    net.addLink(s1, cdn, port1 = 3)
    
    # Switch 2
    net.addLink(s2, s4, port1 = 2, port2 = 2)
    net.addLink(s2, user2, port1 = 3)
    
    # Switch 3
    net.addLink(s3, s4, port1 = 1, port2 = 1)
    net.addLink(s3, user3, port1 = 3)   
    net.addLink(s3, user6, port1 = 4)   

    # Switch 4
    net.addLink(s4, user4, port1 = 3)   
      

    info( '*** Starting network\n')
    net.build()
    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info( '*** Starting switches\n')
    net.get('s1').start([c1])
    net.get('s3').start([c1])
    net.get('s2').start([c1])
    net.get('s4').start([c1])
    info( '*** Post configure switches and hosts\n')

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    MyTopo()

topos = { 'mytopo': ( lambda: MyTopo() ) }
