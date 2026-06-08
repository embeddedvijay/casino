from ..constants.text import frame_header_list,rs_sym_type,tax_list
from ..constants.number import check_num
from copy import deepcopy

def frame_check(lines:list)->bool:
    frameable = False
    for line_num,line in enumerate(lines):
        line = [x for x in line if x.isnumeric() or x in frame_header_list]
        num_in_line = [x for x in line if x.isnumeric()]

        if any( x in frame_header_list for x in line) and len(num_in_line)>1:
            return False
        
        if any( x in frame_header_list for x in line):
            frameable = True
    if frameable:
        return True
    return False

def process_frames(lines:list)->list:
    old_lines = deepcopy(lines)
    new_lines = []

    while old_lines:
        line = old_lines.pop(0)
        num_in_line = [x for x in line if x.isnumeric()]
        header = [x for x in line if x in frame_header_list]
        if new_lines and len(new_lines[-1])==1 and new_lines[-1][0] in frame_header_list:
            if (''.join(x for x in [*header,new_lines[-1][0]]) in tax_list):
                header = [''.join(x for x in [*header,new_lines[-1][0]])]
                new_lines.pop(-1)
        #is a frame header
        if old_lines and any( x in frame_header_list for x in line) and len(num_in_line)<2 and [x for x in old_lines[0] if x.isnumeric()]:
            if 'MP' in header or 'MP' in header[0]:
                joined_header = ''.join(x for x in header)
                if new_lines and [x for x in new_lines[-1] if x.isnumeric()] and len([x for x in new_lines[-1] if x.isnumeric()][0])>3 and any('MP' in x for x in old_lines[0] if x.isalpha()):
                    pass
                else:
                    while old_lines and [x for x in old_lines[0] if x.isnumeric()] and len([x for x in old_lines[0] if x.isnumeric()][0])>3 and not any(x in ['T',*tax_list] for x in old_lines[0]):
                        line = old_lines.pop(0)
                        if joined_header in ['MPSP','MPDP','MPSPDP','SPMP','DPMP','MPDPSP','SPDPMP','DPSPMP']:
                            if 'MP' in header[-1] and len(header[-1])==2:
                                joined_header = 'MP' + ''.join(x for x in header[:-1])
                            line.append(joined_header)
                        else:
                            line = [ x for x in line if x.isalnum()]
                            for i,x in enumerate(line):
                                if x in ['SP','DP','SPDP','DPSP']:
                                    if any(x in ['MPSP','MPDP'] for x in line):
                                        if 'MPSP' in line and x == 'DP':
                                            line[line.index('MPSP')] = 'MPSPDP'
                                        elif 'MPDP' in line and x == 'SP':
                                            line[line.index('MPDP')] = 'MPSPDP'
                                        line.pop(i)
                                        continue

                                    line[i] = 'MP' + x
                                    if num_in_line and i==len(line)-1:
                                        line.append(num_in_line[0])
                        new_lines.append(line)
                        line = []

            elif any(x in header[0] for x in ['SP','DP','TP']) and len([x for x in old_lines[0] if x.isnumeric()][0])==1:
                while old_lines and [x for x in old_lines[0] if x.isnumeric()] and len([x for x in old_lines[0] if x.isnumeric()][0])==1:
                    if any( x in [*frame_header_list,'T'] for x in old_lines[0]):
                        break
                    line = old_lines.pop(0)
                    
                    temp_num_in_line = [x for x in line if x.isnumeric()]
                    if all(len(x)==len(temp_num_in_line[0]) for x in temp_num_in_line):
                        if num_in_line:
                            line.extend([''.join(x for x in header),num_in_line[0]])
                        else:
                            if len(temp_num_in_line)  == 1:
                                pass
                            elif ('R' in line) or  (line[-2] in rs_sym_type and line[-1].isnumeric()):
                                temp_num_in_line.insert(-1,''.join(x for x in header))
                                line = temp_num_in_line
                            else:
                                if len(temp_num_in_line) > 1:
                                    line = temp_num_in_line
                                    line.insert(-1,''.join(x for x in header))
                                else:
                                    line.append(''.join(x for x in header))

                    elif all(len(x)==len(temp_num_in_line[0]) for x in temp_num_in_line[:-1]) and len(temp_num_in_line[0])!=len(temp_num_in_line[-1]):
                        temp_num_in_line.insert(-1,''.join(x for x in header))
                        line = temp_num_in_line
                    else:
                        pass   
                    new_lines.append(line)
                    line = []

            
            elif any(x in header for x in ['SINGLE','DOUBLE','PANNA']):

                len_dict = {
                    'SINGLE':1,
                    'DOUBLE':2,
                    'PANNA':3
                }
                while old_lines and [x for x in old_lines[0] if x.isnumeric()] and len([x for x in old_lines[0] if x.isnumeric()][0])==len_dict[header[0]]:
                    #print(old_lines[0])
                    if any( x in  [*frame_header_list,'T'] for x in old_lines[0]):
                        break
                    line = old_lines.pop(0)
                    temp_num_in_line = [x for x in line if x.isnumeric()]
                    if all(len(x)==len(temp_num_in_line[0]) for x in temp_num_in_line):
                        if num_in_line:
                            line.extend(['R',num_in_line[0]])
                        else:
                            if len(temp_num_in_line)  == 1:
                                pass
                            elif ('R' in line) or  (line[-2] in rs_sym_type and line[-1].isnumeric()) :
                                temp_num_in_line.insert(-1,'R')
                                line = temp_num_in_line
                            #else:
                             #   line.append('R')
                        

                    elif all(len(x)==len(temp_num_in_line[0]) for x in temp_num_in_line[:-1]) and len(temp_num_in_line[0])!=len(temp_num_in_line[-1]):
                        temp_num_in_line.insert(-1,'R')
                        line = temp_num_in_line
                    else:
                        pass                
                    new_lines.append(line)
                    line = []

            elif 'CP' in header[0] and len([x for x in old_lines[0] if x.isnumeric()][0]) == 2:
                while old_lines and [x for x in old_lines[0] if x.isnumeric()] and len([x for x in old_lines[0] if x.isnumeric()][0])==2:
                    if any( x in [*frame_header_list,'T'] for x in old_lines[0]):
                        break
                    line = old_lines.pop(0)
                    temp_num_in_line = [x for x in line if x.isnumeric()]
                    if all(check_num('CP',x) for x in temp_num_in_line):
                        if num_in_line:
                            line.extend(['CP',num_in_line[0]])
                        else:
                            if len(temp_num_in_line)  == 1:
                                pass
                            elif ('R' in line) or  (line[-2] in rs_sym_type and line[-1].isnumeric()):
                                temp_num_in_line.insert(-1,'CP')
                                line = temp_num_in_line
                            else:
                                line.append('CP')

                    elif all(check_num('CP',x) for x in temp_num_in_line[:-1]):
                        temp_num_in_line.insert(-1,'CP')
                        line = temp_num_in_line
                    else:
                        pass                
                    new_lines.append(line)
                    line = []

                pass
            
            elif 'FM' in header[0] and len([x for x in old_lines[0] if x.isnumeric()][0]) in [2,3]:
                while old_lines and [x for x in old_lines[0] if x.isnumeric()] and len([x for x in old_lines[0] if x.isnumeric()][0])in[2,3]:
                    if any( x in [*frame_header_list,'T'] for x in old_lines[0]):
                        break
                    line = old_lines.pop(0)
                    temp_num_in_line = [x for x in line if x.isnumeric()]
                    if all( len(x)==len(temp_num_in_line[0]) and check_num('FM',x) for x in temp_num_in_line):
                        if num_in_line:
                            line.extend(['FM',num_in_line[0]])
                        else:
                            if len(temp_num_in_line)  == 1:
                                pass
                            elif ('R' in line) or  (line[-2] in rs_sym_type and line[-1].isnumeric()):
                                temp_num_in_line.insert(-1,'FM')
                                line = temp_num_in_line
                            else:
                                line.append('FM')

                    elif all(check_num('FM',x) for x in temp_num_in_line[:-1]):
                        temp_num_in_line.insert(-1,'FM')
                        line = temp_num_in_line
                    else:
                        pass                
                    new_lines.append(line)
                    line = []
                pass
            else:
                print("New case over here",header)
                new_lines.append(header)

        if line:
            for x in ['SINGLE','DOUBLE','PANNA']:
                if x in line:
                    line.pop(line.index(x))
            new_lines.append(line)
    return new_lines
            

            

        
        

    



