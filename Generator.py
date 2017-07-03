from random import shuffle, randint
import pickle
class WalkNumberGenerator(object):
    def __init__(self,number_of_nodes):
        self.list = []
        self.index = 0
        for i in range(1,number_of_nodes+1):
            self.list.append(i)
        self.list = self.list+self.list+self.list
        shuffle(self.list)
        #print self.list
        pickle.dump( self.list, open( "walk_seed.p", "wb" ) )

    def get_next(self):
        result = self.list[self.index]
        self.index = (self.index+1)%len(self.list)
        return result


class LinkNumberGenerator(object):
    def __init__(self,number_of_nodes,number_of_link=3,link_range=1,upload_cap=200,download_cap=200):
        self.list = []
        self.index =0
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

    def get_current(self):
        result = self.list[self.index]
        return result

    def get_next(self):
        result = self.list[self.index]
        self.index = (self.index+1)%len(self.list)
        return result






if __name__ == "__main__":
    #wg = WalkNumberGenerator(10)
    #for i in range(0,50):
        #print wg.get_next()
    lng = LinkNumberGenerator(number_of_nodes=10,link_range=2)
    for i in range(0,50):
        print lng.get_next()


