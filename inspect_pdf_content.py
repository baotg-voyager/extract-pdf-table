#!/usr/bin/env python3
"""
PDF Content Inspector
Helps identify employee names and IDs in the template PDF for use with the generator.
"""

import re
from pathlib import Path
from typing import Set

import pikepdf


def inspect_pdf_content(pdf_path: str, max_blocks: int = 100):
    """
    Inspect PDF content and show decoded text blocks.
    
    Args:
        pdf_path: Path to the PDF file
        max_blocks: Maximum number of text blocks to display
    """
    pdf = pikepdf.open(pdf_path)
    
    print(f"=== PDF Content Inspector ===\n")
    print(f"File: {pdf_path}")
    print(f"Total pages: {len(pdf.pages)}\n")
    
    # Extract font mappings
    font_mappings = {}
    
    for page_idx, page in enumerate(pdf.pages):
        if '/Resources' not in page:
            continue
        
        resources = page.Resources
        if '/Font' not in resources:
            continue
        
        fonts_dict = dict(resources.Font)
        
        for font_name, font_obj in fonts_dict.items():
            if font_name in font_mappings:
                continue
            
            font_mappings_dict = {}
            
            if '/ToUnicode' in font_obj:
                try:
                    to_unicode_stream = font_obj['/ToUnicode']
                    to_unicode_data = to_unicode_stream.read_bytes()
                    to_unicode_text = to_unicode_data.decode('latin-1', errors='ignore')
                    
                    # Parse mappings
                    pattern = r'<([0-9a-fA-F]+)>\s+<([0-9a-fA-F]+)>'
                    for match in re.finditer(pattern, to_unicode_text):
                        cid_hex, unicode_hex = match.groups()
                        try:
                            cid = int(cid_hex, 16)
                            unicode_val = int(unicode_hex, 16)
                            font_mappings_dict[cid] = chr(unicode_val)
                        except:
                            pass
                except Exception:
                    pass
            
            if font_mappings_dict:
                font_mappings[font_name] = font_mappings_dict
    
    print(f"Extracted {len(font_mappings)} font mappings\n")
    
    # Inspect content from last page
    page_to_inspect = pdf.pages[-1]
    
    print(f"=== Content from Last Page ===\n")
    
    if '/Contents' in page_to_inspect:
        content_ref = page_to_inspect.Contents
        
        if isinstance(content_ref, pikepdf.Array):
            stream = content_ref[0]
        else:
            stream = content_ref
        
        data = stream.read_bytes()
        content_text = data.decode('latin-1', errors='ignore')
        
        # Find and decode text blocks
        text_blocks = re.findall(r'\[(<[0-9A-Fa-f]+>(?:<[0-9A-Fa-f]+>)*)\]', content_text)
        
        print(f"Found {len(text_blocks)} text blocks\n")
        print("First decoded text blocks:")
        print("-" * 60)
        
        shown = 0
        for block in text_blocks:
            hex_cids = re.findall(r'<([0-9A-Fa-f]+)>', block)
            
            # Try to decode using each font
            for font_name, font_map in font_mappings.items():
                decoded_text = ""
                all_found = True
                
                for hex_cid in hex_cids:
                    cid = int(hex_cid, 16)
                    if cid in font_map:
                        decoded_text += font_map[cid]
                    else:
                        all_found = False
                        break
                
                if all_found and decoded_text.strip():
                    print(f"{decoded_text}")
                    shown += 1
                    break
            
            if shown >= max_blocks:
                break
        
        print("-" * 60)
    
    pdf.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        pdf_path = "materials/出勤簿 - shukkinbo - attendance book.pdf"
    
    try:
        inspect_pdf_content(pdf_path)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
