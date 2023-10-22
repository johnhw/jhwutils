
#!/usr/bin/env python
"""
simple example script for scrubping solution code cells from IPython notebooks

Usage: `scrub_code.py foo.ipynb [bar.ipynb [...]]`

Marked code cells are scrubbed from the notebook
"""

import io
import re
import os
import sys

from nbformat import read, write

code_stub = ""#### PUT YOUR SOLUTION HERE ###"
text_stub = ""# PUT YOUR SOLUTION HERE"
begin_delimiter = "### BEGIN SOLUTION"
end_delimiter = "### END SOLUTION"



def remove_solution(cell):
        """Find a region in the cell that is delimited by
        `self.begin_delimeter` and `self.end_delimeter` (e.g.
        ### BEGIN SOLUTION and ### END SOLUTION). Replace that region either
        with the code stub or text stub, depending the cell type.

        This modifies the cell in place, and then returns True if a
        solution region was replaced, and False otherwise.

        """

        
        # pull out the cell input/source
        lines = cell.source.split("\n")
        if cell.cell_type == "code":
            stub_lines = code_stub.split("\n")
        else:
            stub_lines = text_stub.split("\n")

        new_lines = []
        in_solution = False
        replaced_solution = False

        for line in lines:
            # begin the solution area
            if begin_delimiter in line:

                # check to make sure this isn't a nested BEGIN
                # SOLUTION region
                if in_solution:
                    raise RuntimeError(
                        "encountered nested begin solution statements")

                in_solution = True
                replaced_solution = True

                # replace it with the stub, indented as necessary
                indent = re.match(r"\s*", line).group(0)
                # omit "hidden" solution blocks
                if "HIDDEN" not in line:
                    for stub_line in stub_lines:
                        new_lines.append(indent + stub_line)

            # end the solution area
            elif end_delimiter in line:
                in_solution = False

            # add lines as long as it's not in the solution area
            elif not in_solution:
                new_lines.append(line)

        # we finished going through all the lines, but didn't find a
        # matching END SOLUTION statment
        if in_solution:
            raise RuntimeError("no end solution statement found")

        # replace the cell source
        cell.source = "\n".join(new_lines)

        return replaced_solution

def scrub_code_cells(nb):
    scrubbed = 0
    cells = 0
    
    for cell in nb.cells:                      
        # scrub cells marked with initial '## Solution' comment
        # any other marker will do, or it could be unconditional
        if cell['cell_type'] == 'code' and cell['source'].startswith("## Solution"):
            cell['source'] = '# Solution goes here'
            scrubbed += 1
            cells += 1
            cell['outputs'] = []
        
        if (begin_delimiter in cell.source):
                removed = remove_solution(cell)
                if removed:
                    print("Removed solution block.")
        
        if cell['cell_type']=='code':
            cell['outputs'] = []
    
    print("scrubbed %i/%i code cells from notebook %s" % (scrubbed, cells, nb.metadata))

if __name__ == '__main__':
        ipynb = sys.argv[1]
        print("scrubbing %s" % ipynb)
        with io.open(ipynb, encoding='utf8') as f:
            nb = read(f, 4)
        scrub_code_cells(nb)             
        new_ipynb = sys.argv[2]
        with io.open(new_ipynb, 'w', encoding='utf8') as f:
            write(nb, f)
        print("wrote %s" % new_ipynb)

