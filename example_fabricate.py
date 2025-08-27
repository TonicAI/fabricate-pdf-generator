#!/usr/bin/env python3
"""
Example script demonstrating Fabricate integration with PDF Generator.

This script shows how to use the FabricateManager to generate databases
dynamically and then create PDFs from them.
"""

import os
from pdf_generator import FabricateManager, PDFGenerator, create_progress_callback


def main():
    """Example Fabricate integration"""
    
    # Check if API key is set
    if not os.environ.get('FABRICATE_API_KEY'):
        print("❌ Please set your FABRICATE_API_KEY environment variable:")
        print("   export FABRICATE_API_KEY='your-api-key-here'")
        return
    
    print("🚀 Fabricate PDF Generator Example")
    print("=" * 50)
    
    # Example: Generate database and PDFs with automatic cleanup
    with FabricateManager(workspace='Default') as fabricate:
        try:
            print("\n📊 Generating 'ecommerce' database from Fabricate...")
            
            # Create progress callback
            progress = create_progress_callback(verbose=True)
            
            # Generate database
            db_path = fabricate.generate_database(
                database_name='ecommerce',
                on_progress=progress
            )
            
            print(f"\n📄 Creating PDFs from 'customers' table...")
            
            # Generate PDFs
            generator = PDFGenerator(
                db_path=db_path,
                table_name='customers',
                output_dir='./example_output',
                use_image=True,  # Use image mode for scanned look
                title="Customer Information Form"
            )
            
            generator.generate_all_pdfs()
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return
    
    print("\n✅ Example completed successfully!")
    print("🧹 Temporary database automatically cleaned up")
    print("📁 Check './example_output' for generated PDFs")


if __name__ == "__main__":
    main()
