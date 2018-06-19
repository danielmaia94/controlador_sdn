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

# switches da rede
switches = []

#m ymac[srcmac]->(switch, port)
mymac = {}

# mapeia de um switch para outro
adjacency = defaultdict(lambda:defaultdict(lambda:None))

class OFPHandler(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]    
	
    def __init__(self, *args, **kwargs):
        super(OFPHandler, self).__init__(*args, **kwargs)

        # registra velocidade das portas
        self.port_speed = {}

        # registra velocidade do fluxo
        self.flow_speed = {}   

        # the length of speed list of per port and flow.
        self.state_len = 3    

        # mac -> porta
        self.mac_to_port = {}        
	
	# dict dp
	self.datapaths = {}

        # lista de dp
        self.datapath_list = []        
        
        # thread para monitorar trafego
        self.monitor_thread = hub.spawn(self._monitor)
    
    #Requisita dados de trafego de todos os switches
    def _monitor(self):
        while True:
            for dp in self.datapaths.values():
                self._request_stats(dp)
            hub.sleep(10)

    #Retorna minima distancia de um nodo
    def minimum_distance(distance, Q):
	minimum = float('Inf')

        node = 0

        for v in Q:
            if distance[v] < minimum:
                minimum = distance[v]
                node = v

        return node

    #Algoritmo de Dijkstra
    def get_path (src, dst, first_port, final_port):  
        print "get_path is called, src=",src," dst=",dst, " first_port=", first_port, " final_port=", final_port

        distance = {}
        previous = {}

        for dpid in switches:
            distance[dpid] = float('Inf')
            previous[dpid] = None

        distance[src] = 0
        Q = set(switches)
        print "Q=", Q

        while len(Q) > 0:
            u = minimum_distance(distance, Q)
            Q.remove(u)

            for p in switches:
                if adjacency[u][p] != None:
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

        # adiciona as portas
        r = []
        in_port = first_port

        for s1, s2 in zip(path[:-1], path[1:]):
            out_port = adjacency[s1][s2]
            r.append((s1,in_port,out_port))
            in_port = adjacency[s2][s1]

        r.append((dst,in_port,final_port))

        return r

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
	
        # obtem dados de flow
        req = parser.OFPFlowStatsRequest(datapath)
        datapath.send_msg(req)
	
        # obtem dados das portas
        req = parser.OFPPortStatsRequest(datapath, 0, ofproto.OFPP_ANY)
        datapath.send_msg(req)
    
    #Recebe respostas das requisicoes de flow stats
    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):
        body = ev.msg.body

        self.logger.info('datapath         '
                         'in-port  eth-dst           '
                         'out-port packets  bytes')
        self.logger.info('---------------- '
                         '-------- ----------------- '
                         '-------- -------- --------')
        for stat in sorted([flow for flow in body if flow.priority == 1],
                           key=lambda flow: (flow.match['in_port'],
                                             flow.match['eth_dst'])):
            self.logger.info('%016x %8x %17s %8x %8d %8d',
                             ev.msg.datapath.id,
                             stat.match['in_port'], stat.match['eth_dst'],
                             stat.instructions[0].actions[0].port,
                             stat.packet_count, stat.byte_count)

    #Recebe respostas das requisicoes de port stats
    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def _port_stats_reply_handler(self, ev):
        body = ev.msg.body

        self.logger.info('datapath         port     '
                         'rx-pkts  rx-bytes rx-error '
                         'tx-pkts  tx-bytes tx-error')
        self.logger.info('---------------- -------- '
                         '-------- -------- -------- '
                         '-------- -------- --------')
        for stat in sorted(body, key=attrgetter('port_no')):
            self.logger.info('%016x %8x %8d %8d %8d %8d %8d %8d',
                             ev.msg.datapath.id, stat.port_no,
                             stat.rx_packets, stat.rx_bytes, stat.rx_errors,
                             stat.tx_packets, stat.tx_bytes, stat.tx_errors)

    # @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    # def switch_features_handler(self, ev):
    #     datapath = ev.msg.datapath
    #     ofproto = datapath.ofproto
    #     parser = datapath.ofproto_parser
     
    #     match = parser.OFPMatch()
    #     actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
    #                                       ofproto.OFPCML_NO_BUFFER)]
    #     self.add_flow(datapath, 0, match, actions)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures , CONFIG_DISPATCHER)
    def switch_features_handler(self , ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]

        mod = datapath.ofproto_parser.OFPFlowMod(
            datapath=datapath, match=match, cookie=0,
            command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
            priority=0, instructions=inst)

        datapath.send_msg(mod)    
    
    #Adiciona uma  entrada na tabela do switch
    def add_flow(self, p, ev, src_mac, dst_mac):
       msg = ev.msg
       datapath = msg.datapath
       ofproto = datapath.ofproto
       parser = datapath.ofproto_parser

       for sw, in_port, out_port in p:         
            match = parser.OFPMatch(in_port=in_port, eth_src=src_mac, eth_dst=dst_mac)
            actions = [parser.OFPActionOutput(out_port)]
            datapath = self.datapath_list[int(sw) - 1]

            inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS , actions)]

            mod = datapath.ofproto_parser.OFPFlowMod(
            datapath = datapath, match = match, idle_timeout = 0, hard_timeout = 0,
            priority = 1, instructions = inst)

       datapath.send_msg(mod)    	

    #Evento de packet_in, switch envia essa mensagem para o controlador ao receber um pacote
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # extrai informacoes do pacote
        pkt = packet.Packet(msg.data)
        eth_pkt = pkt.get_protocol(ethernet.ethernet)
        dst = eth_pkt.dst
        src = eth_pkt.src

        # porta pela qual switch recebeu o pacote
        in_port = msg.match['in_port']
        
        if src not in mymac.keys():
            mymac[src] = (dpid,  in_port)            

        # Percorre
        if dst in mymac.keys():
            # Dijkstra
            p = get_path(mymac[src][0], mymac[dst][0], mymac[src][1], mymac[dst][1]) 
            # instala regra no switch para evitar flood           
            self.add_flow(p, ev, src, dst)
            # porta para qual pacote sera encaminhado
            out_port = p[0][2]
        else:
            # flood
            out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]

        # instala regra para evitar packet in na proxima vez
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_src=src, eth_dst=dst)

        data = None
        if msg.buffer_id==ofproto.OFP_NO_BUFFER:
           data = msg.data

        # encaminhao pacote
        out = parser.OFPPacketOut(
            datapath = datapath, buffer_id = msg.buffer_id, in_port = in_port,
            actions = actions, data = data)
        datapath.send_msg(out)

        # loga os dados do pacote
        self.logger.info("packet in %s %s %s %s", dpid, src, dst, in_port)             

