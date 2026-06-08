from .constant import fm_jodis,fm_pannas,tax_len_dict,tax_num_dict,all_tax_list,main_num_list,mpsp_list,mpdp_list
from prettytable import PrettyTable
from datetime import datetime
from fuzzywuzzy import fuzz
from copy import deepcopy
import logging
import time
import re


logger = logging.getLogger()
logger.setLevel(logging.INFO)
# logging.basicConfig(level=logging.DEBUG)
log = logger.debug
##########################################################################################
    #                  				CONSTANTS
##########################################################################################

reject_msg = ['half','full','sangam','sangm','half sangam','halfsangam','f/s','h/s','hs','fs','hs','fs','hS','fs','हॉफ','संगम']
rs_type = ['.rs','.RS','.Rs','.rS','.R','.r','.rr','rs','RS','Rs','rss','rS','R','r','rr','rrr','ru','at','AT','रु','र','₹','₹','रुपया']
open_brackets = ['(','{','[','<']
close_brackets = [')','}',']','>']
repeated_no_price_sym = ['"','+']
rs_sym_type = ['/-','💸','💵','💴','💶','💷','💰','🤑','🏧','💳']
premultiplier_type = ['ALL','AAL','SABHI','EVERY','EACH','ICH','INTO','INTU','PER','सर्व','से']
cancel_msg = ["CANCEL","CANCELED","कैन्सल्","कैन्सल","कैंसिल","कंस"]
total_type = ['total','टोटल','vepar','tt','tot','t','tota','totel','ttl','to','टो','ट','totalamount','toyal','toal','totally','totil','totli']
tax_list = ['fm', 'fmily','family', 'fhmily', 'fam', 'fhamly', 'femeli', 'femliy','femely','फॅमिली' ,'fan','fmv','fml',
    'tp','tip','teen','tin','triple','tripal','sp','single','singal', 'dp','double','doble','cp','fmly','Fmly','comsp','commsp','comdp','commdp','mpsp','motor sp','spmp','mpdp','motor dp','dpmp']
tax_list_fun = { 'fm': ['fm', 'fmily','family', 'fhmily', 'fam', 'fhamly', 'femeli', 'femliy','femely','फॅमिली','fan','fmv','fml','fmly','Fmly'],
    # fm_list
    'tp':['tp','tip','teen','tin','triple','tripal'],
    # sp_dp_list 
    'cp':['cp'],
    # cp_list
    'sp':['sp','single','singal'],
    # sp_list
    'dp':['dp','double','doble'],
    # dp_list
    'comsp':['comsp','commsp'],
    #compsp
    'comdp':['comdp','commdp'],
    #comdp
    'mpsp' : ['mpsp','motor sp','spmp'],
    'mpdp' : ['mpdp','motor dp','dpmp']
}
word_seprators = ["all","n8","ni8","टोटल","ki","h/s","f/s","comsp","commsp","comdp","commdp",'mpsp','motor sp','spmp','mpdp','motor dp','dpmp',"sp","dp","tp"]

##########################################################################################
    #                  				IN-BUILT FUNCTIONAlity
##########################################################################################
tax_msg_flag = False
def convert_tax_to_act_msg(tax:str,msg:list):
    global tax_msg_flag
    tax_msg_flag = True
    amt = msg.pop()
    local_result = []
    # for sp dp cp tp comsp comdp
    for tax_name in tax_num_dict.keys():
        if(tax == tax_name):
            if(not(all(len(x)== tax_len_dict[tax][0] for x in msg))):
                # risk += ''
                return []
            for x in msg:
                temp_local_result = deepcopy(tax_num_dict[tax_name][x])
                temp_local_result.append(amt)
                local_result.append(temp_local_result)
            return local_result
        
    if(tax in ('mpsp','mpdp')):
        store_list = mpdp_list
        if(tax == 'mpsp'):
            store_list = mpsp_list

        for x in msg:
            temp_local_result = list()
            while(len(x)>3):
                temp = [num for num in store_list if(all(digit in x for digit in num))]
                temp_local_result.extend(temp)
                x = ''.join(x[1:])
            temp_local_result = list(set(temp_local_result))
            temp_local_result.append(amt)
            local_result.append(temp_local_result)
        return local_result

    # for fm
    if(tax == 'fm'):
        if(not(all(len(x)==len(msg[0]) for x in msg))):
            #risk += ''
            return []
        for x in msg:
            if(len(x)==3):
                for sub in fm_pannas: 
                    if x in sub:
                        copy_local_fm = deepcopy(sub)
                        copy_local_fm.append(amt)
                        local_result.append(copy_local_fm)
            elif(len(x)==2):
                for sub in fm_jodis: 
                    if x in sub:
                        copy_local_fm = deepcopy(sub)
                        copy_local_fm.append(amt)
                        local_result.append(copy_local_fm)
            else:
                #risk += ''
                return []
        return local_result
    else:
        # risk += ''
        return []
    

def left_join(arr:list,total:int):
    L = False
    R = False
    
    if(len(arr)>1):
        new_arr = deepcopy(arr)
        if(len(new_arr[0][-1]) == len(new_arr[0][-2])):
            new_arr[0].extend(new_arr[1])
            new_arr.pop(1)
            new_total = int(0)
            for sl in new_arr:
                if(len(sl)!=len(set(sl))):
                    return False
                new_total += int(len(sl[:-1]) * int(sl[-1]))
            if((total==new_total)):
                return new_arr
            L = left_join(new_arr,(total))
        if(L):
            return L
    
    if(len(arr)>2):
        new_arr = deepcopy(arr)
        if(len(new_arr[0][-1]) == len(new_arr[0][-2])):
            new_arr[0].append(new_arr[1][0])
            new_arr[1].pop(0)
            new_total = int(0)
            for sl in new_arr:
                if(len(sl)!=len(set(sl))):
                    return False
                if(sl):
                    new_total += int(len(sl[:-1]) * int(sl[-1]))
                else:
                    return False
            if((total==new_total)):
                return new_arr
            L = left_join(new_arr,(total))
        if(L):
            return L

        
    # right_join
    for i in range(1,len(arr)):
        if(len(arr)>(i+1)):
            new_arr = deepcopy(arr)
            if(len(new_arr[i][-1]) == len(new_arr[i][-2])):
                new_arr[i].extend(new_arr[i+1])
                new_arr.pop(i+1)
                new_total = int(0)
                for sl in new_arr:
                    if(len(sl)!=len(set(sl))):
                        return False
                    new_total += int(len(sl[:-1]) * int(sl[-1]))
                if((total==new_total)):
                    return new_arr
                R = left_join(new_arr,(total))
            if(R):
                return R
        else:
            break
    return False
    

def slidetrack(temp:list,temp_total:int):
    arr = list()
    total = deepcopy(temp_total)

    for i,sl in enumerate(temp):
        if(sl[:-1] in all_tax_list):
            t = len(sl[:-1])*int(sl[-1])
            total -= t
        else:
            arr.append(sl)

    executed = list()
    L = False
    for i in range(len(arr)):
        L = left_join(arr,total)
        if(L):
            break
        else:
            total -= int(len(arr[0][:-1]) * int(arr[0][-1]))
            executed.append(arr.pop(0))
    if(L):
        executed.extend(L)
        return executed
    else:
        return False


# for string matching
def f_match(input_str, str_list,max_ratio = 80):
    # max_ratio = 80
    matched_str = False
    for str_item in str_list:
        ratio = fuzz.ratio(input_str, str_item)
        if ratio > max_ratio:
            max_ratio = ratio
            matched_str = True
    return matched_str
    
# price calculation always a multiple of 5 or in range 1-9 and if 3 digit number then have 0 in the end
def is_price(num):
    try:
        if(str(num)[0] == '0'):
            return False
        if(num == 0):
            return False
        num = int(num)
        if(num % 5 == 0):
            if(len(str(num))>2):
                if(all(n==str(num)[0] for n in str(num))):
                    return False
                elif(int(str(num)[0])>int(str(num)[1]) and (int(str(num)[1] !=0))):
                    return True
                elif((int(str(num)[-1])!=0) and int(str(num)[-2])>int(str(num)[-1])):
                    return True
                elif(num%25 == 0):
                    return True
                elif((str(num)[-1] == '0') and ((int(str(num)[-2])%2 == 0) or (int(str(num)[-2])%5 == 0) or (int(str(num)[0]) == 1) )):
                    return True
                elif((str(num)[-1] == '5') and ((int(str(num)[-2])%2 == 0) or (int(str(num)[-2])%5 == 0) or (int(str(num)[0]) == 1) )):
                    return True
                else:
                    return False
            return True
        elif(len(str(num)) == 1):
            return True
        else:
            return False
    except:
        return False
def new_all_format(line:list):
    all_presence_check = False
    tax_check = list()
    amt_check = list()

    for el in line:
        if(el.upper() == 'ALL'):
            all_presence_check = True
        elif(el.upper() in ["SP","DP","TP"]):
            tax_check.append(el.upper())
        elif(el.isnumeric()):
            amt_check.append(el)
        else:
            return False
    
    if(all_presence_check and (len(tax_check)==1) and (len(amt_check))==1):
        return ["0","1","2","3","4","5","6","7","8","9",tax_check[0],str(amt_check[0])]

    return False


# converting every mark to flag to be used everywhere
flags = ['R','P','T']
# all|n8|ni8|टोटल|ki|h/s|f/s|comsp|commsp|comdp|commdp|sp|dp|tp
# premultiplier,Rupees,Total
##########################################################################################
    #                  				PRE-PROCESSING
##########################################################################################

