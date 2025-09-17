#!/usr/bin/env python
"""
Strip code from Jupyter notebooks and output Markdown.
Optionally, embed Markdeep JS for rendering in the browser.
Can also strip images, and optionally retain them as attachments.

Code cells with `retain_img("filename")` will have their output images included in the output.
"""

import io
from nbconvert import MarkdownExporter
from pathlib import Path
import re
from hashlib import sha1
from base64 import b64decode
import click

# Jupyter compatibility imports
try:
    # Jupyter >= 4
    from nbformat import read, write, NO_CONVERT
except ImportError:
    # IPython 3
    try:
        from IPython.nbformat import read, write, NO_CONVERT
    except ImportError:
        # IPython < 3
        from IPython.nbformat import current

        def read(f, as_version):
            return current.read(f, "json")

        def write(nb, f):
            return current.write(nb, f, "json")


def convert_indented_to_fenced_blocks(markdown: str) -> str:
    lines = markdown.splitlines(keepends=True)
    output = []
    in_fenced_block = False
    indent_threshold = None

    for i, line in enumerate(lines):
        stripped_line = line.lstrip()
        current_indent = len(line) - len(stripped_line)

        if stripped_line == '':
            # Keep empty lines as is
            output.append(line)
            continue

        if not in_fenced_block:
            # Check if we are starting an indented block
            if current_indent > 0:
                # Find the previous line that has less indentation
                if i > 0 and len(lines[i - 1].lstrip()) > 0 and (len(lines[i - 1]) - len(lines[i - 1].lstrip())) < current_indent:
                    in_fenced_block = True
                    indent_threshold = current_indent
                    output.append("```\n")
                    output.append(line[current_indent:])  # Dedent the line
                else:
                    output.append(line)
            else:
                output.append(line)
        else:
            # We are inside a fenced block
            if current_indent >= indent_threshold:
                output.append(line[current_indent:])  # Dedent the line
            else:
                # End of fenced block
                output.append("```\n")
                in_fenced_block = False
                indent_threshold = None
                output.append(line)

    if in_fenced_block:
        output.append("```\n")  # Close block if file ends in an indented block

    return ''.join(output)

# Find <img> tags and ![]() entries strip them out
def strip_image(source):
    """Remove any image or audio tags (either MD or HTML style) from a string"""
    # Define regular expressions for detecting markdown-style and HTML-style images
    markdown_image_pattern = r"!\[[^\]]*\]\([^)]*\)"
    html_image_pattern = r"<img\s+[^>]*>"
    image_credit = r"\*Image credit:.*\*"
    image = r"Image((:)|( by)).*"
    audio = r"<audio\s+[^>]*>"
    source = re.sub(markdown_image_pattern, "", source)
    source = re.sub(html_image_pattern, "", source)
    source = re.sub(image_credit, "", source)
    source = re.sub(image, "", source)
    source = re.sub(audio, "", source)
    return source


def clean_html(source):
    """Replace < and > with &lt; and &gt;"""
    source = re.sub(r"<", "&lt;", source)
    source = re.sub(r">", "&gt;", source)
    return source


def _cells(nb):
    """Yield all cells in an nbformat-insensitive manner"""
    if nb.nbformat < 4:
        for ws in nb.worksheets:
            for cell in ws.cells:
                yield cell
    else:
        for cell in nb.cells:
            yield cell


def strip_output_from_cell(cell):
    """Remove outputs and prompt numbers from code cell"""
    if "outputs" in cell:
        cell["outputs"] = []
    if "prompt_number" in cell:
        cell["prompt_number"] = None
    return cell


def sha(s):
    """return the SHA1 hash of a string"""
    return sha1(s.encode("utf8")).hexdigest()

def write_image(b64, fname):
    """Write a base64-encoded image to a file"""
    with open(fname, "wb") as f:
        f.write(b64decode(b64))

def get_attachment_path(nb_path, *args, extension="png"):
    output_dir = nb_path.resolve().parent / "generated"
    Path.mkdir(output_dir, exist_ok=True)
    cell_id = sha(nb_path.name + "".join(str(s) for s in args))
    return output_dir / f"attachment_{cell_id}.{extension}"
    

