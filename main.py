#!/usr/bin/env python3
"""
Main entry point for PDF Generator.

This script provides the command-line interface for generating PDFs
from SQLite database rows with support for load testing features.
"""

import argparse
import os
import sys

from pdf_generator import PDFGenerator, FabricateManager, create_progress_callback


def main():
    """Main entry point with argument parsing"""
    parser = argparse.ArgumentParser(
        description="Generate PDFs from Fabricate database rows for load testing",
        epilog="""
Examples:
  # Generate PDFs from Fabricate database
  python %(prog)s --workspace Default --database ecommerce --table customers --output ./pdfs
  
  # Generate with image mode and custom title
  python %(prog)s -w MyWorkspace -d ecommerce -t orders -o ./pdfs --image --title "Order Forms"
  
  # Generate specific entity and keep database
  python %(prog)s --workspace Default --database ecommerce --table orders --output ./pdfs --entity Orders --keep-database
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Required arguments
    parser.add_argument("--workspace", "-w", required=True,
                       help="Fabricate workspace name")
    parser.add_argument("--database", "-d", required=True,
                       help="Fabricate database name to generate")
    parser.add_argument("--table", "-t", required=True,
                       help="Name of the database table to process")
    parser.add_argument("--output", "-o", required=True,
                       help="Output directory for generated PDFs")
    
    # Optional arguments
    parser.add_argument("--image", action="store_true",
                       help="Generate image-based PDFs (simulates scanned documents)")
    parser.add_argument("--title",
                       help="Custom title for the forms (default: table name with proper formatting)")
    parser.add_argument("--entity", "-e",
                       help="Generate only a specific table/entity from Fabricate")
    parser.add_argument("--keep-database", action="store_true",
                       help="Keep generated Fabricate database after PDF generation")
    parser.add_argument("--database-output-dir",
                       help="Directory to save generated Fabricate database (default: temporary)")
    
    parser.add_argument("--version", action="version", version="PDF Generator 1.0.0")
    
    args = parser.parse_args()
    
    fabricate_manager = None
    
    try:
        # Generate database using Fabricate
        print(f"🚀 Generating database '{args.database}' from workspace '{args.workspace}'...")
        
        fabricate_manager = FabricateManager(workspace=args.workspace)
        
        # Create progress callback
        progress_callback = create_progress_callback(verbose=True)
        
        # Generate the database
        db_path = fabricate_manager.generate_database(
            database_name=args.database,
            output_dir=args.database_output_dir,
            entity=args.entity,
            on_progress=progress_callback
        )
        
        # Create and run PDF generator
        print(f"\n📄 Generating PDFs from table '{args.table}'...")
        generator = PDFGenerator(
            db_path=db_path,
            table_name=args.table,
            output_dir=args.output,
            use_image=args.image,
            title=args.title
        )
        
        generator.generate_all_pdfs()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
        
    finally:
        # Cleanup Fabricate database if not keeping it
        if fabricate_manager and not args.keep_database:
            fabricate_manager.cleanup_temp_database()


if __name__ == "__main__":
    main()
