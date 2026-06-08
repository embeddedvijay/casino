from ..constants.number import mpdp_list,mpsp_list,tax_num_dict,fm_jodis,fm_pannas
from copy import deepcopy

def get_total(local_result:list,price:str)->int:
    price = int(price)
    amt = len(local_result) * price
    return amt


def MP(tax_name:str,num_line:list):
    store_list = mpdp_list
    if tax_name == 'SP':
        store_list = mpsp_list
    
    def get_list_amt(num_list:list,price:str):
        local_result = list()
        for x in num_list:
            while(len(x)>3):
                temp = [num for num in store_list if(all(digit in x for digit in num))]
                local_result.extend(temp)
                x = ''.join(x[1:])
            local_result = list(set(local_result))
        amt = get_total(local_result,price)
        local_result.append(int(price))
        return [local_result],amt
    
    result,amount = get_list_amt(num_line[:-1],num_line[-1])
    return result,amount

def PANAL(tax_name:str,num_line:list):
    if len(num_line)>3:
        multipliers = {
            'COMSP': 36,
            'COMDP': 18,
            'CP': 10,
            'SP': 12,
            'DP': 9,
            'TP': 1
        }
        if tax_name in multipliers:
            if int(num_line[-1]) == multipliers[tax_name] * len(num_line[:-3]) * int(num_line[-2]):
                num_line = num_line[:-1]

    def get_list_amt(num_list:list,price:str):
        local_result = list()
        temp_total = 0

        for x in num_list:
            temp_local_result = deepcopy(tax_num_dict[tax_name][x])
            temp_total += get_total(temp_local_result,price)
            temp_local_result.append(int(price))
            local_result.append(temp_local_result)

        amt = temp_total
        return local_result,amt

    result,amount = get_list_amt(num_line[:-1],num_line[-1])
    return result,amount

def FM(tax_name:str,num_line:list):
    if len(num_line[0]) == 2:
        fm_list = fm_jodis
    else:
        fm_list = fm_pannas

    def get_list_amt(num_list:list,price:str):
        local_result = list()
        temp_total = 0

        for x in num_list:
            for sub_list in fm_list:
                if x in sub_list:
                    temp_local_result = deepcopy(sub_list)
                    temp_total += get_total(temp_local_result,price)
                    temp_local_result.append(int(price))
                    local_result.append(temp_local_result)

        amt = temp_total
        return local_result,amt
    
    result,amount = get_list_amt(num_line[:-1],num_line[-1])
    return result,amount
