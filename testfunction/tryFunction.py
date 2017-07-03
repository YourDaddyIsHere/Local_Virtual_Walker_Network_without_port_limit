
class testFunctionClass():
    def __init__(self):
        c1=1
        c2=3
        print(self.fb(c1,c2))

    def fa(self,a,b):
        return a+b
    def fb(self,a,b):
        f = self.fa
        return f(a,b)



if __name__ == "__main__":
    t = testFunctionClass()
