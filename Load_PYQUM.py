from os import listdir
from os import stat
from numpy import array,arctan2,append,concatenate,diff,linspace,mean,ndarray,prod,sqrt,unwrap
from ast import literal_eval
from re import split
from pandas import DataFrame,concat

class Load_pyqum:
    def __init__(self,pyqum_path):
        try:
            jobid = int(pyqum_path)
            self.pyqum_path,_ = jobid_search_pyqum(jobid)
        except:
            self.pyqum_path = pyqum_path
        print(self.pyqum_path)
        self.dataframe,self.jobid,self.file_label = pyqum_load_data(self.pyqum_path)
    def add_amp(self):
        if 'Amp' not in self.dataframe.columns:
            print('Add Amp')
            df_amp =DataFrame(sqrt(self.dataframe['I']**2+self.dataframe['Q']**2), columns = ['Amp'])
            self.dataframe = concat([self.dataframe,df_amp],axis =1)
            self.dataframe = self.dataframe.astype(float)
    def add_phase(self):
        if 'UPhase' not in self.dataframe.columns:
            print('Add UPhase')
            UPhase = diff(unwrap(arctan2(self.dataframe['Q'],self.dataframe['I'])))
            UPhase = append(UPhase, mean(UPhase))
            df_UPhase =DataFrame(UPhase, columns = ['UPhase'])
            self.dataframe = concat([self.dataframe,df_UPhase],axis =1)
            self.dataframe = self.dataframe.astype(float)
    def comment(self):
        return str(self.file_label['comment'])
    def corder(self):
        return self.file_label['c-order']
    def rjson(self):
        return literal_eval(self.file_label['perimeter']['R-JSON'])
    def print_parameter(self):
        corder = self.file_label['c-order']
        try: perimeter = self.file_label['perimeter']
        except(KeyError): perimeter = {}

        print("C-order :")
        for key, value in corder.items():
            print('\t',key, ' : ', value)

        if 'READOUTYPE' in perimeter.keys():
            print("R-JSON :")
            RJSON = literal_eval(perimeter['R-JSON'])
            for key, value in RJSON.items():
                print('\t',key, ' : ', value)
            if perimeter['READOUTYPE'] == 'continuous':
                shot = int(perimeter['RECORD-SUM'])
                print('RECORD-SUM : ',shot)
                time_unit = int(perimeter['TIME_RESOLUTION_NS'])
                time_ns = int(perimeter['RECORD_TIME_NS'])
                print('RECORD_TIME_NS : ',time_ns)
                print('TIME_RESOLUTION_NS : ',time_unit)
                print('RECORD_TIME_dot : ',int(time_ns/time_unit))

            if perimeter['READOUTYPE'] == 'one-shot':
                shot = int(perimeter['RECORD-SUM'])
                print('RECORD-SUM : ',shot)
                time_ns = int(perimeter['RECORD_TIME_NS'])
                print('RECORD_TIME_NS : ',time_ns)

