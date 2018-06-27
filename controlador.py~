from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib import hub
from ryu.controller import mac_to_port
from ryu.controller.handler import set_ev_cls
from ryu.lib.mac import haddr_to_bin
from ryu.lib import mac
from ryu.topology.api import get_switch, get_link
from ryu.app.wsgi import ControllerBase
from ryu.topology import event, switches
from collections import defaultdict
from operator import attrgetter
from ryu.lib.packet.arp import arp
from ryu.ofproto import ether
import sys
from ryu.lib.packet import ether_types
from ryu.lib import dpid as dpid_lib
from ryu.lib import ofctl_utils

HOST_IPADDR1 = "10.0.0.1"
HOST_IPADDR2 = "10.0.0.2"
HOST_IPADDR3 = "10.0.0.3"
HOST_IPADDR4 = "10.0.0.4"
HOST_IPADDR6 = "10.0.0.6"
HOST_MACADDR1 = "00:00:00:00:00:01"
HOST_MACADDR2 = "00:00:00:00:00:02"
HOST_MACADDR3 = "00:00:00:00:00:03"
HOST_MACADDR4 = "00:00:00:00:00:04"
HOST_MACADDR6 = "00:00:00:00:00:06"
HOST_PORT1 = 3
HOST_PORT2 = 3
HOST_PORT3 = 3
HOST_PORT4 = 3
HOST_PORT6 = 4

# switches da rede
switches = [1,2,3,4]

#mymac[srcmac]->(switch, port)
mymac = {}

# mapeia de um switch para outro
adjacency = defaultdict(lambda:defaultdict(lambda:None))

class OFPHandler(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]    
	
    def __init__(self, *args, **kwargs):
        super(OFPHandler, self).__init__(*args, **kwargs)

        # registra velocidade das portas
        self.port_speed = defaultdict(lambda:defaultdict(lambda:None))
        self.port_speed[1][1] = 0
	self.port_speed[1][2] = 0
	self.port_speed[1][3] = 0
	self.port_speed[2][1] = 0
	self.port_speed[2][2] = 0
	self.port_speed[2][3] = 0
	self.port_speed[3][1] = 0	
	self.port_speed[3][2] = 0
	self.port_speed[3][3] = 0
	self.port_speed[3][4] = 0
	self.port_speed[3][4] = 0
	self.port_speed[4][1] = 0
	self.port_speed[4][2] = 0
	self.port_speed[4][3] = 0

        # the length of speed list of per port and flow.
        self.state_len = 3    

        # mac -> porta
        self.mac_to_port = {}

        # O conteudo indica a porta que os conecta
        adjacency[1][1] = 0
        adjacency[1][2] = 1
        adjacency[1][3] = 2
        adjacency[1][4] = 0

        adjacency[2][1] = 1
        adjacency[2][2] = 0
        adjacency[2][3] = 0
        adjacency[2][4] = 2

        adjacency[3][1] = 2
        adjacency[3][2] = 0
        adjacency[3][3] = 0
        adjacency[3][4] = 1

        adjacency[4][1] = 0
        adjacency[4][2] = 2
        adjacency[4][3] = 1
        adjacency[4][4] = 0

        
        self.host_port = {}
        self.host_port["00:00:00:00:00:01"] = (1,3)
        self.host_port["00:00:00:00:00:02"] = (2,3) 
        self.host_port["00:00:00:00:00:03"] = (3,3) 
        self.host_port["00:00:00:00:00:06"] = (3,4) 
        self.host_port["00:00:00:00:00:04"] = (4,3) 
              
	# dict dp
	self.datapaths = {}

        # lista de dp
        self.datapath_list = []        
        
        # thread para monitorar trafego
        self.monitor_thread = hub.spawn(self._monitor)
    
	self.topology_api_app = self
    	
    #Requisita dados de trafego de todos os switches
    def _monitor(self):
        while True:
            for dp in self.datapath_list:
                self._request_stats(dp)
            hub.sleep(10)
            #print " "
            #print "*********************** Nova Leitura  ***************************"
            #print " "
# -----------------------------------------------------------------------------------
# 
# -----------------------------------------------------------------------------------
    #Retorna minima distancia de um nodo
    def minimum_distance(self, distance, Q):
	#print "Entrei Distancia minima"
        minimum = float('Inf')

        node = 0
        for v in Q:
            #print "Distance[" + str(v) + "]:" + str(distance[v]) 

            if distance[v] < minimum:
                #print "Nova Distancia Minima"
                minimum = distance[v]
                node = v
        return node

    #Algoritmo de Dijkstra
    def get_path (self, src, dst, first_port, final_port):  
        print "get_path is called, src=",src," dst=",dst, " first_port=", first_port, " final_port=", final_port

        distance = {}
        previous = {}

        for dpid in switches:
            distance[dpid] = float('Inf')
            previous[dpid] = None
        
        distance[src]=0
        Q = set(switches)
        print "Q=", Q

        while len(Q) > 0:
            u = self.minimum_distance(distance, Q)
            Q.remove(u)

            for p in switches:
                if adjacency[u][p] != 0:
                    w = 1
                    if distance[u] + w < distance[p]:
                        distance[p] = distance[u] + w
                        previous[p] = u

        r = []
        p = dst
        r.append(p)
        q = previous[p]

        while q is not None:
            if q == src:
                r.append(q)
                break
            p = q
            r.append(p)
            q=previous[p]

        r.reverse()

        if src == dst:
            path = [src]
        else:
            path=r
        print "Comeco porta"
        # adiciona as portas
        r = []
        in_port = first_port

        for s1, s2 in zip(path[:-1], path[1:]):
            out_port = adjacency[s1][s2]
            r.append((s1,in_port,out_port))
            in_port = adjacency[s2][s1]

        r.append((dst,in_port,final_port))

        print "Retorno get path",r
        return r
