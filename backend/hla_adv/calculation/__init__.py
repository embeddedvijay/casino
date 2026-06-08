
from .combination_solve import tax_solve
from .number_solve import number
from ..constants.text import tax_list
from ..constants.number import main_num_list,isprice
from .common_functionality import get_total
from .line_by_line import line_by_line
from .multi_by_multi import multi_by_multi

class calculate(tax_solve,number,line_by_line,multi_by_multi):
    def __init__(self) -> None:
        pass

    def solve(self)->None:
        while self.num_list:
            line = self.num_list.pop(0)
            
            if any(x in tax_list for x in line):
                self.tax_calculate(line)
            else:
                self.num_calculate(line)
        
        if len(self.temp_res)>1 and all(len(x)==len(self.temp_res[0]) and x in main_num_list for x in self.temp_res[:-1] ):
            self.res_total += get_total(self.temp_res[:-1],self.temp_res[-1])
            temp_list = [x for x in line[:-1] if x.isnumeric()]
            temp_list.append(int(self.temp_res[-1]))
            self.res_list.append(temp_list)
            self.temp_res = []
        #print(self.res_list,self.res_total)
        lbl,lbl_list,lbl_total = self.lbl_solve()
        #print(self.lbl_solve())
        mbm,mbm_list,mbm_total = self.mbm_solve()
        #print(self.mbm_solve())

        totals = [lbl_total,mbm_total,self.res_total]
        checks = [lbl,mbm,True]
        total = 0
        # print(self.GIVEN_TOTAL,self.IDEN_TOTAL,self.res_total,self.res_list)
        # print(self.res_list)
        # print(self.res_total)

        gt , it = 0,0
        if self.GIVEN_TOTAL:
            total = min((total for total,check in zip(totals,checks) if check), key=lambda x: abs(x - int(self.GIVEN_TOTAL[-1])),default=self.res_total)
            gt = self.GIVEN_TOTAL[-1]
        elif self.IDEN_TOTAL:
            total = min((total for total,check in zip(totals,checks) if check), key=lambda x: abs(x - int(self.IDEN_TOTAL)),default=self.res_total)
            it = self.IDEN_TOTAL

        elif mbm and lbl and lbl_total and lbl_total==mbm_total :
            total = lbl_total
            self.RISK = ''
            self.REJECT = False
        #print(total)



        if not any(str(x)==str(self.res_total) for x in [gt,it]):
            if mbm and not lbl and isprice(mbm_total) :
                total = mbm_total
                if lbl_total==mbm_total:
                    self.RISK = ""
                    self.REJECT = False

            if mbm and self.res_total==mbm_total :
                total = mbm_total
                self.RISK = ""
                self.REJECT = False
                self.res_list = mbm_list
            elif lbl and self.res_total==lbl_total :
                total = lbl_total
                self.RISK = ""
                self.REJECT = False
                self.res_list = lbl_list

        


        if total:
            if (total == lbl_total and lbl) :
                self.log("By LBL")
                self.res_total = lbl_total
                self.res_list = lbl_list
            elif total == self.res_total:
                pass
            elif total == mbm_total and mbm:
                self.log("By MBM")
                self.res_total = mbm_total
                self.res_list = mbm_list
        # if self.REJECT==False:
        #     print(gt,'ppppp',abs(int(500)-total)/int(500) )
        #     if gt and abs(int(gt)-total)/int(gt) /100 > 50:
        #         self.REJECT= True
        #         self.RISK += f"Total diff {gt[0]} : {abs(int(gt[0])-int(total))/int(gt[0])/100 }  "
        #     elif it and abs(int(it)-total)/int(it) /100 > 50:
        #         self.REJECT= True
        #         self.RISK += f"Total diff {it} : {abs(int(it)-total)/int(it)/100  } "

                
        print(self.lbl_solve())
        print(self.mbm_solve())

        return



    
