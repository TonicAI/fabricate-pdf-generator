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
export FABRICATE_API_KEY="your-api-key-here"
```

2. **Generate your first PDFs**:

```bash
python main.py --workspace Default --database ecommerce --table customers --output ./my_pdfs
```

3. **Check the results**:

```bash
ls -la ./my_pdfs/
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

### Advanced Examples

```bash
# Custom workspace with specific entity
python main.py --workspace MyWorkspace --database ecommerce --table orders --output ./output_pdfs --entity Orders

# Keep the generated database for reuse
python main.py -w Default -d ecommerce -t customers -o ./output_pdfs --keep-database --database-output-dir ./databases

# Generate image-based PDFs with custom settings
python main.py -w Default -d ecommerce -t products -o ./output_pdfs --image --title "Product Catalog"
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

## Database Integration

### Supported Structures

The application works with **any SQLite table structure**. Data is automatically formatted into professional forms regardless of the table schema.

### Example Database Structure

```sql
CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    email TEXT,
    phone TEXT,
    address TEXT,
    city TEXT,
    state TEXT,
    zip_code TEXT,
    file_size INTEGER,        -- Special: Controls PDF file size in KB
    file_name TEXT           -- Special: Custom filename for PDF
);
```

### Special Control Columns

The generator recognizes special columns that control PDF generation behavior:

| Column      | Type    | Purpose                | Notes                                                          |
| ----------- | ------- | ---------------------- | -------------------------------------------------------------- |
| `file_size` | INTEGER | Target file size in KB | Used for load testing; automatically inflates PDF to this size |
| `file_name` | TEXT    | Custom PDF filename    | Auto-sanitized for filesystem safety; must end with `.pdf`     |

**Important**: Special columns are excluded from PDF content - they control generation only.

### Sample Data

```sql
INSERT INTO customers VALUES (
    1, 'John', 'Doe', 'john.doe@email.com', '555-1234',
    '123 Main St', 'Anytown', 'CA', '12345',
    150,                     -- Generate 150KB PDF
    'customer_john_doe.pdf'  -- Custom filename
);
```

This will generate a PDF named `customer_john_doe.pdf` with a target size of 150KB containing a form with all the customer data (excluding the control columns).

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

The codebase follows a clean, modular architecture with clear separation of concerns:

| Component            | Purpose               | Key Features                                               |
| -------------------- | --------------------- | ---------------------------------------------------------- |
| **PDFGenerator**     | Main orchestrator     | Coordinates all components, manages workflow               |
| **FabricateManager** | Fabricate integration | API calls, database generation, cleanup                    |
| **DatabaseManager**  | SQLite operations     | Query execution, table validation, column detection        |
| **StyleManager**     | PDF styling           | Custom paragraph styles, layout configuration              |
| **ContentGenerator** | Form layout           | Content creation, padding for file size inflation          |
| **ImageGenerator**   | Image processing      | PIL image generation, PDF embedding for scanned simulation |
| **FileSizeInflator** | File size control     | Binary padding, size target validation                     |

### Design Principles

- **Single Responsibility**: Each class has a focused, well-defined purpose
- **Dependency Injection**: Components receive their dependencies, enabling easy testing
- **Error Handling**: Comprehensive exception handling with clear error messages
- **Resource Management**: Proper cleanup of temporary files and database connections
- **Configuration**: Environment-based configuration for Fabricate integration
