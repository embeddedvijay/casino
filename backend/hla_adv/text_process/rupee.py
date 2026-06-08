class R:
    def __init__(self) -> None:
        pass

    def r(self):
        t = list()
        for i in range(0,len_of_raw):
            if(raw_msg[i].isnumeric() or i == idx):
                t.append(raw_msg[i])
        if((any(r in tax_list for r in raw_msg)) and ('R' in raw_msg) and (raw_msg.count('R')>1)):
            risk += f" multiple R in tax Line:{idx}, raw:{raw} , Line:{raw_msg} \n" 
            num_list.insert(-1,'R')
            price = True
            continue
        if(len(t) == 2):
            if(t[0].isnumeric()):
                num_list.insert(0,'R')
            else:
                num_list.append('R')
            price = True
            multiline = True
        elif(t[-1] == 'R'):
            num_list.insert(-1,'R')
            price = True
        elif(t[-2] == 'R'  and t[-1].isnumeric()):
            num_list.append('R')
            price = True
        elif((t[1] == raw or t[0] == raw) and len(t) > 3 and all(x.isnumeric() for x in t if(x!=raw))):
            num_list.append('R')
            price = True
            invert = True
        else:
            risk += f" Unrecognized position of R in Line:{idx}, raw:{raw} , Line:{t} \n" 