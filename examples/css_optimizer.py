#!/usr/bin/env python3
"""
CSS Optimizer

A practical example showing how tree rewriting can optimize CSS.
"""

import sys
sys.path.insert(0, '../src')

from tree_rewriter import rewrite, when, bottom_up
import re

print("CSS Optimizer")
print("=" * 50)

# Helper functions
def shorten_hex(color):
    """#RRGGBB -> #RGB if possible"""
    if match := re.match(r'^#([0-9a-f])\1([0-9a-f])\2([0-9a-f])\3$', color, re.I):
        return f"#{match.group(1)}{match.group(2)}{match.group(3)}"
    return color

def remove_zero_unit(value):
    """0px -> 0"""
    if re.match(r'^0(px|em|rem|%)$', value):
        return '0'
    return value

# Common color names to hex
color_names = {
    'white': '#fff',
    'black': '#000',
    'red': '#f00',
    'blue': '#00f',
}

# CSS optimization rules
css_rules = [
    # Optimize hex colors
    when('color', lambda v: isinstance(v, str) and v.startswith('#')).then(
        lambda value: ('color', shorten_hex(value))
    ),
    
    # Convert color names
    when('color', lambda v: v in color_names).then(
        lambda value: ('color', color_names[value])
    ),
    
    # Remove units from zero
    when('size', lambda v: isinstance(v, str)).then(
        lambda value: ('size', remove_zero_unit(value))
    ),
]

# Example CSS structures
print("\nOptimizing CSS properties:\n")

test_cases = [
    ('color', '#ffffff'),
    ('color', '#ff0000'),
    ('color', 'white'),
    ('color', 'black'),
    ('size', '0px'),
    ('size', '0em'),
    ('size', '10px'),
]

for prop_type, value in test_cases:
    expr = (prop_type, value)
    result = rewrite(expr, *css_rules)
    _ignored, new_value = result
    print(f"{prop_type}: {value:10} => {new_value}")

# More complex CSS structure
print("\n" + "=" * 50)
print("Complete CSS rule optimization:\n")

css_rule = ('rule', '.button',
    ('props',
        ('prop', 'color', ('color', '#ffffff')),
        ('prop', 'background', ('color', 'red')),
        ('prop', 'margin', ('size', '0px')),
        ('prop', 'padding', ('size', '10px')),
    )
)

def print_css(rule):
    """Pretty print CSS rule"""
    if rule[0] == 'rule':
        selector = rule[1]
        props = rule[2]
        print(f"{selector} {{")
        for prop in props[1:]:
            if prop[0] == 'prop':
                name = prop[1]
                value = prop[2][1] if isinstance(prop[2], tuple) else prop[2]
                print(f"  {name}: {value};")
        print("}")

print("Original:")
print_css(css_rule)

optimized = rewrite(css_rule, *[bottom_up(r) for r in css_rules])

print("\nOptimized:")
print_css(optimized)

# Size comparison
def css_size(rule):
    """Calculate CSS string size"""
    size = 0
    if rule[0] == 'rule':
        size += len(rule[1]) + 2  # selector + { }
        for prop in rule[2][1:]:
            if prop[0] == 'prop':
                size += len(prop[1]) + 2  # name + : ;
                value = prop[2][1] if isinstance(prop[2], tuple) else prop[2]
                size += len(str(value))
    return size

original_size = css_size(css_rule)
optimized_size = css_size(optimized)

print(f"\nSize reduction: {original_size} -> {optimized_size} bytes")
print(f"Saved: {original_size - optimized_size} bytes ({round((1 - optimized_size/original_size) * 100)}%)")

print("\n" + "=" * 50)
print("Benefits:")
print("- Automatic optimization")
print("- Easy to add new rules")
print("- Could be part of a build pipeline")
print("- Handles nested structures with bottom_up()")
