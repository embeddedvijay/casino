from ..constants.number import main_num_list
from ..constants.text import tax_list
from ..constants.number import isprice
type = {
    1:"SINGLE",
    2:"JODI",
    3:"PANAL"
}
class validate:
    def __init__(self) -> None:
        pass

    def verify(self,res_list:list)->bool:
        if res_list:
            for sl in res_list:
                if len(sl)>1 and sl[-1] and all(x in main_num_list for x in sl[:-1]) and isinstance(sl[-1],int) and all(len(x)== len(sl[0]) for x in sl[:-1]):
                    self.INSIDE.add(type[len(sl[0])])
                    continue
                else:
                    self.risk(f"High Risk Something went wrong in here {sl}")
                    self.REJECT = True
                    return False
        else:
            self.risk(f"High Risk Empty res_list")
            self.REJECT = True
            return False
        return True
        
    def process_result(self,market_name:str)->tuple[str,str]:
        total = self.GIVEN_TOTAL [-1] if self.GIVEN_TOTAL else 0
        iden_total = self.IDEN_TOTAL
        result_total = self.res_total
        flag = ''
        action = ''

        if((total or iden_total) and not self.REJECT):
            if(result_total):
                if((total) and (total.isnumeric() and int(total)!=0)):
                    self.data['present_total'] = int(total)
                    if(int(result_total) == int(total)):
                        action = "✅"
                    elif( (str(total) in str(result_total)) or (str(result_total) in str(total))  ):
                        action = f"✅ *Total = {result_total}*"
                    elif( (abs((int(total) - int(result_total))/int(total))<=(0.60))):
                        action = f"✅ *Total = {result_total}*"
                    else:
                        print("yes")
                        self.REJECT = True
                elif(iden_total):
                    self.data['iden_total'] = int(iden_total)
                    if((int(result_total) == int(iden_total))):
                        total = int(iden_total)
                        action = "✅"
                    elif((abs((int(iden_total) - int(result_total))/int(iden_total))<=(0.60))):
                        total = int(iden_total)
                        action = f"✅ Total = {result_total}"
                    elif( str(total) in str(result_total)):
                        action = f"✅ Total = {result_total}"
                        total = int(iden_total)
                    else:
                        print("yes2")
                        self.REJECT = True
                else:
                    print("yes3")
                    self.REJECT = True
            else:
                print("yes4")
                self.REJECT = True
        elif not self.REJECT:
            action = f"✅ *Total = {result_total}*"
        
        if ('CL' in market_name) and not self.REJECT :
            if(any(len(num)==2 for sl in self.res_list for num in sl[:-1])):
                action = "❌"
                self.REJECT = True
                self.risk("2 digit term inside close market ")

        if(not self.REJECT ):
            if((int(result_total)>31000) and (action!="✅")):
                flag = 'amt'
                print("amt false")
                self.REJECT = True
                action = "✅✅"
            elif self.GIVEN_TOTAL and self.GIVEN_TOTAL[-1] not in str(self.res_total) and not all(isprice(x[-1]) for x in self.res_list):
                flag = 'total'
                print("total false")
                self.REJECT = True
                action = "✅✅"

        
        if(self.RISK):
            self.data["risk"] = self.RISK
            action = "✅✅"
            # print(f"_______________Risk_______________\n{msg}\nTotal_Risk::{total_risk}\n______________________________")
        
        if(self.CANCEL):
            self.data["cancel"] = True
            if(not self.REJECT):
                action = "✅🔴"
        # print(f"List:\n{result_list} \n Total:{result_total} \n Acc:{acceptance} \n RIsk::{total_risk}")
        if any(x in tax_list for x in [self.INSIDE]):
            flag = 'sp'
            
        # elif('Motor' in total_risk):
        #     flag = 'motor'

        if(flag):
            self.data['flag'] = flag
        
        return action,flag

        
        







        