def text_process(msg:list):
    msg = r'''{}'''.format(msg)
    total = False
    premultiplier = False
    CANCEL = False
    lines = [line for line in msg.split('\n')]
    main_dict = dict()
    malfunctioned_msg =  False
    wait_list = list()
    risk = ''
    raw_table = PrettyTable(['sym_dict','raw_msg','num_list'])
    for line_num,line in enumerate(lines):
        # if('Motor' in risk):
        #     break
        # getting all numbers and symbols except the spaces and also hindi words 
        #\d{2}/\d{2}/\d{4}|
        sep_pattern = "|".join(map(re.escape, word_seprators))
        pattern = rf'\d+|{sep_pattern}|[a-zA-Z]+|/-|[^\W\d_][\u0900-\u097F]*|\S'
        raw_msg = re.findall(pattern, line, re.IGNORECASE)
       
        if(new_all_format(raw_msg)):
            raw_msg = new_all_format(raw_msg)
        # to maintin uniqueness and idnetity of each symbol
        sym_dict = dict()
        sym_ind_list = list()
        #temporary identier to keep only one total and premultiplier in a line
        p_p = False
        t_p = False
        # keep track of index to be delted after replacing them with flags
        indx_to_dlt = list()
        numbers_present_inside = list()
        # structure is always to divide whole line in to num str and other(symbol)
        #date check
        date_raw = re.findall(r'\d+',line)
        if(len(date_raw)>2):
            dates = [datetime.now().strftime("%d%m%y"),datetime.now().strftime("%m%d%y"),
                datetime.now().strftime("%d%m%Y"),datetime.now().strftime("%d%m%Y"),
            # datetime.now().strftime("%d%m%Y"),datetime.now().strftime("%m%d%Y")
            ]
            if(any(d == ''.join(date_raw[:3]) for d in dates)):
                raw_msg.pop(raw_msg.index(date_raw[0]))
                raw_msg.pop(raw_msg.index(date_raw[1]))
                raw_msg.pop(raw_msg.index(date_raw[2]))
        for i,x in enumerate(raw_msg):
            if(x.isnumeric()):
                numbers_present_inside.append(x)
                continue
            elif(x.isalpha()):
                if(x.upper() in cancel_msg):
                    CANCEL = True
                    raw_msg[i] = ""
                if(x.lower() in reject_msg):
                    risk += f" Motor Detected in Line:{line_num}, raw:{raw_msg}\n" 
                if((f_match(x.lower(),tax_list)) or (x.lower() in tax_list)):
                    for name,name_list in tax_list_fun.items():
                        if((x.lower() == name) or (x.lower() in name_list) ):
                            raw_msg[i] = name
                    if(any(xt.lower()=='t' for xt in raw_msg)):
                        for it,xt in enumerate(raw_msg):
                            if(xt.lower()=='t'):
                                raw_msg[it] = 'tp'
                elif(x.upper() in premultiplier_type):
                    if(not p_p):
                        raw_msg[i] = 'P'
                        p_p = True
                    else:
                        indx_to_dlt.append(i)
                        continue
                elif(x.upper() in rs_type ):
                    raw_msg[i] = 'R'
                elif((x.lower() in total_type) or f_match(x,total_type)):
                    if(not t_p):
                        raw_msg[i] = 'T'
                        t_p = True
                    else:
                        indx_to_dlt.append(i)
                        continue  
            else:
                if(x.upper() in cancel_msg):
                    CANCEL = True
                    raw_msg[i] = ""
                if(x.lower() in reject_msg):
                    risk += f" Motor Detected in Line:{line_num}, raw:{x}\n" 
                    # break
                # hindi total check
                elif(f_match(x,total_type)):
                    if(not t_p):
                        raw_msg[i] = 'T'
                        t_p = True
                    else:
                        indx_to_dlt.append(i)
                    continue 
                # TAX HINDI    
                elif(f_match(x,tax_list)):
                    for z in tax_list_fun:
                        if(f_match(x,z)):
                            raw_msg[i] = z[0]
                            break
                    continue
                # rs hindi symbol check
                elif(f_match(x,rs_type) or (x in rs_sym_type) ):
                    raw_msg[i] = 'R'  
                    continue
                    # break         
                if(x in sym_dict.keys()):
                    sym_dict[x].append(i)
                else:
                    sym_dict[x] = [i]
                sym_ind_list.append(i)

        sym_dlt_ind = [sym_ind_list[i+1] for i in range(len(sym_ind_list)-1) if (sym_ind_list[i+1]-sym_ind_list[i] == 1 and (raw_msg[sym_ind_list[i]] == raw_msg[sym_ind_list[i+1]]))]
        re_sym_dlt_ind = list()
        t_sym_list = list()

        for n in sym_dlt_ind:
            if(len(t_sym_list) == 0):
                t_sym_list.append(int(n))
            else:
                if(int(n)-int(t_sym_list[-1]) == 1):
                    t_sym_list.append(int(n))
                else:
                    re_sym_dlt_ind.append(t_sym_list)
                    t_sym_list = list()
                    t_sym_list.append(int(n))
        if(t_sym_list):
            re_sym_dlt_ind.append(t_sym_list)
            t_sym_list = list()

        if(sym_dlt_ind):

            while((len(sym_dlt_ind)>1) and (sym_dlt_ind[-1] - sym_dlt_ind[-2] == 1)):
                indx_to_dlt.append(sym_dlt_ind.pop())
            if((not (all(len(sl) == len(re_sym_dlt_ind[0]) for sl in re_sym_dlt_ind) and (len(re_sym_dlt_ind)>1))) and (raw_msg[sym_dlt_ind[-1]-1] not in repeated_no_price_sym)  ):
                raw_msg[sym_dlt_ind[-1]-1] = "!"
                
            indx_to_dlt.extend(sym_dlt_ind)
            indx_to_dlt.sort()
        # elif(len(sym_ind_list) ==1):
        # elif(len(sym_ind_list) ==1 and not(raw_msg[sym_ind_list[-1]] in repeated_no_price_sym)):
        elif(len(sym_ind_list) ==1 and (raw_msg[sym_ind_list[-1]] in rs_sym_type)):
            raw_msg[sym_ind_list[-1]] = "!"
        elif(len(sym_ind_list) ==1 and (len(numbers_present_inside)==2) and (raw_msg[sym_ind_list[-1]] in ['/'])):
            raw_msg[sym_ind_list[-1]] = "!"
        if(len([k for k in sym_dict.keys()]) ==2):
            k = [x for x in sym_dict.keys()]
            if(not(all(k in rs_sym_type or total_type or rs_type))):
                l1 = len(sym_dict[k[0]])
                l2 = len(sym_dict[k[1]])
                if(l1!=l2):
                    if(l1 ==1 and ((len([x for x in raw_msg[raw_msg.index(k[0]):] if(x.isnumeric())])) == 1)):
                        raw_msg[raw_msg.index(k[0])] = 'R'
                    elif(l2 == 1 and ((len([x for x in raw_msg[raw_msg.index(k[1]):] if(x.isnumeric())])) == 1)):
                        raw_msg[raw_msg.index(k[1])] = 'R'
        del p_p
        del t_p
        if(indx_to_dlt):
            new = list()
            for i,x in enumerate(raw_msg):
                if(i in indx_to_dlt):
                    if(x in sym_dict.keys()):
                        sym_dict[x].pop(sym_dict[x].index(i))
                    continue
                new.append(x)
            raw_msg = new
        del indx_to_dlt
        del sym_dlt_ind
        len_of_raw  = len(raw_msg)
        # main list to contain the line wise numbers
        num_list = list()
        # FLAGS
        price = False
        tax = False
        # tax for all sp dp and special cases 
        multiline = False
        invert = False
        # to tackle inverted messages like 200 @ 1,2,3
        for idx,raw in enumerate(raw_msg): 
            # print(raw,raw_msg)
            # diving each token in raw msg into 3 category num str or sym
            if(raw.isnumeric()):
                # waitlist is implementd to deal with multiline or lines having more spaces 
                # to clealy identify T and P
                # if value is not there it can forget as well by implementing more than required wait number strategy
                # this uses diffrent flags to keep them alog diffrent record
                # have to improve to use one kind of flag only
                # data type of wait list is [[flag,indx]] and after that elemnt is found it changes len to 3 [[flag,indx,0]]
                if(wait_list):
                    t = [x for x in raw_msg if (x.isnumeric() or x in flags[1:])]
                    if(main_dict[line_num-1][0] == [] or any(str(x[1])[0].upper() in main_dict[line_num-1][0] for x in wait_list )):
                        temp_flag = False
                        if(wait_list[0][1]=='premultiplier'):
                            temp_flag = 'P'
                        else:
                            temp_flag = 'T'
                        if(any(x in flags for x in t)):
                            popped_index = main_dict[wait_list[0][0]][0].index(temp_flag)
                            main_dict[wait_list[0][0]][0].pop(popped_index)
                            if(len(main_dict[wait_list[0][0]][0])>1 and (t[0].isnumeric())):
                                num_list.append(temp_flag)
                                num_list.append(raw)
                                premultiplier = True
                                wait_list[0].append(0)
                            elif(len(main_dict[wait_list[0][0]][0])>1 and (t[0] in flags)):
                                main_dict[wait_list[0][0]][0].insert(popped_index-1,temp_flag)
                                main_dict[wait_list[0][0]][2] = True
                                wait_list[0].append(0)
                                num_list.append(raw)
                            else:
                                risk+= f"Risk Unrecognized Flag Found--{wait_list[0]}"
                            temp_flag = False
                        elif(len(t) ==  1):
                            for wait_ind,wait in enumerate(wait_list):
                                if(len(wait) == 2):
                                    if(wait[1] == 'premultiplier'):
                                        premultiplier = True
                                        num_list.append('P')
                                    elif(wait[1] == 'total'):
                                        total = True
                                        num_list.append('T')
                                    elif(wait[1] == 'price'):
                                        price = True
                                        num_list.append('R')
                                    else:
                                        print("CRITICAL::Sochenge @ waitList upper 1")
                                    num_list.append(raw)
                                    wait.append(0)
                                    break
                        elif(len(t) == len(wait_list)):
                            for wait_ind,wait in enumerate(wait_list):
                                
                                if(len(wait) == 2):
                                    if(wait[1] == 'premultiplier'):
                                        premultiplier = True
                                        num_list.append('P')
                                    elif(wait[1] == 'total'):
                                        total = True
                                        num_list.append('T')
                                    elif(wait[1] == 'price'):
                                        price = True
                                        num_list.append('R')
                                    else:
                                        print("CRITICAL::Sochenge @ waitList upper 2")
                                    num_list.append(raw)
                                    wait.append(0)
                                    break
                        else:
                            popped_index = main_dict[wait_list[0][0]][0].index(temp_flag)
                            main_dict[wait_list[0][0]][0].pop(popped_index)
                            main_dict[wait_list[0][0]][0].insert(popped_index-1,temp_flag)
                            main_dict[wait_list[0][0]][2] = True
                            temp_flag = False
                            num_list.append(raw)
                            wait_list = list()

                        if(temp_flag):
                            popped_index = main_dict[wait_list[0][0]][0].index(temp_flag)
                            main_dict[wait_list[0][0]][0].pop(popped_index)

                        if(wait_list):
                            l_l = [len(x) for x in wait_list]
                            check = all(x == 3 for x in l_l)
                            if(check):
                                wait_list = list()
                        continue
                    else:
                        num_list.append(raw)
                else:
                    if(num_list):
                        temp_t = [n for n in num_list if(n.isnumeric())]
                        temp_t_ = [n for n in num_list if(n.isnumeric() or (n in flags) or (n in tax_list))]
                        if(temp_t):
                            if(len(temp_t[-1]) != len(raw) and (not temp_t_[temp_t_.index(temp_t[-1])-1].isalpha() )):
                                #if(is_price(raw)):
                                if(raw.isnumeric()):
                                    num_list.append('R')
                                else:
                                    risk += f"message not clear token:{raw_msg}, raw:{raw}"

                    if((raw in main_num_list) or ((len(raw)>3) and ('0' in raw) and (((len(set(raw)) == len(raw) and (raw[-1]=='0') and all(raw[i] < raw[i+1] for i in range(len(raw)-2))) or  ((len(set(raw)) == len(raw) and (raw[0]=='0') and all(raw[i] < raw[i+1] for i in range(len(raw)-1)))) ) ) )):
                        num_list.append(raw)
                    elif(('0' not in raw) and ((len(raw)>3) and all(raw[i] < raw[i+1] for i in range(len(raw)-1)))):
                        num_list.append(raw)
                    else:
                        num_list.append('R')
                        num_list.append(raw)

                    if(len_of_raw == 1):
                        pass
                    elif((idx == (len_of_raw-1)) and(all(n.isnumeric() for n in num_list))):
                        multiline = True
                        
            # Tracking the string ones
            elif(raw.isalpha()):
                if((raw.lower() in reject_msg) or f_match(raw,reject_msg,max_ratio=79) ):
                    risk += f" Motor Detected in Line:{idx}, raw:{raw}\n" 
                    break
                if(raw == 'P'):
                    # to identify things it checks both side left and right and then check numbers and strategy
                    # dividing into 3 categoty left only, right only and left and right both side numbers present of the flag P
                    t = list()
                    for i in range(0,len_of_raw):
                        if(raw_msg[i].isnumeric()):
                            t.append(raw_msg[i])
                        elif(i == idx):
                            t.append('P')
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
                                break
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
                                break
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
                                break
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

                if(raw.lower() in tax_list):
                    if(raw.lower() in reject_msg):
                        risk += f" Motor Detected in tax(T) Line:{idx}, raw:{raw}\n" 
                        break

                    tax = re.findall(r'[A-Za-z]+',' '.join(raw_msg))
                    tax = [n for n in tax if(n.lower() in tax_list)]
                    
                    tax = list(dict.fromkeys(tax))
                    if(len(tax) > 1):
                        last = int(0)
                        line_ending_index = int(0)
                        increaser = int(0)
                        more_than_one_tax = [x for x in raw_msg if((x in tax_list) or (x.isnumeric()))]
                        more_than_one_tax_one_line = list()
                        for i_x,x in enumerate(more_than_one_tax):
                            if(x in tax_list):
                                if(more_than_one_tax_one_line):
                                    if((more_than_one_tax[i_x-1] in tax_list)):
                                        pretend_price = 'NULL'
                                        for curr_index,temp_pretend_price in enumerate(more_than_one_tax[i_x:]):
                                            if((curr_index+i_x)<=increaser):
                                                continue
                                            if(temp_pretend_price.isnumeric()):
                                                increaser = i_x+curr_index
                                                pretend_price = temp_pretend_price
                                                # more_than_one_tax.pop(i_x+curr_index)
                                                break
                                        if(pretend_price=="NULL"):
                                            pretend_price = more_than_one_tax_one_line[-1][1]
                                        more_than_one_tax_one_line.append([x,pretend_price])
                                    elif((more_than_one_tax[i_x+1].isnumeric() and (more_than_one_tax[i_x-2] in tax_list) )):
                                        more_than_one_tax_one_line.append([x,more_than_one_tax[i_x+1]])
                                    else:
                                        if((len_of_raw-1) > (raw_msg.index(x) + 1)):
                                            if(raw_msg[raw_msg.index(x) + 1].isnumeric()):
                                                more_than_one_tax_one_line.append([raw_msg[last+1:raw_msg.index(x)+2]])
                                                last = raw_msg.index(x)+1
                                            # elif (((len_of_raw-1) > (raw_msg.index(x)+2)) and (raw_msg[raw_msg.index(x)+2].isnumeric())):
                                            #     more_than_one_tax_one_line.append([raw_msg[raw_msg.index(x)+2:]])
                                            else:
                                                more_than_one_tax_one_line.append([raw_msg[last+1:raw_msg.index(x)+2]])
                                                last = raw_msg.index(x)+1
                                                risk += "More High Risk (indication to break line) not clear"
                                        else:
                                            more_than_one_tax_one_line.append([raw_msg[last+1:raw_msg.index(x)+1]])
                                            last = raw_msg.index(x)
                                            risk += " Too More High Risk (indication to break line) not clear"
                                        #indication to break line
                                        # risk += "High Risk (indication to break line) not clear"
                                else:
                                    if(more_than_one_tax[i_x+1].isnumeric() and (more_than_one_tax[i_x+2] in tax_list) and(more_than_one_tax[-1].isnumeric())):
                                        line_ending_index = idx - 1
                                        more_than_one_tax_one_line.append([x,more_than_one_tax[i_x+1]]) 
                                     
                                    #NEW LINES ADDED FOR 1,2,3,20SP 40dp
                                    elif(len(tax)==2 and more_than_one_tax[i_x-1].isnumeric() and (more_than_one_tax[i_x+1].isnumeric()) and (more_than_one_tax[i_x+2] in tax_list) and(more_than_one_tax[-1] in tax_list) ):
                                        more_than_one_tax[i_x-1],more_than_one_tax[i_x]=more_than_one_tax[i_x],more_than_one_tax[i_x-1]
                                        more_than_one_tax[i_x+1],more_than_one_tax[i_x+2]=more_than_one_tax[i_x+2],more_than_one_tax[i_x+1]
                                        raw_msg[raw_msg.index(more_than_one_tax[i_x-1])],raw_msg[raw_msg.index(more_than_one_tax[i_x])]=raw_msg[raw_msg.index(more_than_one_tax[i_x])],raw_msg[raw_msg.index(more_than_one_tax[i_x-1])]
                                        raw_msg[raw_msg.index(more_than_one_tax[i_x+1])],raw_msg[raw_msg.index(more_than_one_tax[i_x+2])]=raw_msg[raw_msg.index(more_than_one_tax[i_x+2])],raw_msg[raw_msg.index(more_than_one_tax[i_x+1])]
                                        line_ending_index = idx - 2
                                        more_than_one_tax_one_line.append([more_than_one_tax[i_x-1],more_than_one_tax[i_x]])  
                                    elif(len(tax)==3 and more_than_one_tax[i_x-1].isnumeric() and (more_than_one_tax[i_x+1].isnumeric()) and (more_than_one_tax[i_x+2] in tax_list) and (more_than_one_tax[i_x+3].isnumeric()) and (more_than_one_tax[i_x+4] in tax_list) and(more_than_one_tax[-1] in tax_list)):
                                        more_than_one_tax[i_x-1],more_than_one_tax[i_x]=more_than_one_tax[i_x],more_than_one_tax[i_x-1]
                                        more_than_one_tax[i_x+1],more_than_one_tax[i_x+2]=more_than_one_tax[i_x+2],more_than_one_tax[i_x+1]
                                        more_than_one_tax[i_x+3],more_than_one_tax[i_x+4]=more_than_one_tax[i_x+4],more_than_one_tax[i_x+3]
                                        raw_msg[raw_msg.index(more_than_one_tax[i_x-1])],raw_msg[raw_msg.index(more_than_one_tax[i_x])] = raw_msg[raw_msg.index(more_than_one_tax[i_x])],raw_msg[raw_msg.index(more_than_one_tax[i_x-1])]
                                        raw_msg[raw_msg.index(more_than_one_tax[i_x+1])],raw_msg[raw_msg.index(more_than_one_tax[i_x+2])] = raw_msg[raw_msg.index(more_than_one_tax[i_x+2])],raw_msg[raw_msg.index(more_than_one_tax[i_x+1])]
                                        raw_msg[raw_msg.index(more_than_one_tax[i_x+3])],raw_msg[raw_msg.index(more_than_one_tax[i_x+4])] = raw_msg[raw_msg.index(more_than_one_tax[i_x+4])],raw_msg[raw_msg.index(more_than_one_tax[i_x+3])]
                                        line_ending_index = idx - 2
                                        more_than_one_tax_one_line.append([more_than_one_tax[i_x-1],more_than_one_tax[i_x]])  
                                    #till here
                                        
                                    elif(more_than_one_tax[i_x+1] in tax_list):
                                        line_ending_index = idx - 1
                                        pretend_price = 'NULL'
                                        for curr_index,temp_pretend_price in enumerate(more_than_one_tax[i_x+1:]):
                                            if(temp_pretend_price.isnumeric()):
                                                nums_after_tax = len([x for x in more_than_one_tax[i_x+1:] if (x.isnumeric())])
                                                if((len(tax) != nums_after_tax) and (nums_after_tax>1)):
                                                    risk += f"High Risk too many Number after taxes Line:{idx}, raw:{raw}\n"
                                                pretend_price = temp_pretend_price
                                                increaser = i_x+curr_index+1
                                                # more_than_one_tax.pop(i_x+curr_index)
                                                break
                                        if(pretend_price == 'NULL'):
                                            for i in range(line_num+1,len(lines)):
                                                forward_raw = re.findall(r'\d+',lines[i])
                                                if(len(forward_raw)==1):
                                                    pretend_price = forward_raw[0]
                                                    lines.pop(i)
                                                elif(len(forward_raw)==0):
                                                    continue
                                                else:
                                                    risk += f"High Risk no Number in any line after taxes Line:{idx}, raw:{raw}\n"
                                                    break
                                        more_than_one_tax_one_line.append([x,pretend_price])        
                                    else:
                                        last = idx+1
                                        more_than_one_tax_one_line.append([raw_msg[:last+1]])
                        if(all(len(x) == 2 for x in more_than_one_tax_one_line)):
                            new_lines = list()
                            temp_more_index = 0
                            while(more_than_one_tax_one_line):
                                new_line = list()
                                new_line = raw_msg[:line_ending_index+1]
                                if(more_than_one_tax_one_line[0][-1] in raw_msg):
                                    raw_msg.pop(raw_msg.index(more_than_one_tax_one_line[0][-1]))
                                raw_msg.pop(raw_msg.index(more_than_one_tax_one_line[0][0]))
                                new_line.extend(more_than_one_tax_one_line.pop(0))
                                new_lines.append(new_line)
                            line_ending = raw_msg[line_ending_index+1:]
                            if(line_ending and any(x.isnumeric() for x in line_ending)):
                                new_lines.append(line_ending)
                            raw_msg[:] = new_lines.pop(0)
                            len_of_raw = len(raw_msg)
                            insert_line_num = line_num+1
                            while(new_lines):
                                lines.insert(insert_line_num,' '.join(new_lines.pop(0)))
                                insert_line_num += 1
                        elif(all(len(x) == 1 for x in more_than_one_tax_one_line)):
                            raw_msg[:] = more_than_one_tax_one_line.pop(0).pop(0)
                            len_of_raw = len(raw_msg)
                            insert_line_num = line_num+1
                            while(more_than_one_tax_one_line):
                                lines.insert(insert_line_num,' '.join(more_than_one_tax_one_line.pop(0).pop(0)))
                                insert_line_num += 1
                        else:
                            risk += f" High Risk Number in between two tax Line:{idx}, raw:{raw}\n" 
                            break
                    
                    for name,name_list in tax_list_fun.items():
                        if((raw.lower() == name) or (raw.lower() in name_list) ):
                            tax = name

                    t = list()
                    for i in range(0,len_of_raw):
                        if(raw_msg[i].isnumeric() ):
                            t.append(raw_msg[i])
                        elif((((i == idx) and (raw_msg[i] in raw_msg)) or (raw_msg[i] in raw_msg))and raw_msg[i] in tax_list ):
                            t.append(tax)
                    if(len(t)==1):
                        pass
                    elif(t[0] == tax):
                        if(all(len(n)==len(t[1]) for n in t[1:]) and all(n in main_num_list for n in t[1:])):
                            pass
                        elif(tax in ('mpsp','mpdp')):
                            min_len = 3
                            if(tax == 'mpdp'):
                                min_len = 2
                            right = t[1:]
                            right_check = False
                            for num in right:
                                if((len(num)>=min_len) and '0' in num and (num[-1]=='0' or num[0]=='0')):
                                    if(len(set(num)) == len(num) and (num[-1]=='0') and all(num[i] < num[i+1] for i in range(len(num)-2))):
                                        right_check = True
                                    elif(len(set(num)) == len(num) and (num[0]=='0') and all(num[i] < num[i+1] for i in range(len(num)-1))):
                                        right_check = True                                        
                                elif((len(num)>=min_len) and all(num[i] < num[i+1] for i in range(len(num)-1))):
                                    right_check = True
                                elif(t[-1] == num):
                                    right_check = True
                                    if(raw_msg[-2] == 'R' or (raw_msg[-1] == 'R' and raw_msg[-1].isnumeric())):
                                        pass
                                    else:
                                        raw_msg.insert(raw_msg.index(raw_msg[-1]),'R')
                                    price = True
                                else:
                                    right_check = False
                                    risk+= f"Risk Uncertain pattern motor right {tax}: {t}"
                                    break

                        elif(all(len(n)==len(t[1]) for n in t[1:-1]) and all(n in main_num_list for n in t[1:-1])):
                            right_check = False
                            right = t[1:-1]
                            if(tax == 'fm'):
                                right_check = (all(len(x) in [2,3] for x in right) and all(x in main_num_list for x in right))
                            else:  
                                right_check = (all(len(x)==tax_len_dict[tax][0] for x in right) and all(x in list(tax_num_dict[tax].keys()) for x in right))
                            if(right_check):
                                if(raw_msg[-2] == 'R' or (raw_msg[-1] == 'R' and raw_msg[-1].isnumeric())):
                                    pass
                                else:
                                    raw_msg.insert(raw_msg.index(raw_msg[-1]),'R')
                                price = True
                        else:
                            risk+= f"High Risk Uncertain pattern {tax}: {t}"
                    elif(t[-1] == tax):
                        multiline = True
                        if(len(t)>1):
                            left = t[:t.index(tax)]
                            left_check = False
                            if(tax == 'fm'):
                                left_check = (all(len(x) in [2,3] for x in left) and all(x in main_num_list for x in left))
                            elif(tax in ('mpsp','mpdp')):
                                min_len = 3
                                if(tax == 'mpdp'):
                                    min_len = 2
                                for num in left:
                                    if((len(num)>=min_len) and '0' in num and (num[-1]=='0' or num[0]=='0')):
                                        if(len(set(num)) == len(num) and (num[-1]=='0') and all(num[i] < num[i+1] for i in range(len(num)-2))):
                                            left_check = True
                                        elif(len(set(num)) == len(num) and (num[0]=='0') and all(num[i] < num[i+1] for i in range(len(num)-1))):
                                            left_check = True
                                    elif((len(num)>=min_len) and all(num[i] < num[i+1] for i in range(len(num)-1))):
                                        left_check = True
                                    else:
                                        left_check = False
                                        risk+= f"Risk Uncertain pattern motor left {tax}: {t}"
                                        break
                            else:  
                                left_check = (all(len(x)==tax_len_dict[tax][0] for x in left) and all(x in list(tax_num_dict[tax].keys()) for x in left))
                            if(not left_check):
                                risk += f"Cancel Risk Number invalid {tax} numbers {t}"
                    else:
                        left = t[:t.index(tax)]
                        right = t[(t.index(tax)+1):]                        
                        if(tax == 'fm'):
                            left_check = (all(len(x) in [2,3] for x in left) and all(x in main_num_list for x in left))
                            right_check = (all(len(x) in [2,3] for x in right) and all(x in main_num_list for x in right))
                        elif(tax in ('mpsp','mpdp')):
                                min_len = 3
                                if(tax == 'mpdp'):
                                    min_len = 2
                                left_check = False
                                right_check = False
                                for num in left:
                                    if((len(num)>=min_len) and '0' in num and (num[-1]=='0' or num[0]=='0')):
                                        if(len(set(num)) == len(num) and (num[-1]=='0') and all(num[i] < num[i+1] for i in range(len(num)-2))):
                                            left_check = True
                                        elif(len(set(num)) == len(num) and (num[0]=='0') and all(num[i] < num[i+1] for i in range(len(num)-1))):
                                            left_check = True
                                    elif((len(num)>=min_len) and all(num[i] < num[i+1] for i in range(len(num)-1))):
                                        left_check = True
                                    else:
                                        left_check = False
                                        break
                                for num in right:
                                    if((len(num)>=min_len) and '0' in num and (num[-1]=='0' or num[0]=='0')):
                                        if(len(set(num)) == len(num) and (num[-1]=='0') and all(num[i] < num[i+1] for i in range(len(num)-2))):
                                            right_check = True
                                        elif(len(set(num)) == len(num) and (num[0]=='0') and all(num[i] < num[i+1] for i in range(len(num)-1))):
                                            right_check = True
                                    elif((len(num)>=min_len) and all(num[i] < num[i+1] for i in range(len(num)-1))):
                                        right_check = True
                                    else:
                                        right_check = False
                                        break
                        else:                              
                            left_check = (all(len(x)== tax_len_dict[tax][0] for x in left) and all(x in list(tax_num_dict[tax].keys()) for x in left))
                            right_check = (all(len(x)== tax_len_dict[tax][0] for x in right) and all(x in list(tax_num_dict[tax].keys()) for x in right))
                        if(left_check and right_check):
                            if(len(right)==1):
                                pass
                            elif((len(right)==2)):
                                left.append(right[0])
                                new__tot_check = convert_tax_to_act_msg(tax,left)
                                check_total = (len(new__tot_check[0])-1)*(int(new__tot_check[0][-1]))
                                if(int(right[-1])==(check_total)):
                                    price = True
                                    raw_msg[raw_msg.index(right[-1])] = ""
                                elif(len(left)==1):
                                    price = True
                                    invert = True
                                else:
                                    risk+= f"High Risk Uncertain pattern {tax}: {t}"
                        elif(right_check):
                            pass
                        elif(not left_check):
                            risk += f"Unrecognized Format  tax Line:{idx}, raw:{raw}\n" 
                        if((len(right)>1) and len(left)==1):
                            if((len(right)==2)):
                                left.append(right[0])
                                new__tot_check = convert_tax_to_act_msg(tax,left)[0]
                                check_total = (len(new__tot_check)-1)*(int(new__tot_check[-1]))
                                if(int(right[-1])==(check_total)):
                                    price = True
                                    raw_msg[raw_msg.index(right[-1])] = ""
                                elif(len(left)==1):
                                    price = True
                                    invert = True
                                else:
                                    risk+= f"High Risk Uncertain pattern {tax}: {t}"
                    num_list.append(tax)
                if(raw == 'R'):
                    t = list()
                    for i in range(0,len_of_raw):
                        if(raw_msg[i].isnumeric() or i == idx):
                            t.append(raw_msg[i])
                    if((any(r in tax_list for r in raw_msg)) and ('R' in raw_msg) and (raw_msg.count('R')>1)):
                        risk += f" multiple R in tax Line:{idx}, raw:{raw} , Line:{raw_msg} \n" 
                        num_list.insert(-1,'R')
                        price = True
                        continue
                    if(len(t) == 2):
                        if(t[0].isnumeric()):
                            num_list.insert(0,'R')
                        else:
                            num_list.append('R')
                        price = True
                        multiline = True
                    elif(t[-1] == 'R'):
                        num_list.insert(-1,'R')
                        price = True
                    elif(t[-2] == 'R'  and t[-1].isnumeric()):
                        num_list.append('R')
                        price = True
                    elif((t[1] == raw or t[0] == raw) and len(t) > 3 and all(x.isnumeric() for x in t if(x!=raw))):
                        num_list.append('R')
                        price = True
                        invert = True
                    else:
                        risk += f" Unrecognized position of R in Line:{idx}, raw:{raw} , Line:{t} \n" 
                # Stucture of P and T is completely same just condidering the size few line changed
                if(raw == 'T'):
                    t = list()
                    
                    for i in range(0,len_of_raw):
                        if(raw_msg[i].isnumeric() or i == idx):
                            t.append(raw_msg[i])
                        # elif(raw_msg[i] == 'T'):
                        #     t.append('T')
                    if(len(t[t.index('T'):])==3 ):
                        raw_msg[idx+raw_msg.index(t[-2])] = t[-2]+t[-1]
                        raw_msg[idx+raw_msg.index(t[-1])] = "NULL"
                        t[-2] = t[-2]+t[-1]
                        t.pop(1)

                    if(len(t) == 2 ):
                        if(num_list):
                            num_list.insert(0,'T')
                        else:
                            num_list.append('T')
                        total = True    
                    elif(len(t) > 2):
                        try:
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
                            if( 'T' in num_list):
                                risk += f" More than one T Line:{idx}, raw:{raw}\n" 
                                break
                            else:
                                for i,x in enumerate(zip(t,t_len)):

                                    if(i == 0):
                                        continue

                                    if(x[1] == 0):
                                        if(t_len[i+1] == 0 and t[i] == 'T'):
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
                                                    risk += f" LR both same number T  LR Line:{idx}, raw:{raw}\n" 
                                                    break
                                                total = True
                                                premultiplier = True
                                                break
                                            elif(i == (len(t_len)-3)):
                                                if(int(t[i-1]) > int(t[i+2])):
                                                    num_list.insert((len(num_list)-2),'T')
                                                    total = True
                                                elif(int(t[i-1]) < int(t[i+2])):
                                                    num_list.append('T')
                                                    total = True
                                            else:
                                                risk += f" Dirst if unrecognized format T  LR Line:{idx}, raw:{raw}\n" 
                                        elif(t[i] == 'T'):
                                            if(i == (len(t_len)-2)):
                                                if(int(t[i+1]) == biggest_num or is_price(t[i+1])):
                                                    num_list.append('T')
                                                    total = True
                                                else:
                                                    risk += f" Price not in type 1 T  LR Line:{idx}, raw:{raw}\n" 
                                            elif(i == (len(t_len)-3)):
                                                if(is_price(t[i-1]) ):
                                                    num_list.insert(num_list.index(t[i-1]),'T')
                                                    total = True
                                                    if(not any(r in tax_list for r in raw_msg)):
                                                        num_list.append('P')
                                                        wait_list.append([line_num,'premultiplier'])
                                                    break
                                                else:
                                                    risk += f" Price not in type 2 T  LR Line:{idx}, raw:{raw}\n" 
                                            elif(i == (len(t_len)-4)):
                                                if(int(t[i+1]) == biggest_num or is_price(t[i+1])):
                                                    num_list.append('T')
                                                    total = True
                                                else:
                                                    risk += f" Price not in type 4 T  LR Line:{idx}, raw:{raw}\n" 
                                            else:
                                                risk += f" Unrecognized format T  LR Line:{idx}, raw:{raw}\n" 

                                        elif(t[i] == 'P'):
                                            continue
                                        break
                        elif(left):
                            if( 'T' in num_list):
                                risk += f"More thn one T  L Line:{idx}, raw:{raw}\n" 
                                break
                            else:
                                for i,x in enumerate(zip(t,t_len)):
                                    if(i == 0):
                                        continue
                                    if(x[1] == 0 ):
                                        if(t[i] == 'T' and (len(t_len) == 2)):
                                            if(int(t[i-1]) == biggest_num or is_price(t[i-1])):
                                                num_list.insert(num_list.index(t[i-1]),'T')
                                                total = True
                                            
                                            else:
                                                risk += f" Price not in type T  L Line:{idx}, raw:{raw}\n" 
                                        elif(t[i] == 'P'):
                                            continue
                                        else:
                                            if(not any(r in tax_list for r in raw_msg)):
                                                num_list.append('T')
                                                wait_list.append([line_num,'total'])
                                        break
                                        
                            
                        elif(right):
                            if( 'T' in num_list):
                                risk += f"More than one T  R Line:{idx}, raw:{raw}\n" 
                                break
                            else:
                                for i,x in enumerate(zip(t,t_len)):
                                    if(x[1] == 0):
                                        if(t_len[i+1] == 0 and t[i] == 'T'):
                                            if(i == (len(t_len)-4)):
                                                if(int(t[i+2]) < int(t[i+3])):
                                                    if(is_price(t[i+3]) or (t[i+3] == biggest_num)):
                                                        num_list.append('T')
                                                        num_list.append(t[i+3])
                                                        total = True
                                                    else:
                                                        risk += f"price not in type T  R Line:{idx}, raw:{raw}\n"
                                                    if(is_price(t[i+2])):
                                                        num_list.append('P')
                                                        num_list.append(t[i+2])
                                                        premultiplier = True
                                                    else:
                                                        risk += f"price not in type T  R 2 Line:{idx}, raw:{raw}\n"

                                                elif(int(t[i+2]) > int(t[i+3])):
                                                    if(is_price(t[i+2]) or (t[i+2] == biggest_num)):
                                                        num_list.append('T')
                                                        num_list.append(t[i+2])
                                                        total = True
                                                    else:
                                                        risk += f"price not in type T  R3 Line:{idx}, raw:{raw}\n"
                                                    if(is_price(t[i+3])):
                                                        num_list.append('P')
                                                        num_list.append(t[i+3])
                                                        premultiplier = True
                                                    else:
                                                        risk += f"price not in type T  R4 Line:{idx}, raw:{raw}\n"
                                                else:
                                                    risk += f"Unrecognise format T  R Line:{idx}, raw:{raw}\n"
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
                                                else:
                                                    risk += f"price not in type T  R5 Line:{idx}, raw:{raw}\n"

                                            else:
                                                risk += f"Unrecognized format T  R Line:{idx}, raw:{raw}\n"
                                        elif(t[i] == 'T'):
                                            if(int(t[i+1]) == biggest_num or is_price(t[i+1])):
                                                num_list.append('T')
                                                total = True
                                            elif(any(t_t.isnumeric() and is_price(t_t) and int(t_t) == biggest_num for t_t in t)):
                                                for t_t in t:
                                                    if(t_t.isnumeric()):
                                                        if(is_price(t_t) and int(t_t) == biggest_num):
                                                            num_list.append('T')
                                                            total = True
                                                        else:
                                                            num_list.append(t_t)
                                                    else:
                                                        risk += f"price not in type T  R6 Line:{idx}, raw:{raw}\n"
                                                break
                                            else:
                                                risk += f"Unrecognized format T  R 2 else Line:{idx}, raw:{raw}\n"
                                        elif(t[i] == 'P'):
                                            continue
                                        else:
                                            risk += f"Unrecognized format T  R 3 else Line:{idx}, raw:{raw}\n"
                                        break
                        else:
                            num_list.append('T')
                            if(not any(r in tax_list for r in raw_msg)):
                                num_list.append('T')
                                wait_list.append([line_num,'total'])
                    else:
                        if(not any(r in tax_list for r in raw_msg)):
                            num_list.append('T')
                            wait_list.append([line_num,'total'])
            else:
                if(raw.lower() in reject_msg):
                    risk += f" Motor Detected in Line:{idx}, raw:{raw}\n" 
                    break
                t = list()
                for i in range(0,len_of_raw):
                    if(raw_msg[i].isnumeric() or i == idx):
                        t.append(raw_msg[i])
                
                if((raw == '=') and ((len(t)>2) and t[-2] == '=') and (len(sym_dict['=']) == 1)):
                    if((len(lines)-1) > line_num):
                        temp_next_line = re.findall(r'\d+|all|n8|ni8|टोटल|ki|h/s|f/s|sp|dp|tp|[a-zA-Z]+|फॅमिली|\b[ऀ-ॿ]+\b|/-|[^ ]W+|\S',lines[line_num+1], re.IGNORECASE)
                        temp_next_line = ''.join(temp_next_line)
                        temp_next_line_nums = re.findall(r'\d+',temp_next_line)
                        if((temp_next_line_nums and (len(temp_next_line_nums[0])==len(t[-1])))):
                            if(len(temp_next_line.split('='))<=2 and ((len(t)==3 and is_price(t[2])) or len(t)>3)):
                                num_list.append('R')
                        else:
                            num_list.append('R')
                elif((raw == '@') and ((len(t)>2) and t[-2] == '@') and (len(sym_dict['@']) == 1)):
                    num_list.append('R')
                elif(t.index(raw) == (len(t)-2) and (len(t)>1) and not invert and ( (raw_msg[-1].isnumeric()) or (t[-1].isnumeric()) )):
                    if(t[-1].isnumeric() ):
                        if((raw == '!') and (len(sym_dict.keys())>1)):
                            num_list.append('R')
                        elif((raw == '!') and (len(sym_dict.keys())==1) and (t.index(raw) == (len(t)-2)) and ((len(t)>2) and (len(sym_dict[list(sym_dict.keys())[0]])>0))):
                            t__ = [x for i,x in enumerate(raw_msg) if(x.isnumeric() or i == idx )]
                            if((t__[-1].isnumeric()) and (is_price(t__[-1]))):
                                num_list.append('R')
                            if((t__[-1].isnumeric()) and (len(t)==3) ):
                            # if((t__[-1].isnumeric())):
                                num_list.append('R')
                        elif((raw in rs_sym_type or raw in close_brackets) and is_price(t[-1] and(len(sym_dict[raw]) == 1))):
                            num_list.append('R')
                            if(t.index(raw)==1):
                                price = True
                                invert = True
                        else:
                            continue
                        price = True
                    else:
                        risk += f"Price not in type  S 1 Line:{idx}, raw:{raw}\n"
                elif(raw in close_brackets and (t.index(raw) == 0 or t.index(raw) == 1)):
                    invert = True
                    price = True
                    continue
                elif(raw in open_brackets and (t.index(raw) == 0 or t.index(raw) == 1)):
                    multiline = True
                    if(t.index(raw)==1):
                        price = True
                        invert = True
                    continue
                elif(t.index(raw) == (len(t)-1) and (len(t)>1) and (raw not in rs_sym_type)):
                    multiline = True
                    continue
                # elif(raw in rs_sym_type and (t.index(raw)>0) and ((len(t)-1) > (t.index(raw))) and (len(sym_dict[raw])==1) and ('R' not in num_list)):
                #     t_i = t.index(raw)
                #     if(t_i == 1):
                #         if(is_price(t[0])):
                #             num_list.insert(num_list.index(t[0]),'R')
                #             invert = True
                #             price = True
                #     else:
                #         risk += f"Symbol not invert  S  Line:{idx}, raw:{raw}\n"
                # 
                # elif(raw in rs_sym_type and (num_list)):
                elif(raw in rs_sym_type ):
                    t_i = t.index(raw)
                    l_i = len(t)-1
                    # left-right and left
                    if( t_i != 0 and ((l_i >= t_i))):
                        num_list.insert(-1,'R')
                    else:
                        print("CRITICAL:: Decide something for here rawsymtype")
                        # risk += f"Symbol not invert  S  Line:{idx}, raw:{raw}\n"
                    
            if(wait_list):
                for i in range(0,line_num-1):
                    t = list()
                    for x in main_dict[i][0]:
                        if(x == 'P' or x == 'T' or x == 'R'):
                            break
                        elif(x.isnumeric()):
                            t.append(x)
                    if(any(n in main_dict[i][0] for n in flags)):
                        break
                    if(any(n in main_dict[i][0] for n in tax_list)):
                        break
                    if(not t):
                        continue
                    if(not wait_list):
                        break
                    for wait_ind,wait in enumerate(wait_list):
                        if(len(wait) == 2):
                            if(len(t) ==  1):
                                if(wait[1] == 'premultiplier'):
                                    # main_dict[i][2] = True 
                                    main_dict[i][0].insert(0,'P')
                                elif(wait[1] == 'total'):
                                    # main_dict[i][5] = True 
                                    main_dict[i][0].insert(0,'T')
                                elif(wait[1] == 'price'):
                                    main_dict[i][3] = True 
                                    main_dict[i][0].insert(0,'R')
                                wait.append(0)
                            elif(len(t) == len(wait_list)):
                                if(wait[1] == 'premultiplier'):
                                    # main_dict[i][2] = True 
                                    main_dict[i][0].insert(main_dict[i][0].index(t[wait_ind]),'p')
                                elif(wait[1] == 'total'):
                                    # main_dict[i][5] = True 
                                    main_dict[i][0].insert(main_dict[i][0].index(t[wait_ind]),'t')
                                elif(wait[1] == 'price'):
                                    main_dict[i][3] = True 
                                    main_dict[i][0].insert(main_dict[i][0].index(t[wait_ind]),'p')
                                wait.append(0)                            
                        if(wait_list):
                            l_l = [len(x) for x in wait_list]
                            check = all(x == 3 for x in l_l)
                            if(check):
                                wait_list = list()
                        break
                if(not wait_list):
                    continue
        raw_table.add_row([sym_dict,raw_msg,num_list])         
        main_dict[line_num] = [num_list,invert, multiline,price,tax]
    
    table = PrettyTable(["num_list","invert","multiline","price","Tax"])
    # cleaning the num list ( C )
    for k_i,k in enumerate(main_dict.keys()):
        P = list()
        R = list()
        T = list()
        key_len = len(main_dict.keys())-1
        l = (len(main_dict[k][0])-1)
        i = -1
        while(i < l):
            if(i<0):
                i += 1
            if(i == (len(main_dict[k][0])-1)):
                break
            x = main_dict[k][0][i]
            if(x == 'P'):
                if(P):
                    if(main_dict[k][0][i-1] == 'P'):
                        main_dict[k][0].pop(i)
                        continue
                    else:
                        risk += f"More than one P in C Line:{main_dict[k][0]}, key:{k}\n"
                else:
                    if(main_dict[k][0][i+1] == 'R'):
                        main_dict[k][0].pop(i+1)
                    if(main_dict[k][0][i+1] == 'T'):
                        main_dict[k][0].pop(i)
                    
                    if(main_dict[k][0][i+1] in tax_list):
                        if((not(any(n in main_dict[k-1][0] for n in flags or tax_list))) and (main_dict[k-1][0]) ):
                            temp_t = [x for j,x in enumerate(main_dict[k][0]) if(x.isnumeric() or j == i )]
                            temp_t = temp_t[(temp_t.index(x)+1):]
                            if(len(temp_t) ==1):
                                temp_k = k-1
                                while((temp_k) and (not(any(n in main_dict[temp_k][0] for n in flags or tax_list))) and (main_dict[temp_k][0]) ):
                                    # add tax 
                                    main_dict[temp_k][1:] = main_dict[k][1:]
                                    # append tax
                                    main_dict[temp_k][0].append(main_dict[k][0][i+1])
                                    temp_k = temp_k-1
                        elif((not(any(n in main_dict[k+1][0] for n in flags or tax_list))) and (main_dict[k+1][0]) ):
                            temp_t = [x for j,x in enumerate(main_dict[k][0]) if(x.isnumeric() or j == i )]
                            temp_t = temp_t[(temp_t.index(x)+1):]
                            if(len(temp_t) ==1):
                                temp_k = k+1
                                while((temp_k) and (not(any(n in main_dict[temp_k][0] for n in flags or tax_list))) and (main_dict[temp_k][0]) ):
                                    # add tax 
                                    main_dict[temp_k][1:] = main_dict[k][1:]
                                    # append tax
                                    main_dict[temp_k][0].append(main_dict[k][0][i+1])
                                    temp_k = temp_k+1
                        main_dict[k][0].pop(i)
                        continue
                        # premultiplier = False
                        # i +=1
                        # continue
                    elif(i == l or not main_dict[k][0][i+1].isnumeric()):
                        premultiplier = False
                        main_dict[k][0].pop(i)
                        continue
                    temp_t = [x for j,x in enumerate(main_dict[k][0]) if(x.isnumeric() or j == i )]
                    temp_t = temp_t[(temp_t.index(x)+1):]
                    P.append([k,i])
                    premultiplier = temp_t[0]
            elif(x == 'R'):
                if(R or P or T):
                    if(main_dict[k][0][i-1] == 'R'):
                        main_dict[k][0].pop(i)
                        continue
                    elif(main_dict[k][0][i-1] == 'T'):
                        main_dict[k][0].pop(i)
                        continue
                    elif(main_dict[k][0][i-1] == 'P'):
                        main_dict[k][0].pop(i)
                        continue
                    elif(main_dict[k][0][i-1] in tax_list ):
                        main_dict[k][0].pop(i)
                        continue
                    elif(main_dict[k][0][i+1].isnumeric() or main_dict[k][0][i-1].isnumeric()):
                        i += 1
                        continue
                    else:
                        risk += f"Unrecignised format of R in C Line:{main_dict[k][0]}, key:{k}\n"
                else:
                    # if((t[1] == raw) and len(t) > 3 and all(x.isnumeric() for x in t if(x!=raw))):
                    #     price = True
                    #     invert = True
                    if((main_dict[k][0][i+1].isalpha()) and (main_dict[k][0][i+1] not in flags) and (main_dict[k][0][i+1] not in tax_list)):
                        main_dict[k][0].pop(i+1)
                        continue
                    if(len(main_dict.keys())>(k_i+1) and ('P' in main_dict[[x for x in main_dict.keys()][k_i+1]][0])):
                        main_dict[k][0].pop(i)
                        continue
                    if(any(m in tax_list for m in main_dict[k][0]) and (main_dict[k][0][-1] in tax_list) and (main_dict[k][0][-3]=='R') and (main_dict[k][0][-2].isnumeric()) ):
                        main_dict[k][0][-3] = main_dict[k][0][-1]
                        main_dict[k][0].pop()
                        continue
                    if(i == l or not main_dict[k][0][i+1].isnumeric()):
                        if((not any(x == 'R' for x in main_dict[k][0])) ):
                            main_dict[k][3] = False
                        main_dict[k][0].pop(i)
                        continue

                    if((k_i < key_len) and (len(main_dict[k_i+1][0])==2) and ('R' in main_dict[k_i+1][0]) and ((k_i+1) != key_len)):
                        main_dict[k][0].pop(i)
                        continue
                    if(i>0 and main_dict[k][0][i-1] in tax_list ):
                        main_dict[k][0].pop(i)
                        continue
                    main_dict[k][3] = True
                    R.append([k,i])
            elif(x == 'T'):
                if(T):
                    if(main_dict[k][0][i-1] == 'T'):
                        main_dict[k][0].pop(i)
                        continue
                    else:
                        risk += f"More than one T in C Line:{main_dict[k][0]}, key:{k}\n"
                else:
                    
                    if(main_dict[k][0][i+1] == 'R'):
                        main_dict[k][0].pop(i+1)
                        if(main_dict[k][0][i+1] == 'R'):
                            continue

                    elif(i == l or (not main_dict[k][0][i+1].isnumeric())):
                        total = False
                        main_dict[k][0].pop(i)
                        continue
                    # if(main_dict[k][0][i+1].isnumeric()):
                    total = main_dict[k][0][i+1]
                    T.append([k,i])
            i += 1
        if(main_dict[k][1] and not (main_dict[k][4] and (main_dict[k][0][-2] in tax_list) and main_dict[k][0][-1].isnumeric() and ((main_dict[k][4] in tax_len_dict.keys())  and int(tax_len_dict[main_dict[k][4]][0]))!=len(main_dict[k][0][-1]))):
            token = main_dict[k][0]
            token.reverse()
            for f in flags:
                if(f in token):
                    for i in range(0,len(token)-1):
                        if((i>0) and token[i-1] == 'R'):
                            token[i-1],token[i] = token[i],token[i-1] 

    for key in main_dict.keys():
        table.add_row([main_dict[key][0],main_dict[key][1],main_dict[key][2],main_dict[key][3],main_dict[key][4]])
    
    log(f"RAW TABLE \n{raw_table}")
    log(f"TABLE \n , Premultiplier = {premultiplier}, Total = {total} \n{table}")
    
    return main_dict,total,premultiplier,risk,CANCEL

