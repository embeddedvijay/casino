from copy import deepcopy
from ..constants.text import tax_list,tax_group
from ..constants.number import isprice
from .common_functionality import get_total,MP,PANAL,FM
class multi_by_multi:
    
    def mbm_check_acceptibility(self)->bool:
        message = deepcopy(self.before_joining)
        for line_num,line in enumerate(message):
            line = [x for x in line if x.isnumeric() or x in tax_list]
            num_in_line = [x for x in line if x.isnumeric()]
            if any(x in tax_list for x in line):
                if len([x for x in line if x.isnumeric()])<2:
                    return False
                num_lengths = len(set([len(x) for x in line if x.isnumeric()]))
                if num_lengths >2:
                    return False
            #elif num_in_line and not isprice(num_in_line[-1]):
                #return (False,0,[])
        return True

    def mbm_solve(self)->tuple[bool,list,int]:
        message = deepcopy(self.before_joining)
        looks_good = self.mbm_check_acceptibility()
        temp = []
        res_list = []
        res_total = 0
        if not looks_good:
            return looks_good,res_list,res_total

        def solve_line(line:list):
            nonlocal res_total
            res_list.append([*line[:-1],line[-1]])
            res_total += get_total(line[:-1],line[-1])

        for line_num,line in enumerate(message):
            line = [x for x in line if x.isnumeric() or x in ['T','P',*tax_list]]
            num_in_line = [x for x in line if x.isnumeric()]
            if not line:
                continue
            if not num_in_line :
                if 'T' in line:
                    continue
                print("not look1",line,message[line_num])
                looks_good = False
                continue
            
            if 'T' in line:
                if len(num_in_line)==1:
                    total = num_in_line[0]
                else:
                    looks_good = False
            elif 'R' in line:
                if temp:
                    if  len(temp[0]) == len(num_in_line[0]):
                        temp.extend(num_in_line)
                        num_in_line = temp
                    else:
                        solve_line(temp)
                    temp = []
                solve_line(num_in_line)
            elif 'P' in line:
                looks_good = False


            elif num_in_line and  (len(line))==len(num_in_line):
                if (all(len(x)==len(num_in_line[0]) for x in num_in_line[:-1]) and len(num_in_line[0])!=len(num_in_line[-1])):
                    if temp:
                        temp.extend(num_in_line)
                        num_in_line =  deepcopy(temp)
                        temp = []
                    solve_line(num_in_line)

                elif temp:
                    
                    if len([x for x in message[line_num-1] if x.isnumeric()]) == len(num_in_line) and len(temp[0])==len(num_in_line[-1]) and len(temp[0])==len(num_in_line[0]) :
                        temp.extend(num_in_line)
                    else:
                        if  len(temp[0])!=len(num_in_line[0]):
                            if len(num_in_line) == 1:
                                pass
                            else:
                                solve_line(temp)
                                temp = num_in_line
                                continue
                        temp.extend(num_in_line)
                        solve_line(temp)
                        temp = []
                    
                else:
                    if line_num < len(message)-1 and any(x.isnumeric() for x in message[line_num+1]) and len([x for x in message[line_num+1] if x.isnumeric()][0]) != len(num_in_line[0]):
                        solve_line(num_in_line)
                        continue
                    temp.extend(num_in_line)

            
            elif len([x for x in line if x in tax_list])==1:
                taxes = {
                    PANAL : ['SP','DP','TP','COMSPDP','COMSP','COMDP','SPDPTP','SPDP','SPTP','DPTP','CP'],
                    MP : ['MPSPDP','MPSP','MPDP'],
                    FM : ['FM']
                }
                if temp:
                    if len(temp[-1])==len(num_in_line[0]) and len(temp[0])==len(num_in_line[0]):
                        temp.extend(num_in_line)
                        num_in_line = deepcopy(temp)
                    else:
                        solve_line(temp)
                    temp = []
                tax_in_here = [x for x in line if x in tax_list][0]
                if 'MP' in tax_in_here:
                    pass
                elif len(num_in_line[0])<4 and tax_in_here in tax_group[len(num_in_line[0])] and all(len(x)==len(num_in_line[0]) for x in num_in_line[:-1]):
                    pass
                elif len(num_in_line[0])<4 and tax_in_here in tax_group[len(num_in_line[-1])] and all(len(x)==len(num_in_line[1]) for x in num_in_line[1:]):
                    num_in_line.reverse()
                else:
                    looks_good = False 
                    continue
                
                if 'COM' in tax_in_here:
                    tax_name = 'COM'
                    tax_in_here = tax_in_here.replace('COM','')
                else:
                    tax_name = ''
                for i in range(0,len(tax_in_here)-1,2):
                    if 'COM' in tax_name:
                        tax_name += tax_in_here[i:i+2]
                    else:
                        tax_name = tax_in_here[i:i+2]

                    if tax_name == 'MP':
                        continue
                    res,amt = [key for key,val in taxes.items() if any(x in val for x in line if x.isalpha())][0](tax_name,num_in_line)

                    if not res:
                        looks_good = False
                    res_list.extend(res)
                    res_total += amt
            else:
                #print("not look",line)
                looks_good = False
        if temp :
            solve_line(temp)
        for i,sl in enumerate(res_list):
            if isprice(sl[-1]):
                res_list[i] = [*sl[:-1],int(sl[-1])]
            else:
                looks_good = False
                # self.risk(f"Unkown Price in MBM line ; {sl} price {sl[-1]}")
        
        return (looks_good,res_list,res_total)
                


            
                
                





            
            


