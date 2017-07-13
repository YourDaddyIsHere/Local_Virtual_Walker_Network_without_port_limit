import random
class EdgeSet(object):
    def __init__(self,random_seed=23333333):
        self.edges = dict()
        self.random_seed = random_seed
        self.random_number_generator = random.Random()
        self.random_number_generator.seed(self.random_seed)

    def has_edge(self,start_node,end_node):
        if start_node in self.edges:
            if end_node in self.edges[start_node]:
                return True
            else:
                return False
        else:
            return False

    def add_edge(self,start_node,end_node,upload,download):
        if start_node not in self.edges:
            edge = dict()
            edge[end_node] = (upload,download)
            self.edges[start_node] = edge
        elif end_node not in self.edges[start_node]:
            self.edges[start_node][end_node] = (upload,download)
    def get_edge(self,start_node,end_node):
        if self.has_edge(start_node,end_node):
            return self.edges[start_node][end_node]
        else:
            return None
    def has_node(self,node):
        if node in self.edges:
            return True
        else:
            return False
    def get_random_edge(self,node):
        edge_list=[]
        for destination_node in self.edges[node]:
            edge=((node,destination_node),self.edges[node][destination_node])
            edge_list.append(edge)
        index = self.random_number_generator.randint(0,len(edge_list)-1)
        #the edge is represented in form ((start_node,end_node),(upload,download))
        return edge_list[index]
    def get_all_edge(self,node):
        edge_list=[]
        for destination_node in self.edges[node]:
            edge=((node,destination_node),self.edges[node][destination_node])
            edge_list.append(edge)
        return edge_list




if __name__ == "__main__":
    #e = EdgeSet()
    d = dict()
    d["a"]={"name":"22"}
    d["b"]={"name":"33"}
    for item in d:
        print d[item]
    for i in range(0,0):
        print "hahahaha"
    print(-100%4000)
