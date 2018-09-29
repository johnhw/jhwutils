import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

def check_convert(fname):
    with open(fname) as f:
        nb = nbformat.read(f, as_version=4)
    ep  = ExecutePreprocessor(timeout=1000, interrupt_on_timeout=True, kernel_name='python3', allow_errors=True)
    ep.preprocess(nb, {"metadata": {"path":"."}})
    for cell in nb.cells:
        outputs = cell.get("outputs", [])
        for out in outputs:
            if out["output_type"]=="display_data":
                html=out["data"].get("text/html")
                if html:
                    print(html)
    
    
check_convert("week_1_intro.ipynb")    