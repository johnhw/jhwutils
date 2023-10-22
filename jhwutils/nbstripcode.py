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

def extract_attachments(attachments, ix, nb_path):
    """Extract attachments from a cell.
    (i.e. inline base64-encoded images).

    Expects the attachments to be a dictionary of dictionaries; a cell
    index and a path (used to create a unique filename).

    Outputs images to nb_path/generated/attachment_{cell_id}_{fname}.
    """
    # get the output path and cell id
    output_dir = nb_path.resolve().parent / "generated"
    Path.mkdir(output_dir, exist_ok=True)
    cell_id = sha(nb_path.name + str(ix))
    output_names = {}
    # iterate over attachments
    for fname, attach in attachments.items():
        # note: we need to create an ID, because the filename is not unique
        out_name = output_dir / f"attachment_{cell_id}_{fname}"
        with open(out_name, "wb") as f:
            for mimetype, b64 in attach.items():
                attachment = b64decode(b64)
                f.write(attachment)
        output_names[fname] = out_name
        print(f"Extracted {fname} to {out_name}.")
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
        # markdown cell
        if cell.cell_type == "markdown":
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
            cells.append(cell)
        # code cell
        if cell.cell_type == "code":
            if strip_outputs:
                cell = strip_output_from_cell(cell)
            if not strip_code:
                cells.append(cell)
            # check for "retain_img(...)" in this cell
            match = re.search(r'retain_img\("([^\)]*)"\)', cell.source)
            if match and not strip_images and retain_imgs:
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
    "--strip-images", is_flag=True, help="Strip images from the notebook", default=False
)
@click.option(
    "--strip-code",
    is_flag=True,
    help="Strip code cells from the notebook",
    default=True,
)
@click.option(
    "--strip-output", is_flag=True, help="Strip output from the notebook", default=True
)
@click.option(
    "--retain-attachments",
    is_flag=True,
    help="Retain attachments in the notebook",
    default=True,
)
@click.option(
    "--retain-imgs",
    is_flag=True,
    help="Keep images with `retain_img()` in the code cells of a notebook",
    default=True,
)
@click.option(
    "--markdeep", is_flag=True, help="Use Markdeep format for the output", default=True
)
@click.option(
    "--css-file",
    type=click.Path(),
    help="Path to a CSS file for styling the output",
    default=None,
)
@click.option(
    "--link-css",
    is_flag=True,
    help="Link to CSS file instead of embedding",
    default=False,
)
@click.option(
    "--link-markdeep",
    is_flag=True,
    help="Link to Markdeep JS instead of embedding",
    default=False,
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
    nb, path, with_markdeep=True, embed_markdeep=True, css_file=None, css_link=False
):
    markdown_exporter = MarkdownExporter()
    markdown_output, _ = markdown_exporter.from_notebook_node(nb)

    # add markdeep JS to footer if requested
    if with_markdeep:
        header = "<html><head><meta charset='utf-8'></head><body>\n\n"
        html_css = get_css(css_file, css_link)+"\n\n"
        html_js = get_markdeep(embed_markdeep)
        markdown_output = header + html_css + markdown_output + html_js + "</body></html>"

    stem = path.parent / path.stem
    # split extension from path using pathlib
    if with_markdeep:
        new_md = str(stem) + ".md.html"
    else:
        new_md = str(stem) + ".md"
    with io.open(new_md, "w", encoding="utf8") as f:
        f.write(markdown_output)
    print(f"Writing to {new_md}.")


if __name__ == "__main__":
    convert()
