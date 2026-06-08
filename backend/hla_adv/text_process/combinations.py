from ..constants.text import tax_list,tax_group
from ..constants.number import isprice, check_num, main_num_list,tax_num_dict


class TAX:
    def __init__(self) -> None:
        pass
    
    def tax(self,line:list) -> None:
        tax_in_line = list({x for x in line if x in tax_list})
        numeric_list = [x for x in line if x.isnumeric()]
        len_dict = {length: [number for number in numeric_list if len(str(number)) == length] for length in set(len(number) for number in numeric_list)}

        if len(numeric_list)==1:
            self.risk(f"Invalid Messsage Line: {line}")
            return
        elif len(numeric_list) == len(tax_in_line) and self.new_lines:
            #   and self.new_lines[-1][-2] == 'R':
            # all(len(x)==len(self.num_list[-1][0]) for x in self.num_list[-1][:-1]) and len(self.num_list[-1][-1] != self.num_list[-1][0]) :
            nums = [x for x in self.new_lines[-1] if x.isnumeric()]
            if all(len(x) == len(nums[0]) for x in nums[:-1]) and len(nums[0]) != len(nums[-1]):
                nums.pop()
            if all(check_num(tax_in_line[0],num) for num in nums):
                line = [*nums,*line]
                # print(line)
                numeric_list = [*nums,*numeric_list]
            else:
                self.risk(f"Previous Line not couplable and the text line == {self.new_lines[-1]} isnt compatible with those len of num:{line}")
            
                
        if len(len_dict.keys())>2:
            # print(numeric_list[:-len(tax_in_line)])
            if len(tax_in_line)>1 and all(len(x)==len(numeric_list[0]) for x in numeric_list[:-len(tax_in_line)]):
                pass
            else:
                self.risk(f"Invalid Messsage with diff len numbers Line: {line}")
                return

        if all(x in tax_in_line for x in ('FM','CP')):
            self.risk(f"FM and CP numbers can't be coupled.line:{line}")
            return 
        
        inside = [] #numbers that are verified for that tax
        temp = []
        can_be_price = [] #
        # FOR ONE TAX ONLY
        if len(tax_in_line) == 1:
            # WHEN ALL NUMBER IN LINE ARE OF SAME LEN
            if numeric_list and all(len(x)==len(numeric_list[0]) for x in numeric_list) and 'MP' not in tax_in_line[0] and (tax_in_line[0] in tax_group[len(numeric_list[0])] ):
                #verify all are tax compatible number
                for idx,word in enumerate(line):
                    if word.isnumeric():
                        if (isprice(word) and ((word in (numeric_list[0]) and line[0] in tax_list) or (word in numeric_list[-1] and line[-1] in tax_list))): 
                            can_be_price.append(word)
                        elif check_num(tax_in_line[0],word):
                            inside.append(word)
                        else:
                            can_be_price.append(word)
                        temp.append(word)
                    
                    elif word == tax_in_line[0]:
                        if idx == 0:
                            continue

                        if idx == (len(line)-2) and line[-1].isnumeric():
                            if all(check_num(tax_in_line[0],x) for x in temp):
                                temp.append(tax_in_line[0])
                                temp.append(line[-1])
                                self.num_list = temp
                                return
                            continue
                        
                        if word == tax_in_line[0] and idx == 1 and line[0].isnumeric():

                            if all(check_num(tax_in_line[0],x) for x in numeric_list[1:]):
                                price = numeric_list.pop(0)
                                numeric_list.extend([tax_in_line[0],price])
                                self.num_list = numeric_list
                                return
                            continue
                        if word == tax_in_line[0] and idx == len(line)-1 and len(numeric_list)>2:
                            
                            if all(check_num(tax_in_line[0],x) for x in numeric_list[1:]):
                                price = numeric_list.pop()
                                numeric_list.extend([tax_in_line[0],price])
                                self.num_list = numeric_list
                                return
                            continue
                        self.risk(f"TAX AT UNKNOWN LOCATION line:{line}, word:{word}")
                        
                    elif word in ('!','R'):
                        if any(x.isnumeric() for x in temp) and len([x for x in line[idx:] if x.isnumeric()])==1:
                            temp.append(tax_in_line[0])
                            temp.append(numeric_list[-1])
                            self.num_list = temp
                            return
                # deciding based on recorded values clearing ties
                if can_be_price and inside:
                    if len(can_be_price) == 1:
                        inside.extend([tax_in_line[0],can_be_price[0]])
                        self.num_list =  inside
                        return
                    
                    if len(can_be_price) == 2:
                        if all(check_num(tax_in_line[0],x) for x in can_be_price):
                            #FM 100 200 300
                            if line[0] == tax_in_line[0]:
                                inside.extend([can_be_price[1],tax_in_line[0],can_be_price[0]])
                                self.num_list =  inside
                                return
                            # 100 200 ---300 FM
                            elif line[-1] == tax_in_line[0]:
                                inside.extend([can_be_price[0],tax_in_line[0],can_be_price[1]])
                                self.num_list =  inside
                                return
                            
                        elif(check_num(tax_in_line[0],can_be_price[0])):
                            inside.extend([can_be_price[0],tax_in_line[0],can_be_price[1]])
                            self.num_list =  inside
                            return
                        elif(check_num(tax_in_line[0],can_be_price[1])):
                            inside.extend([can_be_price[1],tax_in_line[0],can_be_price[0]])
                            self.num_list =  inside
                            return
        
                self.risk(f"High RIsk UNKNOWN Format line:{line}, can_be_price :{can_be_price},inside:{inside}")
                return 
            #NOT ALL NUM ARE OF SAME LENGTH
            elif any(len(x)!=len(numeric_list[0]) for x in numeric_list):
                if not any(len(val)==1 for k,val in len_dict.items()):
                    self.risk(f"Invalid Messsage with confusing numbers Line: {line}")
                    return
                
                if tax_in_line[0] == 'FM':
                    if len(numeric_list)==2:
                        if all(check_num(tax_in_line[0],x)for x in numeric_list) or check_num(tax_in_line[0],numeric_list[0]):
                            l = len(numeric_list[0])
                        elif check_num(tax_in_line[0],numeric_list[1]):
                            l = len(numeric_list[1])
                        else:
                            self.risk(f"Invalid Numbers of FM {line}")
                    else:
                        l = max(len_dict, key=lambda k: len(len_dict[k]))
                # WHOLE SEPRATE SWITCH CASE
                elif 'MP' in tax_in_line[0]:
                    for word in line:
                        if word.isnumeric():
                            if check_num(tax_in_line[0],word):
                                inside.append(word)
                            else:
                                can_be_price.append(word)
                    if len(can_be_price)==1:
                        self.num_list = [*inside,tax_in_line[0],*can_be_price]
                        return
                    self.risk(f"High Risk Unknown Format of MP line {line} ,unkown price : {can_be_price} ")

                else:
                    l = max(len_dict, key=lambda k: len(len_dict[k]))
                    # l = int([key for key,val in tax_group.items() if tax_in_line[0] in val][0])

                # len_dict = {len(x):[n for n in numeric_list if len(x)==len(n)] for x in numeric_list}

                if len(len_dict.keys())==2 and any(len(val)==1 for val in len_dict.values()) and any(len(val)!=1 for val in len_dict.values()):
                    len_dict[l].extend([tax_in_line[0],*[v[0] for v in len_dict.values() if len(v)==1]])
                    self.num_list = len_dict[l]
                    return
                elif len(numeric_list) ==2:
                    if any(check_num(tax_in_line[0],x) for x in numeric_list):
                        if check_num(tax_in_line[0],numeric_list[0]):
                            numeric_list.insert(-1,tax_in_line[0])
                        else:
                            numeric_list.reverse()
                            numeric_list.insert(-1,tax_in_line[0])
                        self.num_list = numeric_list
                        return

                self.risk(f"High Risk Unknown Format of Tax line {line} ")
                return
        # MORE THAN ONE TAX PRESRNT
        elif any(all(x in val for x in tax_in_line) for val in tax_group.values()):
            group_key = [k for k,v in tax_group.items() if all(x in v for x in tax_in_line)][0]
            tax_with_price = []
            # CHECKS IF ITS POSSBLE TO HAVE TAXES IN SAME NUMBER
            line = [x for x in line if x.isnumeric() or x in tax_in_line]
            if group_key in (1,4):
                # 1,2,3 SP 20 DP 30
                if all(line[idx+1].isnumeric() for idx,x in enumerate(line[:-2]) if x in tax_list) and line[-1].isnumeric():
                    while line:
                        x = line.pop(0)
                        if x.isnumeric():
                            if check_num(tax_in_line[0],x):
                                inside.append(x)
                            else:
                                self.risk(f"Numbers not suitable based on tax line:{line}")
                                return
                            
                        if x in tax_list:
                            tax_with_price.append([x,line.pop(0)])
                    for twp in tax_with_price:
                        self.lines.insert(self.line_num+1,[*inside,*twp])
                    return
                # 1,2,3 20 SP 30 DP
                elif all(line[idx-1].isnumeric() for idx,x in enumerate(line) if x in tax_list) and line[-1] in tax_list:
                    while line:
                        x = line.pop(0)
                        if x.isnumeric():
                            if (line[0] not in tax_list):
                                if check_num(tax_in_line[0],x):
                                    inside.append(x)
                                else:
                                    self.risk(f"Numbers not suitable based on tax line:{line}")
                                    return
                            else:
                                can_be_price.append(x)

                        if x in tax_list:
                            if len(can_be_price) == 1:
                                tax_with_price.append([x,can_be_price.pop(0)])
                            else:
                                self.risk(f"Numbers with tax format not suitable line:{line}")
                                return
                    for twp in tax_with_price:
                        self.lines.insert(self.line_num+1,[*inside,*twp])
                    return
            self.risk(f"Unkown coupled tax in more than one tax in line line:{line}")
        self.risk(f"High Risk Multiple uncouplable taxes line:{line},tax_in_line:{tax_in_line}")
        return
        
       