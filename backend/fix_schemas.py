#!/usr/bin/env python3
"""Fix schema files for Python 3.9 compatibility."""

import re
from pathlib import Path

schemas_dir = Path("app/schemas")

# Patterns to replace
patterns = [
    (r': str \| None', ': Optional[str]'),
    (r': int \| None', ': Optional[int]'),
    (r': bool \| None', ': Optional[bool]'),
    (r': datetime \| None', ': Optional[datetime]'),
    (r': EmailStr \| None', ': Optional[EmailStr]'),
    (r': dict\[str, Any\] \| None', ': Optional[dict[str, Any]]'),
]

for schema_file in schemas_dir.glob("*.py"):
    if schema_file.name == "__init__.py":
        continue

    print(f"Processing {schema_file}...")
    content = schema_file.read_text()

    # Apply replacements
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)

    # Add Optional import if needed
    if 'Optional[' in content and 'from typing import Optional' not in content:
        # Find existing typing imports
        typing_import = re.search(r'from typing import (.*)', content)
        if typing_import:
            # Add Optional to existing import
            imports = typing_import.group(1)
            if 'Optional' not in imports:
                new_imports = f"Optional, {imports}"
                content = content.replace(f"from typing import {imports}", f"from typing import {new_imports}")
        else:
            # Add new typing import after __future__
            content = content.replace(
                'from __future__ import annotations\n',
                'from __future__ import annotations\nfrom typing import Optional\n'
            )

    schema_file.write_text(content)

print("Done!")
