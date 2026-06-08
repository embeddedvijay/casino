from ..constants.number import main_num_list,isprice
from .common_functionality import get_total
from ..constants.text import tax_list
from copy import deepcopy

class number:
    def __init__(self) -> None:
        pass

    def in_line_total_handle(self,in_line:list)->list:
        line = [x for x in in_line if x != 'R'][::-1]
        full_list = [x for sl in self.num_list for x in sl if x != 'R' and not any(y in tax_list for y in sl)][::-1] + line
        full_list.reverse()
        idx = -len(line)+1
        line = []
        line_validation = True
        # print(f'{self.res_total}full list is  -----{full_list}')
        for i,x in enumerate(full_list):
            line.append(x)
            # print(int(i+1) , int(full_list[i+1]) , int(full_list[i+2]))
            # print(i+1,line,full_list[i+1])
            if len(full_list)-1-i>2 and i+1 == int(full_list[i+1]) and isprice(full_list[i+1]):
                tot = int(i+1) * int(full_list[i+2])
                if tot == int(full_list[i+3]) and isprice(full_list[i+3]):
                    idx += i+3
                    line.extend(['R',int(full_list[i+2])])
                    break

            elif len(full_list)-1-i>2 and i+1 == int(full_list[i+2]) and isprice(full_list[i+2]):
                tot = int(i+1) * int(full_list[i+1])    
                if tot == int(full_list[i+3]) and isprice(full_list[i+3]):
                    idx += i+3
                    line.extend(['R',int(full_list[i+1])])
                    break

            elif len(full_list)-1-i>1 and int((i+1) * int(full_list[i+1])) == int(full_list[i+2]) and isprice(full_list[i+1]) and isprice(full_list[i+2]):
                idx += i+2
                line.extend(['R',int(full_list[i+1])])
                break

            elif len(full_list)-1-i>1 and int((i+1) * int(full_list[i+1])) == (int(full_list[i+2])-int(self.res_total)) and isprice(full_list[i+1]) and isprice(full_list[i+2]):
                idx += i+2
                line.extend(['R',int(full_list[i+1])])
                break
           



            # elif self.res_total and 
        if len(line)>3 and idx>0:
            temp = [str(line[0])]
            for x in [str(x) for x in line[1:]]:
                if len(temp[-1])==len(x):
                    temp.append(x)
                    continue
                elif any(len(y)==len(x) for y in temp):
                    line_validation = False
                    break
                else:
                    temp.append(x)
            if not all(len(x)==len(line[0]) for x in line[:-2]):
                line_validation = False
            # print("ok",line)

        else:
            line_validation = False

        if  idx>0 and len(line)>3 and line_validation:
            while idx:
                if self.num_list[0]:
                    if self.num_list[0].pop(0).isnumeric():
                        idx -= 1
                else:
                    self.num_list.pop(0)
            if line and idx==0:
                return line
        return in_line
        
    def num_calculate(self,line:list):
        num_in_line = [x for x in line if x.isnumeric()]
        # self.log(f"{line},{self.temp_res}")
       
        
        if len([x for y in self.num_list for x in y if x.isnumeric() and len([z for z in y if z.isnumeric()])>2 ])>2:
            line = self.in_line_total_handle(line)
        

        if self.temp_res:
            def sol():
                t_temp_list = [x for x in self.temp_res[:-1] if x.isnumeric()]
                self.res_total += get_total(self.temp_res[:-1],self.temp_res[-1])
                self.AMOUNTS.append(self.temp_res[-1])
                t_temp_list.append(int(self.temp_res[-1]))
                self.res_list.append(t_temp_list)
                self.temp_res = []

            if len(line)==1 and isprice(line[0]):
                if str(self.res_total + get_total(self.temp_res[:-1],self.temp_res[-1])) in line[0]:
                    sol()
                    
            else:
                sol()

        if len(line) == 1:
            if self.temp_res:
                if all(x.isnumeric() and x in main_num_list for x in self.temp_res):
                    if line[0] in self.GIVEN_TOTAL:
                        temp_total = get_total(self.temp_res[:-1],self.temp_res[-1]) + self.res_total
                        if self.num_list and temp_total == line[0]:
                            self.res_total += get_total(self.temp_res[:-1],line[-1])
                            self.AMOUNTS.append(line[-1])
                            self.temp_res.append(int(line[0]))
                            self.res_list.append(self.temp_res)
                            self.temp_res = []
                        else:
                            temp_total = int(line[0]) - self.res_total
                            temp_total_check = temp_total%len(self.temp_res)
                            # print("tota check--",temp_total>0,  temp_total_check==0 , isprice(int(temp_total/len(self.temp_res))) )
                            if temp_total>0 and temp_total_check==0 and isprice(int(temp_total/len(self.temp_res))):
                                temp_total_check = int(temp_total/len(self.temp_res))
                                self.res_total += get_total(self.temp_res,temp_total_check)
                                self.AMOUNTS.append(temp_total_check)
                                self.temp_res.append(int(temp_total_check))
                                self.res_list.append(self.temp_res)
                                self.temp_res = []
                            else:
                                temp_total = int(line[0])
                                temp_total_check = temp_total%len(self.temp_res)
                                # print("tota check--",temp_total>0,  temp_total_check==0 , isprice(int(temp_total/len(self.temp_res))) )
                                if temp_total>0 and temp_total_check==0 and isprice(int(temp_total/len(self.temp_res))):
                                    temp_total_check = int(temp_total/len(self.temp_res))
                                    self.res_total += get_total(self.temp_res,temp_total_check)
                                    self.AMOUNTS.append(temp_total_check)
                                    self.temp_res.append(int(temp_total_check))
                                    self.res_list.append(self.temp_res)
                                    self.temp_res = []
                                    return
                                self.risk(f"Given Total is less than Calculated and Remaining temp_res: {self.temp_res}")

                    else:
                        if not self.num_list and line[0] not in self.PREMULTIPLIER and self.AMOUNTS and line[0]>self.AMOUNTS[-1] :
                            
                            if self.res_total < int(line[0]):
                                temp_iden_total = int(line[0]) - self.res_total
                                temp_iden_total_check = temp_iden_total/len(self.temp_res)
                                self.log(f"temp iden total{temp_iden_total_check} ::{temp_iden_total_check.is_integer()}::{isprice(temp_iden_total_check)}")
                                if temp_iden_total_check.is_integer():
                                    temp_iden_total_check = int(temp_iden_total_check)
                                    if isprice(temp_iden_total_check):
                                        self.IDEN_TOTAL = int(line[0])
                                        self.res_total += get_total(self.temp_res,temp_iden_total_check)
                                        self.AMOUNTS.append(temp_iden_total_check)
                                        self.temp_res.append(int(temp_iden_total_check))
                                        self.res_list.append(self.temp_res)
                                        self.temp_res = []
                                        return
                                else:
                                    temp_iden_total = int(line[0])
                                    temp_iden_total_check = temp_iden_total/len(self.temp_res)
                                    if temp_iden_total_check.is_integer():
                                        temp_iden_total_check = int(temp_iden_total_check)
                                        if isprice(temp_iden_total_check):
                                            self.IDEN_TOTAL = int(line[0]) + self.res_total
                                            self.res_total += get_total(self.temp_res,temp_iden_total_check)
                                            self.AMOUNTS.append(temp_iden_total_check)
                                            self.temp_res.append(int(temp_iden_total_check))
                                            self.res_list.append(self.temp_res)
                                            self.temp_res = []
                                            return

                        self.res_total += get_total(self.temp_res,line[0])
                        self.AMOUNTS.append(line[0])
                        self.temp_res.append(int(line[0]))
                        self.res_list.append(self.temp_res)
                        self.temp_res = []
                else:
                    self.risk(f"Unknown pattern temp_res:{self.temp_res}")
            else:
                if not self.num_list and isprice(line[0]):
                    self.IDEN_TOTAL = int(line[0])
                elif self.res_total == int(line[0]):
                    pass
                elif self.GIVEN_TOTAL and self.res_total and str(self.res_total) in  str(self.GIVEN_TOTAL):
                    # self.temp_res = []
                    pass
                elif self.IDEN_TOTAL and self.res_total and str(self.res_total) in  str(self.IDEN_TOTAL):
                    # self.temp_res = []
                    pass
                elif self.num_list and line[0].isnumeric() and self.num_list[0][0].isnumeric() and len(line[0]) == len(self.num_list[0][0]):
                    self.num_list[0].insert(0,line[0])
                elif self.res_list and len([x for x in line if x.isnumeric()])==1 and len(self.res_list[-1][0]) == len(line[0]) and line[0].isnumeric():
                    self.res_list.append([line[0],self.res_list[-1][-1]])
                elif line[0] in self.GIVEN_TOTAL:
                    pass
                else:
                    self.risk(f"Unknown empty number line:{line}")

        elif len(num_in_line)>2 and  all(len(x)==len(num_in_line[0]) for x in num_in_line[:-1]) and (int(len(num_in_line[:-2])*int(num_in_line[-2])) + self.res_total == int(num_in_line[-1])) and isprice(num_in_line[-2]):
            self.IDEN_TOTAL = int(num_in_line[-1])
            temp_list = [x for x in num_in_line[:-2]]
            self.res_total += get_total(num_in_line[:-2],num_in_line[-2])
            self.AMOUNTS.append(num_in_line[-2])
            temp_list.append(int(num_in_line[-2]))
            self.res_list.append(temp_list)

        elif len(line)>1 and line[-2] == 'R' and all(x in main_num_list for x in line[:-2]):
            temp_list = [x for x in line[:-1] if x.isnumeric()]
            self.res_total += get_total(line[:-2],line[-1])
            self.AMOUNTS.append(line[-1])
            temp_list.append(int(line[-1]))
            self.res_list.append(temp_list)

        else:
            
            if len(self.num_list)>1 and len(self.num_list[0])==1 and len(self.num_list[1])==1:
                self.temp_res.extend(line)
                self.temp_res.extend(self.num_list.pop(0))
            elif all(x.isnumeric() for x in line) and all(len(x)==len(line[0]) for x in line):
                self.temp_res.extend(line)
            else:
                self.risk(f"SOmething Else line: {line}")
    
    
            






    