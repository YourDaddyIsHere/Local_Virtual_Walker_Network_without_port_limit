from Node_Database import NodeDatabase,Node

#contains a node list, the index of the list is the node id
#also contains a dict, the key is ip and port and the value is node id
class NodeTable(object):
    def __init__(self):
        #the nodes list, list index is node id
        self.node_dict_by_id = dict()
        #the key is (ip,port), the value is node id
        self.node_dict_by_ip_and_port = dict()

    def add_nodes(self,nodes):
        for node in nodes:
            self.add_node(node)

    def add_node(self,node):
        self.node_dict_by_id[node.id] = node
        address = (str(node.ip),int(node.port))
        self.node_dict_by_ip_and_port[address] = node.id 
        #print("nodes add, the id is: "+str(node.id))

    def get_node_by_ip_and_port(self,ip,port):
        address = (str(ip),int(port))
        node_id = self.node_dict_by_ip_and_port[address]
        node = self.node_dict_by_id[node_id]
        return node

    def get_node_by_id(self,id):
        return self.node_dict_by_id[int(id)]

if __name__ == "__main__":
    print(-6%10)