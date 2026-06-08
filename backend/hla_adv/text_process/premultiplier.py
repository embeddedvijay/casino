from ..constants.text import tax_list
class P:
    def __init__(self) -> None:
        pass
    
    def settle_p(self,price = ''):
        if not price:
            price = self.PREMULTIPLIER[-1]

        if self.num_list:
            self.num_list.extend(['R',price])
        for i,l in enumerate(self.num_list):
            if all(x.isnumeric() for x in l):
                self.num_list[i].extend(['R',price])    
            elif any(x in tax_list for x in l):
                if l[-1] in tax_list:
                    self.num_list[i].append(price)

    def p(self,line)->None:
        if len(line)!=2:
            risk += "Formate Error of P"

        #num_of_p = [line_num for line_num,line in enumerate(self.lines[self.line_num:]) if 'P' in line]
        #print("---ccccccccc---",num_of_p)

        # if num_of_p == 1:
        #     self.PREMULTIPLIER.append(self.line[-1])
        # else:
        #self.line.pop(0)
        price = self.PREMULTIPLIER[-1]
        self.settle_p(price)
        return
        

    def p2(self):
        return
        t = [x for i,x in enumerate(self.line) if(x.isnumeric() or self.idx == i) ]
    
        if( any(r in tax_list for r in raw_msg)):
            pass

        elif(len(t) == 2 ):
            if(num_list):
                num_list.insert(0,'P')
            else:
                num_list.append('P')
            premultiplier = True
            
        elif(len(t) > 2):
            try:
                if(t.index(raw) == 0):
                    left = False
                else:
                    left = t[t.index(raw)-1]
            except:
                left = False
            try:
                right = t[t.index(raw)+1]
            except:
                right = False
            del t
            t = list()
            t_len = list()
            biggest_num = list()
            for i in range(0,len_of_raw):
                if(raw_msg[i].isnumeric() or raw_msg[i].isalpha()):
                    n = raw_msg[i]
                    if(n.isnumeric()):
                        n_l = len(str(raw_msg[i]))
                        biggest_num.append(int(n))
                    elif(n == 'P' or n == 'T'):
                        n_l = 0
                    else:
                        continue
                    t.append(n)
                    t_len.append(n_l)
            biggest_num = max(biggest_num, key = lambda x: x if is_price(x) else 0)
            if(left and right):
                if('P' in num_list ):
                    risk += f"More than one P Present(P->LR) Line:{idx}, raw:{raw}\n"
                    pass
                else:
                    for i,x in enumerate(zip(t,t_len)):
                        if(i == 0):
                            continue
                        # can be T or P
                        if(x[1] == 0):
                            if(t_len[i+1] == 0 and t[i] == 'P'):
                                if(i == (len(t_len)-4)):
                                    num_list.append('P')
                                    if(int(t[i+2]) < int(t[i+3])):
                                        num_list.append(t[i+2])
                                        num_list.append('T')
                                        num_list.append(t[i+3])
                                    elif(int(t[i+2]) > int(t[i+3])):
                                        num_list.append(t[i+3])
                                        num_list.append('T')
                                        num_list.append(t[i+2])
                                    else:
                                        risk += f"Equal numbers in LR(P->LR) Line:{idx}, raw:{raw}\n"
                                        break
                                    total = True
                                    premultiplier = True
                                    break
                                elif(i == (len(t_len)-3)):
                                    if(int(t[i-1]) < int(t[i+2])):
                                        num_list.insert((num_list.index(t[i-1])),'P')
                                        premultiplier = True
                                    elif(int(t[i-1]) > int(t[i+2])):
                                        num_list.append('P')
                                        premultiplier = True
                                else:
                                    risk += f"Shuffled or Unordered Numbers in LR(P->LR) Line:{idx}, raw:{raw}\n"
                            elif(t[i] == 'P'):
                                if(i == (len(t_len)-2)):
                                    if(is_price(t[i+1])):
                                        num_list.append('P')
                                        premultiplier = True
                                    else:
                                        risk += f"Number not in Price criteria LR(P->LR->P->-2) Line:{idx}, raw:{raw}\n"
                                elif(i == (len(t_len)-3)):
                                    if(is_price(t[i-1])):
                                        num_list.insert(num_list.index(t[i-1]),'P')
                                        premultiplier = True
                                        if(not any(r in tax_list for r in raw_msg)):
                                            num_list.append('T')
                                            wait_list.append([line_num,'total'])
                                        break
                                    else:
                                        risk += f"Number not in Price criteria LR(P->LR->P->-3) Line:{idx}, raw:{raw}\n"
                                elif(i == (len(t_len)-4)):
                                    if(is_price(t[i+1])):
                                        num_list.append('P')
                                        premultiplier = True
                                    else:
                                        risk += f"Number not in Price criteria LR(P->LR->P->-4) Line:{idx}, raw:{raw}\n"
                                else:
                                    risk += f" Unrecognizable format LR(P->LR->P->else) Line:{idx}, raw:{raw}\n"  
                            elif(t[i] == 'T'):
                                continue
                            break
            elif(left):
                if('P' in num_list ):
                    risk += f" More than one P in L(P->L) Line:{idx}, raw:{raw}\n"
                    pass
                else:
                    for i,x in enumerate(zip(t,t_len)):
                        if(i == 0):
                            continue
                        if(x[1] == 0 ):
                            if(t[i] == 'P' and (len(t_len) == 2)):
                                if(is_price(t[i-1])):
                                    num_list.insert(num_list.index(t[i-1]),'P')
                                    premultiplier = True
                                else:
                                    risk += f" Number not in price in L(P->L) Line:{idx}, raw:{raw}\n"
                            elif(t[i] == 'T'):
                                continue
                            # elif(i+1==len(t)):
                            #     next_line = 0
                            #     if(len(lines)-1>line_num):
                            #         next_line = re.findall(r'\d+',lines[line_num+1])
                            #     if(not next_line):
                            #         num_list.insert(num_list.(t[i-1]),'P')
                            #         premultiplier = True
                            else:
                                if(not any(r in tax_list for r in raw_msg)):
                                    num_list.append('P')
                                    wait_list.append([line_num,'premultiplier'])
                            break
                        
                
            elif(right):
                
                if('P' in num_list ):
                    risk += f" More than one P in R(P->R) Line:{idx}, raw:{raw}\n"
                    pass
                else:
                    for i,x in enumerate(zip(t,t_len)):
                        if(x[1] == 0):
                            if(t_len[i+1] == 0 and t[i] == 'P'):
                                if(i == (len(t_len)-4)):
                                    if(int(t[i+2]) < int(t[i+3])):
                                        if(is_price(t[i+3]) or (t[i+3] == biggest_num)):
                                            num_list.append('T')
                                            num_list.append(t[i+3])
                                            total = True
                                        else:
                                            risk += f" Number not in price in P(P->L->P->+3) Line:{idx}, raw:{raw}\n"
                                        if(is_price(t[i+2])):
                                            num_list.append('P')
                                            num_list.append(t[i+2])
                                            premultiplier = True
                                        else:
                                            risk += f" Number not in price in P(P->L->P->+2) Line:{idx}, raw:{raw}\n"

                                    elif(int(t[i+2]) > int(t[i+3])):
                                        if(is_price(t[i+2]) or (t[i+2] == biggest_num)):
                                            num_list.append('T')
                                            num_list.append(t[i+2])
                                            total = True
                                        else:
                                            risk += f" Number not in price in P(P->L->P->+2+3) Line:{idx}, raw:{raw}\n"
                                        if(is_price(t[i+3])):
                                            num_list.append('P')
                                            num_list.append(t[i+3])
                                            premultiplier = True
                                        else:
                                            risk += f" Number not in price in R(P->L->P->+2+3) Line:{idx}, raw:{raw}\n"
                                    else:
                                        risk += f" Equal Numbers price in P(P->L->P->+2+3) Line:{idx}, raw:{raw}\n"
                                    break
                                elif(i == (len(t_len)-3)):
                                    if(biggest_num == t[i+2]):
                                        num_list.append('T')
                                        num_list.append(t[i+2])
                                        if(not any(r in tax_list for r in raw_msg)):
                                            num_list.append('P')
                                            wait_list.append([line_num,'premultiplier'])
                                    elif(is_price(t[i+2])):
                                        num_list.append('P')
                                        num_list.append(t[i+2])
                                        if(not any(r in tax_list for r in raw_msg)):
                                            num_list.append('T')
                                            wait_list.append([line_num,'total'])
                                    break
                                else:
                                    risk += f" Number not in price in R(P->L->P->-3) Line:{idx}, raw:{raw}\n"
                            elif(t[i] == 'P'):
                                if(is_price(t[i+1])):
                                    num_list.append('P')
                                    premultiplier = True
                                else:
                                    num_list.append('P')
                                    risk += f" Number not in format in P(P->L->P->-else) Line:{idx}, raw:{raw}\n"        
                            elif(t[i] == 'T'):
                                continue
                            break
            else:
                if(not any(r in tax_list for r in raw_msg)):
                    num_list.append('P')
                    wait_list.append([line_num,'premultiplier'])
