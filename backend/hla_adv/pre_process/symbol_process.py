from ..constants.number import isprice,ismotor,main_num_list,isprice
from ..constants.text import flags,tax_list,rs_sym_type,repeated_no_price_sym
import copy
from itertools import groupby
from time import sleep


def solve_bracket(lines:list)->list:
    # print("solve brakcet Lines::",lines)
    open_brackets = '('
    close_brackets = ')'
    brackets = ['(',')']
    temp_lines = copy.deepcopy(lines)
    final_lines = []

    bracket_open = False
    num_in_bracket = []
    temp = []
    line_num = 0
    sym_dict = {key:[i for i,x in enumerate(temp_lines[0]) if x==key] for key in temp_lines[0] if(key in brackets)}
    # print("BEFORE-----",lines)
    # one line bracket for invert
    if len(sym_dict.keys())==2 and len(sym_dict[open_brackets])==len(sym_dict[close_brackets]):
        len_number_in_line = len([x for x in temp_lines[0] if(x.isnumeric())])
        number_in_line = [x for x in temp_lines[0] if(x.isnumeric())]
        for idx,word in enumerate(temp_lines[0]):
            if bracket_open:
                if word.isnumeric():
                    num_in_bracket.append(word)
                    len_number_in_line -= 1
                    continue

                if word.isalpha() or word==open_brackets:
                    if word.isalpha():
                        num_in_bracket.append(word)
                    temp.extend(num_in_bracket)
                    num_in_bracket = []
                    continue

                if word not in brackets:
                    num_in_bracket.append(word)
                    continue
                if word == close_brackets and len(sym_dict[open_brackets])==1:
                    if len(num_in_bracket) == 1:
                        if len_number_in_line and len(num_in_bracket)==1 and (num_in_bracket[0] in [number_in_line[0],number_in_line[-1]]):
                            if not all( x.isalpha() for x in temp_lines[0]):
                                temp.extend(temp_lines[0][idx+1:])
                                temp.extend(['R',num_in_bracket[0]])
                                num_in_bracket = []
                                break
                            elif len([x for x in temp_lines[0] if(x.isalpha())])==1 and temp_lines[0][-1] in tax_list:
                                temp.append(num_in_bracket[0])
                                num_in_bracket = []
                                break
                        temp.append(num_in_bracket[0])
                    num_in_bracket = []
                    bracket_open = False
            elif word == open_brackets:
                bracket_open = True
            elif word == close_brackets:
                bracket_open= False
            else:
                temp.append(word)
                if word.isnumeric():
                    len_number_in_line -= 1
        temp_lines.pop(0)

    # multiline msg check
    elif len(sym_dict.keys())==1 and any(x == close_brackets for x in [word for words in temp_lines for word in words]):
        # print("2nd")
        to_close = False
        while temp_lines:
            if temp_lines[0]:
                word = temp_lines[0].pop(0)
                if bracket_open:
                    if word.isnumeric():
                        num_in_bracket.append(word)
                        continue

                    if word.isalpha() or word in [open_brackets,close_brackets]:
                        if word.isalpha():
                            num_in_bracket.append(word)
                            temp.append(word)
                        if word == close_brackets:
                            bracket_open = False
                            to_close = True
                        temp.extend(num_in_bracket)
                        num_in_bracket = []
                        continue

                    if word not in [open_brackets,close_brackets]:
                        num_in_bracket.append(word)
                        continue  

                elif word == open_brackets:
                    bracket_open = True
                elif word == close_brackets:
                    bracket_open = False
                else:
                    temp.append(word)
            else:
                temp_lines.pop(0)
                line_num +=1
                if temp_lines[0] and any(x == open_brackets for x in temp_lines[0]):
                    temp.extend(num_in_bracket)
                    final_lines.append(temp)
                    temp = []
                    num_in_bracket = []
                if not to_close:
                    continue
                break
        line_num -=1
        # print(temp,num_in_bracket,'\n\n')
    # line_num +=1
    if num_in_bracket:
        temp.extend(num_in_bracket)
    if temp:
        final_lines.append(temp)
    # print("temp==",temp)
    temp_lines = []

    for linenum in range(line_num+1,len(lines)):
        temp_lines.append(lines[linenum])
    final_lines.extend(temp_lines)
    # print("left====",final_lines,f"\n{line_num}\n\n")
    # print("BEFORE-----",final_lines)
    return final_lines