##########################################################################################
    #                  				CALCULATION
##########################################################################################

def solve(main_dict:dict,total:int,premultiplier:int):
    
    c_list = list()
    c_ml_list = list()
    t_ml_list = list()
    t_list = list()
    t_tax_list = list()
    c_total = int(0)
    num_list = list()
    travel = [main_dict[k][0].copy() for k in main_dict.keys()]
    any_tax = any(m[4] for m in main_dict.values())
    prev_price_list = [x for y in travel for i,x in enumerate(y) if((len(y)>0 and ((len(y)-1)==i) and x.isnumeric()) or ((len(y)>0) and (i > 0) and (y[i-1]=='R')  ))]
    prev_price = [x for x in set(prev_price_list) if(prev_price_list.count(x)>1)]
    l = (len(travel) - 1)
    line_num = 0
    risk = ''
    if(premultiplier and int(premultiplier) != 0 ):
        in_table = PrettyTable(["line","Travel"])
        for _,t in enumerate(travel):
            if(t):
                if(not any(i in t for i in flags)):
                    if(any(i in t for i in tax_list)):
                        if(t[-1] in tax_list):
                            travel[_].append(premultiplier)
                        else:
                            continue
                    elif((_>1) and (main_dict[_-1][4] and main_dict[_-1][2])):
                        main_dict[_][4] = True
                        if(len(travel)>_):
                            if(any(t in travel[_+1] for t in tax_list)):
                                continue
                            elif(not any(i in t for i in flags)):
                                travel[_].append('R')
                                travel[_].append(premultiplier)
                        continue
                    elif((_<l) and (len(travel[_+1]) == 2) and (travel[_+1][0] == 'P' or travel[_+1][0] == 'R')):

                        if(travel[_+1][1] == premultiplier):
                            travel[_].append('R')
                            travel[_].append(premultiplier)
                        elif(travel[_+1][0] == 'R' and travel[_+1][1].isnumeric()):
                            travel[_].append('R')
                            travel[_].append(travel[_+1][1])
                        else:
                            continue
                    else:
                        travel[_].append('R')
                        travel[_].append(premultiplier)
            in_table.add_row([_,t])
        log(f"Travel Table \n {in_table}")
        
    if(not any_tax):
        for sl in travel:
            if(len(sl)>0):
                t = [x for x in sl if(x.isnumeric())]
                if(t):
                    t_ml_list.append(t)

                        
    timeout = time.time() + 0.5

    while(travel):
        if time.time() > timeout:
            risk += f"High Risk Infinite loop break status t_tax_list:{t_tax_list}, t_list:{t_list}"
            return False,False, risk
            # break

        token = lambda: travel[0]
        
        if(premultiplier and (len(token())>1)):
            if((flag in token() for flag in flags)):
                seq_check_list = [int(x) for x in token() if(x.isnumeric())]
                if((len(seq_check_list)>1) and all(abs(seq_check_list[i-1] - seq_check_list[i]) == 1 for i in range(1,len(seq_check_list))) and not(len(seq_check_list)==2)):
                    risk += "Unrecognizable format may sequence found \n"
        if(main_dict[line_num][4]):
            # FOR LEN OF NUM             
            if(main_dict[line_num][4]):
                while(travel and len(token()) == 1 and (token()[0] in tax_list) ):
                    tax_fun = main_dict[line_num][4]
                    tax = token()[0]
                    travel.pop(0)
                    line_num += 1
                    if(not travel):
                        return c_list,c_total,risk
                else:
                    tax = [x for x in token() if(x in tax_list)]
                    if(tax):
                        tax = tax[0]
                if((not t_tax_list) and token()):
                    while token():
                        if(token()[0].isnumeric()):
                            t_l = len(token()[0])
                            break
                        else:
                            if(token()[0] in tax_list):
                                tax = token()[0]
                                tax_fun = main_dict[line_num][4]
                            if((token()[0] == 'R')):
                                token().pop()
                            elif((token()[0]=='P')):
                                token().pop(0)
                                if(num_list):
                                    check = all(len(n) == len(num_list[0]) for n in num_list)
                                    num_list.append(token().pop(0))
                                    if(check):
                                        new_tax_list = globals()[main_dict[line_num][4]](num_list)
                                        for each in new_tax_list:
                                            c_total += (len(each)-1) * int(each[-1])
                                            c_list.append(each)
                                            t_tax_list = list()
                                        
                            if(token()):
                                token().pop(0)
                    if(len(travel[0]) == 0):
                        travel.pop(0)
                        line_num +=1
                        continue
                if(travel[0] and token()[0].isnumeric() and (tax in token()) and  not all(len(t)==len(token()[0]) for t in token()[:(token().index(tax))])):
                    risk+= f"Unidentified sequence of taxes {token()}"
                while((travel) and (token()) and (tax != token()[0]) and (token()[0] != 'R' and token()[0] != 'P' and token()[0] != 'T' ) and (t_l == len(token()[0]))):
                    if(any(t in token() for t in tax_list)):
                        tax_fun = main_dict[line_num][4]
                    if(not t_tax_list):
                        n = re.findall(r"\d+", ''.join(token()[0]))
                        if(n):
                            l = len(n[0])
                    if(token()[0] == tax):
                        token().pop(0)
                        if(not token()[0]):
                            line_num += 1
                            travel.pop(0)
                    if(l == len(token()[0]) and token()[0].isnumeric()):
                        t_tax_list.append(token().pop(0))
                        if(len(token())==0):
                            line_num += 1
                            travel.pop(0)
                        elif((len(token())==2) and (token()[1] == tax)):
                            tax_fun = main_dict[line_num][4]
                            t_tax_list.append(token().pop(0))
                            line_num += 1
                            travel.pop(0)
                            break
                        elif((len(token())==1) and token()[0].isnumeric() and(len(travel)>1) and travel[1]):
                            t_tax_list.append(token().pop(0))
                            line_num += 1
                            travel.pop(0)
                        elif((len(token())==1) and (tax == token()[0])):
                            token().pop(0)
                            if(not token() and len(travel)>0):
                                line_num += 1
                                travel.pop(0)
                        continue
                    else:
                        break
                # if(tax_fun )
                log(f"T_TAX_list::{t_tax_list},_______Token::{token() if len(travel) > 0 else 'NO token()'} tax_fun::{tax_fun}")
                if(t_tax_list):

                    if(any((len(x)  > 3 ) for x in t_tax_list)):
                        for j,y in enumerate(t_tax_list):
                            if(len(y) > 3):
                                if((not (j>0) )and (not(t_tax_list[j-1] in flags or tax_list))):
                                    risk += "High risk Invalid msg len of digit detected"
                    if((len(travel)>0) and travel[0] and token()[0].isnumeric()):
                        t_tax_list.append(token().pop(0))
                        if((len(t_tax_list)>1)):
                            new_tax_list = convert_tax_to_act_msg(tax_fun,t_tax_list)
                            # new_tax_list = globals()[tax_fun](t_tax_list)
                            for each in new_tax_list:
                                c_total += (len(each)-1) * int(each[-1])
                                c_list.append(each)
                                t_tax_list = list()
                        elif(not (len(t_tax_list)>1)):
                            risk += f"Len doest match Solve 1 t_tax_list:{t_tax_list}, t_list:{t_list}\n"

                    elif((len(travel)>0) and  (len(travel[0])>1) and (token()[0] == 'R' or token()[0] == 'P' or (token()[0] in tax_list and tax_fun == token()[0])) ):
                        token().pop(0)
                        if (travel[0] and not(token()[0].isnumeric())):
                            if(token()[0] == 'R' or token()[0] == 'P'):
                                token().pop(0)
                        t_tax_list.append(token().pop(0))
                        if((len(t_tax_list)>1)):
                            new_tax_list = convert_tax_to_act_msg(tax_fun,t_tax_list)
                            for each in new_tax_list:
                                c_total += (len(each)-1) * int(each[-1])
                                c_list.append(each)
                                t_tax_list = list()
                        elif(not (len(t_tax_list)>1)):
                            risk += f"Len doest match Solve 2 t_tax_list:{t_tax_list}, t_list:{t_list}\n"
                        if(travel[0] and not any(t in tax_list for t in travel[0])):
                            main_dict[line_num][4] = False
                            continue
                            

                    elif((len(travel)>0) and (len(travel[0])>0) and (token()[-1] not in tax_list)):
                        if((len(t_tax_list)>1)):
                            new_tax_list = convert_tax_to_act_msg(tax_fun,t_tax_list)
                            for each in new_tax_list:
                                c_total += (len(each)-1) * int(each[-1])
                                c_list.append(each)
                                t_tax_list = list()
                        elif(not (len(t_tax_list)>1)):
                            pass
                            # risk += f"Len doest match Solve 3 t_tax_list:{t_tax_list}, t_list:{t_list}\n"
                        else:
                            token().pop(0)
                            risk += "High Risk inside while token1"
                    elif(travel and not travel[0] and len(t_tax_list)>1):
                        # temp_price = t_tax_list[-1]
                        # for tra in travel:
                        #     if(len(tra)==0):
                        #         travel.pop(0)
                        #         continue
                        #     elif(len(tra)>1):
                        #         break
                        #     elif(len(tra)==1 and tra[0].isnumeric()):
                        #         temp_price = tra.pop(0)
                        #         break
                        new_tax_list = convert_tax_to_act_msg(tax_fun,t_tax_list)
                        for each in new_tax_list:
                            c_total += (len(each)-1) * int(each[-1])
                            c_list.append(each)
                            t_tax_list = list()
                                

                    if( (len(travel)>0) and (len(travel[0])!=0) and (token()[0] == tax) ):
                        token().pop(0)
                    elif( (len(travel)>0) and (len(travel[0])!=0) and (token()[0] in flags) ):
                        if(token()[0] == 'R'):
                            risk += "unclear R in Tax List"
                        token().pop(0)

            else:
                risk += f"More than one tax Solve t_tax_list:{t_tax_list}, t_list:{t_list}\n"
        elif(token()):
            if(not t_list):
                l = len((token()[0]))
            while( token() and (l== len(token()[0])) and (token()[0] not in flags) and (not((token()[0] in prev_price and (len(token())==1)) and (len(main_dict[line_num][0]) > 1)))) :
                t_list.append(token().pop(0))
                if(len(token()) == 0 and (len(travel)>1)):
                    t_c_flags = main_dict[line_num][1:]
                    t_f_flags = main_dict[line_num+1][1:]
                    line_num += 1
                    travel.pop(0)
                    if(t_c_flags == t_f_flags):
                        continue
                    else:
                        if((main_dict[line_num][4])):
                            #check_if_adding_them_to_tax
                            check_if_adding = False
                            if(int(total)>0 and (len(t_list)>1) and ( (len(travel[0])>1) and travel[0][-1].isnumeric() and travel[0][-2] in tax_list) ):
                                check_temp_total = int(total) - int(c_total)
                                check_temp_total_1 =  (len(t_list[:-1]) * int(t_list[-1]))
                                check_temp_total_1_list = list()
                                check_temp_total_1_list.extend(travel[0][:-2])
                                check_temp_total_1_list.append(travel[0][-1])
                                check_temp_total_1_list = convert_tax_to_act_msg(main_dict[line_num][4],check_temp_total_1_list)
                                for check_temp_total_1_list_t in check_temp_total_1_list:
                                    check_temp_total_1 += len(check_temp_total_1_list_t[:-1]) * int(check_temp_total_1_list_t[-1])
                                check_temp_total_1 -= int(check_temp_total) 

                                check_temp_total_2_list = deepcopy(t_list)
                                check_temp_total_2_list.extend(travel[0][:-2])
                                check_temp_total_2_list.append(travel[0][-1])
                                check_temp_total_2_list = convert_tax_to_act_msg(main_dict[line_num][4],check_temp_total_2_list)
                                check_temp_total_2 = int(0)
                                for check_temp_total_2_list_t in check_temp_total_2_list:
                                    check_temp_total_2 += len(check_temp_total_2_list_t[:-1]) * int(check_temp_total_2_list_t[-1])
                                check_temp_total_2 -= int(check_temp_total)
                                # print(f"her--------{check_temp_total_1},{check_temp_total_2}")

                                if((check_temp_total_1)<0 and check_temp_total_2>=0):
                                    check_if_adding = True
                                elif(check_temp_total_2<0 and check_temp_total_1>=0):
                                    check_if_adding = False
                                elif(check_temp_total_1<0 and check_temp_total_2<0):
                                    if(abs(check_temp_total_1)<abs(check_temp_total_2)):
                                        check_if_adding = False
                                elif(check_temp_total_1<check_temp_total_2):
                                    check_if_adding = False
                                else:
                                    check_if_adding = True
                            #if((t_list and (len(travel[0])>1) and not(any(t in token() for t in t_list))) and check_if_adding):
                            if(check_if_adding ):
                                for t in t_list:
                                    t_tax_list.append(t)
                                t_list = list()
                                t_l = len(t_tax_list[0])
                            tax_fun = main_dict[line_num][4]
                            break
                        elif(len(travel)>1 and ( not token())):
                            
                            if((main_dict[line_num+1][4])):
                                break
                            line_num += 1
                            travel.pop(0)
                        while((len(travel)>0) and token() and (l== len(token()[0])) and (token()[0] not in flags)):
                            t_list.append(token().pop(0))
                            # if(len(set(t_list))!= len(t_list)):
                            #     break
                        else:
                            break 
                # if(len(set(t_list))!= len(t_list)):
                #     break     
            log(f"T_LIST:: {t_list},____Token:{token() if len(travel) > 0 else 'NO remain'}")

            if(t_list):
                if(len(travel[0])>0 and travel[0][0] in tax_list and travel[0][1].isnumeric()):
                    for t in t_list:
                        t_tax_list.append(t)
                    t_list = list()
                    t_l = len(t_tax_list[0])
                    tax_fun = main_dict[line_num][4]
                    continue
                        
                temp_tax_here = list()
                if(total and len(travel)>1 and (len(travel[0])==0 or( len(travel[0])==1 and travel[0][0].isnumeric()) ) and  any((m[4] and len(m[0])==1 ) for m in list(main_dict.values())[line_num:])):
                    while(len(travel[0]) == 1 and travel[0][0].isnumeric()):
                        temp_tax_here.append(travel.pop(0))
                        line_num+=1
                    while( len(travel[0]) == 0 and len(travel)>1):
                        travel.pop(0)
                        line_num +=1
                    if(main_dict[line_num][4] and len(main_dict[line_num][0])==1):
                        t_tax_list = deepcopy(t_list)
                        for x in temp_tax_here:
                            t_tax_list.extend(x)
                        t_list = list()
                        continue
                    else:
                        for x in temp_tax_here:
                            line_num -=1
                            travel.insert(0,x)


                if(len(travel)>1)and((main_dict[line_num+1][4] and len(travel[0])==0) or (main_dict[line_num][4])):
                
                # if((len(travel)>1)and(main_dict[line_num+1][4]) and (len(travel[0])==0)):
                    if(len(t_list)<2):
                        risk += f"High Risk t_list single num unidentified {t_list}"

                    #this can be used but havent been used before so im commenting 
                    #if(main_dict[line_num][4] and len(token())==2):
                     #   t_tax_list = deepcopy(t_list)
                      #  t_list = list()
                       # continue

                    c_total += (len(t_list)-1)*int(t_list[-1])
                    c_list.append(t_list)
                    num_list.extend(t_list)
                    num_list.pop()
                    t_list = list()
                    continue
                # if(len(set(t_list))!= len(t_list)):
                #     c_total += (len(t_list)-1)*int(t_list[-1])
                #     c_list.append(t_list)
                #     num_list.extend(t_list)
                #     num_list.pop()
                #     t_list = list()
                #     if(len(travel)>0 and len(travel[0])>0 and travel[0][0]=='R' ):
                #         token().pop(0)
                #     if(len(travel)>0 and len(travel[0])>0):
                #         continue
                
                if((len(travel)>0) and (len(token())==1) and (token()[0] in prev_price)):
                    if(((len(travel)>1) and (travel[1]) and (travel[1][0]=='R'))):
                        t_list.append(token().pop(0))
                        travel.pop(0)
                        line_num += 1
                        travel[0].pop(0)
                    t_list.append(token().pop(0))
                    # c_total += (len(t_list)-1)*int(t_list[-1])
                    # c_list.append(t_list)                                                            
                    # num_list.extend(t_list)
                    # num_list.pop()
                    # t_list = list()

                if( any((len(x)  > 3 ) for x in t_list)):
                    if(len(travel)==1 or all(t==[] for t in travel)):
                        continue
                    for j,y in enumerate(t_list):
                        if(len(y) > 3):
                            if((j == 0 )):
                                risk += f"High risk Invalid msg len of digit detected:{y}"
                            elif(not(t_list[j-1] in flags or tax_list)):
                                risk += f"High risk Invalid msg len of digit detected:{y}"


                if((len(travel)>0) and token() and token()[0] != 'T'):
                    if((len(token())>1) and (token()[0].isalpha()) and token()[1].isnumeric()):
                        # check
                        token().pop(0)
                        t_list.append(token().pop(0))
                        #NEWLINE FOR CHECKING IF TOTAL NUMBER OF ITEM GIVEN TO MULTIPLY WITH ALL PRICE
                        if((len(travel[0])==1) and (travel[0][0].isnumeric()) and ((len(t_list)-1)==int(travel[0][0]))):
                            token().pop(0)
                        #ENDS
                        if(len(travel[0]) == 0 and all(len(l)==t_list[0] for l in t_list)):
                            for i,sl in enumerate(travel):
                                if(len(sl)==0):
                                    continue
                                elif((len(sl)==2) and sl[0]=='R'):
                                    travel[i].pop(0)
                                    t_list.append(travel[i].pop(0))
                                else:
                                    break
                        c_total += (len(t_list)-1)*int(t_list[-1])
                        c_list.append(t_list)
                        num_list.extend(t_list)
                        num_list.pop()
                        t_list = list()
                    # elif(token() and (len(t_list)>0) and (((l!=len(token()[0]))) and (len(token())==1)) and ((len(travel)>1) and(len(travel[1])>0 and travel[1][0].isnumeric()) and not (len(token()[0])==len(travel[1][0]) )) and is_price(token()[0])):
                    elif(((len(travel[0])==3) and travel[0][0].isnumeric() and travel[0][1]=='T') or ((len(travel)>0) and token() and (len(t_list)>0) and (((l!=len(token()[0]))) and (len(token())==1)) ) and is_price(token()[0] and not((len(travel)>1) and ((len(travel[1])>0) and travel[1][0].isnumeric()) and ( (len(travel[1][0]) == len(travel[0][0])))))):
                        # and (token()[0].isnumeric())
                        t_list.append(token().pop(0))
                        c_total += (len(t_list)-1)*int(t_list[-1])
                        c_list.append(t_list)
                        num_list.extend(t_list)
                        num_list.pop()
                        t_list = list()
                    # elif(token() and (len(t_list)>0) and (((l!=len(token()[0]))) and (len(token())==1)) and ((len(travel)>1) and(len(travel[1])>0 and travel[1][0].isnumeric()) and (len(token()[0])==len(travel[1][0]) )) and is_price(token()[0])):
                    # elif((len(travel)>0) and token() and (len(t_list)>0) and (((l!=len(token()[0])))  and ( ( len(token()[0])!=len(t_list[0]) )) and is_price(token()[0]))):
                    elif((len(travel)>0) and token() and (len(t_list)>0) and (((l!=len(token()[0])))  and ( ( len(token()[0])!=len(t_list[0]) )) and (token()[0]).isnumeric())  ):
                        dig = {1:[],2:[],3:[]}
                        dig[len(t_list[0])] = t_list
                        if(len(t_list[0])>3):
                            risk += f"risk occured of unkown pattern {travel[0]}\n"
                        
                        t_list = list()
                        while(token() and token()[0].isnumeric() and token()[0]!= 'R' and token()[0]!= 'T'):
                            dig[len(token()[0])].append(token().pop(0))
                            if(t_list and len(t_list[0])>3):
                                risk += f"risk occured of unkown pattern2nd {travel[0]} \n"
                                break
                            if((len(travel[0]) == 0) and (len(travel)>0) and any((len(sl)>0) for sl in travel )):
                                travel.pop(0)
                                line_num +=1
                                continue
                            elif((len(travel[0]) == 0) and (len(travel)==0)):
                                break
                        
                        tot = int(0)
                        lit = list()

                        if(travel[0] and token()[0] == 'R'):
                            token().pop(0)
                            r = str(int(token().pop(0)))
                            for k in dig.keys():
                                if(dig[k]):
                                    dig[k].append(r)
                                    lit.append(dig[k])
                                    tot += (len(dig[k])-1) * int(dig[k][-1])

                        elif(all(len(dig[k])==2 for k in dig.keys() if(dig[k]) )):
                            for k in dig.keys():
                                if(dig[k]):
                                    lit.append(dig[k])
                                    tot += ((len(dig[k])-1) * int(dig[k][-1]))
                        elif(travel[0] and token()[0] == 'T'):
                            token().pop(0)
                            t = int(token().pop(0))
                            t_len = int(0)
                            for k in dig.keys():
                                if(dig[k]):
                                    lit.append(dig[k])
                                    t_len += len(dig[k])
                            if(total and (((int(total)-c_total)/(t_len)).is_integer()) and ((int(total)-c_total)/(t_len)) ):
                                r = str(int((int(total)-c_total)/(t_len)))
                                for i,x in enumerate(lit):
                                    lit[i].append(r)
                                tot = str(int((int(total)-c_total)))
                            else:
                                risk += f"risk occured of unkown pattern3rd {travel[0]} \n"
                        else:
                            risk += "Unidentified Risk"

                        
                        
                        if(tot and lit):
                            c_list.extend(lit)
                            c_total += int(tot)

                    elif((len(travel)>0) and token() and (len(t_list)>0) and (((l!=len(token()[0]))) and not(is_price(token()[0]))) and (token()[0]!='R')):
                        t_t_list = list()
                        while(token() and token()[0]!= 'R'):
                            t_t_list.append(token().pop(0))
                            if(len(token())==0 and all((len(sl)==0) for sl in travel)):
                                break
                            elif(not token() and travel):
                                line_num += 1
                                travel.pop(0)
                        if((len(t_t_list) == 1) and all((len(sl)==0) for sl in travel)  ):
                            t_list.append(t_t_list[0])
                            c_total += (len(t_list)-1)*int(t_list[-1])
                            c_list.append(t_list)
                            t_list = list()
                            continue
                        if(not all(len(t)==len(t_t_list[0]) for t in t_t_list)):
                            risk+= f"Pattern not clear t_t_list{t_t_list} "
                        elif(token() and ((token()[0]=='R' and token()[1].isnumeric()) or (token()[0].isnumeric())) ):
                            if(token()[0] == 'R'):
                                token().pop(0)
                            t_t_list.append(token()[0])
                            t_list.append(token().pop(0))
                            c_total += (len(t_list)-1)*int(t_list[-1])
                            c_total += (len(t_t_list)-1)*int(t_t_list[-1])
                            c_list.append(t_list)
                            c_list.append(t_t_list)
                            num_list.extend(t_list)
                            num_list.pop()
                            num_list.extend(t_t_list)
                            num_list.pop()
                            t_list = list()
                        else:
                            risk+= f"Pattern not clear t_t_list{t_t_list} "
                        # t_t_list.append(token)
                        # c_total += (len(t_list)-1)*int(t_list[-1])
                        # c_list.append(t_list)
                        # num_list.extend(t_list)
                        # num_list.pop()
                        # t_list = list()
                    elif((len(t_list)>1) and (is_price(t_list[-1]) or (len(t_list[-1]) != len(t_list[-2])))):
                        c_total += (len(t_list)-1)*int(t_list[-1])
                        c_list.append(t_list)
                        num_list.extend(t_list)
                        num_list.pop()
                        t_list = list()
                    else:
                        if((len(travel)>0) and len(token()) == 0 and travel[1]):
                            line_num +=1
                            travel.pop(0)
                        else:
                            t_list.append(token().pop(0))
                            # token().pop(0)
                            # risk += f"Riskkkkkk inside while token2{token()}"
                        continue
                elif((len(travel)>0) and token() and token()[0] == 'T'):
                    #check_for_need_of_adding_new_num 
                    check_add = (len(t_list)-1) * int(t_list[-1])
                    if((check_add+c_total) == int(token()[1])):
                        c_total += (len(t_list)-1)*int(t_list[-1])
                        c_list.append(t_list)
                        num_list.extend(t_list)
                        num_list.pop()
                        t_list = list()
                    token().pop(0)
                    token().pop(0)
                else:
                    if((len(travel)>0) and token()):
                        t_list.append(token().pop(0))
                    if( t_list and any(sl for sl in travel) and (not (t_list[-1] in prev_price) )):
                        line_num +=1
                        travel.pop(0)
                    elif((len(t_list)>1) and (is_price(t_list[-1]) or (t_list[-1] in prev_price))  ):
                        c_total += (len(t_list)-1)*int(t_list[-1])
                        c_list.append(t_list)
                        num_list.extend(t_list)
                        num_list.pop()
                        t_list = list()
                    else:
                        if((len(travel)>0) and len(token()) == 0 and (len(travel)>1) and (travel[1])):
                            line_num +=1
                            travel.pop(0)
                        else:
                            if((len(travel)>0) and token()):
                                t_list.append(token().pop(0))
                            # risk += f"High Riskkkkkk inside while token1 {token()}, list {t_list}"
            else:
                if((len(travel)>0) and token()[0] in flags ):
                    if(token()[0] == 'R'):
                        # if((len(token())>1) and (token()[1].isnumeric()) and (int(token()[1])==c_total) and not(total)):
                        #     total = int(token()[1])
                        #     token().pop(0)
                        #     t_list.append(token().pop(0))
                        #     c_list.append(t_list)
                        #     t_list = list()

                        # print(token(),t_list,c_list)
                        if((len(token())>1) and (token()[1].isnumeric()) and ((int(token()[1])==c_total) or (c_total and (abs(c_total-int(token()[1]))/int(token()[1]))<=0.99) ) and not(total)):
                            total = int(token()[1])
                            token().pop(0)
                            # t_list.append(token().pop(0))
                            # c_list.append(t_list)
                            t_list = list()

                        else:
                            risk +=f"Riskkkk inside while token --{travel[0]}"
                    travel.pop(0)
                    line_num += 1
                elif(main_dict[line_num][4]):
                    continue
                else:                    
                    token().pop(0)
                    risk +=f"Riskkkkkkkk inside while token"

              
        if(travel):
            if(token()):
                continue
            travel.pop(0)
            line_num += 1
        else:
            break
    #print(f"{t_list},{travel},{c_total},{total},{(len(t_list) == 1) and (c_total<=int(t_list[0]))}")
    if(t_list):
        t_list = re.findall(r'\d+',' '.join(t_list))
        #if((len(t_list) == 1) and (c_total<=int(t_list[0]))):
        if((len(t_list) == 1) and (c_total and abs(c_total - int(t_list[0]))/c_total)<=0.99):
            if(not((total) and total.isnumeric())):
                total = int(t_list[0])
            # c_list.append(t_list)
            log(f"found total {total}")
        else:
            if(total and ((int(total)-c_total)>0) and all(len(x)==len(t_list[0]) for x in t_list) and (((int(total)-c_total)/len(t_list)).is_integer()))  and ( len(travel)==0 or all(t==[] for t in travel)) :
                t_list.append(str(int((int(total)-c_total)/len(t_list))))
                c_total += (len(t_list)-1) * int(t_list[-1])
                c_list.append(t_list)
                num_list.extend(t_list)
                num_list.pop()
                t_list = list()
            else:
                if(total):
                    c_total += (len(t_list)-1) * int(t_list[-1])
                    if(c_total == int(total) or (abs(c_total - int(total))/c_total<=0.99) ):
                        c_list.append(t_list)
                    else:
                        risk +="High Risk t_list not cleared1"
                else:
                    if((len(t_list)==1) and (c_total == int(t_list[0]))):
                        total = int(t_list[0]) 
                    else:
                        risk +="High Risk t_list not cleared2"
                t_list =list()
    if(t_tax_list):
        risk +="High Risk t_tax_list not cleared"
    # recheck
    # if(c_total )
    
    if((not(any(main_dict[k][4] for k in main_dict.keys() ))) and (total and int(total)!=int(c_total)) ):
        dig = {1:[],2:[],3:[],'oth':[]}
        # other_dig = dig['oth']
        for sl in c_list:
            for n in sl:
                if(premultiplier and len(n) in dig.keys() and (int(n)!=int(premultiplier))):
                    dig[len(n)].append(n)
                elif(not(premultiplier) and  len(n) in dig.keys() ):
                    dig[len(n)].append(n)
                else:
                    dig['oth'].append(n)
        new_temp_list = list()
        new_temp_total = int(0)
        if((premultiplier) and premultiplier.isnumeric()):
            for key in list(dig.keys())[:3]:
                if(dig[key]):
                    new_temp_total += len(dig[key]) * int(premultiplier)
                    dig[key].append(premultiplier)
                    new_temp_list.append(dig[key])
        else:
            new_len_ls = [len(dig[k]) for k in dig.keys() ]
            active_list_count = int(0)
            active_list_key = list()
            for l in zip(new_len_ls,dig.keys()):
                if(l[0]>0):
                    active_list_count +=1
                    active_list_key.append(l[1])

            if(active_list_count == 2 and any(len(set(dig[k]))==1 for k in active_list_key ) and not(all((len(set(dig[k]))==1 for k in active_list_key ))) ):
                for key_index,key in enumerate(active_list_key):
                    if(len(set(dig[key]))==1):
                        if(key_index == 0):
                            dig[active_list_key[1]].append(dig[key][0])
                            new_temp_list = dig[active_list_key[1]]
                            new_temp_total += (len(new_temp_list)-1) * int(new_temp_list[-1])
                        else:
                            dig[active_list_key[0]].append(dig[key][0])
                            new_temp_list = dig[active_list_key[0]]
                            new_temp_total += (len(new_temp_list)-1) * int(new_temp_list[-1])
                        # total = new_temp_total
        if(new_temp_list and new_temp_total):
            if(total and (int(c_total) != int(total)) and (int(total)==new_temp_total) and all(len(l)==len(set(l)) for l in new_temp_list)):
                c_list = new_temp_list
                c_total = new_temp_total
            elif(not(total) and (dig['oth']) and (len(set(dig['oth'])) ==1) and (int(dig['oth'][0])==int(premultiplier))):
                c_list = new_temp_list
                c_total = new_temp_total
                t_ml_list= list()
            elif(not(total) and not(dig['oth']) and all(len(set(dig[k])) == len(dig[k]) for k in dig.keys() if(dig[k])) and (int(c_total)%5 != 0) and (int(new_temp_total)%5 == 0 ) ):
                c_list = new_temp_list
                c_total = new_temp_total
                t_ml_list= list()
                risk += "Minor Risk for Premultiplier"
    

    if(total):
        total = int(total)
        if(c_total == int(total)):
            t_ml_list= list()
        else:
            st_list = False
            #slidetrack(c_list,total)
            if(st_list):
                if(all(n in main_num_list for sl in st_list for n in sl[:-1])):
                    log("BY SLIDETRCAK")
                    c_list= st_list
                    c_total = int(total)
                    t_ml_list= list()

    log(f"\nC_List::,{c_list},\nC_List_total::{c_total}\n")
    if(c_list and (len(c_list)>0) and not any_tax ):
        # all check
        t_c_list = [x for l in c_list for x in l ]
        if(all(len(x) == len(t_c_list[0]) for x in t_c_list[:-1])):
            t_total = (len(t_c_list)-1) * int(t_c_list[-1])
            if((t_total <= c_total) ):
                if( total and (abs((int(total) - int(c_total))/int(total))<=(0.99))):
                    pass
                elif(total and t_total <= int(total) ):
                    c_list = list()
                    c_list.append(t_c_list)
                    c_total = t_total
                elif(any(not is_price(x[-1]) for x in c_list)):
                    log("implement a risk stratregy here")
                    c_list = list()
                    c_list.append(t_c_list)
                    c_total = t_total
        # line by line check
        if(t_ml_list):
            t_l = list()
            c_l_list = list()
            c_l_total = int(0)
            if(all(len(l) == len(sl[0]) for sl in t_ml_list for l in sl[:-1])):
                for sl in t_ml_list:
                    if(len(sl) == 1):
                        t_l.extend(sl)
                    else:
                        t_l.extend(sl)
                        c_l_list.append(t_l)
                        c_l_total += (len(t_l)-1) * int(t_l[-1])
                        t_l = list()
                if(t_l and (int(t_l[0]) == int(total))):
                    t_l.pop(0)
            log(f"L_B_L_List::,{c_l_list},\n L_B_L_List_Total::{c_l_total}\n")
            if(c_l_total == c_total and (total and (c_l_total == int(total)))):
                    t_ml_list = list()
            elif(c_l_total == c_total and not(total)):
                    t_ml_list = list()

            if(c_l_list and (all(len(l) == len(sl[0]) for sl in c_l_list for l in sl[:-1])) and (not t_l) and all(is_price(l[-1]) for l in c_l_list) ):
                if(total and ( ((int(total) > c_l_total) and (c_l_total < c_total)) or (int(total) == c_l_total) )  and not(c_total == int(total)) and (abs(c_total - int(total)) > abs(c_l_total - int(total)) ) ):
                    log("using line by line")
                    c_list = c_l_list
                    c_total = c_l_total
                elif((not total) and (c_l_total < c_total) and (c_l_total%5==0)):
                    log("using line by line else")
                    c_list = c_l_list
                    c_total = c_l_total
        # multiline check
        if(t_ml_list):
            t_t_l = list()
            prev_len = int(0)
            c_ml_total = int(0)
            if(all(len(l) == len(sl[0]) for sl in t_ml_list for l in sl[:-1])):
                for sl in t_ml_list:
                    if(prev_len == 0):
                        t_t_l.extend(sl)
                        prev_len = len(sl)
                    else:  
                        if(((len(sl)-prev_len) != 0) and (len(sl[0]) == len(t_t_l[-1])) ) :
                            t_t_l.extend(sl)
                            c_ml_total += (len(t_t_l)-1) * int(t_t_l[-1])
                            c_ml_list.append(t_t_l)
                            t_t_l = list() 
                            prev_len = 0
                        elif( ((len(sl)-prev_len) == 0) and (len(sl[0]) == len(t_t_l[-1]))):
                            t_t_l.extend(sl)
                        elif((len(sl[0]) != len(t_t_l[-1]))):
                            c_ml_total += (len(t_t_l)-1) * int(t_t_l[-1])
                            c_ml_list.append(t_t_l)
                            t_t_l = list() 
                            t_t_l.extend(sl)
                            prev_len = len(sl)
                if(t_t_l and (int(t_t_l[0]) == int(total) or (len(t_t_l) ==1))):
                    t_t_l.pop(0)
                # check of no more than two number are same on list
                check_double = [True for sl in c_ml_list if(len(set(sl[:-1])) != len(sl[:-1]))]
                check_double = any(check_double)
                log(f"M_L_List::,{c_ml_list},\n M_L_List_total:: {c_ml_total}\n")   
                # log(f"ml.  \ n {all(len(sl) > 1 for sl in c_ml_list) and all(len(l)==len(sl[0]) for sl in c_ml_list for l in sl[:-1])} {(not t_t_l)} {all(is_price(l[-1]) for l in c_ml_list)} {not(check_double)}")
                if(all(len(sl) > 1 for sl in c_ml_list) and all(len(l)==len(sl[0]) for sl in c_ml_list for l in sl[:-1]) and (not t_t_l) and all(is_price(l[-1]) for l in c_ml_list) and (not(check_double)) ):
                    if(total and (((int(total) > c_ml_total) and (c_ml_total < c_total)) or (int(total) == c_ml_total) ) and not(c_total == int(total)) and (abs(c_total - int(total)) > abs(c_ml_total - int(total)) )):
                        log("using multiline")
                        c_list = c_ml_list
                        c_total = c_ml_total
                    elif((not total) and (c_ml_total < c_total)):
                        log("using multiline els")
                        c_list = c_ml_list
                        c_total = c_ml_total
        
                    
    return c_list,c_total,risk,total

