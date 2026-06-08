from ..constants.number import isprice
from ..constants.text import repeated_no_price_sym,rs_sym_type,flags,tax_list
import copy

def clean_symbol_typos(lines:list)->list:
    new_lines = []
    for line in lines:
        new_line = []
        for idx,word in enumerate(line):
            if not word.isalnum():

                if len(line)-1>idx and not line[idx+1].isalnum() and line[idx+1]!=word :
                # and not any(word in ls for ls in ['(',')']) :
                    # if idx>0 and not line[idx-1].isnalnum() and line[idx-1]!=word:
                    #     if line[idx-1] == line[idx+1]:
                    new_line.append(line[idx+1])
                else:
                    new_line.append(word)
            else:
                new_line.append(word)
        if new_line:
            new_lines.append(new_line)
    return new_lines


def get_sym_dict_list(line:list)->tuple[dict,list]:
    sym_dict = {}
    sym_idx_list = []
    idx_list = []
    # print("line isn",line,any(word in ('(',')') for word in line))
    for idx,word in enumerate(line):
        if not word.isalnum():
            if not (word in ('(',')')):
                if word in sym_dict.keys():
                    sym_dict[word].append(idx)
                else:
                    sym_dict[word] = [idx]
                
                if idx_list:
                    if idx-idx_list[-1]==1:
                        idx_list.append(idx)
                        continue
                    else:
                        sym_idx_list.append(idx_list)
                        idx_list = []
                idx_list.append(idx)
    if idx_list:
        sym_idx_list.append(idx_list)

        

    return sym_dict,sym_idx_list

def solve_repeated(line:list, lines = [])->list:
    # print(f"line came for {line}")
    num_in_line = [x for x in line if x.isnumeric()]
    line_without_sym = [x for x in line if x.isalnum()]
    sym_dict,sym_idx_list = get_sym_dict_list(line)
    linear_line = [x for i,x in enumerate(line) if ((i>0 and x!=line[i-1]) or i==0)]#no repeat
    linear_sym_dict,linear_sym_idx_list = get_sym_dict_list(linear_line)

    # if any(x == 'R' for x in line_without_sym) or len(line)>1 and line[-2] in line_without_sym:
    # if any(x == 'R' for x in line_without_sym) or (len(line)>1 and line[-2] in line_without_sym):
    #     return line_without_sym        
    if len(num_in_line)==1 and not any(x in [*tax_list,'T','P'] for x in line):
        return ['R',*num_in_line]
    
    
    elif (not any(x in [*tax_list,'T'] for x in line)) and num_in_line and \
            all(len(x)==len(num_in_line[0]) for x in num_in_line[:-1]) and len(num_in_line[0])!=len(num_in_line[-1]):
        num_in_line.insert(-1,'R')
        return num_in_line
    
    elif len(line_without_sym)>2 and line_without_sym[-2] in tax_list and line[-1].isnumeric():
        # print("This",line_without_sym)
        return line_without_sym
    
    elif any(x in flags for x in line ):
        return line_without_sym

    elif lines and len([x for x in lines[0] if x.isnumeric()])==1 and ('R' in lines[0] or 'P' in lines[0]) and not ('T' in lines[0]):
        return line_without_sym    
    


    elif len(sym_dict.keys()) == 1 and not any(x in tax_list for x in line):
        if all(len(x)==len(sym_idx_list[0])for x in sym_idx_list):
            if len(sym_idx_list) ==1 and (len(sym_idx_list[0])>1 or [sym_dict.keys()][0] in rs_sym_type):
                num_in_line.insert(-1,'R')
                return num_in_line
            else:
                return num_in_line
            
        elif all(len(sym_idx_list[-1])!=len(x) for x in sym_idx_list[:-1]):
            if lines:
                num_nxt_line = [ x for x in lines[0] if x.isnumeric()]
                if num_nxt_line and  len(num_nxt_line[0]) == len(num_in_line[-1]) and len(num_in_line)==len(num_nxt_line):

                    
                    return num_in_line
            num_in_line.insert(-1,'R')
            return num_in_line
    
    elif any(x in tax_list for x in line) :
        return line_without_sym
    
    elif linear_sym_idx_list and len(linear_sym_dict.get(linear_line[linear_sym_idx_list[-1][-1]],[])) == 1:
        num_in_line.insert(-1,'R')
        return num_in_line
    
    if sym_idx_list and all(len(x)==len(sym_idx_list[0])for x in sym_idx_list[:-1]) and len(sym_dict.keys())==1:
        if all(len(x)==len(sym_idx_list[0])for x in sym_idx_list[:-1]):
            num_in_line.insert(-1,'R')
            return num_in_line
    else:
        last_sym = ''
        temp = []
        for i,x in enumerate(line):
            if x.isalnum():
                if x.isalpha():
                    if temp and temp[-1] == x:
                        continue
                elif x.isnumeric():
                    if temp and temp[-1]=='R':
                        temp.append(x)
                        continue    
                temp.append(x)
            else:
                if last_sym and last_sym!=x and temp and temp[-1].isnumeric():
                    temp.append('R')
                else:
                    last_sym = x
        return temp


    
