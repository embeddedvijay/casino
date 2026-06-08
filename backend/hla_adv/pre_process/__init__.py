from ..constants.text import text_dict,tax_list,skip_words,reject_msg,flags,replace_dict
from .word_process import confine_words,isreject
from .symbol_process import confine_symbol
import re
from copy import deepcopy
import unicodedata

class pre_processing():

    re_exp = str()
    def __init__(self) -> None:
        match_words = sorted([x for values in list(text_dict.values()) for x in values],key=lambda x: len(x),reverse=True)
        skip_words.extend(match_words)
        global re_exp
        re_exp = rf"\d+|{'|'.join(skip_words)}|[a-zA-Z]+|/-|[^\W\d_][\u0900-\u097F]*|\S"
    
    def clean(self,lines:list)->list:
        new_lines = []
        for line in lines:
            new_line = []
            for word in line:
                if word.isalpha():
                    if word in [*tax_list,*flags]:
                        new_line.append(word)
                    elif word in replace_dict.keys():
                        new_line.extend(replace_dict[word])
                    if word in reject_msg:
                        self.REJECT = True
                        self.risk(f"Reject Message Found:: {line}")
                        if word in ["HALF","FULL","SANG"]:
                            self.data["Sangam"] = True
                        return []
                else:
                    new_line.append(word)
            if new_line:
                new_lines.append(new_line)
        return new_lines
        
    def pre_process(self,message:str):
        translation_table = str.maketrans('०१२३४५६७८९', '0123456789')
        message = message.translate(translation_table)
        lines = [re.findall(re_exp,unicodedata.normalize('NFKD', line.lower()),re.IGNORECASE) for line in message.split('\n') if line]  
        # lines,self.CANCEL,self.RISK = confine_words(self,lines)
        lines,self.CANCEL = confine_words(self,lines)
        self.word_process = deepcopy(lines)
        # print("Step 1::word:",lines,'\n')
        

        lines = confine_symbol(lines)
        self.sym_process = deepcopy(lines)
        # print("Step 2::sym:",lines,'\n')

        lines = self.clean(lines)
        self.clean_process = deepcopy(lines)
        # print("Step 3::clean:",lines,'\n')

        return lines




