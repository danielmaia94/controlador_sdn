from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_0 "OpenFlow v1.0"

class OFPHandler(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_0.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(OFPHandler, self).__init__(*args, **kwargs)
    
    "Evento de Hello, talvez não precise, o ryu faz isso sozinho aparentemente"
    @set_ev_cls(ofp_event.EventOFPHello, HANDSHAKE_DISPATCHER)
    def hello_handler(self, ev):     
    
    "Controller envia essa mensagem para modificar a flow table do switch"		
    @set_ev_cls(ofp_event.EventOFPFlowMod, MAIN_DISPATCHER)
    def flow_mod_handler(self, ev):  

    "Evento de packet_in, switch envia essa mensagem para o controlador ao receber um pacote"
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):	
    
    "Controlador usa essa mensagem para enviar um pacote através do switch"
    @set_ev_cls(ofp_event.EventOFPPacketOut, MAIN_DISPATCHER)
    def packet_out_handler(self, ev):	
	
