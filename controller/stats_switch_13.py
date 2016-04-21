# Copyright (C) 2016 Mircea Iordache.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ipv4
from ryu.lib.packet import tcp as tcp_pkt
from ryu.lib.packet import ether_types

import ast
import json
import logging
from webob import Response
from ryu.app.wsgi import ControllerBase, WSGIApplication
from ryu.controller import dpset
from ryu.lib import ofctl_v1_3

supported_ofctl = {
    ofproto_v1_3.OFP_VERSION: ofctl_v1_3,
}

LOG = logging.getLogger('ryu.app.ofctl_rest')

class StatsController(ControllerBase):
  def __init__(self, req, link, data, **config):
    super(StatsController, self).__init__(req, link, data, **config)
    self.dpset = data['dpset']
    self.waiters = data['waiters']
  
  def get_flow_stats(self, req, dpid, **_kwargs):

        if req.body == '':
            flow = {}

        else:

            try:
                flow = ast.literal_eval(req.body)

            except SyntaxError:
                LOG.debug('invalid syntax %s', req.body)
                return Response(status=400)

        if type(dpid) == str and not dpid.isdigit():
            LOG.debug('invalid dpid %s', dpid)
            return Response(status=400)

        dp = self.dpset.get(int(dpid))

        if dp is None:
            return Response(status=404)

        _ofp_version = dp.ofproto.OFP_VERSION

        _ofctl = supported_ofctl.get(_ofp_version, None)
        flows = ""
        if _ofctl is not None:
            flows = _ofctl.get_flow_stats(dp, self.waiters, flow)
        else:
            LOG.info('Unsupported OF protocol')
            return Response(status=501)
        body = json.dumps(flows)
        return Response(content_type='application/json', body=body)
  
  def anomaly_notifications(self, req, **_kwargs):
	if req.body != '':
	  try:
	    data = ast.literal_eval(req.body)
	  except SyntaxError:
	    LOG.debug('invalid syntax %s', req.body)
	    
	  LOG.info('got anomaly notification from s%s', data['dpid'])
	return Response()
  
class StatsSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    _CONTEXTS = {
        'dpset': dpset.DPSet,
        'wsgi': WSGIApplication
    }


    def __init__(self, *args, **kwargs):
        super(StatsSwitch13, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
	self.tcp_ip_stored = {}
	self.existing_flow = {}
	self.dpset = kwargs['dpset']
        wsgi = kwargs['wsgi']
        self.waiters = {}
        self.data = {}
        self.data['dpset'] = self.dpset
        self.data['waiters'] = self.waiters
        mapper = wsgi.mapper

        wsgi.registory['StatsController'] = self.data
        path = '/stats'
	uri = path + '/{dpid}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='get_flow_stats',
                       conditions=dict(method=['GET', 'POST']))
	
	uri = '/notify'
	mapper.connect('stats', uri,
		       controller=StatsController, action='anomaly_notifications',
		       conditions=dict(method=['POST']))
    
    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def stats_reply_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath

        if dp.id not in self.waiters:
            return
        if msg.xid not in self.waiters[dp.id]:
            return
        lock, msgs = self.waiters[dp.id][msg.xid]
        msgs.append(msg)

        flags = 0
        if dp.ofproto.OFP_VERSION == ofproto_v1_3.OFP_VERSION:
            flags = dp.ofproto.OFPMPF_REPLY_MORE

        if msg.flags & flags:
            return
        del self.waiters[dp.id][msg.xid]
        lock.set()
	
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # install table-miss flow entry
        #
        # We specify NO BUFFER to max_len of the output action due to
        # OVS bug. At this moment, if we specify a lesser number, e.g.,
        # 128, OVS will send Packet-In with invalid buffer_id and
        # truncated packet data. In that case, we cannot output packets
        # correctly.  The bug has been fixed in OVS v2.1.0.
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_eth_flow(datapath, 0, match, actions)

    def add_tcp_flow(self, datapath, match, buffer_id=None):
	ofproto = datapath.ofproto
	parser = datapath.ofproto_parser
	
	inst = [parser.OFPInstructionGotoTable(1)]
	
	if buffer_id:
	    mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
				  priority=1000, match=match,
				  instructions=inst)
	else:
	    mod = parser.OFPFlowMod(datapath=datapath, priority=1000,
				    match=match, instructions=inst)
	
	#LOG.info("Adding Flow %s:%s -> %s:%s", match['ipv4_src'], match['tcp_src'], match['ipv4_dst'], match['tcp_dst'])
	datapath.send_msg(mod)
	
    def add_eth_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst, table_id=1)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst, table_id=1)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        # If you hit this you might want to increase
        # the "miss_send_length" of your switch
        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("packet truncated: only %s of %s bytes",
                              ev.msg.msg_len, ev.msg.total_len)
        
        is_ip = False
        ip = None
        tcp = None
        msg = ev.msg
        datapath = ev.msg.datapath
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

     	ofproto = datapath.ofproto
	parser  = datapath.ofproto_parser
	in_port = msg.match['in_port']
	
	if eth.ethertype == ether_types.ETH_TYPE_LLDP:
	    return
	
	if pkt.get_protocols(tcp_pkt.tcp):
	    is_ip = True
	    ip = pkt.get_protocols(ipv4.ipv4)[0]
	    tcp = pkt.get_protocols(tcp_pkt.tcp)[0]
	
	dpid = datapath.id
	self.existing_flow.setdefault(dpid, [])
	self.mac_to_port.setdefault(dpid, {})
	
	if (eth.dst, in_port) not in self.existing_flow[dpid]:
	    self.eth_packet_in_handler(msg)

	if is_ip:
	    self.tcp_ip_stored.setdefault(dpid, {})
	    self.tcp_ip_stored[dpid].setdefault((ip.src, tcp.src_port), [])
	    
	    if (ip.dst, tcp.dst_port) not in self.tcp_ip_stored[dpid][(ip.src, tcp.src_port)]:
		self.tcp_packet_in_handler(msg) 
	
        if eth.dst in self.mac_to_port[dpid]:
	    out_port = self.mac_to_port[dpid][eth.dst]
	else:
	    out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]
	
	data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data
	
        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=msg.match['in_port'], actions=actions, data=data)
        datapath.send_msg(out)
	
    def tcp_packet_in_handler(self, msg):
	datapath = msg.datapath
	pkt = packet.Packet(msg.data)
	ip = pkt.get_protocols(ipv4.ipv4)[0]
	tcp = pkt.get_protocols(tcp_pkt.tcp)[0]
	dpid = datapath.id
	
	ofproto = datapath.ofproto
	parser  = datapath.ofproto_parser
	
	ip_src = ip.src
	ip_dst = ip.dst
	tcp_src = tcp.src_port
	tcp_dst = tcp.dst_port
	
	self.tcp_ip_stored[dpid][(ip_src, tcp_src)].append((ip_dst, tcp_dst))
	
	match = parser.OFPMatch(eth_type=2048, ip_proto=6, ipv4_src=ip_src, ipv4_dst=ip_dst, tcp_src=tcp_src, tcp_dst=tcp_dst)
	
        if msg.buffer_id != ofproto.OFP_NO_BUFFER:
	    self.add_tcp_flow(datapath, match, msg.buffer_id)
	else:
	    self.add_tcp_flow(datapath, match)

    
    def eth_packet_in_handler(self, msg):
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']
	
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        dst = eth.dst
        src = eth.src
        dpid = datapath.id
	
        #self.logger.info("packet in dpid %s src %s dst %s in_port %s", dpid, src, dst, in_port)
       
        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = in_port
        
        if dst in self.mac_to_port[dpid]:
	    out_port = self.mac_to_port[dpid][dst]
	else:
	    out_port = ofproto.OFPP_FLOOD


	
        # install a flow to avoid packet_in next time
        if out_port != ofproto.OFPP_FLOOD:
	    actions = [parser.OFPActionOutput(out_port)]
	    self.existing_flow[dpid].append((dst, in_port))
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst)
            # verify if we have a valid buffer_id, if yes avoid to send both
            # flow_mod & packet_out
            if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                self.add_eth_flow(datapath, 1, match, actions, msg.buffer_id)
            else:
                self.add_eth_flow(datapath, 1, match, actions)
