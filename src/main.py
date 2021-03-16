import argparse
import shutil
import os
import sys
from os.path import join as join_paths
import logging

from input import pdftotext
from input import tesseract
from input import tesseract4

from output import to_csv
from output import to_json
from output import to_xml

from extract.loader import load_templates


logger = logging.getLogger(__name__)

input_mapping = {
    "pdftotext": pdftotext,
    "tesseract": tesseract,
    "tesseract4": tesseract4
}

output_mapping = {
    "csv": to_csv,
    "json": to_json,
    "xml": to_xml
}


def extract_data(invoice_file, templates, input_module=pdftotext):
    """Extracts structured data from PDF/image invoices.

    This function uses the text extracted from a PDF file or image and
    pre-defined template(s) to find structured data.

    Required fields are matched from templates.

    Parameters
    ----------
    invoice_file : str
        path of electronic invoice file in PDF, JPEG, PNG
    templates : list of instances of class `InvoiceTemplate`, optional
        Templates are loaded using `load_template` function in `loader.py`
    input_module : {'pdftotext', 'tesseract'}, optional
        library to be used to extract text from the given `invoicefile`,

    Returns
    -------
    dict or False
        extracted and matched fields as dict, or None if such extraction fails,
        or False if no template matches

    Notes
    -----
    Import required `input_module` when using invoice2data as a library

    See Also
    --------
    load_templates : Function where templates are loaded
    InvoiceTemplate : Class representing a single template file that live as a .yml file on the disk
    """

    extracted_str = input_module.to_text(invoice_file).decode("utf-8")
    logger.debug(extracted_str)

    logger.debug("Checking template files")
    logger.debug(f"Done [{len(templates)} / {len(templates)}]")
    for t in templates:
        optimized_str = t.prepare_input(extracted_str)
        if t.matches_input(optimized_str):
            return t.extract(optimized_str)

    logger.error("No template found for %s", invoice_file)
    return False


def create_parser():
    """Returns an argument parser"""

    parser = argparse.ArgumentParser(
        description="Extract structured data from PDF files and save to JSON, XML, or CSV."
    )

    parser.add_argument(
        "input_file",
        help="The PDF file to analyze."
    )

    parser.add_argument(
        "--template", "--templates",
        help="A template file; can be a folder containing invoice templates."
    )

    parser.add_argument(
        "--input-reader",
        choices=input_mapping.keys(),
        default="pdftotext",
        help="Choose text extraction technology. Default: pdftotext"
    )

    parser.add_argument(
        "--output-date-format",
        default="%Y-%m-%d",
        help="Choose output date format. Default: %%Y-%%m-%%d (ISO 8601 Date)"
    )

    parser.add_argument(
        "--output-file",
        help="Name of the output file. Extension will be added based on the chosen output-format."
    )

    parser.add_argument(
        "--output-format",
        choices=output_mapping.keys(),
        default="json",
        help="Choose output format. Default: JSON"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug information."
    )

    parser.add_argument(
        "--copy",
        help="Copy and rename processed PDFs to specified folder.",
    )

    parser.add_argument(
        "--move",
        help="Move and rename processed PDFs to specified folder."
    )

    parser.add_argument(
        "--filename-format",
        dest="filename",
        default="{date} Invoice {invoice_number}.pdf",
        help="Filename format to use when moving or copying processed PDFs."
        'Default: "{date} Invoice {invoice_number}.pdf"'
    )

    parser.add_argument(
        "--include-builtin-templates",
        help="Choose whether to include or ignore built-in templates.",
        action="store_true"
    )

    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    input_module = input_mapping[args.input_reader]
    output_module = output_mapping[args.output_format]

    templates = []
    # load template/s from the the given file/folder
    if args.template:
        templates += load_templates(os.path.abspath(args.template))

    # if enabled, load internal templates as well
    if args.include_builtin_templates:
        builtin_path = os.path.join(os.getcwd(), "data", "templates")
        templates += load_templates(builtin_path)

    data = extract_data(args.input_file, templates, input_module=input_module)
    if type(data) is dict:
        logger.info(data)
        if args.copy:
            filename = args.filename.format(
                date=data["date"].strftime("%Y-%m-%d"),
                invoice_number=data["invoice_number"],
            )
            shutil.copyfile(args.input_file, join_paths(args.copy, filename))
        if args.move:
            filename = args.filename.format(
                date=data["date"].strftime("%Y-%m-%d"),
                invoice_number=data["invoice_number"],
            )
            shutil.move(args.input_file, join_paths(args.move, filename))

        if not args.output_file:
            args.output_file = f"invoice-{data['invoice_number']}"
        output_module.write_to_file(data, args.output_file, args.output_date_format)


if __name__ == "__main__":
    sys.exit(main())
