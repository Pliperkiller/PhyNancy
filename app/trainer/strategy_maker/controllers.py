class Chart:
    def __init__(self,name, df, period):
        self.name = name
        self.df = df
        self.period = period
        pass

class Strategy:
    def __init__(self,name,func,*kwargs):
        self.name = name
        self.func = func
        self.kwargs = kwargs
        pass

    def apply_strategy(self,data):
        return self.func(data=data,**self.kwargs)



if __name__ =='__main__':
    
    
    pass