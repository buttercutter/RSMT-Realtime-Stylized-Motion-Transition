#!/usr/bin/env python3
"""
RSMT Documentation Link Checker
Validates links and references in documentation files.
"""

import re
import sys
from pathlib import Path
from typing import List, Dict, Any, Set
import urllib.request
import urllib.error
import argparse


class RSMTDocChecker:
    """Checks documentation for broken links and references."""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.checked_urls = {}  # Cache for URL checks
        
    def check_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Check a single documentation file."""
        issues = []
        
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Check markdown links
            issues.extend(self._check_markdown_links(file_path, content))
            
            # Check internal references
            issues.extend(self._check_internal_references(file_path, content))
            
            # Check code references
            issues.extend(self._check_code_references(file_path, content))
            
            # Check image references
            issues.extend(self._check_image_references(file_path, content))
            
        except Exception as e:
            issues.append({
                'file': str(file_path),
                'line': 0,
                'type': 'error',
                'message': f"Failed to check file: {e}"
            })
        
        return issues
    
    def _check_markdown_links(self, file_path: Path, content: str) -> List[Dict[str, Any]]:
        """Check markdown-style links [text](url)."""
        issues = []
        lines = content.split('\n')
        
        # Pattern for markdown links
        link_pattern = r'\[([^\]]*)\]\(([^)]+)\)'
        
        for line_num, line in enumerate(lines, 1):
            matches = re.finditer(link_pattern, line)
            
            for match in matches:
                text, url = match.groups()
                
                # Skip empty links
                if not url.strip():
                    issues.append({
                        'file': str(file_path),
                        'line': line_num,
                        'type': 'error',
                        'message': f"Empty link: [{text}]()"
                    })
                    continue
                
                # Check different types of links
                if url.startswith('http://') or url.startswith('https://'):
                    # External URL
                    issues.extend(self._check_external_url(file_path, line_num, url))
                elif url.startswith('#'):
                    # Anchor link
                    issues.extend(self._check_anchor_link(file_path, line_num, url, content))
                elif url.startswith('/') or not url.startswith('mailto:'):
                    # Relative path
                    issues.extend(self._check_relative_path(file_path, line_num, url))
        
        return issues
    
    def _check_internal_references(self, file_path: Path, content: str) -> List[Dict[str, Any]]:
        """Check internal file references and includes."""
        issues = []
        lines = content.split('\n')
        
        # Pattern for file references like `src/core/models/base.py`
        file_ref_pattern = r'`([^`]+\.py)`'
        
        for line_num, line in enumerate(lines, 1):
            matches = re.finditer(file_ref_pattern, line)
            
            for match in matches:
                ref_path = match.group(1)
                
                # Check if file exists
                full_path = file_path.parent / ref_path
                if not full_path.exists():
                    # Try from project root
                    root_path = self._find_project_root(file_path) / ref_path
                    if not root_path.exists():
                        issues.append({
                            'file': str(file_path),
                            'line': line_num,
                            'type': 'warning',
                            'message': f"Referenced file not found: {ref_path}"
                        })
        
        return issues
    
    def _check_code_references(self, file_path: Path, content: str) -> List[Dict[str, Any]]:
        """Check references to classes, functions, and modules."""
        issues = []
        lines = content.split('\n')
        
        # Pattern for code references like `rsmt.core.models.BaseModel`
        code_ref_pattern = r'`(rsmt\.[a-zA-Z0-9_.]+)`'
        
        for line_num, line in enumerate(lines, 1):
            matches = re.finditer(code_ref_pattern, line)
            
            for match in matches:
                ref = match.group(1)
                
                # Try to import and check if it exists
                try:
                    # This is a simplified check - in a real implementation,
                    # you'd want to parse the actual module structure
                    parts = ref.split('.')
                    if len(parts) < 2 or parts[0] != 'rsmt':
                        issues.append({
                            'file': str(file_path),
                            'line': line_num,
                            'type': 'warning',
                            'message': f"Invalid code reference format: {ref}"
                        })
                except Exception:
                    # Could not validate reference
                    pass
        
        return issues
    
    def _check_image_references(self, file_path: Path, content: str) -> List[Dict[str, Any]]:
        """Check image references."""
        issues = []
        lines = content.split('\n')
        
        # Pattern for image references ![alt](path)
        img_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
        
        for line_num, line in enumerate(lines, 1):
            matches = re.finditer(img_pattern, line)
            
            for match in matches:
                alt_text, img_path = match.groups()
                
                # Check if image file exists
                if not img_path.startswith('http'):
                    full_path = file_path.parent / img_path
                    if not full_path.exists():
                        # Try from project root
                        root_path = self._find_project_root(file_path) / img_path
                        if not root_path.exists():
                            issues.append({
                                'file': str(file_path),
                                'line': line_num,
                                'type': 'error',
                                'message': f"Image not found: {img_path}"
                            })
                
                # Check alt text
                if not alt_text.strip():
                    issues.append({
                        'file': str(file_path),
                        'line': line_num,
                        'type': 'warning',
                        'message': f"Image missing alt text: {img_path}"
                    })
        
        return issues
    
    def _check_external_url(self, file_path: Path, line_num: int, url: str) -> List[Dict[str, Any]]:
        """Check if external URL is accessible."""
        issues = []
        
        # Skip checking in quick mode or if already checked
        if url in self.checked_urls:
            if not self.checked_urls[url]:
                issues.append({
                    'file': str(file_path),
                    'line': line_num,
                    'type': 'warning',
                    'message': f"External URL not accessible: {url}"
                })
            return issues
        
        try:
            # Quick HEAD request to check if URL exists
            req = urllib.request.Request(url, method='HEAD')
            req.add_header('User-Agent', 'RSMT-DocChecker/1.0')
            
            with urllib.request.urlopen(req, timeout=10) as response:
                self.checked_urls[url] = response.getcode() < 400
                
        except (urllib.error.URLError, urllib.error.HTTPError, Exception):
            self.checked_urls[url] = False
            issues.append({
                'file': str(file_path),
                'line': line_num,
                'type': 'warning',
                'message': f"External URL not accessible: {url}"
            })
        
        return issues
    
    def _check_anchor_link(self, file_path: Path, line_num: int, anchor: str, content: str) -> List[Dict[str, Any]]:
        """Check if anchor link target exists in the document."""
        issues = []
        
        # Remove the # from anchor
        target = anchor[1:].lower().replace(' ', '-')
        
        # Look for headers that would create this anchor
        header_patterns = [
            rf'^#{1,6}\s+.*{re.escape(target)}.*$',
            rf'^#{1,6}\s+.*{re.escape(target.replace("-", " "))}.*$',
        ]
        
        found = False
        for pattern in header_patterns:
            if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                found = True
                break
        
        if not found:
            issues.append({
                'file': str(file_path),
                'line': line_num,
                'type': 'warning',
                'message': f"Anchor target not found: {anchor}"
            })
        
        return issues
    
    def _check_relative_path(self, file_path: Path, line_num: int, rel_path: str) -> List[Dict[str, Any]]:
        """Check if relative path exists."""
        issues = []
        
        # Resolve relative path
        if rel_path.startswith('/'):
            # Absolute path from project root
            target_path = self._find_project_root(file_path) / rel_path[1:]
        else:
            # Relative to current file
            target_path = file_path.parent / rel_path
        
        if not target_path.exists():
            issues.append({
                'file': str(file_path),
                'line': line_num,
                'type': 'error',
                'message': f"File not found: {rel_path}"
            })
        
        return issues
    
    def _find_project_root(self, file_path: Path) -> Path:
        """Find the project root directory."""
        current = file_path.parent
        
        while current != current.parent:
            if (current / '.git').exists() or (current / 'pyproject.toml').exists():
                return current
            current = current.parent
        
        return Path('.')


def main():
    parser = argparse.ArgumentParser(description='Check RSMT documentation links')
    parser.add_argument('files', nargs='*', help='Files to check')
    parser.add_argument('--external', action='store_true', help='Check external URLs (slower)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    checker = RSMTDocChecker()
    all_issues = []
    
    # Get files to check
    if args.files:
        files = [Path(f) for f in args.files if f.suffix in ['.md', '.rst', '.txt']]
    else:
        # Check all documentation files
        files = []
        for pattern in ['docs/**/*.md', '*.md', 'docs/**/*.rst']:
            files.extend(Path('.').glob(pattern))
    
    # Check each file
    for file_path in files:
        if file_path.exists():
            issues = checker.check_file(file_path)
            all_issues.extend(issues)
    
    # Filter out external URL checks if not requested
    if not args.external:
        all_issues = [i for i in all_issues if 'External URL' not in i['message']]
    
    # Report issues
    errors = [i for i in all_issues if i['type'] == 'error']
    warnings = [i for i in all_issues if i['type'] == 'warning']
    
    if args.verbose or errors or warnings:
        print(f"RSMT Documentation Check Results:")
        print(f"Files checked: {len(files)}")
        print(f"Errors: {len(errors)}")
        print(f"Warnings: {len(warnings)}")
        print()
    
    # Print errors
    for issue in errors:
        print(f"ERROR: {issue['file']}:{issue['line']} - {issue['message']}")
    
    # Print warnings  
    for issue in warnings:
        print(f"WARNING: {issue['file']}:{issue['line']} - {issue['message']}")
    
    # Exit code
    if errors:
        sys.exit(1)
    elif warnings and not args.verbose:
        print(f"\n{len(warnings)} warnings found. Use --verbose for details.")
    
    sys.exit(0)


if __name__ == '__main__':
    main()
