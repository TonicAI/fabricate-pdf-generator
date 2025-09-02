# PDF Generator for Load Testing

A Python application that generates PDFs from Fabricate database rows, with optional image conversion to simulate scanned documents. Perfect for load testing scenarios that require realistic PDF files with customizable sizes.

## Installation

### Prerequisites

- Python 3.8+
- Virtual environment (recommended)

### Setup

1. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Quick Start

1. **Set up Fabricate credentials**:

```bash
export FABRICATE_API_KEY="your-api-key-here" # On Windows: $env:FABRICATE_API_KEY = "your-api-key-here"
```

2. **Create your Fabricate Fatabase**:

Sign into [Fabricate](https://fabricate.tonic.ai) and create a new database and table. Add columns for the data that you want to be included in the generated PDFs. You can control the file size and file names by adding columns called `file_size` and `file_name`. See the [Fabricate Configuration](#fabricate-configuration) section for more details.

3. **Generate your PDFs**:

```bash
python main.py --workspace my_workspace --database my_database --table my_table --output ./pdfs
```

## Usage

### Basic Usage

```bash
python main.py --workspace Default --database ecommerce --table customers --output ./output_pdfs
```

### With Image Conversion (Simulated Scans)

The following command will generate PDFs with embedded images that simulate scanned documents:

```bash
python main.py --workspace Default --database ecommerce --table customers --output ./output_pdfs --image
```

### With Custom Title

The following command will generate PDFs with a custom title:

```bash
python main.py --workspace Default --database ecommerce --table customers --output ./output_pdfs --title "Customer Registration Form"
```

## CLI Options

### Required Options

- `--workspace, -w`: Fabricate workspace name (required)
- `--database, -d`: Fabricate database name to generate (required)
- `--table, -t`: Name of the database table to process (required)
- `--output, -o`: Output directory for generated PDFs (required)

### PDF Generation Options

- `--image`: Generate image-based PDFs simulating scanned documents
- `--title`: Custom title for the forms (default: table name with proper formatting)

## Environment Variables

The PDF generator uses the Fabricate service to dynamically generate SQLite databases for testing. You need to configure your API credentials:

Set these environment variables before running the application:

- `FABRICATE_API_KEY`: Your Fabricate API key (required)
- `FABRICATE_API_URL`: The Fabricate API URL (optional, only set if you are using a self-hosted Fabricate instance)

## Features

- **Fabricate Integration**: Generate SQLite databases on-demand using Fabricate
- **Dual Generation Modes**:
  - **Direct PDF**: Clean text-based forms
  - **Image Mode**: High-quality image generation → PDF embedding (simulates scanned documents)
- **Flexible PDF Naming**:
  - Uses `file_name` column if present in database
  - Falls back to `{row_index}.pdf`
  - Automatic filename sanitization for filesystem compatibility
- **Dynamic Titles**: Uses table name by default, customizable with `--title`

## Output

- **PDF Mode**: Generates clean, text-based PDF forms with professional layout
- **Image Mode**: Generates PDFs containing embedded images (simulating scanned documents)
- **File Size Control**: Automatically inflates files to match database `file_size` column (in KB)
- **Smart Naming**:
  - Uses `file_name` column if present in database
  - Falls back to `{row_index}.pdf`
  - Automatically sanitizes filenames for filesystem compatibility

## Fabricate Configuration

The generator uses Fabricate to dynamically generate data for the PDF files. Create a Fabricate database and add a table with any columns you want to include in the PDF.

### Special Control Columns

The generator recognizes special columns that control PDF generation behavior:

| Column      | Type    | Purpose                | Notes                                                          |
| ----------- | ------- | ---------------------- | -------------------------------------------------------------- |
| `file_size` | INTEGER | Target file size in KB | Used for load testing; automatically inflates PDF to this size |
| `file_name` | TEXT    | Custom PDF filename    | Auto-sanitized for filesystem safety; must end with `.pdf`     |

**Important**: Special columns are excluded from PDF content - they control generation only.

## Project Structure

```
pdf-generator/
├── main.py                 # Command-line entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── pdf_generator/         # Main package
    ├── __init__.py        # Package initialization
    ├── generator.py       # Main PDF generator orchestrator
    ├── styles.py          # PDF styling and layout management
    ├── content.py         # PDF content creation and form layout
    ├── images.py          # Image generation for scanned document simulation
    ├── inflation.py       # File size inflation utilities
    ├── database.py        # Database operations and connectivity
    └── fabricate.py       # Fabricate integration for dynamic database generation
```