##########################################################################################
    #                  				DRIVER
##########################################################################################
# columns = ["timestamp","message","result","total","risk_p","risk","acceptance","total_present","premultiplier","main_dict"]
def hla_calculate(msg:list, debug = False,market = False):

    action = str()
    data = dict()
    global tax_msg_flag
    tax_msg_flag = False

    main_dict,total,premultiplier,process_risk,cancel = text_process(msg)
    if(premultiplier):
        data["premultiplier"] = premultiplier
    result_list, result_total, risk, iden_total = solve(main_dict,total,premultiplier)
    total_risk = risk + process_risk
    acceptance = True
    if(result_list == [] or int(result_total) == 0):
        total_risk += "Unkown Message Falsify"
    for i,r in enumerate(result_list):
        if(len(r)<2):
            if((i == len(result_list)-1) and (int(r[0]) >= int(result_total))):
                acceptance = True
                result_list.pop()
            else:
                total_risk += f"High Risk Single number in list: {r}"
                acceptance = False
        if(int(r[-1]) == 0):
            acceptance = False
            total_risk += f"High Risk Price as Zero in List : {r}"
        if((len(r)>2) and not (all(len(x)== len(r[0]) for x in r[:-1]) and all(len(x) < 4 for x in r[:-1])) ):
            total_risk += f"Model Falsify output {r}"

    if((total or iden_total) and acceptance):
        if(result_total):
            if((total) and (total.isnumeric() and int(total)!=0)):
                data['present_total'] = int(total)
                if(int(result_total) == int(total)):
                    acceptance = True
                    action = "✅"
                elif( (str(total) in str(result_total)) or (str(result_total) in str(total))  ):
                    acceptance = True
                    action = f"✅ *Total = {result_total}*"
                elif( (abs((int(total) - int(result_total))/int(total))<=(0.99))):
                    acceptance = True
                    action = f"✅ *Total = {result_total}*"
                else:
                    acceptance = False
            elif(iden_total):
                data['iden_total'] = int(iden_total)
                if((int(result_total) == int(iden_total))):
                    acceptance = True
                    total = int(iden_total)
                    action = "✅"
                elif((abs((int(iden_total) - int(result_total))/int(iden_total))<=(0.99))):
                    acceptance = True
                    total = int(iden_total)
                    action = f"✅ Total = {result_total}"
                elif( str(total) in str(result_total)):
                    acceptance = True
                    action = f"✅ Total = {result_total}"
                    total = int(iden_total)
                else:
                    acceptance = False
            else:
                acceptance = False
        else:
            acceptance = False
    else:
        action = f"✅ *Total = {result_total}*"
        acceptance = True
    if(total_risk and (total_risk != '')):

        if((total or iden_total) and (((total) and int(result_total) == int(total))) or (iden_total and int(result_total) == int(iden_total))):
            if(('High' not in total_risk.split(' '))  and ('Falsify' not in total_risk.split(' ')) and ('Motor' not in total_risk.split(' ')) ):
                acceptance = True
            if(('Motor'  in total_risk.split(' '))):
                action = "✅✅"
                acceptance = False
            else:
                acceptance = False
        else:
            acceptance = False

    if((((market) and ('CL' in market)) or ('Cancel' in total_risk)) and acceptance):
        if(any(len(num)==2 for sl in result_list for num in sl[:-1])):
            action = "❌"
            acceptance = False
            total_risk += "2 digit term inside close market "
    flag = ''
    if(acceptance and result_total):
        for i,sl in enumerate(result_list):
            if(all(n in main_num_list for n in sl[:-1])):
                result_list[i][-1] = int(result_list[i][-1])
            else:
                acceptance = False
                action = "✅✅"
                total_risk += "Number not in main_num_list"


    if(debug):
        # global logger
        # logger.setLevel(logging.DEBUG)
        # if(logging.getLogger().handlers):
        #     stream_handler = logging.getLogger().handlers[0]  
        #     logging.getLogger().removeHandler(stream_handler)
        # handler = logging.StreamHandler()
        # logging.getLogger().addHandler(handler)

        # if(total_risk):
        #     print(f"_______________Risk_______________\n{total_risk}")
        if(acceptance):
            return action,result_list,result_total,total
        else:
            # print(f"False :: List:{result_list},,Total:{result_total}")
            return action,False,False,total
    
    if(acceptance and result_total):
        if((int(result_total)>31000) and (action!="✅")):
            flag = 'amt'
            acceptance = False
            action = "✅✅"
    
    if(total_risk):
        data["risk"] = total_risk
        # print(f"_______________Risk_______________\n{msg}\nTotal_Risk::{total_risk}\n______________________________")
    
    if(cancel):
        data["cancel"] = True
        if(acceptance):
            action = "✅🔴"
    # print(f"List:\n{result_list} \n Total:{result_total} \n Acc:{acceptance} \n RIsk::{total_risk}")
    if(tax_msg_flag):
        flag = 'sp'
    elif('Motor' in total_risk):
        flag = 'motor'
    if(flag):
        data['flag'] = flag
    if(acceptance or flag =='amt'):
        return action,result_list,result_total,data,flag
    else:
        data["result"] = result_list
        data["total"] = result_total
        if(action and (action == '❌')):
            return action,False,False,data,flag
        else:
            return "✅✅",False,False,data,flag
    
