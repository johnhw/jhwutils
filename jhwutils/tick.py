import IPython.display
import contextlib
from contextlib import contextmanager


from IPython.core.magic import Magics, magics_class, cell_magic
from IPython.display import display, Javascript
import json




total_marks = 0
available_marks = 0


def reset_marks():
    global total_marks, available_marks
    total_marks = 0
    available_marks = 0


def js_summarise_marks():
    global total_marks, available_marks
    if available_marks == 0:
        IPython.display.display(
            IPython.display.Javascript(
                """
        $("#TestCodeButton").value("No marks found"))"""
            )
        )

    else:
        IPython.display.display(
            IPython.display.Javascript(
                """
        $("#TestCodeButton").value("%d/%d (%.1f%%)"))"""
                % (total_marks, available_marks, total_marks * 100.0 / available_marks)
            )
        )


# def summarise_marks():
#     global total_marks, available_marks
#     if available_marks == 0:
#         IPython.display.display(
#             IPython.display.HTML(
#                 """<!--{id:"TOTALMARK",marks:"%d", available:"%d"}  -->
        
#         <h1> %d / %d marks (%.1f%%) </h1>
#         """
#                 % (0, 0, 0, 0, 0.0)
#             )
#         )

#     else:
#         IPython.display.display(
#             IPython.display.HTML(
#                 """<!--{id:"TOTALMARK",marks:"%d", available:"%d"}  -->
        
#         <h1> %d / %d marks (%.1f%%) </h1>
#         """
#                 % (
#                     total_marks,
#                     available_marks,
#                     total_marks,
#                     available_marks,
#                     total_marks * 100.0 / available_marks,
#                 )
#             )
#         )


_cell_data_marks = {}

def init_marks():
    global _cell_data_marks
    msg = f"""<div class="alert alert-box alert-success"> <h1> Marking enabled </h1> </div>"""
    _cell_data_marks = {}

def summarise_marks():
    total_marks = 0
    achieved_marks = 0
    for id, data in _cell_data_marks.items():        
        total_marks += data["max"]
        achieved_marks += data["marks"]
    msg = f"""<div class="alert alert-box alert-success">
        <h1> Total marks {achieved_marks}/{total_marks}  ({achieved_marks/total_marks*100:.1f}%) </h1> </div>"""
    IPython.display.display(IPython.display.HTML(msg))
    msg = "<ul>"
    current_part = None    
    ids = sorted(list(_cell_data_marks.keys()))
    part_marks = 0
    for id in ids:
        mark = _cell_data_marks[id]
        part = id.split(".")
        # heading changed
        if len(part) > 0:
            if current_part != part[0]:
                if current_part is not None:
                    msg += f"<li> <b> {current_part} Total </b> {part_marks} </li>"
                current_part = part[0]
                part_marks = 0
                msg += f"<h2> {current_part} </h2>"                               
        color = "green" if mark["marks"] == mark["max"] else "red"
        msg += f"""
        <li> <b> {id} </b> <font color={color}> {mark["marks"]}/{mark["max"]} </font> </li> """
    msg += "</ul>"
    IPython.display.display(IPython.display.HTML(msg))

@contextmanager
def Marks(id, marks):
    _cell_data_marks[id] = {"max":marks, "marks":0}
    try:
        yield
        IPython.display.display(
            IPython.display.HTML(
                f"""
        <div class="alert alert-box alert-success">
        <h1> 
        {id} ✓ [{marks} marks] 
         </h1> </div>"""                
            )
        )
        _cell_data_marks[id]["marks"] = marks        
    except Exception as e:
        IPython.display.display(
            IPython.display.HTML(
                f"""<hr style="height:10px;border:none;color:#f00;background-color:#f00;" />
        <div class="alert alert-box alert-danger">
        <h1> {id} Test failed ✘ [0/%{marks}] marks  </h1> </div>"""                
            )
        )
        _cell_data_marks[id]["marks"] = 0
        raise e

@contextmanager
def marks(marks):
    global total_marks, available_marks
    available_marks += marks
    try:
        yield
        IPython.display.display(
            IPython.display.HTML(
                """
        <div class="alert alert-box alert-success">
        <h1> <!--{id:"CORRECTMARK", marks:"%d"}--> 
         ✓ [%d marks] 
         </h1> </div>"""
                % (marks, marks)
            )
        )
        total_marks += marks
    except Exception as e:
        IPython.display.display(
            IPython.display.HTML(
                """<hr style="height:10px;border:none;color:#f00;background-color:#f00;" />
        <div class="alert alert-box alert-danger">
        <h1> <!--{id:"WRONGMARK", marks:"%d"}--> Test failed ✘ [0/%d] marks  </h1> </div>"""
                % (marks, marks)
            )
        )
        raise e

@contextmanager
def prestige_mark():
    try:
        yield
        IPython.display.display(
            IPython.display.HTML(
                f"""
        <div class="alert alert-box alert-success" style="background-color: #ddaa88">
        <h1> <!--{id:"PRESTIGEMARK", marks:"%d"}--> 
         ☺ Prestige mark achieved!
         </h1> </div>"""
            )
        )
    except Exception as e:
        IPython.display.display(
            IPython.display.HTML(
                f""""""             
            )
        )
        raise e

@contextmanager
def tick():
    try:
        yield
        IPython.display.display(
            IPython.display.HTML(
                """ 
        <div class="alert alert-box alert-success">
        <h1> <font color="green"> ✓ Correct </font> </h1>
        </div>
        """
            )
        )
    except Exception as e:
        IPython.display.display(
            IPython.display.HTML(
                """
        <div class="alert alert-box alert-success">                        
        <hr style="height:10px;border:none;color:#f00;background-color:#f00;" /><h1> <font color="red"> ✘ Problem: test failed  </font> </h1>        
        </div>
        """
            )
        )
        raise e


import pickle


def _get_check(val):
    return pickle.dumps(val)


def check_answer(val, pxk):
    with tick():
        assert val == pickle.loads(pxk)