def solve_symbol(line:list)-> list:

    sym_dict = {key:[idx for idx,sym in enumerate(line) if (sym==key)] for key in line if(not key.isalnum())}
    sym_ind_list = [idx for row in sym_dict.values() for idx in row]#all index of sym
    re_sym_ind = [sym_ind_list[i+1] for i in range(len(sym_ind_list)-1) if ((sym_ind_list[i+1]-sym_ind_list[i] == 1 ) and (line[sym_ind_list[i]] == line[sym_ind_list[i+1]]))]#repeated sym only like 1,2,3-->2,3
    re_sym_ind_list = [[x[1] for x in g] for k,g in groupby(enumerate(re_sym_ind), lambda x: abs(x[0] - x[1])) ]#same sym repeated index in a list
    # re_sym_ind_list = [[x for x in val[1:]] for val in sym_dict.values() if(len(val)>1)]
    numbers_present_inside = [x for x in line if x.isnumeric()]
    indx_to_dlt = [] 
    # print("resym ind",re_sym_ind,re_sym_ind_list)
   
    if re_sym_ind:
        if((not (all(len(sl) == len(re_sym_ind_list[0]) for sl in re_sym_ind_list)) and (len(re_sym_ind_list)>1)) and (line[re_sym_ind_list[-1][0]-1] not in repeated_no_price_sym)):
            line[re_sym_ind_list[-1][0]-1] = "!"
        elif(len(re_sym_ind_list) ==1 and (line[re_sym_ind[-1]] in rs_sym_type)):
            line[re_sym_ind_list[-1][0]-1] = "!"
        elif(len(re_sym_ind_list) ==1 and (len(numbers_present_inside)==2) and (line[re_sym_ind[-1]] in ['/'])):
            line[re_sym_ind_list[-1][0]] = "!"
        indx_to_dlt.extend(re_sym_ind)

    if(len([k for k in sym_dict.keys()]) ==2) and not any(x=='R' for x in line) :
        k = [x for x in sym_dict.keys()]
        if(not(all(x in rs_sym_type for x in k))):
            l1 = len(sym_dict[k[0]])
            l2 = len(sym_dict[k[1]])
            if(l1!=l2):
                if(l1 ==1 and ((len([x for x in line[line.index(k[0]):] if(x.isnumeric())])) == 1)):
                    line[line.index(k[0])] = 'R'
                elif(l2 == 1 and ((len([x for x in line[line.index(k[1]):] if(x.isnumeric())])) == 1)):
                    line[line.index(k[1])] = 'R'

    final_line = [x for i,x in enumerate(line) if i not in indx_to_dlt]
    return final_line,sym_dict
    
def sym_clean(lines:list,sym_dict_list:list) -> list:
    new_lines = []
    for line_num,line in enumerate(lines):
        num_list = []

        def append():
            if num_list and (num_list[-1] != 'R'):
                num_list.append('R')

        sym_dict = sym_dict_list[line_num]

        for idx,raw in enumerate(line):
            if raw.isnumeric():
                num_list.append(raw)
                continue

            if raw.isalpha():
                if num_list and num_list[-1]==raw:
                    continue
                if raw == 'R':
                    append()
                    continue
                if raw in tax_list or flags:
                    num_list.append(raw)
                    continue

            t = [x for i,x in enumerate(line) if(x.isnumeric() or i == idx)]

            if((raw == '=') and ((len(t)>2) and t[-2] == '=') and (len(sym_dict['=']) == 1)):
                if((len(lines)-1) > line_num):
                    next_line_nums = [x for x in lines[line_num+1] if x.isnumeric()]
                    if((next_line_nums and (len(next_line_nums[0])==len(t[-1])))):
                        if((lines[line_num+1].count('='))==1 and ((len(t)==3 and isprice(t[2])) or len(t)>3)):
                            append()
                    else:
                        append()

            elif((raw == '@') and ((len(t)>2) and t[-2] == '@') and (len(sym_dict['@']) == 1)):
                append()

            elif(t.index(raw) == (len(t)-2) and (len(t)>1) and t[-1].isnumeric()):
                if((raw == '!') and (len(sym_dict.keys())>1)):
                    append()
                elif((raw == '!') and (len(sym_dict.keys())==1) and (t.index(raw) == (len(t)-2)) and ((len(t)>2) and (len(sym_dict[list(sym_dict.keys())[0]])>0))):
                    if((t[-1].isnumeric()) and (isprice(t[-1]))):
                        append()
                    if((t[-1].isnumeric()) and (len(t)==3) ):
                        append()
                elif((raw in rs_sym_type or raw ==')') and isprice(t[-1]) and(len(sym_dict[raw]) == 1)):
                    append()
                else:
                    continue

            elif(raw in rs_sym_type ):
                t_i = t.index(raw)
                l_i = len(t)-1
                # left-right and left
                if( t_i != 0 and ((l_i >= t_i))):
                    num_list.insert(-1,'R')

        if num_list:
            new_lines.append(num_list)
    return new_lines
                



def confine_symbol(in_lines:list)-> list:
    new_lines = []
    open_brackets = '('
    lines = copy.deepcopy(in_lines)
    sym_dict_list = []
    
    while lines:
        # print("line is ",lines[0])
        if any(x==open_brackets for x in lines[0]):
            lines = solve_bracket(lines)
        # print(lines[0],'\n')
        lines[0],sym_dict = solve_symbol(lines[0])
        # print("after symbol -------",len(lines))
        sym_dict_list.append(sym_dict)
        new_lines.append(lines.pop(0))
        # print("after-->",new_lines[-1])
        # input("\n\n conti-----\n\n")
    new_lines = sym_clean(new_lines,sym_dict_list)
    lines = []

    for line in new_lines:
        if len([x for x in line if x in tax_list])==1 and 'R' in line:
            tax_in_here = [x for x in line if x in tax_list]
            line.pop(line.index(tax_in_here[0]))
            line[line.index('R')] = tax_in_here[0]
        lines.append(line)
            

    # print("final===>",new_lines,'\n')
    return new_lines

   