def symbol_normalize(lines:list)->list:
    lines = clean_symbol_typos(lines)
    len_of_lines = len(lines)-1
    can_be_price = [line[-1] for line in [[x for x in line if x.isnumeric()] for line in lines] if line]
    possible_prices = list(set([num for num in can_be_price if can_be_price.count(num)>1]))
    # possible_prices = set([line[-1] for line in lines if line[-1].isnumeric() and isprice(line[-1])])
    new_lines = []
    for line_num,line in enumerate(lines):
        sym_dict,sym_idx_list = get_sym_dict_list(line)
        # print(line,sym_dict)
        sym_len_dict = {len(x):len([y for y in sym_idx_list if len(y)==len(x)]) for x in sym_idx_list}
        nums_in_line = [x for x in line if x.isnumeric()]
        #print("nums in line is ",nums_in_line,line)
        if not any(x.isalpha() for x in line):
            if len(nums_in_line)==1:
                if line_num < len_of_lines:
                    if line_num and new_lines and len([x for x in new_lines[-1] if x.isnumeric()])==2 and len(new_lines[-1][0])==len(nums_in_line[0]):
                        if any(tax in new_lines[-1] for tax in tax_list):
                            new_lines.append([nums_in_line[0],''.join([x for x in new_lines[-1] if x in tax_list]),[x for x in new_lines[-1] if x.isnumeric()][-1]])
                        else:
                            new_lines.append([nums_in_line[0],'R',[x for x in new_lines[-1] if x.isnumeric()][-1]])
                        continue
                    elif len([x for x in lines[line_num+1] if x.isnumeric()])==2:
                        new_lines.append(nums_in_line)
                        continue
                    # elif len([x for x in lines[line_num+1] if x.isnumeric()])==1 and (len([x for x in lines[line_num-1] if x.isnumeric()][0])==len(nums_in_line[0]) ):
                    #     new_lines.append(nums_in_line)
                    #     continue
                    elif len([x for x in lines[line_num+1] if x.isnumeric()])==1 and not any(x.isalpha() for x in lines[line_num+1]):
                        new_lines.append(nums_in_line)
                        continue
                
                new_lines.append(['R',nums_in_line[0]])

            elif len(nums_in_line)==2:
                if sym_dict.keys() and (not(list(sym_dict.keys())[0] in repeated_no_price_sym) and ( (list(sym_dict.keys())[0] in rs_sym_type)) or (len(sym_idx_list)>1)):
                    new_lines.append([nums_in_line[0],'R',nums_in_line[1]])
                    continue

                elif line_num < len_of_lines:
                    temp_line_num = copy.deepcopy(line_num)
                    while(len([x for x in lines[temp_line_num] if x.isnumeric()])==2):
                        if temp_line_num < len_of_lines:
                            # temp_line = lines[line_num+1]
                            temp_line_num +=1
                            if any(x.isalpha() for x in lines[temp_line_num]):
                                break
                        else:
                            break

                    if line_num and  len([x for x in lines[line_num-1] if x.isnumeric()])==1:
                        new_lines.append([nums_in_line[0],'R',nums_in_line[1]])
                        continue
                    elif len([x for x in lines[temp_line_num] if x.isnumeric()])==1:
                        new_lines.append([nums_in_line[0],nums_in_line[1]])
                        continue
                    elif len([x for x in lines[temp_line_num] if x.isnumeric()])==2 and isprice(nums_in_line[1]):
                        new_lines.append([nums_in_line[0],'R',nums_in_line[1]])
                        continue
                    else:
                        if nums_in_line[1] not in possible_prices:
                            new_lines.append([nums_in_line[0],nums_in_line[1]])
                            continue
                        elif len([x for x in lines[line_num+1] if x.isnumeric()])==2:
                            if len(nums_in_line[0]) == len(nums_in_line[1]):
                                if nums_in_line[1] in possible_prices:
                                    new_lines.append([nums_in_line[0],'R',nums_in_line[1]])
                                else:
                                    new_lines.append(line)
                            else:
                                new_lines.append([nums_in_line[0],'R',nums_in_line[1]])
                            # new_lines.append(line)
                            continue
                        new_lines.append([nums_in_line[0],'R',nums_in_line[1]])
                        continue
                else:
                    new_lines.append([nums_in_line[0],'R',nums_in_line[1]])
                    continue


            elif len(nums_in_line)>2 :
                # print(sym_dict)
                # print("line in here",line)

                if len(nums_in_line)>3 and len(sym_len_dict.keys())==2 and \
                        (any(len(x)!=len(sym_idx_list[i+1]) and line[x[-1]] != line[sym_idx_list[i+1][-1]] for i,x in enumerate(sym_idx_list[:-1]) or \
                             any(len(x)>1 and line[x[-1]+1].isnumeric() and line[x[-1]+2].isnumeric() for x in sym_idx_list))):
                    
                    last_idx = 0
                    for i,x in enumerate(sym_idx_list[:-1]):
                        if (len(x)>1 or line[x[0]] in rs_sym_type) and \
                              ((i>0 and len(sym_idx_list[i-1])>len(x)) or  
                               (i<(len(sym_idx_list)-1) and len(sym_idx_list[i+1])<len(x) ) and 
                                any(x.isnumeric() for x in line[x[-1]+2:])  ):
                            temp = solve_repeated(line[last_idx:x[-1]+2])
                            last_idx = x[-1]+2
                            new_lines.append(temp)
                        elif (len(x)>1 or line[x[0]] in rs_sym_type) and \
                            ((i>0 and len(sym_idx_list[i-1])>len(x)) or
                             (i<(len(sym_idx_list)-1) and line[x[-1]+1].isnumeric() and line[x[-1]+2].isnumeric() )
                              and any(x.isnumeric() for x in line[x[-1]+2:]) ):
                            temp = solve_repeated(line[last_idx:x[-1]+2])
                            last_idx = x[-1]+2
                            new_lines.append(temp)
                    if last_idx < len(line)-1:
                    # sym_idx_list[-1][-1]:
                        temp = solve_repeated(line[last_idx:],lines[line_num+1:])
                        # print(line[last_idx:])        
                        if len([x for x in temp if x.isnumeric()]) == 1:
                            new_lines[-1].extend(temp)
                        else:
                            new_lines.append(temp)
                        continue
                    # print("hiii",new_lines)
                else:
                    #print("going for solve",line)
                    temp = solve_repeated(line,lines[line_num+1:])
                    #print("after  solve",temp)
                    new_lines.append(temp)
            
        else:
            # print("her",line)
            new_lines.append(solve_repeated(line))
    lines = []
    for line_num,line in enumerate(new_lines):

        if line and line[-1] == 'R' and any(x for x in line if x.isnumeric()):
            line.pop()

            if len(line)>1 and line[-2] in ['T','P']:
                pass
            else:
                line.insert(-1,'R')
        elif line and line[-1] == 'T' and any(x for x in line if x.isnumeric()):
            if line_num < len(new_lines)-1:
                num_curr = [x for x in line if x.isnumeric()]
                num_for = [x for x in new_lines[line_num+1] if x.isnumeric()]
                if num_curr[-1]>num_for[-1]:
                    line.pop()
                    line.insert(-1,'T')
                elif num_curr[-1]<num_for[-1]:
                    line.pop()
                    new_lines[line_num+1].insert(0,'T')
            else:
                line.pop()
                num_curr = [x for x in line if x.isnumeric()]
                if len(num_curr) == 1:
                    line.insert(0,'T')
                elif 'R' in line and [x for x in line if x.isnumeric() or x== 'R'][-2]=='R':
                    line.insert(-1,'T')
                elif all(len(num_curr[-1])!=len(x) for x in num_curr[:-1]):
                    line.insert(-1,'T')
        if line:
            lines.append(line)
    


    return lines



                




    
    


