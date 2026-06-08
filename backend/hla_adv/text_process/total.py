class T:
    def __init__(self) -> None:
        pass

    def settle_t(self,price = ''):
        if not price:
            price = self.PREMULTIPLIER

        if self.num_list:
            self.num_list.extend(['R',price])
        for i,l in enumerate(self.num_list):
            if all(x.isnumeric() for x in l):
                self.num_list[i].extend(['R',price])    
            elif any(x in tax_list for x in l):
                if l[-1] in tax_list:
                    self.num_list[i].append(price)

    def t(self,line)->None:
        if len(line)!=2:
            risk += "Formate Error of P"

        num_of_p = [line_num for line_num,line in enumerate(self.lines[self.line_num:]) if 'P' in line]

        if num_of_p == 1:
            self.PREMULTIPLIER = self.line[-1]
        else:
            self.line.pop(0)
            price = self.line[-1]
            self.settle_p(price)
        return
        
    