def extract_attachments(attachments, ix, nb_path):
    """Extract attachments from a cell.
    (i.e. inline base64-encoded images).

    Expects the attachments to be a dictionary of dictionaries; a cell
    index and a path (used to create a unique filename).

    Outputs images to nb_path/generated/attachment_{cell_hash}.
    """
    # get the output path and cell id
    output_names = {}
    # iterate over attachments
    for fname, attach in attachments.items():
        # note: we need to create an ID, because the filename is not unique
        
        for mimetype, b64 in attach.items():            
            extension = mimetype.split("/")[-1]
            out_name = get_attachment_path(nb_path, ix, fname, extension=extension)        
            write_image(b64, out_name)                                                    
        output_names[fname] = out_name
        click.echo(f"Extracted {fname} to {out_name}.")
    return output_names


def extract_data(data, ix, j, nb_path):
    """Extract inline data from a cell.
    Each data item is a dictionary with a mimetype and a base64-encoded
    string.

    Outputs images to nb_path/generated/data_{cell_hash}.
    """
    output_names = []
 
    for i, (mimetype, b64) in enumerate(data.items()):
        mime, extension = mimetype.split("/")
        if mime == "image":            
            out_name = get_attachment_path(nb_path, ix, j, i, mimetype, extension=extension)
            write_image(b64, out_name)
            output_names.append(out_name)
            click.echo(f"Extracted data to {out_name}.")
    
    return output_names

def strip_code_nb(
    nb,
    nb_path,
    strip_images=False,
    strip_code=True,
    strip_outputs=True,
    retain_imgs=True,
    retain_attachments=True,
):
    """strip the outputs from a notebook object"""
    nb.metadata.pop("signature", None)
    cells = []
    for ix, cell in enumerate(_cells(nb)):
        # markdown cellco
        if cell.cell_type == "markdown":
            # fix indented code blocks to make sure they are fenced
            # cell.source = convert_indented_to_fenced_blocks(cell.source) # disabled for now
            if strip_images:
                cell.source = strip_image(cell.source)
            else:
                if retain_attachments:
                    # need to check for attached images
                    if "attachments" in cell:
                        extracted = extract_attachments(cell.attachments, ix, nb_path)
                        # replace the attachment with a link
                        for fname, out_name in extracted.items():
                            cell.source = cell.source.replace(
                                f"attachment:{fname}", str(out_name)
                            )
            cell.source = clean_html(cell.source)
            cells.append(cell)
        # code cell
        if cell.cell_type == "code":            
            if not strip_code:                       
                if strip_outputs:
                    cell = strip_output_from_cell(cell)
                cell.source = clean_html(cell.source)

                if not strip_outputs:
                    # check for attached images in the data output     
                    if "outputs" in cell:
                        cell.source = strip_image(cell.source) 
                        outs = cell["outputs"]
                        cell["outputs"] = []
                        for j,output in enumerate(outs):
                            
                            if "data" in output:                                                                
                                if "text/plain" in output["data"] and "HTML" in output["data"]["text/plain"]:
                                    html = output["data"]["text/html"] 
                                    html = html.replace("\n","")
                                    output["data"]["text/html"]  = html
                                    cell["outputs"].append(output)
                                images = extract_data(output["data"], ix, j, nb_path)                                
                                if len(images)==0:
                                    cell["outputs"].append(output)
                                else:
                                    # replace the attachment with a link
                                    img_cell = cell.copy()
                                    img_cell.cell_type = "markdown"
                                    img_cell.source = ""
                                    for out_name in images:
                                        img_cell.source += f"![]({out_name})\n\n"
                                    cells.append(img_cell)
                
                cells.append(cell)                

            # check for "retain_img(...)" in this cell
            # but only if images are enabled and we have already stripped the outputs
            match = re.search(r'retain_img\("([^\)]*)"\)', cell.source)
            if match and not strip_images and strip_outputs and retain_imgs:
                img = match.group(1)
                cell = cell.copy()
                cell.cell_type = "markdown"
                # generate fake markdown cell with a link to the image
                cell.source = f"![](generated/{img})"
                cells.append(cell)

    click.echo(f"Removed {len(nb.cells)-len(cells)} code cells.")
    nb.cells = cells
    return nb


