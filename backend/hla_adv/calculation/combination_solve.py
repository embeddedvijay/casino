from ..constants.text import tax_list
from .common_functionality import MP,PANAL,FM


class tax_solve:
    def __init__(self) -> None:
        pass
    
    def tax_calculate(self,line:list):
        if line[-2] in tax_list:
            tax = line[-2]
            num_line = [x for x in line if x.isnumeric()]
        else:
            self.risk(f"cant solve unkonw tax positon line:{line}")

        if 'MP' in tax:
            self.INSIDE.add('MP')
            for i in range(2,len(tax),2):
                tax_name = tax[i:i+2]
                out_list,out_price = MP(tax_name,num_line)
                self.res_list.extend(out_list)
                self.res_total += out_price

        elif tax == 'FM':
            self.INSIDE.add('FM')
            out_list,out_price = FM('FM',num_line)
            self.res_list.extend(out_list)
            self.res_total += out_price

        elif 'COM' in tax:
            for i in range(3,len(tax),2):
                tax_name = 'COM' + tax[i:i+2]
                self.INSIDE.add(tax_name)
                out_list,out_price = PANAL(tax_name,num_line)
                self.res_list.extend(out_list)
                self.res_total += out_price

        elif tax == 'CP':
            self.INSIDE.add('CP')
            tax_name = 'CP'
            out_list,out_price = PANAL(tax_name,num_line)
            self.res_list.extend(out_list)
            self.res_total += out_price

        else:
            temp_ran = False
            for i in range(0,len(tax),2):
                temp_ran = True
                tax_name = tax[i:i+2]
                self.INSIDE.add(tax_name)
                out_list,out_price = PANAL(tax_name,num_line)
                self.res_list.extend(out_list)
                self.res_total += out_price
            if not temp_ran:
                self.risk(f"cant solve unkonw tax positon line:{line}")


