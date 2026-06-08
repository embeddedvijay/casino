from .numbers import NUM
from .combinations import TAX
# from .premultiplier import P
# from .total import T
# from .rupee import R
from ..constants.text import tax_list

# class text_processing(NUM,P,R,T,TAX)

class text_processing(NUM,TAX):

    def __init__(self) -> None:
        super().__init__()

    def text_process(self,lines:list)->list:
        new_lines = []
        self.lines = lines


        for line_num, line in enumerate(lines):
            
            self.num_list = []
            self.line_num = line_num
            self.line = line
            self.new_lines = new_lines
            # print("line",line,self.new_lines)
            # print(line,line[0] == 'T' and line[1].isnumeric())
            if len(line)==2 and ( (line[0] == 'T' and line[1].isnumeric()) or  (line[1] == 'T' and (len(lines)-line_num == 2) and len([x for x in lines[-1] if x.isnumeric()])==1)):
                lines[-1].append('T')
                line.pop(line.index('T'))
                #for removing the t if written is 20 se total \n 600 then it will do the work
                #its seprate from below if statements

            if len(line)==2 and  ((line[0] == 'P' and line[1].isnumeric()) or (line[1] == 'P' and line[0].isnumeric())):
                if line[1] == 'P' and line[0].isnumeric():
                    line = line.reverse()
                self.PREMULTIPLIER.append(line[1])
                self.num_list.append(line[1])
                
            elif len(line)==2 and ( (line[0] == 'T' and line[1].isnumeric()) or  (line[1] == 'T' and line[0].isnumeric())):
                if  line[1] == 'T' and line[0].isnumeric():
                    line.reverse()
                self.GIVEN_TOTAL.append(line[1])
                self.num_list.append(line[1])

            elif any(x in tax_list for x in line):
                self.tax(line)
            
            else :
                for idx,word in enumerate(line):
                    self.idx = idx

                    if word.isnumeric():
                        self.num(word,line)

                    elif word == 'R':
                        if idx==len(line)-1:
                            self.num_list.insert(-1,'R')
                            continue
                        self.num_list.append('R')
                    # elif word == 'P':
                    #     self.num_list.append('R')
                    elif word == 'T' and len(lines)==(line_num+1):
                        continue

                    else:
                        self.risk(f"Unknown Thing Found word {word} ,line{line}")
            if self.num_list :
                new_lines.append(self.num_list)
                self.num_list = []
        self.lines = new_lines     
        #print(self.PREMULTIPLIER)       
        return self.lines

        