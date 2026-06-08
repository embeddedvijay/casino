from ..constants.text import text_dict,replace_dict,combine_dict,reject_msg,open_brackets,close_brackets,tax_list,flags,frame_header_list
from ..constants.number import check_num,ismotor
from .word_sym_process import symbol_normalize
from fuzzywuzzy import fuzz
from datetime import datetime
from copy import deepcopy
from .frame_process import frame_check,process_frames
import re

def f_match(input_str, str_list,max_ratio = 80):
    matched_str = False
    for str_item in str_list:
        ratio = fuzz.ratio(input_str, str_item)
        if ratio > max_ratio:
            max_ratio = ratio
            matched_str = True
    return matched_str

def isreject(lines:str)-> bool:
    for line in lines:
        for word in line:
            if word in reject_msg:
                return True
    return False

def confine_words(self,lines: list) -> list:
    CANCEL = False
    # risk = ''
    new_lines = []
    current_date_strs = {
        datetime.now().strftime(fmt) for fmt in ("%d%m%y", "%m%d%y", "%d%m%Y","%d%m")
    }
    for line in lines:
        # print(line)
        new_line = []
        date_raw = [x for x in line if x.isnumeric()]
        #Date Removal

        if len(date_raw) > 1 and len(date_raw) < 4 and any(''.join(date_raw[:3]) == d for d in current_date_strs):
            for date in date_raw[:3]:
                line.remove(date)
        # word map to dict name
        for word in line:
            word = word.lower()
            if word.isnumeric():
                new_line.append(word)
                continue
            
            appended = False
            for key, values in text_dict.items():
                if word in values or (key not in ['FLSANG', 'HFSANG'] and f_match(word, values, max_ratio=89)) :
                    if new_line and key==new_line[-1]:
                        pass
                

                    elif key == 'CANCEL':
                        CANCEL = True

                    elif replace_dict.get(key, []):
                        if key[0]=='A' and len([x for x in line if x.isnumeric()])>1:
                            new_line.append(key[1:])
                            #risk += f'Unkown Numbers After All-tax line:{line}'
                        else:
                            new_line.extend(replace_dict.get(key, []))

                    else:
                        new_line.append(key)
                    appended = True
                    break
            
            if not appended and not word.isalpha():
                if new_line and new_line[-1].isalpha() :
                    pass
                elif word in open_brackets:
                    new_line.append(open_brackets[0])
                elif word in close_brackets:
                    new_line.append(close_brackets[0])
                else:
                    new_line.append(word)

        if any(x.isnumeric() or x in text_dict for x in new_line):
            if 'R' in new_line and len(new_lines)==0 and not any(x.isnumeric() for x in new_line):
                continue
            new_lines.append(new_line)
    #TO TAKE SIMPLE LINE IN AND REMOVE MISLEADING SYMBOLS
    # FIXED FORMAT IMP
    # ROVEMENT 
    # print(new_lines)
    for line_num,line in enumerate(new_lines):
        temp_num_in_line = [x for x in line if x.isnumeric()]

        
        if line and ('T' in line[-1] or 'T' in line[0])  and not any(x in tax_list for x in line) or \
            (line_num and new_lines[line_num-1] and new_lines[line_num-1][-1]=='T') :
            temp_num_in_line = [x for x in line if x.isnumeric()]
            if len(temp_num_in_line)==2 and len(temp_num_in_line[1]) == 3 :
                if (line_num and new_lines[line_num-1][-1]=='T'):
                    new_lines[line_num] = [''.join(temp_num_in_line)]
                else:
                    new_lines[line_num] = ['T',''.join(temp_num_in_line)]
            elif len(temp_num_in_line)==1:
                new_lines[line_num] = ['T',temp_num_in_line[0]]
        
        
       
        elif 'T' not in line :
            temp_line = [x for x in line if x in tax_list or x.isnumeric()]

            # n1,n2,n3...tax.r,r ---> n1,n2,n3...tax r \n n1,n2,n3 r
            if len(temp_line)>3 and (temp_line[-3] in tax_list) and \
                (temp_line[-2].isnumeric() and temp_line[-1].isnumeric()) and \
                      all(len(x)==len(temp_line[0]) for x in temp_line[:-3]):
                
                temp_amt = new_lines[line_num].pop()
                new_lines.insert(line_num+1,[*temp_line[:-3],'R',temp_amt])

            # n1,n2,n3...r.tax.r ---> n1,n2,n3...tax r \n n1,n2,n3 r
            elif len(temp_line)>3 and (temp_line[-2] in tax_list) and \
                (temp_line[-1].isnumeric() and temp_line[-3].isnumeric()) and \
                      all(len(x)==len(temp_line[0]) for x in temp_line[:-3]) and len(temp_line[-3])!=len(temp_line[0]):
                
                # self.REJECT = True
                # self.risk(f"Confusing Pattern of num and tax Line:{' '.join(line)}")
                temp_amt = new_lines[line_num].pop(-3)
                new_lines.insert(line_num+1,[*temp_line[:-3],'R',temp_amt])

            # n1,n2,n3...r.r.tax ---> n1,n2,n3...tax r \n n1,n2,n3 r
            # elif len(temp_line)>3 and (temp_line[-1] in tax_list) and \
            #     (temp_line[-2].isnumeric() and temp_line[-3].isnumeric()) and \
            #           all(len(x)==len(temp_line[0]) for x in temp_line[:-2]) and len(temp_line[-2])!=len(temp_line[-3]):
            #     self.REJECT = True
            #     print(temp_line)
            #     self.risk(f"Confusing Pattern of tax and num line:{' '.join(line)}")
                
                
       

        # if 'T' not in line:
        #     temp_line = [x for x in line if x in tax_list or x.isnumeric()]

        #     if len(temp_line)>3 and (temp_line[-3] in tax_list) and \
        #         (temp_line[-2].isnumeric() and temp_line[-1].isnumeric()) and \
        #               all(len(x)==len(temp_line[0]) for x in temp_line[:-3]):
                
        #         temp_amt = new_lines[line_num].pop()
        #         new_lines.insert(line_num+1,[*temp_line[:-3],'R',temp_amt])
        # elif 'T' in line and not any(x in tax_list for x in line):
        #     temp_num_in_line = [x for x in line if x.isnumeric()]
        #     if len(temp_num_in_line)==2 and len(temp_num_in_line[1]) == 3:
        #         new_lines[line_num] = ['T',''.join(temp_num_in_line)]
        
        # 9999-> 9 or 000000-> 0 etc:
        for idx,word in enumerate(line):
            if word.isnumeric() and len(word)>3 and all(x==word[0] for x in word):
                new_lines[line_num][idx] = word[0]
        

        # 12345 sp 2 or 123456 2 sp ----> 12345 mpsp 2
        if any(x in ('SP','DP') for x in line) and not any(x=='MP' for x in line) and \
            len([x for x in line if x.isnumeric()])==2 and any(ismotor(x) for x in line if x.isnumeric()) :
            if 'SP' in line:
                line[line.index('SP')] = 'MPSP'
            elif 'DP' in line:
                line[line.index('DP')] = 'MPDP'

        # [n1,n2,n3..n] \n [R 5] -> [n1,n2,n3..n R 5]
        if all(len(x)==len(temp_num_in_line[0]) for x in temp_num_in_line) and not any(x.isalpha() for x in line[:-1]) \
            and line_num < len(new_lines)-1 and len([x for x in new_lines[line_num+1] if x.isnumeric() ])==1 and 'R' in new_lines[line_num+1] and 'T' not in new_lines[line_num+1] :
            new_lines[line_num].extend(new_lines[line_num+1])
            new_lines[line_num+1] = []

    # SANGAM DETECTION
    for line_num,line in enumerate(new_lines):
        temp_num_in_line = [x for x in line if x.isnumeric()]
        if not any(x in [*tax_list,'T'] for x in line):
            if len(temp_num_in_line)>2:
                if len(temp_num_in_line)==3 and len(temp_num_in_line[0])==3 and len(temp_num_in_line[1]) in (1,2):
                    self.REJECT = True
                    self.risk("High Risk Half Sangam Like Pattern Found")
                    self.data["Sangam"] = True
                elif len(temp_num_in_line)==3 and len(temp_num_in_line[0])==1 and len(temp_num_in_line[1])==3:
                    self.REJECT = True
                    self.data["Sangam"] = True
                    self.risk("High Risk Half Sangam Like Pattern Found")
                elif len(temp_num_in_line)==4 and len(temp_num_in_line[0])==3 and len(temp_num_in_line[1])==1 and len(temp_num_in_line[2])==1 :
                    self.REJECT = True
                    self.data["Sangam"] = True
                    self.risk("High Risk Half Sangam Like Pattern Found")
                elif len(temp_num_in_line) in (4,3) and len(temp_num_in_line[0])==3 and len(temp_num_in_line[1])==2 and len(temp_num_in_line[2])==3 :
                    self.REJECT = True
                    self.data["Sangam"] = True
                    self.risk("High Risk Full Sangam Like Pattern Found")
                elif len(temp_num_in_line) in (4,5) and len(temp_num_in_line[0])==3 and len(temp_num_in_line[1])==1 and len(temp_num_in_line[2])==1 and len(temp_num_in_line[3])==3 :
                    self.REJECT = True
                    self.data["Sangam"] = True
                    self.risk("High Risk Full Sangam Like Pattern Found")
            # if any(len(x)==3 for x in temp_num_in_line[:-1]) and any(len(x)==1 for x in temp_num_in_line[:-1]):
            #     self.REJECT = True
            #     self.risk("High Risk Sangam Like Pattern Found")
    
    self.log(f"before joingin:{new_lines}\n")
    self.before_joining = deepcopy(new_lines)

    #Process Frame Messages
    new_lines = process_frames(new_lines)
    self.log(f"from frames:{new_lines}\n")

    new_lines = symbol_normalize(new_lines)
    can_be_price = [line[-1] for line in [[x for x in line if x.isnumeric()] for line in new_lines] if line]
    can_be_price = list(set([num for num in can_be_price if can_be_price.count(num)>1]))
    lines = []
    line = []
    #joining of all words
    self.log(f"before joingin:{new_lines}\n")
    for line_num,new_line in enumerate(new_lines):
        # print(lines)
        for idx, word in enumerate(new_line):
            # print(word,new_line,line)
            # print(word,line)
            # try:
            #     print(word,any(word in cd for cd in combine_dict.values()) ,lines , any('line[-1]' in cd for cd in combine_dict.values()))
            # except:
            #     import traceback
            #     traceback.print_exc()
            #     pass
            # print(new_line,word,line)
            if line and ( (word =='MP' and line[-1] == 'PANNA') or (word =='PANNA' and line[-1] == 'MP')):
                if word == 'MP':
                    line.pop()
                    line.append('MP')
                continue

            elif line and line[-1] == 'T':
                if word.isnumeric():
                    if any(x.isnumeric() for x in line):
                        if max([int(x) for x in line if x.isnumeric()]) < int(word):
                            line.pop()
                            lines.extend([line,['T',word]])
                            line = []
                            continue
                        elif line[-2].isnumeric()  and int(line[-2]) > int(word):
                            line.pop()
                            num = line.pop()
                            lines.extend([line,['T',num]])
                            line = []
                    else:
                        line.append(word)
                        lines.append(line)
                        line = []
                        continue

            elif line and line[-1] == 'P':
                if word.isnumeric() and len([x for x in new_line if x.isnumeric()])==1 and not any(x in tax_list for x in new_line):
                    line.pop()
                    lines.extend([line,['P',word]])
                    line = []
                    continue
                elif word.isalpha(): 
                    if not any(all(x in join_val for x in ('P',word)) for join_val in combine_dict.values()):
                        line.pop()
                        if len(line)>1 and line[-1].isnumeric() and not(any(x.isnumeric() for x in new_line[idx:])):
                            num = line.pop()
                            lines.extend([line,['P',num]])
                        elif line and line[-1].isnumeric() and len(line)==1:
                            line.insert(0,'P')
                            line.append(line)
                        elif word == 'R':
                            line.append('P')
                            continue

                        elif word in tax_list:
                            line.append(word)
                            continue
                        else:
                            lines.append(line)

                        line = []
                        continue
                    else:
                        line.pop()
                        line.append(word)
                        continue
                # elif word.isnumeric() and idx==0 :
                #     if any(x.isnumeric() for x in line):
                #         line.pop()
                #         lines.append(line)
                #     line = []
                #     line.append(word)
                #     continue
                elif word.isnumeric() and idx==0:
                    if any(x.isnumeric() for x in line):
                        if 'R' == line[-2]:
                            line.pop()
                        lines.append(line)
                    line = []
                    line.append(word)
                    # print(f'{lines}\n,{line}\n,{new_line}')
                    continue

            elif line and line[-1] == 'R' and word.isnumeric():
                line.append(word)
                if len(new_lines)-1>line_num and len(new_lines[line_num+1]) == 1 and new_lines[line_num+1][0] in tax_list:
                    if len(new_lines)-1>line_num+1 and new_lines[line_num+2] and check_num(new_lines[line_num+1][0],new_lines[line_num+2][0]):
                        lines.append(line) 
                        line = []
                        continue
                    line[-2] = new_lines[line_num+1][0]
                    new_lines.pop(line_num+1)
                    lines.append(line)
                    continue
                elif idx < len(new_line)-1 and new_line[idx+1] in tax_list:
                    continue

                lines.append(line)
                line = []
                continue

            elif len([x for x in line if x.isnumeric()])>1 and line[0] in [*tax_list,'MP'] and  (word in [*tax_list,'MP']):
                lines.append(line)
                line = []
                line.append(word)
                continue

            elif len([x for x in line if x.isnumeric()])>1 and word in [*tax_list,'MP'] and not any(x.isnumeric() for x in new_line[idx:]):
                if len(new_line)-1>idx and any(new_line[idx+1] in cd for cd in combine_dict.values()) and any(word in cd for cd in combine_dict.values()):
                    line.append(word)
                    continue
                line.append(word)
                # print(line)
                lines.append(line)
                line = []
                continue
            
            elif line and all(x.isnumeric() for x in line) and new_line[0] in tax_list and len([x for x in new_line if x.isnumeric()]) ==1:
                if word.isnumeric():
                    line.append(word)
                    lines.append(line)
                    line = []
                elif word in tax_list:
                    line.append(word)
                continue 


            elif line and line[0] in tax_list and line[-1].isnumeric() and word.isnumeric():
                if len(word) == len(line[-1]):
                    line.append(word)
                    continue
                else:
                    line.append(word)
                    lines.append(line)
                    line = []
                    continue



            elif line and line[-1].isnumeric() and word.isnumeric() and all(x.isnumeric() for x in line):
                if len(line)>1 and len([x for x in new_line if x.isnumeric()])==1 and len(new_lines)>line_num+1 and len([x for x in new_lines[line_num+1] if x.isnumeric()])==1:
                    if line_num and len([x for x in new_lines[line_num-1] if x.isnumeric()])!=1:
                        lines.append(line)
                        line = []
                    line.append(word)
                    continue
                elif idx==len(new_line)-1 and word in can_be_price:
                    if len(new_lines)-1>line_num and len(new_lines[line_num+1][0])==len(word) and len(new_lines[line_num+1])>2 and new_lines[line_num+1][-2]=='R':
                        line.append(word)
                        continue
                    line.extend(['R',word])
                    lines.append(line)
                    line = []
                    continue 
                elif len(line[-1]) == len(word):
                    line.append(word)
                    continue
                elif idx == 0:
                    lines.append(line)
                    line = []
                    line.append(word)
                    continue 
                elif any(x in tax_list for x in new_line[idx:]):
                    line.append(word)
                    continue
                else:
                    line.extend(['R',word])
                    lines.append(line)
                    line = []
                    continue    




            elif idx == 0 and line and line[-1] in tax_list:
                if word.isalpha():
                    if word == 'R':
                        continue
                    if word in tax_list and not all(x in combine_dict.values() for x in (word,line[-1]) ):
                        lines.append(line)
                        line = []

                if word.isnumeric():
                    if len([x for x in new_line if x.isnumeric()])>1:
                        if len([x for x in new_line if x in tax_list])==1 and line[-1] in new_line:
                            pass
                        elif len(line) ==1:
                            pass
                        else:
                            lines.append(line)
                            line = []

            elif idx==0 and  word in tax_list and line and line[-1].isnumeric() and len([x for x in line if  x.isnumeric()])!=1:
                lines.append(line)
                line = []

            elif idx!=0 and line and line[-1] in tax_list:
                if word.isalpha():
                    if word in ['P','R']:
                        continue
                    line.append(word)
                    continue
                elif word.isnumeric():
                    if any(x in tax_list for x in new_line[idx:]):
                        line.append(word)
                        continue

                    elif any(x.isnumeric() for x in line):
                        line.append(word)
                        lines.append(line)
                        line = []
                        continue
                else:
                    continue
                
            
            elif line and  word.isalpha() and line[-1].isalpha()  and idx == 0 and any(word in cd for cd in combine_dict.values()) and any(line[-1] in cd for cd in combine_dict.values()):
                pass



            elif line and idx == 0 and not any(x in tax_list for x in line):
                lines.append(line)
                line = []

            elif idx==len(new_line)-1 and line:

                if line_num and len([x for x in new_lines[line_num-1] if x.isnumeric()]) != 1 and len([x for x in new_line if x.isnumeric()]) == 1 :
                    line.append('R')
                    


                # elif any(x in tax_list for x in line[:2]):
                #     if line_num>0 and any(x in tax_list for x in new_lines[line_num-1]):
                        
                #     elif len([x for x in new_lines[line_num-1] if x.isnumeric()]) != len([x for x in new_line if x.isnumeric() ]):
                #         lines.append([*line,word])
                #         line = []
                #         continue



            # else:
            #     print("else ", word,new_line)

            # NONE SYMBOL BETWEEN TWO WORDS
            if word.isalpha() and (not line or line[-1] != word):
                line.append(word)
            elif word.isnumeric() or (line and line[-1].isnumeric()):
                line.append(word)
            else:
                line.append(word)
    if line:
        lines.append(line)
    
    for i,new_line in enumerate(lines):
        if any(x in ['P','T'] for x in new_line):
            lines[i] = [x for x in new_line if x!='R']
        if len(new_line)>2 and new_line[-2] == 'P' and new_line[-1].isnumeric() :
            lines[i] = new_line[:-2]
            lines.insert(i+1, new_line[-2:])



    #joining combinations from combinatin dict
    # self.log(lines)
    for i in range(3):      
        for line_num, line in enumerate(lines):
            for key, values in combine_dict.items():
                indices = [line.index(val) for val in values if val in line]
                indices.sort()
                if len(indices) == len(values) and all(abs(b - a) == 1 for a, b in zip(indices, indices[1:])):
                    lines[line_num][indices[0]] = key
                    for idx in sorted(indices[1:], reverse=True):
                        line.pop(idx)
    # return lines,CANCEL,risk
    return lines,CANCEL
                        
                