class waveform:
    '''Guidelines for Command writing:\n
        1. All characters will be converted to lower case.\n
        2. Use comma separated string to represent string list.\n
        3. Inner-Repeat is ONLY used for CW_SWEEP: MUST use EXACTLY ' r ' (in order to differentiate from r inside word-string).\n
        4. waveform.inner_repeat: the repeat-counts indicated after the ' r ' or '^', determining how every .data's element will be repeated.\n
        5. Option to let waveform be 'function-ized' using f: <base/power/log..> at the end of the command/ order:
            a. Base: data points from dense to sparse.
            b. Power: 0-1: same with Log, >1: same with Base, but slower.
            c: Log: data points from sparse to dense.
        NOTE: '^' is equivalent to ' r ' without any spacing restrictions.
    '''
    def __init__(self, command):
        # defaulting to lower case
        command = str(command)
        self.command = command.lower()

        # special treatment to inner-repeat command: (to extract 'inner_repeat' for cwsweep averaging)
        self.inner_repeat = 1
        if ' r ' in self.command:
            self.command, self.inner_repeat = self.command.split(' r ')
            while " " in self.inner_repeat: self.inner_repeat = self.inner_repeat.replace(" ","")
            self.inner_repeat = int(self.inner_repeat)
        if '^' in self.command:
            self.command, self.inner_repeat = self.command.split('^')
            while " " in self.inner_repeat: self.inner_repeat = self.inner_repeat.replace(" ","")
            self.inner_repeat = int(self.inner_repeat)

        # correcting back ("auto-purify") the command-string after having retrieved the repeat-count or not:
        # get rid of multiple spacings
        while " "*2 in self.command:
            self.command = self.command.replace(" "*2," ")
        # get rid of spacing around keywords
        while " *" in self.command or "* " in self.command:
            self.command = self.command.replace(" *","*")
            self.command = self.command.replace("* ","*")
        while " to" in self.command or "to " in self.command:
            self.command = self.command.replace(" to","to")
            self.command = self.command.replace("to ","to")
        while " (" in self.command or "( " in self.command:
            self.command = self.command.replace(" (","(")
            self.command = self.command.replace("( ","(")
        while " )" in self.command or ") " in self.command:
            self.command = self.command.replace(" )",")")
            self.command = self.command.replace(") ",")")
        while " f" in self.command or "f " in self.command:
            self.command = self.command.replace(" f","f")
            self.command = self.command.replace("f ","f")
        while " :" in self.command or ": " in self.command:
            self.command = self.command.replace(" :",":")
            self.command = self.command.replace(": ",":")
        while " /" in self.command or "/ " in self.command:
            self.command = self.command.replace(" /","/")
            self.command = self.command.replace("/ ","/")
        # print(Fore.CYAN + "Command: %s" %self.command)
        
        command = self.command.split(" ") + [""]
        
        # 1. building string list:
        if ("," in command[0]) or ("," in command[1]):
            # remove all sole-commas from string list command:
            command = [x for x in command if x != ',']
            # remove all attached-commas from string list command:
            command = [i for x in command for i in x.split(',') if i != '']
            self.data = command
            self.count = len(command)
        # 2. building number list:
        else:
            command = [x for x in command if x != ""]
            self.data, self.count = [], 0
            for cmd in command:
                self.count += 1
                if "*" in cmd and "to" in cmd:
                    C = [j for i in cmd.split("*") for j in i.split('to')]
                    try:
                        start = float(C[0])
                        steps = range(int(len(C[:-1])/2))
                        for i, target, asterisk in zip(steps,C[1::2],C[2::2]):
                            num = asterisk.split("f:")[0]
                            self.count += int(num)
                            # 2a. Simple linear space / function:
                            self.data += list(linspace(start, float(target), int(num), endpoint=False, dtype=float64))
                            if i==steps[-1]: 
                                self.data += [float(target)] # data assembly complete
                                # 2b. Customized space / function for the WHOLE waveform: base, power, log scales
                                if "f:" in asterisk:
                                    func = asterisk.split("f:")[1]
                                    # print(Fore.CYAN + "Function: %s" %func)
                                    if 'base' in func:
                                        if "e" == func.split('/')[1]: self.data = list(exp(self.data))
                                        else: self.data = list(power(float(func.split('/')[1]), self.data))
                                    elif 'power' in func:
                                        self.data = list(power(self.data, float(func.split('/')[1])))
                                    elif 'log10' in func:
                                        self.data = list(log10(self.data))
                                    elif 'log2' in func:
                                        self.data = list(log2(self.data))
                                    elif 'log' in func:
                                        self.data = list(log(self.data))
                                    else: print("Function NOT defined YET. Please consult developers")
                                    print("scaled %s points" %len(self.data))
                            else: 
                                start = float(target)
                    except: # rooting out the wrong command:
                        # raise
                        # print("Invalid command")
                        pass
                else: self.data.append(float(cmd))

