from ..constants.number import main_num_list,ismotor,isprice

class NUM:
    def __init__(self) -> None:
        pass

    def num(self,raw:str,raw_msg:list)->None:
        len_of_raw = len(raw_msg)-1
        if self.num_list:
            if self.num_list[-1].isnumeric():
                len_of_previous_num = len(self.num_list[-1])

                if(len(self.num_list[-1]) != len(raw) ):
                    if self.idx == len_of_raw :
                        self.num_list.append('R')
                    else:
                        if raw_msg[self.idx+1].isnumeric() and len(raw_msg[self.idx+1])!=len(raw):
                            self.num_list.append('R')   

                elif (len(raw)/2) == len_of_previous_num and all(r in main_num_list for r in [raw[:len(raw)/2],raw[len(raw)/2:]]) and len(raw)<7:
                    if (self.index==(len_of_raw) and (not isprice(raw))) or (self.index<(len_of_raw) and len_of_previous_num==len(raw_msg[self.idx+1])):
                        self.num_list.append(raw[:len(raw)/2])
                        self.num_list.append(raw[len(raw)/2:])
                        return
            elif raw=='R':
                self.num_list.append(raw)
        
        if (raw in main_num_list) or (ismotor(raw)):
            self.num_list.append(raw)
        else:
            if self.num_list and not self.num_list[-1].isalpha():
                self.num_list.append('R')
            self.num_list.append(raw)


        if(len_of_raw == 0):
            pass
        elif((self.idx == (len_of_raw)) and(all(n.isnumeric() for n in self.num_list))):
            self.MULTILINE = True