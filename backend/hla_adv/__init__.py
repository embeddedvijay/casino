import logging
from .pre_process import pre_processing
from .text_process import text_processing
from .calculation import calculate
from .validation import validate
from prettytable import PrettyTable
from copy import deepcopy
from .hla_beta.hla_beta import hla_calculate as bhla
from .constants.number import isprice
from .constants.text import text_dict
import re
import traceback


class hla(pre_processing,text_processing,calculate,validate):
    def __init__(self,debug:bool) -> None:
        super().__init__()
        self.debug = debug
        self.logger = logging.getLogger()
        if(debug):
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)
        self.log = self.logger.debug

    def reset_logger(self):
        if self.logger.handlers:
            stream_handler = self.logger.handlers[0]  
            self.logger.removeHandler(stream_handler)
        handler = logging.StreamHandler()
        self.logger.addHandler(handler)

    def risk(self,info:str):
        self.RISK += '\n' + str(info)

    def reset_flags(self):
        self.REJECT = False
        self.CANCEL = False
        self.RISK = ""
        self.PREMULTIPLIER = []
        self.AMOUNTS = []
        self.GIVEN_TOTAL = []
        self.IDEN_TOTAL = 0
        self.INSIDE = set()
        self.data = {}
        self.res_total = 0
        self.res_list = []
        self.temp_res = []
        ###DEBUG FLAGS####
        self.word_process = []
        self.sym_process = []
        self.clean_process = []
        self.processed = []
    

    def run(self,message:str,market_name='OP'):
        self.reset_flags()
        lines = self.pre_process(message)
        self.num_list = self.text_process(lines)
        # print(self.lines)
        self.processed = deepcopy(self.num_list)
        self.solve()

        verified = self.verify(self.res_list)
        action,flag = self.process_result(market_name)
        # print("Message\n",message)
        print(self.data)
        if self.debug:
            return self.debug_out(action)
        elif verified and not self.REJECT or flag =='amt':
            return action,self.res_list,self.res_total,self.data,flag
        else:
            self.data["result"] = self.res_list
            self.data["total"] = self.res_total
            if(action and (action == '❌')):
                return action,False,False,self.data,flag
            else:
                return "✅✅",False,False,self.data,flag
            
    def debug_out(self,action):
        table = PrettyTable()

        def column_pad(*columns):
            max_len = max([len(c) for c in columns])
            for c in columns:
                c.extend(['']*(max_len-len(c)))
        
        column_pad(self.word_process,self.sym_process ,self.clean_process ,self.processed )
        
        table.add_column("Word-Process",self.word_process)
        table.add_column("Sym-Process",self.sym_process)
        table.add_column("Pre-Processed",self.clean_process)
        table.add_column("Processed Message",self.processed)

        print(table)
        # print(f"{self.word_process}\n,self.clean_process")
        # print(self.processed)
        print(f"INSIDE.  -- {self.INSIDE}")
        self.reset_logger()
        if(self.RISK):
            print(f"_______________Risk_______________\n{self.RISK}")
        
        if self.GIVEN_TOTAL:
            self.GIVEN_TOTAL = int(self.GIVEN_TOTAL[-1])

        if(not self.REJECT):
            return action,self.res_list,self.res_total,self.GIVEN_TOTAL
        else:
            print(f"False :: List:{self.res_list},,Total:{self.res_total}")
            return action,False,False,self.GIVEN_TOTAL



