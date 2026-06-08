#EVERY PATTERN IN SMALL LETTERS ONLY
text_dict = {
    'MP': ['motar','motor','moter','mp','m p','mortar','moterrr','मोटार'],
    'HALF' : ['half','हॉफ'],
    'FULL' : ['full','फूल'],
    'SANG' : ['sangam','sangm','संगम'],
    'COM' : ['com','complete','common','comm'],
    'CANCEL' : ['cancel', 'canceled', 'कैन्सल्', 'कैन्सल', 'कैंसिल', 'कंस','can'],
    'ASP' : ['allsp','all sp'],
    'ADP' : ['alldp','all dp'],
    'ATP' : ['alltp','all tp'],
    'P' : ['all', 'aal', 'sabhi', 'every', 'each', 'ich', 'into', 'intu', 'per', 'सर्व'],
    'R' : ['r', 'rr', 'rs', 'rss','rrr', 'ru', 'at', 'at', 'रु', 'र', '₹', '₹', 'रुपया','/-','me','se','each'],
    'T' : ['total','टोटल','vepar','tt','tot','t','tota','totel','ttl','to','टो','totalamount','toyal','toal','totally','totil','totli','tutal'],
    'PANNA' : ['panal','panel','panil','panel','panna','patta','patte'],
    'SINGLE' : ['single','singal','sutta',],
    'DOUBLE' : ['double','doble','jodi'],
    'TRIPLE' : ['tip','teen','tin','triple','tripal'],
    'FM' : ['fm','f m', 'fmily','family', 'fhmily', 'fam', 'fhamly', 'femeli', 'femliy','femely','फॅमिली','fan','fmv','fml','fmly','fmly','fameli','फैमिली'],
    'SP' : ['sp','s p','kisp','s.p','एसपी'],
    'DP' : ['dp','d p','डीपी','kidp','d.p'],
    'TP' : ['tp','t p'],
    'CP' : ['cp','c p'],
    'SPDPTP' : ['spdptp','sp dp tp','dptpsp','dp tp sp','tpspdp','tp sp dp','sp, dpt'],
    'SPDP' : ['spdp','sp dp','dpsp','dp sp'],
    'SPTP' : ['sptp','sp tp','tpsp','tp sp'],
    'DPTP': ['dptp','dpt','dp tp','tpdp','tp dp'],
    'MPSPDP': ['motorspdp','motordpsp','mpspdp','motor sp dp','motor dpsp','motor mpsp', 'mp sp dp'],
    'MPSP' : ['mpsp','motor sp','spmp','ms'],
    'MPDP' : ['mpdp','motor dp','dpmp','md'],
    'COMSP' : ['comsp','commsp','com sp','comm sp','comman sp','comm sp'],
    'COMDP' : ['comdp','commdp','com dp','comm dp','comman dp','comm dp'],
    'COMSPDP' : ['comspdp','comm spdp','com sp dp','comsp dp','comman sp dp'], 
    'HFSANG' : ['halfsangam','h/s','hs','half sangam'],
    'FLSANG' : ['fullsangam','f/s','fs','full sangam'],
}
skip_words = ["n8","ni8","tim","raj","taim","n..t","na8","0pen"]
#COMBINE DICTINOARY FOLLOWS THE SAME ORDER TO COMBINE IN WHICH ITEMS ARE ARRANGED LINE BY LINE PRIORITY
combine_dict = {
    # 'SP' : ['SINGLE','PANNA'],
    # 'DP' : ['DOUBLE','PANNA'],
    # 'TP' : ['TRIPLE','PANNA'],
    'MPSPDP':['MP','SP','DP'],
    'COMSPDP' : ['COM','SP','DP'],
    'MPDPSP':['MP','SPDP'],
    'MPSP' : ['MP','SP'],
    'MPDP' : ['MP','DP'],
    'SPDPTP' : ['SP','DP','TP'],
    'SPDP' : ['SP','DP'],
    'SPTP' : ['SP','TP'],
    'DPTP': ['DP','TP'],
    'COMSPDP' : ['COM','SPDP'],
    'COMSP' : ['COM','SP'],
    'COMDP' : ['COM','DP'],
    'HFSANG' : ['SANG','HALF'],
    'FLSANG' : ['SANG','FULL'],
    'ASP' : ['P','SP'],
    'ADP' : ['P','DP'],
    'ATP' : ['P','TP'],
}

replace_dict = {
    'ASP' : ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'SP'],
    'ADP' : ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'DP'],
    'ATP' : ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'TP'],
    'MPDPSP' : ['MPSPDP'],
}

flags = ['R','P','T']
tax_list = ['SP','DP','TP','COMSPDP','COMSP','COMDP','SPDPTP','SPDP','SPTP','DPTP','FM','CP','MPSPDP','MPSP','MPDP']
frame_header_list = [*tax_list,'MP','PANNA','SINGLE','DOUBLE']
tax_group = {
    1 : ['SP','DP','TP','SPDPTP','SPDP','SPTP','DPTP','COMSP','COMDP'],
    2 : ['FM','CP'],
    3 : ['FM'],
    4 : ['MPSPDP','MPSP','MPDP']
}

reject_msg = ['HFSANG','FLSANG','MP','SANG','HALF','FULL','COM']

rs_sym_type = ['=','@','💸','💵','💴','💶','💷','💰','🤑','🏧','💳']

open_brackets = ['(','{','[','<']
close_brackets = [')','}',']','>']
repeated_no_price_sym = ['"']
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

