#!/usr/bin/env python3
"""Test script for HTML to PDF merge functionality."""

import sys
import os
import tempfile

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QEventLoop, QTimer
from img_to_pdf.core.html_to_pdf_converter import HtmlToPdfConverter
from PIL import Image

def test_html_merge():
    """Test merging 3 HTML files into one PDF."""
    print("🧪 Testing HTML to PDF Merge...")
    
    # Create Qt Application (required for WebEngine)
    app = QApplication(sys.argv)
    
    # Find slide files
    slide_files = []
    for i in range(1, 4):
        slide_path = f"slide{i}.html"
        if os.path.exists(slide_path):
            slide_files.append(os.path.abspath(slide_path))
            print(f"✓ Found: {slide_path}")
        else:
            print(f"✗ Missing: {slide_path}")
            return False
    
    if len(slide_files) != 3:
        print("❌ Need exactly 3 slide files!")
        return False
    
    # Step 1: Convert HTML to PDF
    print("\n📄 Converting HTML files to PDF...")
    temp_pdfs = []
    
    for i, html_file in enumerate(slide_files, 1):
        print(f"  [{i}/3] Converting {os.path.basename(html_file)}...", end=" ")
        
        # Create temp PDF
        temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_pdf.close()
        temp_pdf_path = temp_pdf.name
        
        # Convert
        converter = HtmlToPdfConverter()
        result = converter.convert_file_sync(html_file, temp_pdf_path)
        
        if result and os.path.exists(result):
            file_size = os.path.getsize(result)
            print(f"✓ ({file_size:,} bytes)")
            temp_pdfs.append(result)
        else:
            print("✗ Failed!")
            return False
    
    # Step 2: Merge PDFs using pypdf
    print(f"\n📚 Merging {len(temp_pdfs)} PDFs using pypdf...")
    output_pdf = "merged_slides.pdf"
    
    try:
        from pypdf import PdfWriter
        
        merger = PdfWriter()
        for i, pdf_path in enumerate(temp_pdfs, 1):
            print(f"  [{i}/{len(temp_pdfs)}] Adding {os.path.basename(pdf_path)}...")
            merger.append(pdf_path)
        
        print(f"\n💾 Saving merged PDF: {output_pdf}")
        merger.write(output_pdf)
        merger.close()
        
        final_size = os.path.getsize(output_pdf)
        print(f"✅ Success! Created {output_pdf} ({final_size:,} bytes)")
    
    finally:
        # Clean up temp files
        print("\n🧹 Cleaning up temp files...")
        for temp_pdf in temp_pdfs:
            try:
                os.unlink(temp_pdf)
                print(f"  ✓ Deleted {os.path.basename(temp_pdf)}")
            except:
                pass
    
    print("\n" + "="*50)
    print("✅ TEST COMPLETED!")
    print(f"📁 Output: {os.path.abspath(output_pdf)}")
    print("="*50)
    
    return True

if __name__ == "__main__":
    try:
        success = test_html_merge()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
