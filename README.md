###### 

# Load_PYQUM



```python
from Load_PYQUM import Load_pyqum
'''pyqum_path 可以是 jobid 或 the url of.pyqum file'''
pyqum = Load_pyqum(pyqum_path)
# add the column of Amplitude
pyqum.add_amp()
# add the column of UPhase
pyqum.add_phase()
# loaded dataframe
dataframe = pyqum.dataframe
# loaded jobid
jobid = pyqum.jobid
```



```python
# load comment
print(pyqum.comment())
# load corder
print(pyqum.corder())
# load R-JSON
print(pyqum.rjson())
# print all of the pyqum form of data
pyqum.print_parameter()
```



```python
samplename = "19-3(v2) TOMO"
foldername = r"C:/Users/tsung/Downloads/data/"+samplename+"/"
file_dir = listdir(foldername)
user_input = ''
input_message = "Pick an option:\n"
for index, item in enumerate(file_dir):
    if index%5!=4:
        input_message += f'{index+1}) {item}\t'
    else:
        input_message += f'{index+1}) {item}\n'
user_input = input(input_message+'\nYour Choice is ')
pyqum_path = foldername+file_dir[int(user_input) - 1]
```

