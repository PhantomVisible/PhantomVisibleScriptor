#!/usr/bin/env python3

import re

def test_word_counting():
    """Test different word counting methods"""
    
    test_text = """
    Here's a test script with some words. This should count correctly!
    What about multiple spaces?  And punctuation?
    Let's see how many words this has.
    """
    
    # Old method (inaccurate)
    old_count = len(test_text.split())
    
    # New method (accurate)
    new_count = len(re.findall(r'\b\w+\b', test_text))
    
    print(f"Test text: {repr(test_text)}")
    print(f"Old method (split): {old_count} words")
    print(f"New method (regex): {new_count} words")
    print(f"Difference: {new_count - old_count} words")

if __name__ == "__main__":
    test_word_counting()
