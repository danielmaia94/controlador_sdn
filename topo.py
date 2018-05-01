"Topologia utilizada no trabalho final da disciplina de Procolos de Comunicacao: EXPLORANDO OPENFLOW EFICIENTE DE VIDEOS"
#Daniel Maia Cunha - 243672 e Gabriel Piscoya D'Avila 

from mininet.topo import Topo

class MyTopo( Topo ):
    def __init__( self ):
        # Initialize topology
        Topo.__init__( self )

        # Add hosts
	o_cdn1 = self.addHost('h1')
	o_cdn2 = self.addHost('h2')
	cdn = self.addHost('h3')
	user_1 = self.addHost('h4')
	user_2 = self.addHost('h5')

	# Add switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')
        s5 = self.addSwitch('s5')
        s6 = self.addSwitch('s6')
        s7 = self.addSwitch('s7')
        s8 = self.addSwitch('s8')
        s9 = self.addSwitch('s9')
        s10 = self.addSwitch('s10')
	s11 = self.addSwitch('s11')

        # Add links
        self.addLink(s1, s2)
        self.addLink(s1, s3)
        self.addLink(s2, s3)
        self.addLink(s3, s4)
        self.addLink(s4, s5)
        self.addLink(s4, s6)
        self.addLink(s5, s6)
        self.addLink(s6, o_cdn1)
        self.addLink(s6, s8)
        self.addLink(s8, o_cdn2)
	self.addLink(s5, s7)
	self.addLink(s7, s9)
	self.addLink(s8, s10)
	self.addLink(s10, s11)
	self.addLink(s9, s11)
	self.addLink(s11, cdn)
	self.addLink(s11, user_1)
	self.addLink(s11, user_2)

topos = { 'mytopo': ( lambda: MyTopo() ) }
