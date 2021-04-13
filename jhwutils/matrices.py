try:
    import sympy
    sympy.init_printing(use_latex='png')
except: 
    sympy = False

import IPython.display     
def print_matrix(name, matrix, prec=2):

        
    # print scalars
    if not hasattr(matrix, "__len__"):
        IPython.display.display(IPython.display.Latex("${0} = {1}$".format(name, matrix)))
        return

    if str(matrix.dtype).startswith('float'):
        matrix = np.around(matrix, prec)
    

    if len(matrix.shape)==1:
        matrix = matrix[None,:]
        
    if sympy:    
        IPython.display.display(IPython.display.Latex("${0} = {1}$".format(name, sympy.latex(sympy.Matrix(matrix)))))
    else:
        print(name, "\n", matrix)

from matplotlib.patches import Polygon

import numpy as np
import matplotlib.pyplot as plt




def fill_shape(shape):
    n = np.arange(np.prod(shape)).reshape(shape)    
    return n


    
    
def boxed_tensor_ascii(x, j='\n'):    
    
    # force the tensor to be even dimension
    if len(x.shape)&1==1:
        x = x.reshape(tuple(list(x.shape)+[1]))
    
    
    
    shape = np.array(x.shape) + 1
    if len(shape)>2:
        shape[0:2] -= 1
    
    shape = tuple(shape)
    
    row_ixs = np.prod(shape[::2])
    col_ixs = np.prod(shape[1::2])
    
    out = np.zeros((row_ixs, col_ixs)) * np.nan
    
    for i in range(np.prod(x.shape)):
        ix = np.unravel_index(i, x.shape)
        row = np.ravel_multi_index(tuple(ix[::2]), shape[::2])
        col = np.ravel_multi_index(tuple(ix[1::2]), shape[1::2])
        out[row, col] = x[tuple(ix)]
    
    ret = []
    ret.append("--+--" * (col_ixs+1))
    ret.append("\n")
    for row in out:
        if np.all(np.isnan(row)):
            sep = "-----"
        else:
            sep = "  |  "            
        ret.append(sep)
        for col in row:
            if not np.isnan(col):
                ret.append("%5d"%col)
            else:
                ret.append(sep)
        ret.append("\n")
    return "".join(ret)
    



def make_boxed_tensor_ascii(x):    
    if np.isscalar(x):
        return ["%4d"%x]
        
    # force the tensor to be even dimension
    if len(x.shape)&1==1:
        x = x.reshape(tuple(list(x.shape)+[1]))
        
    rows, cols = x.shape[0:2]
    mat = []
    row_size = len(make_boxed_tensor_ascii(x[0,0]))
    n_rows = 0
    for row in range(rows):
        row_buf = [[] for i in range(row_size)]
        for col in range(cols):
            sub_rows = make_boxed_tensor_ascii(col)
            for i,rrow in enumerate(sub_rows):
                row_buf[i].append(rrow)
                row_buf[i].append(" ")
        mat = mat + ["\n".join([" ".join(row) for row in row_buf])]
                
    return mat
                                
    
        
    

def boxed_tensor_ascii(x):
    return "\n".join(make_boxed_tensor_ascii(x))

def make_boxed_tensor_latex(x, box_rows=True, index=0):    
    ixs = "ijklmnopqrst"
    shape = x.shape
    # ensure has at least 2D
    if len(shape)==1:
        x = x[None,:]
        
    rows, cols = x.shape[0:2]
    
    mat = []
    # always generate a matrix starting at the smallest index
    # e.g. a 2x2x3 tensor is a 2x2 matrix of 3 element arrays, not 2 rows of 2x3 matrices    
    for row in range(rows):
        line = []
        for col in range(cols):
            if len(x.shape)==2:
                line.append("\\quad \  \\llap{%d} \ \  \strut " % (x[row,col]))
            else:
                # insert a recursive matrix box
                line.append("%s" % (make_boxed_tensor_latex(x[row,col], box_rows=box_rows, index=index+2)))
        # either box the whole row or just box entire matrices
        if box_rows:
            mat.append("\\fbox { $ "  + " ".join(line) + " \strut $ } ")
        else:
            mat.append(" ".join(line))
    mat_code = "\\\\ \n".join(mat)
    return "  \\fbox{  $ \n "+ mat_code+"  \strut $ }\ \ "


def show_boxed_tensor_latex(x, box_rows=True):    
    # show the matrix in the notebook as a LaTeX equation
    IPython.display.display(IPython.display.Latex("\\[ " + make_boxed_tensor_latex(x, box_rows=box_rows) + " \\]"))


def show_matrix_effect(m, suptitle=""):
    print_matrix(suptitle, m)
    def piped(ax, pts):
        f = 1.08
        a, b, c, d = (pts[:, 0] * f, pts[:, 9] * f, pts[:, 90] * f,
                      pts[:, 99] * f)

        poly = Polygon(
            [a, b, d, c], facecolor=[0.5, 0.75, 0.75, 0.2], edgecolor='k')
        ax.add_patch(poly)
        ax.text(
            a[0], a[1], 'A', color='r', fontsize=30, ha='center', va='center')
        ax.text(b[0], b[1], 'B', fontsize=20, ha='center', va='center')
        ax.text(c[0], c[1], 'C', fontsize=20, ha='center', va='center')
        ax.text(d[0], d[1], 'D', fontsize=20, ha='center', va='center')

    fig = plt.figure()
    lax = fig.add_subplot(1, 2, 1)
    rax = fig.add_subplot(1, 2, 2)
    
    
    # 2D transform
    box_x, box_y = np.meshgrid(
        np.linspace(-1, 1, 10), np.linspace(-1, 1, 10))
    box = np.stack([box_x.reshape([-1]), box_y.reshape([-1])])
    color = np.linspace(0, 1, box.shape[1])
    # do the transform -- just one line
    if m.shape[0]==3:
        mbox = np.concatenate([box, np.ones((1,box.shape[1]))], axis=0)        
        transformed = np.dot(m, mbox)[:-1,:]        
        
    else:
        transformed = np.dot(m, box)
    lax.scatter(box[0, :], box[1, :], c=color, cmap='viridis')
    rax.scatter(
        transformed[0, :], transformed[1, :], c=color, cmap='viridis')
    piped(lax, box)
    piped(rax, transformed)

    # decorate the axes
    lax.set_title("Original")
    rax.set_title("Transformed")
    lax.scatter([0], [0], marker='o', color='k')
    rax.scatter([0], [0], marker='o', color='k')
    lax.axvline(0, color='k', ls=':')
    rax.axvline(0, color='k', ls=':')
    lax.axhline(0, color='k', ls=':')
    rax.axhline(0, color='k', ls=':')

    lax.axis("equal")
    lax.axis("off")
    rax.axis("equal")
    rax.axis("off")

    lax.set_xlim(-1.5, 1.5)
    rax.set_xlim(-1.5, 1.5)
    lax.set_ylim(-1.5, 1.5)
    rax.set_ylim(-1.5, 1.5)        
    plt.suptitle(f"${suptitle}$" if suptitle != "" else "")