def load_rawdata(pyqum_path):
    # --------------load IQdata --------------
    filesize = stat(pyqum_path).st_size
    with open(pyqum_path, 'rb') as datapie:
    #     print(datapie.read())
        i = 0
        while i < (filesize):
            datapie.seek(i)
            bite = datapie.read(7)
            if bite == b'\x02' + bytes("ACTS", 'utf-8') + b'\x03\x04': # ACTS
                datalocation = i
                break
            else: i += 1
        datapie.seek(datalocation+7)
        writtensize = filesize-datalocation-7
        pie = datapie.read(writtensize)
        datacontainer = bite.decode('utf-8')
    selectdata = ndarray(shape=(writtensize//8,), dtype=">d", buffer=pie) # speed up with numpy ndarray, with the ability to do indexing in it.
    # print("Select Data length: %s" %len(selectdata))
    # print(selectdata)
    # --------------load C-order --------------
    with open(pyqum_path, 'rb') as datapie:
        datapie.seek(17)
    #     print(datapie.read())
        dict_label = datapie.read(datalocation-18)
    dict_str = dict_label.decode("UTF-8")
    file_label = literal_eval(dict_str)
    # print(file_label)
    corder = file_label['c-order']
    # print("C-order : \n"+str(corder))
    print("Comment : \n"+str(file_label['comment']))
    # --------------load Perimeter --------------
    try: perimeter = file_label['perimeter']
    except(KeyError): perimeter = {}
    # print("\nperimeter : \n"+str(perimeter))
    try: jobid = perimeter['jobid']
    except(KeyError): jobid = 0

    store_shape = array([waveform(corder[x]).count * waveform(corder[x]).inner_repeat for x in corder if x != 'C-Structure' ])
    cdatasize = int(prod(store_shape, dtype='uint64')) * file_label['data-density'] #data density of 2 due to IQ

    if 'READOUTYPE' in perimeter.keys():
        RJSON = literal_eval(perimeter['R-JSON'])
        RJSON_shape = array([waveform(x).count * waveform(x).inner_repeat for x in RJSON.values()])
        cdatasize*=int(prod(RJSON_shape, dtype='uint64'))
        if perimeter['READOUTYPE'] == 'continuous':
            time_unit = int(perimeter['TIME_RESOLUTION_NS'])
            time_ns = int(perimeter['RECORD_TIME_NS'])
            cdatasize*=int(time_ns/time_unit)
        if perimeter['READOUTYPE'] == 'one-shot':
            shot = int(perimeter['RECORD-SUM'])
            cdatasize*=shot

    # print("\nC-order Data size: \n%s" %cdatasize)
    # print("Select Data length: \n%s" %len(selectdata))   
    # --------------Check data integrity --------------
    if cdatasize == len(selectdata):
        print("\n\tData Checked!\n")
        print("Start load data....")
    else:
        print("examine pyqum data")

    return selectdata, corder,perimeter, jobid, file_label['data-density'],file_label

# c-structure, rjson,readoutype
def command_in_dict(command,dic):
    '''
    command_in_dict(command,dic): 
    command is the output dictionary form
    dic is the raw data dictionary
    '''
    for i in dic:
        if i == 'C-Structure':
            continue
        if waveform(dic[i]).count !=1:
            command['change'] = append(command['change'],i)
            command['change_command'] = append(command['change_command'],waveform(dic[i]).command)
            command['change_len'] = append(command['change_len'],waveform(dic[i]).count)
            if waveform(dic[i]).inner_repeat !=1:
                command['repeat'] = append(command['repeat'],i)
                command['repeat_command'] = append(command['repeat_command'],waveform(dic[i]).inner_repeat)
        elif waveform(dic[i]).inner_repeat !=1:
            command['repeat'] = append(command['repeat'],i)
            command['repeat_command'] = append(command['repeat_command'],waveform(dic[i]).inner_repeat)
        else:
            command['parameter'] = append(command['parameter'],i)
    return command

def repeat_mean(data,repeat,repeat_command):return data.reshape((-1,int(repeat_command[0]))).mean(axis=1)

def construct_layer(where,change_command,change_list_len):
    repeat, group = multiply_except_self(where, change_list_len)
    # print(repeat,group)
    out = list(concatenate([([i]*int(repeat)) for i in seperate(where,change_command)], axis=0))
    out = out*int(group)
    return out

def seperate(idx,change_command):
    try:
        tmp = split('[to*]',change_command[idx])
        out = list(linspace(float(tmp[0]), float(tmp[2]), int(tmp[3])+1))
    except:
        out = change_command[idx].split()
    return out

def multiply_except_self(where, alist):
    repeat, group = 1,1
    for i in range(len(alist)):
        if i > where:
            repeat*=alist[i]
        elif i < where:
            group*=alist[i]
    return repeat, group

def command_analytic(selectdata,corder, perimeter,datadensity):
    command = {'change':[],'change_command':[], 'repeat':[], 'repeat_command':[], 'parameter':[], 'change_len':[]}

    # print("C-order :")
    # for key, value in corder.items():
    #     print('\t',key, ' : ', value)
    command = command_in_dict(command,corder)

    if 'READOUTYPE' in perimeter.keys():
        print("R-JSON :")
        RJSON = literal_eval(perimeter['R-JSON'])
        command =command_in_dict(command,RJSON)
        for key, value in RJSON.items():
            print('\t',key, ' : ', value)
        if perimeter['READOUTYPE'] == 'continuous':
            shot = int(perimeter['RECORD-SUM'])
            print('RECORD-SUM : ',shot)
            time_unit = int(perimeter['TIME_RESOLUTION_NS'])
            time_ns = int(perimeter['RECORD_TIME_NS'])
            print('RECORD_TIME_NS : ',time_ns)
            print('TIME_RESOLUTION_NS : ',time_unit)
            print('RECORD_TIME_dot : ',int(time_ns/time_unit))
            command['change'] = append(command['change'],'RECORD_TIME_NS')
            command['change_command'] = append(command['change_command'],str(1*time_unit)+'to'+str(time_ns)+'*'+str(int(time_ns/time_unit)-1))
            command['change_len'] = append(command['change_len'],int(time_ns/time_unit))
        if perimeter['READOUTYPE'] == 'one-shot':
            shot = int(perimeter['RECORD-SUM'])
            print('RECORD-SUM : ',shot)
            time_ns = int(perimeter['RECORD_TIME_NS'])
            print('RECORD_TIME_NS : ',time_ns)
            command['change'] = append(command['change'],'RECORD-SUM')
            command['change_command'] = append(command['change_command'],'1to'+str(shot)+'*'+str(shot-1))
            command['change_len'] = append(command['change_len'],shot)
    if len(command['change']) != 0:
        print("Change : \n\t",command['change'])
        print("Change command : \n\t",command['change_command'])
    if len(command['repeat']) != 0:
        print("Repeat : \n\t",command['repeat'])
        print("Repeat_command : \n\t",command['repeat_command'])
    # print("Unchange : \n\t",command['parameter'])
    print("\n")

    selectdata_i_data = selectdata[::datadensity]
    selectdata_q_data = selectdata[1::datadensity]
    while len(command['repeat'])!=0:
        selectdata_i_data = repeat_mean(selectdata_i_data,command['repeat'],command['repeat_command'])
        selectdata_q_data = repeat_mean(selectdata_q_data,command['repeat'],command['repeat_command'])
        command['repeat'] = delete(command['repeat'],0)
        command['repeat_command'] = delete(command['repeat_command'],0)

    df = DataFrame()
    for i in range(len(command['change'])):
        df1 = DataFrame(construct_layer(i,command['change_command'],command['change_len']), columns = [command['change'][i]])
        df = concat([df,df1],axis =1)
    df_label = df
    # print(df_label)
    df_label = df_label.astype(float)
    key = list(df_label.select_dtypes('number').columns)
    removable = ['RECORD-SUM']
    [key.remove(i) for i in removable if i in key]
    [print('{:^15} : {:^6} to {:^6} * {:^5}'.format(i,df_label[i].min(),df_label[i].max(),df_label[i].nunique())) for i in key]
    return selectdata_i_data,selectdata_q_data, df_label 

def pyqum_load_data(pyqum_path):
    selectdata, corder, perimeter, jobid, datadensity, file_label = load_rawdata(pyqum_path)
    mean_i_data, mean_q_data, df_label = command_analytic(selectdata,corder, perimeter,datadensity)
    df_i = DataFrame(mean_i_data, columns = ['I'])
    df_q = DataFrame(mean_q_data, columns = ['Q'])
    df_data = concat([df_i,df_q],axis =1)
    tidy_data = concat([df_label,df_data],axis =1)
    tidy_data = tidy_data.astype(float)
    return tidy_data,jobid,file_label

    