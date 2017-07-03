from configobj import ConfigObj
from Node_Database import NodeDatabase,Node
from activewalker.crypto import LibNaCLSK, ECCrypto
from activewalker.Message import Message
import os
from Generator import WalkNumberGenerator,LinkNumberGenerator
from activewalker.Neighbor_group import Determinstic_NeighborGroup
from activewalker.neighbor_discovery import NeighborDiscover
from activewalker.HalfBlockDatabase import HalfBlock
from subprocess import call
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import task
from twisted.internet import reactor
from twisted.internet.defer import Deferred
from hashlib import sha1
BASE = os.path.dirname(os.path.abspath(__file__))

class Placeholder(object):
    def __init__(self,crypto,my_public_key,my_key,my_identity,start_header,global_time):
        self.crypto=crypto
        self.my_public_key=my_public_key
        self.my_key=my_key
        self.my_identity=my_identity
        self.start_header=start_header
        self.global_time=global_time

class Simulation(DatagramProtocol):
    def __init__(self,port=30000,config_file=os.path.join(BASE, 'config.conf')):
        config = ConfigObj(config_file)
        self.port=port
        self.honest_node_number = int(config["honest_node_number"])
        self.evil_node_number = int(config["evil_node_number"])
        self.number_of_nodes = self.honest_node_number + self.evil_node_number
        self.link_per_node = int(config["link_per_node"])
        self.upload_cap = int(config["upload_cap"])
        self.download_cap = int(config["upload_cap"])
        self.link_range = int(config["link_range"])
        self.ip_list = config["ip_list"]
        self.nodes_per_ip = int(config["nodes_per_ip"])+1
        print self.ip_list[0]
        self.crypto = ECCrypto()
        self.node_database = NodeDatabase()
        self.reactor = reactor

        self.master_key = "3081a7301006072a8648ce3d020106052b8104002703819200040503dac58c19267f12cb0cf667e480816cd2574acae" \
                     "5293b59d7c3da32e02b4747f7e2e9e9c880d2e5e2ba8b7fcc9892cb39b797ef98483ffd58739ed20990f8e3df7d1ec5" \
                     "a7ad2c0338dc206c4383a943e3e2c682ac4b585880929a947ffd50057b575fc30ec88eada3ce6484e5e4d6fdf41984c" \
                     "d1e51aaacc5f9a51bcc8393aea1f786fc47cbf994cb1339f706df4a"
        self.master_key_hex = self.master_key.decode("HEX")
        self.ec = self.crypto.generate_key(u"medium")
        self.key = self.crypto.key_from_public_bin(self.master_key_hex)
        self.master_identity = self.crypto.key_to_hash(self.key.pub())
        self.dispersy_version = "\x00"
        self.community_version = "\x01"
        self.start_header = self.dispersy_version+self.community_version+self.master_identity


        #generating nodes and store it in database
        print("generating nodes and store it in database")
        honest_nodes_list = []
        evil_nodes_list = []
        for i in range(1,self.honest_node_number+1):
            key = LibNaCLSK()
            key_bin = key.key_to_bin()
            key_pub = key.pub()
            key_pub_bin = key_pub.key_to_bin()
            node = Node()
            ip = self.ip_list[int(i/self.nodes_per_ip)]
            port = i%self.nodes_per_ip
            node.set(public_key =key_pub_bin,private_key = key_bin,member_identity=self.crypto.key_to_hash(key_pub),honest=True,ip=ip,port=port)
            honest_nodes_list.append(node)
        self.node_database.add_nodes(honest_nodes_list)

        for i in range(self.honest_node_number+1,self.honest_node_number+self.evil_node_number+1):
            key = LibNaCLSK()
            key_bin = key.key_to_bin()
            key_pub = key.pub()
            key_pub_bin = key_pub.key_to_bin()
            node=Node()
            ip = self.ip_list[int(i/self.nodes_per_ip)]
            port = i%self.nodes_per_ip
            node.set(public_key =key_pub_bin,private_key = key_bin,member_identity=self.crypto.key_to_hash(key_pub),honest=False,ip=ip,port=port)
            evil_nodes_list.append(node)
        self.node_database.add_nodes(evil_nodes_list)
        call(["cp","NodeDatabase.db","activewalker"])
        call(["cp","Node_Database.py","activewalker"])

        print("creating determinstic random number generator")
        self.walk_generator = WalkNumberGenerator(number_of_nodes=self.honest_node_number+self.evil_node_number)
        self.link_generator = LinkNumberGenerator(number_of_nodes=self.honest_node_number+self.evil_node_number,number_of_link=self.link_per_node,
                                                  link_range=self.link_range,upload_cap=self.upload_cap,download_cap=self.download_cap)

        neighbor_group = Determinstic_NeighborGroup(walk_generator=self.walk_generator,node_database=self.node_database)
        self.walker = NeighborDiscover(is_listening=False,message_sender=self.receive_packet,neighbor_group=neighbor_group)
        self.reactor.run()

    def generate_blocks(self,node):
        data = self.link_generator.get_current()
        blocks=[]
        crypto = ECCrypto()
        print("the node's private key is: "+repr(node.private_key))
        for i in range(1,len(data)):
            record = data[i]
            block = HalfBlock()
            block.up = record[0]
            block.total_up = record[0]
            block.down = record[1]
            block.total_down = record[1]
            block.sequence_number = i
            block.public_key = node.public_key
            key = crypto.key_from_private_bin(node.private_key)
            print("the type of key is")
            print type(key)
            block.sign(key=key)
            blocks.append(block)
        return blocks



    def send_packet(self,packet,sender_addr):
        self.walker.handle_message(packet,sender_addr)

    def receive_packet(self,packet,destination_addr):
        node = self.node_database.get_node_by_ip_and_port(ip=destination_addr[0],port=destination_addr[1])
        d = Deferred()
        d.addCallback(self.handle_message)
        reactor.callLater(0, d.callback,(packet,destination_addr,node))

    def handle_message(self,args):
        #@param:node: the node which should receive this message
        packet = args[0]
        destination_addr = args[1]
        node = args[2]
        active_walker_addr = ("127.0.0.1",25000)
        crypto = ECCrypto()
        my_public_key=node.public_key
        my_key = crypto.key_from_private_bin(node.private_key)
        my_identity = sha1(my_public_key).digest()
        global_time=0
        placeholder = Placeholder(crypto=crypto,my_public_key=my_public_key,my_key=my_key,my_identity=my_identity,global_time=global_time,start_header=self.start_header)
        print("network:---the public key of the node is:"+repr(my_public_key))

        message_type = ord(packet[22])
        print("message id is:"+str(message_type))
        if message_type == 247:
            print("network:---here is a missing-identity message")
            self.on_missing_identity(packet,active_walker_addr,node,placeholder)
        if message_type == 245:
            print("network:---here is a introduction-response")
            self.on_introduction_response(packet,active_walker_addr,node,placeholder)
        if message_type == 246:
            print("network:---here is a introduction-request")
            self.on_introduction_request(packet,active_walker_addr,node,placeholder)
        if message_type == 250:
            print("network:---here is a puncture request")
            #self.on_puncture_request(packet,active_walker_addr,node,placeholder)
        if message_type == 249:
            print("network:---here is a puncture")
        if message_type == 248:
            print("network:---here is an dispersy-identity")
            self.on_identity(packet,active_walker_addr,node,placeholder)
        if message_type == 1:
            print ("network:---here is a halfblock message")
            self.on_halfblock(packet,active_walker_addr,node,placeholder)
        if message_type == 2:
            print("network:---here is a crawl(request)")
            self.on_crawl_request(packet,active_walker_addr,node,placeholder)
            #messages_to_send=self.manager.on_crawl_request(packet,addr,public_key=self.my_public_key,walker=self)
            #self.send_messages(messages_to_send)

    def on_missing_identity(self,packet,addr,node,placeholder):
        message_missing_identity = Message(packet=packet)
        message_missing_identity.decode_missing_identity()
        self.global_time = message_missing_identity.global_time
        message_identity = Message(neighbor_discovery=placeholder)
        message_identity.encode_identity()
        #return [(message_identity.packet,addr)]
        self.send_packet(message_identity.packet,(str(node.ip),int(node.port)))

    def on_introduction_response(self,packet,addr,placeholder):
        pass
    def on_introduction_request(self,packet,addr,node,placeholder):
        message_request = Message(packet=packet)
        message_request.decode_introduction_request()
        #requester_neighbor = Neighbor(message_request.source_private_address,addr,identity = message_request.sender_identity)
        node_to_introduce_id = (self.link_generator.get_next()[0]+int(node.id))%self.number_of_nodes
        node_to_introduce = self.node_database.get_node_by_id(id=node_to_introduce_id)
        #introduced_private_address = neighbor_to_introduce
        #introduced_public_address = neighbor_to_introduce
        introduced_private_address = (str(node_to_introduce.ip),int(node_to_introduce.port))
        introduced_public_address = (str(node_to_introduce.ip),int(node_to_introduce.port))
        my_address = (str(node.ip),int(node.port))
        message_response = Message(neighbor_discovery=placeholder,identifier=message_request.identifier,destination_address=addr,source_private_address =my_address,source_public_address=my_address,
                                   private_introduction_address=introduced_private_address,public_introduction_address=introduced_public_address)
        message_response.encode_introduction_response()
        message_puncture_request = Message(neighbor_discovery=placeholder,source_private_address=message_request.source_private_address,source_public_address=message_request.source_public_address,
                                               private_address_to_puncture=message_request.source_private_address,public_address_to_puncture=addr)
        message_puncture_request.encode_puncture_request()
        #return([(message_response.packet,addr),(message_puncture_request.packet,(str(node_to_introduce.ip),int(node_to_introduce.port)))])
        self.send_packet(message_response.packet,(str(node.ip),int(node.port)))
        #simulated network don't need puncture request, nor puncture
        #self.send_packet(message_puncture_request.packet,(str(node_to_introduce.ip),int(node_to_introduce.port)))

    def on_puncture_request(self,packet,node,addr,placeholder):
        my_address = (str(node.ip),int(node.port))
        message_puncture_request = Message(packet=packet)
        message_puncture_request.decode_puncture_request()
        self.global_time = message_puncture_request.global_time
        private_address_to_puncture = message_puncture_request.private_address_to_puncture
        public_address_to_puncture = message_puncture_request.public_address_to_puncture
        message_puncture = Message(neighbor_discovery=placeholder,source_private_address=my_address,
                                   source_public_address=my_address)
        message_puncture.encode_puncture()
        #return [(message_puncture.packet,public_address_to_puncture)]
        self.send_packet(message_puncture.packet,public_address_to_puncture)

    def on_crawl_request(self,packet,addr,node,placeholder):
        message_crawl_request = Message(packet=packet)
        message_crawl_request.decode_crawl()
        print("network:---requested sequence number is: "+str(message_crawl_request.requested_sequence_number))
        print("network:---the public key is: "+repr(node.public_key))
        #print("the type of public key in on crawl request is:")
        #print type(public_key)
        blocks=self.generate_blocks(node = node)
        #blocks = self.block_database.get_blocks_since(public_key=node.public_key,sequence_number=int(message_crawl_request.requested_sequence_number))
        #blocks = self.block_database.get_blocks_since(public_key=public_key,sequence_number=1)
        print(blocks)
        messages_to_send = []
        for block in blocks:
            message = Message(neighbor_discovery=placeholder,block=block)
            print("network:---we have following blocks to send: "+str(block.up))
            message.encode_halfblock()
            #messages_to_send.append((message.packet,addr))
            self.send_packet(message.packet,(str(node.ip),int(node.port)))
        #return messages_to_send

    def on_identity(self,packet,addr,placeholder):
        pass
    def on_halfblock(self,packet,addr,placeholder):
        pass


if __name__ == "__main__":
    s = Simulation()