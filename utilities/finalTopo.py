#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call

def myNetwork():

    net = Mininet( topo=None,
                   build=False,
                   ipBase='10.0.0.0/8')

    info( '*** Adding controller\n' )
    c0=net.addController(name='c0',
                      controller=RemoteController,
                      protocol='tcp',
                      port=6633)

    info( '*** Add switches\n')
    s3 = net.addSwitch('s3', cls=OVSKernelSwitch, protocols="OpenFlow13")
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch, protocols="OpenFlow13")
    s4 = net.addSwitch('s4', cls=OVSKernelSwitch, protocols="OpenFlow13")
    s5 = net.addSwitch('s5', cls=OVSKernelSwitch, protocols="OpenFlow13")
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch, protocols="OpenFlow13")
    s6 = net.addSwitch('s6', cls=OVSKernelSwitch, protocols="OpenFlow13")
    s7 = net.addSwitch('s7', cls=OVSKernelSwitch, protocols="OpenFlow13")

    info( '*** Add hosts\n')
    #Endpoints
    h1 = net.addHost('h1', cls=Host, mac='3a:20:45:92:93:fc', ip='10.0.0.1', defaultRoute=None)
    h2 = net.addHost('h2', cls=Host, mac='4e:f0:8b:08:4f:07', ip='10.0.0.2', defaultRoute=None)
    h3 = net.addHost('h3', cls=Host, mac='b2:67:ff:f4:e4:18', ip='10.0.0.3', defaultRoute=None)
    h4 = net.addHost('h4', cls=Host, mac='ba:a1:a6:16:e0:91', ip='10.0.0.4', defaultRoute=None)
    h5 = net.addHost('h5', cls=Host, mac='52:e7:7c:5c:02:66', ip='10.0.0.5', defaultRoute=None)
    h6 = net.addHost('h6', cls=Host, mac='36:35:11:54:5f:95', ip='10.0.0.6', defaultRoute=None)
    h7 = net.addHost('h7', cls=Host, mac='22:bf:70:06:90:ec', ip='10.0.0.7', defaultRoute=None)
    h8 = net.addHost('h8', cls=Host, mac='02:76:81:72:1e:16', ip='10.0.0.8', defaultRoute=None)
    
    #Switch 'Hosts'
    h9 = net.addHost('h9', cls=Host, ip='10.0.0.9', defaultRoute=None)
    h10 = net.addHost('h10', cls=Host, ip='10.0.0.10', defaultRoute=None)
    h11 = net.addHost('h11', cls=Host, ip='10.0.0.11', defaultRoute=None)
    h12 = net.addHost('h12', cls=Host, ip='10.0.0.12', defaultRoute=None)
    h13 = net.addHost('h13', cls=Host, ip='10.0.0.13', defaultRoute=None)
    h14 = net.addHost('h14', cls=Host, ip='10.0.0.14', defaultRoute=None)
    h15 = net.addHost('h15', cls=Host, ip='10.0.0.15', defaultRoute=None)
    
    #External
    h16 = net.addHost('h16', cls=Host, mac='f6:52:56:1a:37:1f', ip='10.0.0.16', defaultRoute=None)

    info( '*** Add links\n')
    net.addLink(s1, h16)
    net.addLink(s1, h15)
    net.addLink(s1, s2)
    net.addLink(s1, s3)
    net.addLink(s3, s7)
    net.addLink(s3, s6)
    net.addLink(s6, h5)
    net.addLink(s6, h6)
    net.addLink(s7, h7)
    net.addLink(s7, h8)
    net.addLink(s5, h4)
    net.addLink(s5, h3)
    net.addLink(s4, h2)
    net.addLink(s4, h1)
    net.addLink(s5, h13)
    net.addLink(s5, s2)
    net.addLink(s2, s4)
    net.addLink(s2, h12)
    net.addLink(s3, h11)
    net.addLink(s7, h9)
    net.addLink(s4, h14)
    net.addLink(s6, h10)

    info( '*** Starting network\n')
    net.addNAT().configDefault()
    net.build()
    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info( '*** Starting switches\n')
    net.get('s3').start([c0])
    net.get('s2').start([c0])
    net.get('s4').start([c0])
    net.get('s5').start([c0])
    net.get('s1').start([c0])
    net.get('s6').start([c0])
    net.get('s7').start([c0])

    info( '*** Post configure switches and hosts\n')

    CLI(net)
    
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()

