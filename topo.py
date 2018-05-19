"Topologia utilizada no trabalho final da disciplina de Procolos de Comunicacao: EXPLORANDO OPENFLOW EFICIENTE DE VIDEOS"
#Daniel Maia Cunha - 243672 e Gabriel Piscoya D'Avila 

from mininet.topo import Topo

class MyTopo( Topo ):
    def __init__( self ):
        # Initialize topology
        Topo.__init__( self )

        # Add hosts
	user1 = self.addHost('h1')
	user2 = self.addHost('h2')
	cdn = self.addHost('h3')

	# Add switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')
        s5 = self.addSwitch('s5')
        s6 = self.addSwitch('s6')

        # Add links
        self.addLink(s1, s2)
        self.addLink(s1, s3)
        self.addLink(s3, s2)
        self.addLink(s2, cdn)
        self.addLink(s3, s4)
        self.addLink(s4, s5)
        self.addLink(s4, s6)
        self.addLink(s6, user1)
        self.addLink(s5, user2)

topos = { 'mytopo': ( lambda: MyTopo() ) }
