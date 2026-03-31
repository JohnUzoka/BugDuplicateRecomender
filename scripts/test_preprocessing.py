# test_preprocessing.py
"""
Test script for text preprocessing
Run this to verify your preprocessing works correctly
"""

from text_preprocessor import TextPreprocessor
from dummy_data import get_dummy_bug_reports
import json

def test_basic_preprocessing():
    """Test basic preprocessing functionality"""
    print("=" * 60)
    print("TEST 1: Basic Preprocessing")
    print("=" * 60)
    
    preprocessor = TextPreprocessor()
    
    test_cases = [
        {
            'name': 'Code blocks removal',
            'input': 'Bug occurs when running this code: ```python\nprint("hello")\n``` Please fix',
            'expected_patterns': ['bug', 'occurs', 'running', 'code', 'please', 'fix']
        },
        {
            'name': 'URL removal',
            'input': 'Check this link: https://github.com/godotengine/godot/issues/1234 for reference',
            'expected_patterns': ['check', 'link', 'reference']
        },
        {
            'name': 'Special characters',
            'input': 'Game crashes!!! with error: "out of memory" #critical',
            'expected_patterns': ['game', 'crash', 'error', 'memory', 'critical']
        },
        {
            'name': 'Stopwords removal',
            'input': 'This is a very important bug that needs to be fixed immediately',
            'expected_patterns': ['important', 'bug', 'need', 'fix', 'immediately']
        }
    ]
    
    for test in test_cases:
        print(f"\nTest: {test['name']}")
        print(f"Input: {test['input']}")
        result = preprocessor.preprocess(test['input'])
        print(f"Output: {result}")
        
        # Verify expected words are present
        for expected in test['expected_patterns']:
            if expected in result:
                print(f"  ✓ '{expected}' found")
            else:
                print(f"  ✗ '{expected}' not found")

def test_bug_report_processing():
    """Test preprocessing on actual bug reports"""
    print("\n" + "=" * 60)
    print("TEST 2: Bug Report Processing")
    print("=" * 60)
    
    preprocessor = TextPreprocessor()
    bug_reports = get_dummy_bug_reports()
    
    # Test first few bug reports
    for report in bug_reports[:3]:
        print(f"\nBug #{report['id']}: {report['title']}")
        print("-" * 40)
        
        # Preprocess title and body separately
        title_processed = preprocessor.preprocess(report['title'])
        body_processed = preprocessor.preprocess(report['body'])
        
        print(f"Original title: {report['title']}")
        print(f"Processed title: {title_processed}")
        print(f"Original body: {report['body'][:80]}...")
        print(f"Processed body: {body_processed[:80]}...")
        
        # Test weighted combination
        combined = preprocessor.combine_text_with_weighting(report['title'], report['body'])
        print(f"Combined (weighted): {combined[:100]}...")

def test_duplicate_similarity():
    """Test that duplicate bugs are similar"""
    print("\n" + "=" * 60)
    print("TEST 3: Duplicate Detection Similarity")
    print("=" * 60)
    
    preprocessor = TextPreprocessor()
    
    # Known duplicate pair: 1002 is duplicate of 1001
    bug_1001 = {
        'title': 'Game crashes when loading large textures',
        'body': 'When trying to load a texture larger than 4096x4096 pixels, the game crashes with "out of memory" error.'
    }
    
    bug_1002 = {
        'title': 'Memory error on big texture import',
        'body': 'Importing textures larger than 4K causes memory allocation failure.'
    }
    
    bug_1003 = {
        'title': 'Button alignment broken in UI editor',
        'body': 'Buttons are misaligned when using HBoxContainer.'
    }
    
    # Get vectors
    text_1001 = preprocessor.combine_text_with_weighting(bug_1001['title'], bug_1001['body'])
    text_1002 = preprocessor.combine_text_with_weighting(bug_1002['title'], bug_1002['body'])
    text_1003 = preprocessor.combine_text_with_weighting(bug_1003['title'], bug_1003['body'])
    
    # Since we don't have vectorizer here, show the processed texts
    print("\nProcessed duplicate bugs:")
    print(f"Bug #1001: {text_1001[:100]}...")
    print(f"Bug #1002: {text_1002[:100]}...")
    print("\nProcessed unrelated bug:")
    print(f"Bug #1003: {text_1003[:100]}...")
    
    print("\nNotice how #1001 and #1002 share common terms like:")
    print("  - 'crash' / 'memory' / 'load' / 'texture'")
    print("While #1003 uses different terms like 'button' / 'align' / 'ui'")

def test_preprocessing_stats():
    """Show statistics about preprocessing"""
    print("\n" + "=" * 60)
    print("TEST 4: Preprocessing Statistics")
    print("=" * 60)
    
    preprocessor = TextPreprocessor()
    bug_reports = get_dummy_bug_reports()
    
    stats = {
        'original_lengths': [],
        'processed_lengths': [],
        'compression_ratios': []
    }
    
    for report in bug_reports:
        original = f"{report['title']} {report['body']}"
        processed = preprocessor.combine_text_with_weighting(report['title'], report['body'])
        
        orig_len = len(original)
        proc_len = len(processed)
        
        stats['original_lengths'].append(orig_len)
        stats['processed_lengths'].append(proc_len)
        stats['compression_ratios'].append(proc_len / orig_len if orig_len > 0 else 0)
    
    print(f"\nProcessed {len(bug_reports)} bug reports:")
    print(f"Average original length: {sum(stats['original_lengths']) / len(stats['original_lengths']):.0f} chars")
    print(f"Average processed length: {sum(stats['processed_lengths']) / len(stats['processed_lengths']):.0f} chars")
    print(f"Average compression ratio: {sum(stats['compression_ratios']) / len(stats['compression_ratios']):.2f}")
    print("\nThis shows how much text is reduced through preprocessing!")

if __name__ == "__main__":
    # Run all tests
    test_basic_preprocessing()
    test_bug_report_processing()
    test_duplicate_similarity()
    test_preprocessing_stats()
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)