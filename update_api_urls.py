"""
Script to update all hardcoded localhost URLs to use dynamic API configuration
"""
import os
import re
from pathlib import Path

def update_html_files():
    frontend_dir = Path(__file__).parent / 'frontend'
    
    # Pattern to match fetch calls with localhost URLs
    patterns = [
        (r"fetch\('http://localhost:8000(/[^']*)'", r"fetch(getApiUrl('\1')"),
        (r'fetch\("http://localhost:8000(/[^"]*)"', r'fetch(getApiUrl("\1")'),
        (r"fetch\(`http://localhost:8000(/[^`]*)`", r"fetch(getApiUrl(`\1`)"),
        (r"const BACKEND_URL = 'http://localhost:8000';", "const BACKEND_URL = getApiUrl('');"),
        (r'<code id="backend-url">http://localhost:8000</code>', '<code id="backend-url"><script>document.write(getApiUrl(\'\'));</script></code>'),
    ]
    
    files_to_update = []
    
    # Find all HTML files
    for html_file in frontend_dir.rglob('*.html'):
        files_to_update.append(html_file)
    
    updated_files = []
    
    for file_path in files_to_update:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Apply all patterns
            for pattern, replacement in patterns:
                content = re.sub(pattern, replacement, content)
            
            # Check if content changed
            if content != original_content:
                # Add config.js and api-helper.js scripts before </head> if not present
                if '<script src="config.js"></script>' not in content and '<script src="/config.js"></script>' not in content:
                    # Find </head> and add scripts before it
                    content = content.replace('</head>', '    <script src="/config.js"></script>\n    <script src="/api-helper.js"></script>\n</head>')
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                updated_files.append(str(file_path.relative_to(frontend_dir)))
                print(f"✓ Updated: {file_path.relative_to(frontend_dir)}")
        
        except Exception as e:
            print(f"✗ Error updating {file_path}: {e}")
    
    return updated_files

if __name__ == '__main__':
    print("Updating HTML files to use dynamic API configuration...")
    print("=" * 60)
    
    updated = update_html_files()
    
    print("=" * 60)
    print(f"\nTotal files updated: {len(updated)}")
    
    if updated:
        print("\nUpdated files:")
        for file in updated:
            print(f"  - {file}")
