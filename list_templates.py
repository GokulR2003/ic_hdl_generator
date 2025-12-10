#!/usr/bin/env python3
import os

print("Checking what template files actually exist:")
print("=" * 60)

template_count = 0
for root, dirs, files in os.walk("hdl_templates"):
    for file in files:
        if file.endswith('.vtpl'):
            rel_path = os.path.relpath(os.path.join(root, file), "hdl_templates")
            print(f"  {rel_path}")
            template_count += 1

print(f"\nTotal template files: {template_count}")