@click.command()
@click.argument("notebook_path", type=click.Path(exists=True))
@click.option(
    "--strip-images/--no-strip-images",  help="Strip images from the notebook", default=False
)
@click.option(
    "--strip-code/--no-strip-code",
    help="Strip code cells from the notebook",
    default=True,
)
@click.option(
    "--strip-output/--no-strip-output",  help="Strip output from the notebook", default=True
)
@click.option(
    "--retain-attachments/--no-retain-attachments",

    help="Retain attachments in the notebook",
    default=True,
)
@click.option(
    "--retain-imgs/--no-retain-imgs",
    help="Keep images with `retain_img()` in the code cells of a notebook",
    default=True,
)
@click.option(
    "--markdeep/--no-markdeep", help="Use Markdeep format for the output", default=True
)
@click.option(
    "--css-file",
    type=click.Path(),
    help="Path to a CSS file for styling the output",
    default=None,
)
@click.option(
    "--link-css/--no-link-css",
    help="Link to CSS file instead of embedding",
    default=False,
)
@click.option(
    "--link-markdeep/--no-link-markdeep",
    help="Link to Markdeep JS instead of embedding",
    default=False,
)
@click.option(
    "--output",
    type=click.Path(),
    help="Output file",
    default=None,
)
def convert(
    notebook_path,
    strip_images,
    strip_code,
    strip_output,
    retain_attachments,
    retain_imgs,
    markdeep,
    css_file,
    link_css,
    link_markdeep,
    output,
):
    """
    Convert a Jupyter notebook to a different format with specified options.
    """
    click.echo(f"Converting notebook {notebook_path}...")
    notebook_path = Path(notebook_path)
    nb = load_notebook(notebook_path)
    nb = strip_code_nb(
        nb,
        notebook_path,
        strip_images=strip_images,
        strip_code=strip_code,
        strip_outputs=strip_output,
        retain_attachments=retain_attachments,
        retain_imgs=retain_imgs,
    )
    export_markdown(
        nb,
        notebook_path,
        output,
        with_markdeep=markdeep,
        embed_markdeep=not link_markdeep,
        css_file=css_file,
        css_link=link_css,
    )
    click.echo("Notebook converted successfully!")


def load_notebook(path):
    with io.open(path, "r", encoding="utf8") as f:
        return read(f, as_version=NO_CONVERT)


def script_dir():
    return Path(__file__).resolve().parent


def get_markdeep(embed_markdeep=True):
    # Get the Markdeep JS (either from the local directory or from the web)
    preamble = '<script>window.markdeepOptions = {tocStyle:"none"};</script><!-- Markdeep: --><style class="fallback">body{visibility:hidden;white-space:pre;font-family:monospace}</style>'
    if embed_markdeep:
        js_file = script_dir() / "markdeep.min.js"
        with open(js_file, "r", encoding="utf8") as f:
            js = f.read()
            html_js = preamble + "<script>" + js + "</script>"
    else:
        html_js = (
            preamble
            + '<script src="https://casual-effects.com/markdeep/latest/markdeep.min.js" charset="utf-8"></script>'
        )
    return html_js


def get_css(css_file=None, link=False):
    if css_file is None:
        css_file = script_dir() / "nb_style.css"
    else:
        css_file = Path(css_file)
    if link:
        # link to css file (stripping the path)
        css = f'<link rel="stylesheet" href="{css_file.name}">'
    else:
        # embed
        with open(css_file, "r", encoding="utf8") as f:
            css = "<style>" + f.read() + "</style>"
    return css


def export_markdown(
    nb, path, output_path, with_markdeep=True, embed_markdeep=True, css_file=None, css_link=False
):
    markdown_exporter = MarkdownExporter()
    markdown_output, _ = markdown_exporter.from_notebook_node(nb)

    # add markdeep JS to footer if requested
    if with_markdeep:
        header = "<html><head><meta charset='utf-8'></head><body>\n\n"
        html_css = get_css(css_file, css_link)+"\n\n"
        html_js = get_markdeep(embed_markdeep)
        markdown_output = header + html_css + markdown_output + html_js + "</body></html>"

    if output_path is None:    
        stem = path.parent / path.stem

        # split extension from path using pathlib
        if with_markdeep:
            new_md = str(stem) + ".md.html"
        else:
            new_md = str(stem) + ".md"
    else:
        new_md = output_path

    with io.open(new_md, "w", encoding="utf8") as f:
        f.write(markdown_output)
    print(f"Writing to {new_md}.")


if __name__ == "__main__":
    convert()
