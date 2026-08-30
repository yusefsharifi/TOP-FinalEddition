#!/usr/bin/env python3
"""
Final comprehensive JSX closing tag fixer.
Fixes ALL remaining mismatches from MUI->Ant Design migration.
"""
import re
import os


def fix_grid_tags(lines):
    """Fix </Grid> tags to match <Row> and <Col> openings."""
    # Strategy: Use a tag stack. When we see <Row> or <Col>, push. When we see </Grid>, pop and use the right closing.
    stack = []
    for i, line in enumerate(lines):
        # Find Row openings
        if '<Row' in line and '</Row>' not in line and '/>' not in line.split('<Row')[1].split('>')[0] if '<Row' in line else False:
            stack.append(('Row', i))
        # Find Col openings
        for m in re.finditer(r'<Col\b', line):
            rest = line[m.start():]
            if '/>' not in rest.split('>')[0]:
                stack.append(('Col', i))
        # Find </Grid> closings
        for m in re.finditer(r'</Grid>', line):
            if stack:
                tag_type, _ = stack.pop()
                new_close = f'</{tag_type}>'
                lines[i] = lines[i].replace('</Grid>', new_close, 1)
    return lines


def fix_typography_tags(lines):
    """Fix Typography.Title and Typography.Text closing tags.
    
    When we see <Typography.Title ...> we need </Typography.Title>
    When we see <Typography.Text ...> we need </Typography.Text>
    When we see <Typography ...> we need </Typography>
    """
    stack = []
    for i, line in enumerate(lines):
        # Find Typography sub-component openings
        for m in re.finditer(r'<Typography\.(Title|Text)\b', line):
            variant = m.group(1)
            rest = line[m.start():]
            is_self_closing = '/>' in rest.split('>')[0]
            if not is_self_closing:
                stack.append((variant, i))
        
        # Find </Typography> closings that should be </Typography.Title> or </Typography.Text>
        if '</Typography>' in line and stack:
            variant, _ = stack.pop()
            lines[i] = lines[i].replace('</Typography>', f'</Typography.{variant}>', 1)
    
    return lines


def fix_tablecontainer_tags(lines):
    """Fix TableContainer closing tags."""
    stack = []
    for i, line in enumerate(lines):
        if '<TableContainer' in line and '</TableContainer>' not in line:
            is_self_closing = '/>' in line.split('<TableContainer')[1].split('>')[0]
            if not is_self_closing:
                stack.append(i)
        if '</TableContainer>' in line and stack:
            stack.pop()  # These should already be correct
    
    # The real issue: opening was changed to <div> but closing is still </TableContainer>
    for i, line in enumerate(lines):
        if '</TableContainer>' in line:
            lines[i] = line.replace('</TableContainer>', '</div>')
    return lines


def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if '@mui' in content:
        return False
    
    original = content
    lines = content.split('\n')
    
    lines = fix_grid_tags(lines)
    lines = fix_typography_tags(lines)
    lines = fix_tablecontainer_tags(lines)
    
    content = '\n'.join(lines)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False


def main():
    base = "src"
    count = 0
    for root, dirs, files in os.walk(base):
        for fname in sorted(files):
            if fname.endswith('.tsx') or fname.endswith('.ts'):
                fpath = os.path.join(root, fname)
                if fix_file(fpath):
                    count += 1
                    print(f"  Fixed: {fpath}")
    print(f"\nFixed {count} files")


if __name__ == "__main__":
    main()
