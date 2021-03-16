# Development

If you are looking to get involved improving `InvoiceReader`, this guide
will help you get started quickly.

## Install

1. Clone repository: `https://...`
3. Install dependencies: `pip install -r requirements.txt`

Some little-used dependencies are optional; like `pytesseract`. Install if needed.


## Folders

Major folders in the `InvoiceReader` package and their purpose:

-   `input`: Has modules for extracting plain text from files. Currently,
    mostly PDF files.
-   `extract`: Get useful data from plain text using templates. The main
    class -- `BaseInvoiceTemplate` -- is in `base_template`. Other
    classes can add extra functions and inherit from it. E.g.
    `LineInvoiceTemplate` adds support for getting individual items.
-   `extract/templates`: Keeps all supported template files. Add new
    templates here.
-   `output`: Modules to output structured data. Currently `CSV`, `JSON`
    and `XML` are supported.
    
