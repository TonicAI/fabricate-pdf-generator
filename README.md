# PDF Generator for Load Testing

A Python application that generates PDFs from Fabricate database rows, with optional image conversion to simulate scanned documents.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
# Generate PDFs from Fabricate database
python main.py --workspace Default --database ecommerce --table customers --output ./output_pdfs
```

### With Image Conversion (Simulated Scans)

```bash
python main.py --workspace Default --database ecommerce --table customers --output ./output_pdfs --image
```

### With Custom Title

```bash
python main.py --workspace Default --database ecommerce --table customers --output ./output_pdfs --title "Customer Registration Form"
```

### Advanced Options

```bash
# Custom workspace
python main.py --workspace MyWorkspace --database ecommerce --table orders --output ./output_pdfs

# Keep the generated database for reuse
python main.py -w Default -d ecommerce -t customers -o ./output_pdfs --keep-database --database-output-dir ./databases

# Generate only a specific entity/table
python main.py -w Default -d ecommerce -t customers -o ./output_pdfs --entity Customers
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

### Advanced Options

- `--entity, -e`: Generate only a specific table/entity from Fabricate
- `--keep-database`: Keep generated Fabricate database after PDF generation
- `--database-output-dir`: Directory to save generated Fabricate database (default: temporary)

## Fabricate Configuration

When using Fabricate database generation, you need to configure your API credentials:

### Environment Variables

The Fabricate client automatically uses these environment variables:

- `FABRICATE_API_KEY`: Your Fabricate API key (required)
- `FABRICATE_API_URL`: The Fabricate API URL (optional, defaults to https://fabricate.tonic.ai/api/v1)

### Setup

```bash
# Set your API key
export FABRICATE_API_KEY="your-api-key-here"

# Optional: Set custom API URL
export FABRICATE_API_URL="https://your-fabricate-instance.com/api/v1"
```

### Example Script

See `example_fabricate.py` for a complete example of using the Fabricate integration programmatically.

## Features

- **Fabricate Integration**: Generate SQLite databases on-demand using Fabricate
- **Form-like Layout**: Creates professional-looking forms from database data
- **Image Mode**: Generates high-quality images, then embeds them in PDFs to simulate scanned documents
- **File Size Inflation**: Automatically inflates PDFs to match `file_size` column values (in KB) for load testing
- **Smart Title Generation**: Uses table name by default, customizable with `--title`
- **Automatic Naming**: PDFs are named using the first column value and row index
- **Modular Architecture**: Clean, readable code with separated concerns
- **Progress Tracking**: Real-time progress updates during Fabricate database generation
- **Error Handling**: Robust error handling for database and file operations
- **Flexible**: Works with any SQLite table structure

## Output

- **PDF Mode**: Generates clean, text-based PDF forms
- **Image Mode**: Generates PDFs containing embedded images (simulating scanned documents)
- **File Size Control**: Automatically inflates files to match database `file_size` column (in KB)
- Files are named: `form_{first_column_value}_{row_index}.pdf`

## Example Database Structure

The application works with any SQLite table. Example:

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT,
    phone TEXT,
    address TEXT
);
```

Each row will generate a separate PDF with all columns formatted as a form.

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

### Architecture

The codebase follows a modular architecture with clear separation of concerns:

- **StyleManager**: Handles all PDF styling and paragraph styles
- **ContentGenerator**: Creates form layouts and manages PDF content
- **ImageGenerator**: Generates PIL images for scanned document simulation
- **FileSizeInflator**: Manages file size inflation for load testing
- **DatabaseManager**: Handles SQLite database operations
- **FabricateManager**: Integrates with Fabricate for dynamic database generation
- **PDFGenerator**: Main orchestrator that coordinates all components
