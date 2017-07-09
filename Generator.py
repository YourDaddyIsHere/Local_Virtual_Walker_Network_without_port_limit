import random
from random import shuffle, randint
import pickle
class WalkNumberGenerator(object):
    def __init__(self,number_of_nodes,random_seed=None):
        #self.list = []
        self.index = 0
        self.number_of_nodes = number_of_nodes
        self.generator = random.Random()
        if random_seed:
            self.generator.seed(random_seed)
        #for i in range(1,number_of_nodes+1):
            #self.list.append(i)
        #self.list = self.list+self.list+self.list
        #shuffle(self.list)
        #print self.list
        #pickle.dump( self.list, open( "walk_seed.p", "wb" ) )

    def get_next(self):
        #result = self.list[self.index]
        #self.index = (self.index+1)%len(self.list)
        #return result
        result = self.generator.randint(1,self.number_of_nodes+1)
        return result


class LinkNumberGenerator(object):
    def __init__(self,number_of_nodes,introduction_seed=None,block_seed=None,number_of_link=3,link_range=1,upload_cap=200,download_cap=200):
        self.list = []
        self.index =0
        self.number_of_nodes = number_of_nodes
        self.number_of_link = number_of_link
        self.link_range=link_range
        self.upload_cap = upload_cap
        self.download_cap = download_cap
        #introduction generator is used to generate the node id of "the node to walk"
        self.introduction_generator = random.Random()
        if introduction_seed:
            self.introduction_generator.seed(introduction_seed)
        #block generator is used to generate the upload/download of block
        self.block_generator = random.Random()
        if block_seed:
            self.block_generator.seed(block_seed)

        self.previous_state_introduction = self.introduction_generator.getstate()
        self.previous_state_block = self.block_generator.getstate()

        #every element in list is a list consisting of 1 integer and multiple tuples
        #the integer means the bias, giving lights of the neighbor will be introduced to others
        #the following  tuples indicate the upload and download of some edges, one tuple for one edge
        for i in range(1,number_of_nodes+1):
            link = [randint(-1*link_range,link_range)]
            for j in range(0,number_of_link):
                upload_and_download = (randint(0,upload_cap),randint(0,download_cap))
                link.append(upload_and_download)
            self.list.append(link)
        #print self.list
        pickle.dump( self.list, open( "link_seed.p", "wb" ) )

    def generate(self):
        result = []
        node_id=0
        while(node_id==0):
            node_id=self.introduction_generator.randint(-1*self.link_range,self.link_range)
        result.append(node_id)
        for i in range(0,self.number_of_link):
            upload_and_download = (self.introduction_generator.randint(-1*self.link_range,self.link_range),self.introduction_generator.randint(0,self.upload_cap),randint(0,self.download_cap))
            result.append(upload_and_download)
        return result

    def get_current(self):
        #result = self.list[self.index]
        #return result
        self.introduction_generator.setstate(self.previous_state_introduction)
        self.block_generator.setstate(self.previous_state_block)
        result = self.generate()
        return result

    def get_next(self):
        #result = self.list[self.index]
        #self.index = (self.index+1)%len(self.list)
        #return result
        result = self.generate()
        self.previous_state_introduction = self.introduction_generator.getstate()
        self.previous_state_block = self.block_generator.getstate()
        return result



class AttackEdgeGenerator(object):
    def __init__(self,honest_node_number,evil_node_number,attack_edge_random_seed=200,block_random_seed=233,upload_cap=600,download_cap=600):
        self.honest_node_number=honest_node_number
        self.evil_node_number=evil_node_number
        self.attack_edge_random_seed=attack_edge_random_seed
        self.upload_cap=upload_cap
        self.download_cap=download_cap
        self.random_edge = random.Random()
        self.random_edge.seed(attack_edge_random_seed)
        self.random_block = random.Random()
        self.random_block.seed(block_random_seed)
    def get_next(self):
        #first tuple is link in the form (node1_id,node2_id),the second tuple is (upload,download)
        edge = []
        link=(self.random_edge.randint(1,self.honest_node_number),self.random_edge.randint(self.honest_node_number+1,self.evil_node_number))
        block=(self.random_block.randint(200,self.upload_cap),self.random_block.randint(200,self.download_cap))
        edge.append(link)
        edge.append(block)
        return edge





if __name__ == "__main__":
    #wg = WalkNumberGenerator(10)
    #for i in range(0,50):
        #print wg.get_next()

    lng = LinkNumberGenerator(number_of_nodes=10,link_range=2)
    for i in range(0,50):
        print lng.get_next()


