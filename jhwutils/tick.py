import IPython.display
import contextlib
from contextlib import contextmanager


total_marks = 0
available_marks = 0

def reset_marks():
    global total_marks, available_marks
    total_marks = 0
    available_marks = 0
    
    
def js_summarise_marks():
    global total_marks, available_marks
    if available_marks==0:
        IPython.display.display(IPython.display.Javascript("""
        $("#TestCodeButton").value("No marks found"))"""))        
    
    else:
        IPython.display.display(IPython.display.Javascript("""
        $("#TestCodeButton").value("%d/%d (%.1f%%)"))"""  % (total_marks, available_marks, total_marks*100.0/available_marks)))
    
    
def summarise_marks():
    global total_marks, available_marks
    if available_marks==0:
        IPython.display.display(IPython.display.HTML("""<!--{id:"TOTALMARK",marks:"%d", available:"%d"}  -->
        
        <h1> %d / %d marks (%.1f%%) </h1>
        """ % (0,0,0,0,0.0)))
    
    else:
        IPython.display.display(IPython.display.HTML("""<!--{id:"TOTALMARK",marks:"%d", available:"%d"}  -->
        
        <h1> %d / %d marks (%.1f%%) </h1>
        """ % (total_marks, available_marks, total_marks, available_marks, total_marks*100.0/available_marks)))
        
@contextmanager
def marks(marks):
    global total_marks, available_marks
    available_marks += marks
    try:
        yield
        IPython.display.display(IPython.display.HTML('<h3> <!--{id:"CORRECTMARK", marks:"%d"}--> <font color="green"> ✓ [%d marks] </font> </h3>' % (marks,marks)))
        total_marks += marks
    except Exception as e:    
        IPython.display.display(IPython.display.HTML('<hr style="height:10px;border:none;color:#f00;background-color:#f00;" /><h3> <!--{id:"WRONGMARK", marks:"%d"}--> <font color="red"> Test failed ✘ [0/%d] marks </font> </h3>' % (marks, marks)))
        raise e

@contextmanager
def tick():
    try:
        yield
        IPython.display.display(IPython.display.HTML(' <h3> <font color="green"> ✓ Correct </font> </h3>'))
    except Exception as e:    
        IPython.display.display(IPython.display.HTML('<hr style="height:10px;border:none;color:#f00;background-color:#f00;" /><h3> <font color="red"> Problem: test failed ✘ [0/%d] marks </font> </h3>'))
        raise e
        

import pickle
def _get_check(val):
    return pickle.dumps(val)
    
def check_answer(val, pxk):    
    with tick():
        assert(val==pickle.loads(pxk))