# -----------------------------------------------------------------------------------
# 
# -----------------------------------------------------------------------------------
    def install_path(self, p, ev, src_mac, dst_mac):

       print "install_path is called"
       #print "p=", p, " src_mac=", src_mac, " dst_mac=", dst_mac
       msg = ev.msg
       datapath = msg.datapath
       ofproto = datapath.ofproto
       parser = datapath.ofproto_parser
       for sw, in_port, out_port in p:
         #print src_mac,"->", dst_mac, "via ", sw, " in_port=", in_port, " out_port=", out_port
         match=parser.OFPMatch(in_port=in_port, eth_src=src_mac, eth_dst=dst_mac)
         actions=[parser.OFPActionOutput(out_port)]
         datapath=self.datapath_list[int(sw)-1]
         inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS , actions)]
         mod = datapath.ofproto_parser.OFPFlowMod(
         datapath=datapath, match=match, idle_timeout=0, hard_timeout=0,
         priority=1, instructions=inst)
         datapath.send_msg(mod)

    #Garantir que switches conectados sejam monitorados
    @set_ev_cls(ofp_event.EventOFPStateChange, [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            if datapath.id not in self.datapaths:
                self.logger.debug('register datapath: %016x', datapath.id)
                self.datapaths[datapath.id] = datapath
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                self.logger.debug('unregister datapath: %016x', datapath.id)
                del self.datapaths[datapath.id]
    
    #Envia mensagem de requisicao de status para determinado switch
    def _request_stats(self, datapath):
        self.logger.debug('send stats request: %016x', datapath.id)
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser	
    
        # obtem dados das portas
        req = parser.OFPPortStatsRequest(datapath, 0, ofproto.OFPP_ANY)
        datapath.send_msg(req)

    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def _port_stats_reply_handler(self, ev):
        body = ev.msg.body	

        self.logger.info('datapath         port     '
                         'rx-pkts  rx-bytes rx-error '
                         'tx-pkts  tx-bytes tx-error '
			 'flow_speed')
        self.logger.info('---------------- -------- '
                         '-------- -------- -------- '
                         '-------- -------- -------- '
			 '--------')
        for stat in sorted(body, key=attrgetter('port_no')):
	    if stat.port_no != 4294967294:
	        self.port_speed[ev.msg.datapath.id][stat.port_no] = stat.rx_bytes - self.port_speed[ev.msg.datapath.id][stat.port_no]
                self.logger.info('%016x %8x %8d %8d %8d %8d %8d %8d %8d',
                             ev.msg.datapath.id, stat.port_no,
                             stat.rx_packets, stat.rx_bytes, stat.rx_errors,
                             stat.tx_packets, stat.tx_bytes, stat.tx_errors,
			     self.port_speed[ev.msg.datapath.id][stat.port_no])


    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # construct flow_mod message and send it.
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                match=match, instructions=inst, idle_timeout=0,
                                hard_timeout=0)
        datapath.send_msg(mod)

    def receive_arp(self, datapath, packet, etherFrame, inPort):
        arpPacket = packet.get_protocol(arp)

        if arpPacket.opcode == 1:
            arp_dstIp = arpPacket.dst_ip
            self.reply_arp(datapath, etherFrame, arpPacket, arp_dstIp, inPort)
        elif arpPacket.opcode == 2:
            pass

    def reply_arp(self, datapath, etherFrame, arpPacket, arp_dstIp, inPort):
        dstIp = arpPacket.src_ip
        srcIp = arpPacket.dst_ip
        dstMac = etherFrame.src
        #print "SRC IP",arpPacket.src_ip
        #print "DST IP",arpPacket.dst_ip
        #print "SRC MAC",etherFrame.src
        #print "DST IP parametro",arp_dstIp
        dpid = datapath.id
        # Outport depende em que switch estamos e de quem fez a pergunta 
        if arp_dstIp == HOST_IPADDR1:
            srcMac = HOST_MACADDR1
            outPort = HOST_PORT1
        elif arp_dstIp == HOST_IPADDR2:
            srcMac = HOST_MACADDR2
            outPort = HOST_PORT2
        elif arp_dstIp == HOST_IPADDR3:
            srcMac = HOST_MACADDR3
            outPort = HOST_PORT3
        elif arp_dstIp == HOST_IPADDR4:
            srcMac = HOST_MACADDR4
            outPort = HOST_PORT4
        elif arp_dstIp == HOST_IPADDR6:
            srcMac = HOST_MACADDR6
            outPort = HOST_PORT6

        if dpid != 3 and arp_dstIp == "10.0.0.6":
            outPort = 3
        if dpid == 3 and arpPacket.src_ip == "10.0.0.6" :
            outPort = 4
        if dpid == 3 and arpPacket.src_ip == "10.0.0.3" :
            outPort = 3

        #print srcMac
        #print outPort
        self.send_arp(datapath, 2, srcMac, srcIp, dstMac, dstIp, outPort)

    def send_arp(self, datapath, opcode, srcMac, srcIp, dstMac, dstIp, outPort):
        if opcode == 1:
            targetMac = "00:00:00:00:00:00"
            targetIp = dstIp
        elif opcode == 2:
            targetMac = dstMac
            targetIp = dstIp

        e = ethernet.ethernet(dstMac, srcMac, ether.ETH_TYPE_ARP)
        a = arp(1, 0x0800, 6, 4, opcode, srcMac, srcIp, targetMac, targetIp)
        p = packet.Packet()
        p.add_protocol(e)
        p.add_protocol(a)
        p.serialize()

        actions = [datapath.ofproto_parser.OFPActionOutput(outPort, 0)]
        out = datapath.ofproto_parser.OFPPacketOut(
            datapath=datapath,
            buffer_id=0xffffffff,
            in_port=datapath.ofproto.OFPP_CONTROLLER,
            actions=actions,
            data=p.data)
        datapath.send_msg(out)

    #Evento de packet_in, switch envia essa mensagem para o controlador ao receber um pacote
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
	print "Entrei Packet In"
        print switches
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        dpid = datapath.id
        
        self.mac_to_port.setdefault(dpid, {})
        print "Sou SW:",dpid
        # extrai informacoes do pacote
        pkt = packet.Packet(msg.data)
        eth_pkt = pkt.get_protocol(ethernet.ethernet)
        dst = eth_pkt.dst
        src = eth_pkt.src

        # porta pela qual switch recebeu o pacote
        in_port = msg.match['in_port']
        print "In_port:" ,in_port
        # Adiciona a relacao MAC Origem com a porta de saida para 
        # futuros casos no sentido oposto 
  
        #if src not in self.mac_to_port[dpid]:
            #print "Adicionando Entrada de Origem"
            #self.mac_to_port[dpid][src] = in_port
        
        #print self.mac_to_port
        print "MAC SRC:" , src
        print "MAC DST:" , dst

        #if dst == 'ff:ff:ff:ff:ff:ff':
            #print "Sou um FF.FF.FF..."
        #if dst in self.mac_to_port[dpid]:
        if eth_pkt.ethertype == ether.ETH_TYPE_ARP:
            print "Solucionando ARP"
            self.receive_arp(datapath, pkt, eth_pkt, in_port)
        elif dst != 'ff:ff:ff:ff:ff:ff':
            print "Port DST: ",self.host_port[dst][1]
            print "Pre Dijsktra"
            p = self.get_path(self.host_port[src][0], self.host_port[dst][0], self.host_port[src][1], self.host_port[dst][1])
            print "Post Dijsktra"
            #print p
            self.install_path(p, ev, src, dst) # Instala todas as regras em todos os sw
            out_port = p[0][2]
        else:
            print "Sou um BroadCast"
            out_port = ofproto.OFPP_FLOOD

        # Como o arp eh tratado artificialmente, esta parte nao eh necessaria     
        if dst != 'ff:ff:ff:ff:ff:ff':   
            actions = [parser.OFPActionOutput(out_port)]
        
            # instala regra para evitar packet in na proxima vez
            if out_port != ofproto.OFPP_FLOOD:
                print "Instalando Regra"
                match = parser.OFPMatch(in_port=in_port, eth_src=src, eth_dst=dst)
                #self.add_flow(datapath, 1, match, actions)

            data=None
            if msg.buffer_id==ofproto.OFP_NO_BUFFER:
               data=msg.data

            out = parser.OFPPacketOut(datapath=datapath,
                                  buffer_id=ofproto.OFP_NO_BUFFER,
                                  in_port=in_port, actions=actions,
                                  data=msg.data)
            datapath.send_msg(out)
        
        # loga os dados do pacote
	if dst != 'ff:ff:ff:ff:ff:ff':
	    self.logger.info("packet in %s %s %s %s", dpid, src, dst, in_port)
        print "Sai Packet in"     

#------------------------------------------------------------------------------
    
    @set_ev_cls(event.EventSwitchEnter)
    def get_topology_data(self, ev):
        global switches
        switch_list = get_switch(self.topology_api_app, None)  
        #switches=[switch.dp.id for switch in switch_list]
        self.datapath_list=[switch.dp for switch in switch_list]
        #print "self.datapath_list=", self.datapath_list
        #print "switches dp", self.datapath_list
     
    
