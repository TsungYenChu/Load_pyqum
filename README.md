###### 

# Load_PYQUM



```python
from Load_PYQUM import Load_pyqum
'''pyqum_path 可以是 jobid 或 the url of.pyqum file'''
pyqum = Load_pyqum(pyqum_path)
# draw the IQ-plot
pyqum.iqplot(self)
# loaded dataframe
dataframe = pyqum.dataframe
# loaded jobid
jobid = pyqum.jobid
# add the column of Amplitude
pyqum.add_amp()
# add the column of UPhase
pyqum.add_phase()
# give a filter of amplitude ; return the condition (eg.dataframe[pyqum.amp_filter(amp_inf,amp_sup)])
pyqum.amp_filter(amp_inf,amp_sup)
# give a filter of phase ; return the condition (eg.dataframe[pyqum.phase_filter(phase_inf,phase_sup)])
pyqum.phase_filter(phase_inf,phase_sup)
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
pyqum_path = find_file(foldername)
```