HLA = hla(debug=False).run
def adv_run(message:str,market='OP'):
    beta = True
    new = True
    try:
        msg = message
        msg = [re.findall(r'\d+',x) for x in msg.split('\n')]

        if len(msg[-1]) == 1:
            can_be_tot = int(msg[-1][-1])
        else:
            can_be_tot = 0
    except:
        traceback.print_exc()
        can_be_tot = 0

    #if not any(x in message for x in ('(',')')):
    try:
        action,result_list,total,hla_analysis,flag = bhla(message,market=market)
        action_,result_list_,result_total_,message_total = bhla(message,debug = True)
        if action == "✅✅":
            beta = False
    except:
        print("e1")
        action,result_list,total,hla_analysis,flag = "✅✅",False,False, {"hla_failure" : True },''
        beta = False

    try:
        ACTION,RESULT_LIST,TOTAL,HLA_ANALYSIS,FLAG = HLA(message,market)
        if ACTION == "✅✅":
            new = False
    except:
        ACTION,RESULT_LIST,TOTAL,HLA_ANALYSIS,FLAG = "✅✅",False,False, {"hla_failure" : True },''
        new = False
        print("e2")

    

                
    # else:
    #     action,result_list,total,hla_analysis,flag = "✅✅",False,False, {"hla_failure" : True },''
    #     beta = False
    #     ACTION,RESULT_LIST,TOTAL,HLA_ANALYSIS,FLAG = "✅✅",False,False, {"hla_failure" : True },''
    #     new = False



    if beta and new:
        if message_total:
            if str(message_total) in str(TOTAL) :
                HLA_ANALYSIS["model"] = "new"
                return ACTION,RESULT_LIST,TOTAL,HLA_ANALYSIS,FLAG
            
            if str(message_total) in str(total):
                hla_analysis["model"] = "beta"
                return action,result_list,total,hla_analysis,flag
            
            final_total = min((t for t in [total,TOTAL]), key=lambda x: abs(x - int(message_total)),default=TOTAL)

            if final_total == TOTAL:
                HLA_ANALYSIS["model"] = "new"
                return ACTION,RESULT_LIST,TOTAL,HLA_ANALYSIS,FLAG
            else:
                hla_analysis["model"] = "beta"
                return action,result_list,total,hla_analysis,flag
        if can_be_tot:
            if str(can_be_tot) in str(TOTAL) :
                HLA_ANALYSIS["model"] = "new"
                return ACTION,RESULT_LIST,TOTAL,HLA_ANALYSIS,FLAG
            
            if str(can_be_tot) in str(total):
                hla_analysis["model"] = "beta"
                return action,result_list,total,hla_analysis,flag
            
            
            final_total = min((t for t in [total,TOTAL]), key=lambda x: abs(x - int(can_be_tot)),default=TOTAL)

            if final_total == TOTAL:
                HLA_ANALYSIS["model"] = "new"
                return ACTION,RESULT_LIST,TOTAL,HLA_ANALYSIS,FLAG
            else:
                hla_analysis["model"] = "beta"
                return action,result_list,total,hla_analysis,flag
            
        elif ACTION == '✅':
            HLA_ANALYSIS["model"] = "new"
            return ACTION,RESULT_LIST,TOTAL,HLA_ANALYSIS,FLAG

            
        if action == '✅':
            hla_analysis["model"] = "beta"
            return action,result_list,total,hla_analysis,flag
        
        
        

        
        if total and all(isprice(x[-1]) for x in result_list) and TOTAL and all(isprice(x[-1]) for x in RESULT_LIST) :
            #hla_analysis["model"] = "beta"
            #return action,result_list,total,hla_analysis,flag
            HLA_ANALYSIS["model"] = "new"
            return ACTION,RESULT_LIST,TOTAL,HLA_ANALYSIS,FLAG
            # if total<TOTAL:
            #     hla_analysis["model"] = "beta"
            #     return action,result_list,total,hla_analysis,flag
            # else:
            #     HLA_ANALYSIS["model"] = "new"
            #     return ACTION,RESULT_LIST,TOTAL,HLA_ANALYSIS,FLAG


        if total and all(isprice(x[-1]) for x in result_list):
            hla_analysis["model"] = "beta"
            return action,result_list,total,hla_analysis,flag
        
        if TOTAL and all(isprice(x[-1]) for x in RESULT_LIST):
            HLA_ANALYSIS["model"] = "new"
            return ACTION,RESULT_LIST,TOTAL,HLA_ANALYSIS,FLAG
        
        
        
        hla_analysis["model"] = "beta"
        return action,result_list,total,hla_analysis,flag
    
    elif new and all(isprice(x[-1]) for x in RESULT_LIST):
        HLA_ANALYSIS["model"] = "new"
        return ACTION,RESULT_LIST,TOTAL,HLA_ANALYSIS,FLAG

    elif beta and new:
        hla_analysis["model"] = "beta"
        return action,result_list,total,hla_analysis,flag
    
    else:
        if HLA_ANALYSIS.get("Sangam",False):
            return "✅✅",False,False, {"hla_failure" : True,"Sangam":True },''
        return "✅✅",False,False, {"hla_failure" : True },''
