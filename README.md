# Data extractor for PDF invoices - InvoiceReader

A command line tool and Python library to support your accounting
process.

1. extracts text from PDF files using different techniques, like
   `pdftotext`, or OCR - `tesseract`, `tesseract4`.
2. searches for regex in the result using a YAML-based template system
3. saves result as CSV, JSON or XML or renames PDF files to match the content.

With the flexible template system you can:

- precisely match content PDF files
- plugins available to match line items and tables
- define static fields that are the same for every invoice
- define custom fields needed in your organisation or process
- have multiple regex per field (if layout or wording changes)
- define currency
- extract invoice-items using the `lines` - plugin developed by [Holger
  Brunn](https://github.com/hbrunn)

Go from PDF files to this:

    {'date': (2014, 5, 7), 'invoice_number': '30064443', 'amount': 34.73, 'desc': 'Invoice 30064443 from QualityHosting', 'lines': [{'price': 42.0, 'desc': u'Small Business StandardExchange 2010\nGrundgeb\xfchr pro Einheit\nDienst: OUDJQ_office\n01.05.14-31.05.14\n', 'pos': u'7', 'qty': 1.0}]}
    {'date': (2014, 6, 4), 'invoice_number': 'EUVINS1-OF5-DE-120725895', 'amount': 35.24, 'desc': 'Invoice EUVINS1-OF5-DE-120725895 from Amazon EU'}
    {'date': (2014, 8, 3), 'invoice_number': '42183017', 'amount': 4.11, 'desc': 'Invoice 42183017 from Amazon Web Services'}
    {'date': (2015, 1, 28), 'invoice_number': '12429647', 'amount': 101.0, 'desc': 'Invoice 12429647 from Envato'}

## Installation

1.  Install pdftotext

If possible get the latest
[xpdf/poppler-utils](https://poppler.freedesktop.org/) version. It's
included with macOS Homebrew, Debian and Ubuntu. Without it, `pdftotext`
won't parse tables in PDF correctly.

2.  Install `invoice2data` using pip

    pip install invoice2data

## Usage

Basic usage. Process PDF files and write result to JSON.

- `invoice2data invoice.pdf --template template-file`
- `invoice2data invoice.pdf -- templates templates-folder/`

Choose any of the following input readers:

- pdftotext `invoice2data invoice.pdf --input-reader pdftotext`
- tesseract `invoice2data invoice.pdf --input-reader tesseract`
- tesseract4 `invoice2data invoice.pdf --input-reader tesseract4`

Choose any of the following output formats:

- csv `invoice2data invoice.pdf --output-format csv`
- json `invoice2data invoice.pdf --output-format json`
- xml `invoice2data invoice.pdf --output-format xml`

Save output file with a custom name, or a specific folder

`invoice2data invoice.pdf --output-format csv --output-name myinvoices/invoice.csv invoice.pdf`

**Note:** The default `output-format` is JSON which consequently creates the file
`output_name.json`

Specify a folder with yml templates. (e.g. your suppliers)

`invoice2data invoice.pdf --templates templates/`

To include the built-in templates

`invoice2data invoice.pdf invoice.pdf --include-built-in-templates --templates templates`

Processes a single file and dumps whole file for debugging (useful when
adding new templates in templates.py)

`invoice2data my_invoice.pdf --debug`

### Use as Python Library

Using in-house templates

    from invoice2data import extract_data
    from invoice2data.extract.loader import read_templates

    templates = read_templates('/path/to/your/templates/')
    result = extract_data(filename, templates=templates)


## Template system

See `data/extract/templates` for existing templates. Just extend
the list to add your own. If deployed by a bigger organisation, there
should be an interface to edit templates for new suppliers. 80-20 rule.
For a short tutorial on how to add new templates, see [TUTORIAL.md](TUTORIAL.md).

Templates are based on Yaml. They define one or more keywords to find
the right template and regexp for fields to be extracted. They could
also be a static value, like the full company name.

Template files are tried in alphabetical order.

We may extend them to feature options to be used during invoice
processing.

Example:

    issuer: Amazon Web Services, Inc.
    keywords:
    - Amazon Web Services
    fields:
      amount: TOTAL AMOUNT DUE ON.*\$(\d+\.\d+)
      amount_untaxed: TOTAL AMOUNT DUE ON.*\$(\d+\.\d+)
      date: Invoice Date:\s+([a-zA-Z]+ \d+ , \d+)
      invoice_number: Invoice Number:\s+(\d+)
      partner_name: (Amazon Web Services, Inc\.)
    options:
      remove_whitespace: false
      currency: HKD
      date_formats:
        - '%d/%m/%Y'
    lines:
        start: Detail
        end: \* May include estimated US sales tax
        first_line: ^    (?P<description>\w+.*)\$(?P<price_unit>\d+\.\d+)
        line: (.*)\$(\d+\.\d+)
        last_line: VAT \*\*

## Development

If you are interested in improving this project, have a look at our
[developer guide](DEVELOP.md) to get you started quickly.

## Roadmap and open tasks

- integrate with online OCR?
- try to 'guess' parameters for new invoice formats.
- can apply machine learning to guess new parameters?

## Developers

-   [Muhammed W. Drammeh](https://www.github.com/w-drammeh)
-   [Modou K Touray](https://github.com/mktcyber/)

## References

This project is being influenced by:

-   [invoice2data](https://github.com/m3nu/invoice2data)
