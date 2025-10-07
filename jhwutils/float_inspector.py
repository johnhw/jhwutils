import numpy as np
from IPython.display import HTML, display




def bitstring_array(x):
    # force to big endian for printing
    endianed = x.dtype.newbyteorder('B')    
    return "".join('{0:08b}'.format(d) for d in x.astype(endianed).tobytes())


import itertools    

import textwrap

def get_binary(data, word_size, offset, n_words):
    binary = "".join(["{0:08b}".format(byte) for byte in data])        
    selection = binary[offset:offset+n_words*word_size]
    return selection

def raw_binary_view(data, word_size, offset, n_words):
    if n_words<0:
        print(get_binary(data, len(data)*8, offset, 1))
        return
        
    selection = get_binary(data, word_size, offset, n_words)
    out = [selection[i*word_size:(i+1)*word_size] for i in range(n_words)]
    print("Bit offset: %08d      Word size: %3d     Words: %4d" % (offset, word_size, n_words))
    print()
    print("\n".join(textwrap.wrap(" ".join(out), width=80)))
    
    
def binary_to_array(data, dtype, offset, shape):
    n_words = np.prod(shape)
    word_size = np.finfo(dtype).bits
    binary = get_binary(data, word_size, offset, n_words)
    binary = binary + "0" * (8-len(binary)%8)
    rbytes = (bytearray(([(int(binary[i*8:(i+1)*8], 2)) for i in range(len(binary)//8)])))    
    return np.fromstring(bytes(rbytes), dtype=dtype, count=n_words).reshape(shape).byteswap()
  
    
def intersperse(s, step, char):
    out = []
    step_cycle = itertools.cycle(step)
    char_cycle = itertools.cycle(char)
    i = 0
    while i<len(s):
        interval = next(step_cycle)
        split_char = next(char_cycle)
        out.append(s[i:i+interval])    
        out.append(split_char)
        i += interval    
    return "".join(out)


def print_float_binary(x):
    print(bitstring_array(np.array(x)))
    
def print_binary_float(fl, word, exp, mantissa):
        
        mantissa -= 1
        bias = (2**(exp-1))-1
        total_width = exp + mantissa + 1 # for sign
        
        sep_word = intersperse(word, [1,exp,mantissa], ['|','|','|'])
        sign, e, m = int(word[0:1],2), int(word[1:1+exp],2)-bias, int(word[1+exp:total_width],2)        
        infinite = e==2**(exp-1)
            
        sign = -1 if sign==1 else 1
        
        print((("{0:4s}|  {1:%ds} |  {2:%ds}|"%(exp-3, mantissa-2)).format("Sign", "Exp", "Mantissa")))
        print("   "+sep_word)
        print((("{0:4d}|  {1:%dd} |  {2:%dd}|"%(exp-3, mantissa-2)).format(sign, e, m)))
        
        if infinite:
            print("Infinite/NaN")
        else:
            print("    {0} * {1} * 2^{2}".format(sign, 1.0+m/(2.0**mantissa), e))
            print("    = {0} * {1} * {2}".format(sign, 1.0+m/(2.0**mantissa), 2**e))
            print("    = %.20f" % fl)
    
        print("")


def print_binary_float_html(fl, word, exp, mantissa):        
        mantissa -= 1
        bias = (2**(exp-1))-1
        total_width = exp + mantissa + 1 # for sign
      
        sep_word = intersperse(word, [1,exp,mantissa], ['</td> <td>','</td> <td>','</td> <td>'])
        bar_word = intersperse(word, [1,exp,mantissa], [' | ',' | ',' | '])[:-1]
        sign, e, m = int(word[0:1],2), int(word[1:1+exp],2)-bias, int(word[1+exp:total_width],2)        
        infinite = e==2**(exp-1)
            
        sign = -1 if sign==1 else 1
        
        html = "<h3> {fl:.20f} / {fl:.2e} </h3>".format(fl=fl)
        rbytes = np.array(fl, dtype=np.float64).tobytes()
        
        html += '<table width="100%"> '
        html += '<tr> <td width="10%"></td> <td width="5%"> <b>  </b> </td> <td> <b>  </b> </td> <td> <b>  </b> </td> </tr>'
        html += '<tr> <td width="5%"> Raw  </td> <td colspan="3"> {word} </td> </tr> '.format(word=str(bar_word))
        html += '<tr> <td width="5%"> Hex </td> <td colspan="3"> ' +" ".join(["%02X" % byte for byte in rbytes]) + "</td></tr>"

        html += '<tr> <td width="10%"></td> <td width="5%"> <b> Sign </b> </td> <td> <b> Exp </b> </td> <td> <b> Mantissa </b> </td> </tr>'
        
        
        html += "<tr> <td> Binary </td> <td>" + sep_word + "</td> </tr>"
        html += ((("<tr> <td> Integer </td> <td> {0:4d} </td> <td> {1:%dd} </td> <td>  {2:%dd} </td> </tr>"%(exp-3, mantissa-2)).format(sign, e, m)))
        
        denormal = (e+bias)==0
        if infinite:
            
            html_sign = str(sign)
            if mantissa==0:
                html_mantissa = "infinite"
            else:
                html_mantissa = "NaN"
            html_exponent = "inf/NaN"                    
        elif not denormal:
            html_sign = sign
            html_mantissa = 1.0+m/(2.0**mantissa)
            html_exponent = "2<sup>{exp}</sup>".format(exp=e)
        else:
            # denormal case
            html_sign = sign
            html_mantissa = m/(2.0**(mantissa-1))
            html_exponent = "2<sup>{exp}</sup>".format(exp=e)
        html += "<tr> <td> Power </td> <td> {sign} </td> <td> {exponent} </td> <td>  {mantissa} </td> </tr>".format(sign=html_sign, mantissa=html_mantissa,
        exponent=html_exponent)

        if not infinite:
            if denormal:
                html += "<tr> <td> = </td> <td> {0}  </td> <td> {2:.2e} </td> <td> {1} </td> </tr>".format(sign, m/(2.0**(mantissa-1)), 2**e)
            else:
                html += "<tr> <td> = </td> <td> {0}  </td> <td> {2:.2e} </td> <td> {1} </td> </tr>".format(sign, 1.0+m/(2.0**mantissa), 2**e)
        html += "<tr><td></td></tr>"
        html += '<tr> <td> Float </td> <td colspan="2"> {fl:.20f} </td><td> {fl:.2e} </td> </tr>'.format(fl=fl)
        html += "</table>"
        
            
        
        display(HTML(html))


def print_binary_float_rich(fl, word, exp, mantissa):
        from rich.console import Console 
        from rich.table import Table
        c = Console() 

        mantissa -= 1
        bias = (2**(exp-1))-1
        total_width = exp + mantissa + 1 # for sign
        
        sep_word = intersperse(word, [1,exp,mantissa], ['</td> <td>','</td> <td>','</td> <td>'])
        bar_word = intersperse(word, [1,exp,mantissa], ['|','|','|'])[:-1]
        sign, e, m = int(word[0:1],2), int(word[1:1+exp],2)-bias, int(word[1+exp:total_width],2)        
        infinite = e==2**(exp-1)
        nan = infinite and m!=0
        sign = -1 if sign==1 else 1
        
        zero = fl==0.0
        denormal = (e+bias)==0 and not zero
        if exp==8:
            dtype="float32"
        else:
            dtype="float64"

        table = Table(f"{fl}")

        details = Table(show_header=False)
        details.add_column()
        details.add_column() 

        details.add_row("dtype", f"{dtype}")
        details.add_row("Flags", f"{'[yellow]denormal[/yellow]' if denormal else ''} {'[red]infinite[/red]' if infinite and not nan else ''} {'[blue]NaN[/blue]' if infinite and nan else ''} {'[cyan]zero[/cyan]' if zero else ''} {'[green]-ve[/green]' if sign==-1 else ''}")
        details.add_row("Float", f"{fl:.40f}")
        details.add_row("Sci.", f"{fl:.40e}")

        table.add_row(details)
        split = Table()
        split.add_column("")
        split.add_column("sign", style="red")
        split.add_column("exponent", style="yellow")
        split.add_column("mantissa", style="blue") 
        
        sign_name = f"{sign}"

        if infinite:
            if mantissa==0:
                mantissa_name = "infinity"
            else:
                mantissa_name = "NaN"
            exponent_name = "inf/NaN"     
        elif zero:
            mantissa_name = "0.0"
            exponent_name = "0.0"
        elif not denormal:
            mantissa_name = f"{1.0+m/(2.0**mantissa):.40f}"
            exponent_name = f"2**{e}"       
        else:
            # denormal case
            mantissa_name = f"{m/(2.0**(mantissa-1)):.40f}"
            exponent_name = f"2**{e}"
            
                
        split.add_row("Binary", word[0], word[1:exp+1], word[1+exp+1:-1])
        split.add_row("Integer", f"{sign}", f"{e-bias}", f"{m}")
        split.add_row("Integer (w/bias)", f"{sign}", f"{e}", f"{m}")
        split.add_row("Float", sign_name, exponent_name, mantissa_name)

           
        table.add_row(split)

        table.add_row(f"[red]{sign_name}[/red] * [yellow]{exponent_name}[/yellow] * [blue]{mantissa_name}[/blue] = {fl}")
        
        c.print(table)
        return 

def print_float(fl, dtype=np.float64):
    if dtype==np.float64:
        print_binary_float(fl, bitstring_array(np.array(fl, dtype=dtype)), 11, 53)    
    elif dtype==np.float32:
        print_binary_float(fl, bitstring_array(np.array(fl, dtype=dtype)), 8, 23)    

def print_float_html(fl, dtype=np.float64):
    if dtype==np.float64:
        print_binary_float_html(fl, bitstring_array(np.array(fl, dtype=dtype)), 11, 53)    
    elif dtype==np.float32:
        print_binary_float_html(fl, bitstring_array(np.array(fl, dtype=dtype)), 8, 23)    

def print_float_rich(fl, dtype=np.float64):
    if dtype==np.float64:
        print_binary_float_rich(fl, bitstring_array(np.array(fl, dtype=dtype)), 11, 53)    
    elif dtype==np.float32:
        print_binary_float_rich(fl, bitstring_array(np.array(fl, dtype=dtype)), 8, 23)    


def print_float_structure(x):
    flat = x.ravel()
    nbits = x.dtype.itemsize*8
    exp, mantissa = {
        16: (5,11),
        32: (8, 24),
        64: (11, 53),
        128: (15, 113),
    }[nbits]
    total_width = exp + mantissa 
    
    bitstring = bitstring_array(x)            
    
    for bit, fl in zip(range(0,len(bitstring),total_width), flat):                
        word = bitstring[bit:bit+total_width]        
        print_binary_float(fl, word, exp, mantissa)
        
        
def print_raw_binary_array(x):
    print(intersperse(bitstring_array(x), [x.dtype.itemsize*8], ['\n']))    
    
def print_flat_array(x):
        print(" ".join(["%f"%f for f in x.ravel()]))
        
def print_shape(x):    
    # array inspector
    print("\tShape:\t\t\t{0}".format(x.shape))
    print("\tStride:\t\t\t{0}".format(x.strides))    
    print("\tData type:\t\t{0}".format(x.dtype))
    print("\tElements:\t\t{0}".format(x.size))
    print("\tNo. of bytes:\t\t{0}".format(x.nbytes))    
    print("\tBits per element:\t{0}".format(8*x.itemsize))    
    print("-"*80)
    print("")



def format_html_row(cols):
    return "<tr><td>" + "</td><td>".join(cols) + "</td></tr>"

def print_shape_html(x):    

    # array inspector
    html = '<table width="100%">'

    html += format_html_row(["Shape", str(x.shape)])
    html += format_html_row(["Strides", str(x.strides)])
    html += format_html_row(["Data type", str(x.dtype)])
    html += format_html_row(["Elements", str(x.size)])
    html += format_html_row(["Num. bytes", str(x.nbytes)])
    html += format_html_row(["Bits per element", str(8*x.itemsize)])
    mem_offset = x.ctypes.data -x.base.ctypes.data 
    html += format_html_row(["Start offset", str(mem_offset//x.itemsize)])


    html += "</table>"
    display(HTML(html))

def show_grouping(x):
    """
    Prints out a multi-dimensional array with parentheses to show the grouping of elements
    """
    shape = x.shape
    flat = x.ravel()  # Raveled (1D) version of the array
    num_elements = flat.size
    current_multi_index = [0] * len(shape)  # Keep track of the current multi-dimensional index
    previous_multi_index = [0] * len(shape)  # Track the previous index to know when to close/open parentheses
    

    elements = []  # List to hold the HTML output
    parens = []

    for _ in range(len(shape)):
        parens.append("(")

    
    elements.extend(parens)


    # Iterate over each element in the raveled array
    for i in range(num_elements):
        # Get the current multi-dimensional index for the raveled index
        current_multi_index = np.unravel_index(i, shape)
        parens = []
        # Close parentheses if finishing a group in a higher dimension
        for dim in reversed(range(len(shape))):
            if current_multi_index[dim] != previous_multi_index[dim]:
                if len(shape)-dim>1:
                    elements[-1] = elements[-1].strip()  # Remove trailing whitespace
                for _ in range(dim+1, len(shape)):
                    parens.append(")")
                for _ in range(dim+1, len(shape)):
                    parens.append(" ")
            
                
        # Open parentheses for new group
        for dim in range(len(shape)):
            if current_multi_index[dim] != previous_multi_index[dim]:
                for _ in range(dim+1, len(shape)):
                    parens.append("(")
                
                    
                break
            
        
        elements.extend(parens)

        # Add the current element as part of the fixed-width display
        elements.append(f'{flat[i]} ')

        # Update the previous multi-dimensional index
        previous_multi_index = list(current_multi_index)

    # Close any remaining open parentheses
    for _ in range(len(shape)):
        elements[-1] = elements[-1].strip()
        elements.append(")")
    
    return ''.join(elements)
