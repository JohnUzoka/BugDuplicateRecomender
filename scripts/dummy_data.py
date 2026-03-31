# dummy_data.py
"""
Dummy bug report data that simulates real Godot bug reports
"""

dummy_bug_reports = [
    {
        'id': 1001,
        'title': 'Game crashes when loading large textures',
        'body': 'When trying to load a texture larger than 4096x4096 pixels, the game crashes with "out of memory" error. This happens on Windows 10 and Linux.'
    },
    {
        'id': 1002,
        'title': 'Memory error on big texture import',
        'body': 'Importing textures larger than 4K causes memory allocation failure. The engine crashes immediately.'
    },
    {
        'id': 1003,
        'title': 'Button alignment broken in UI editor',
        'body': 'Buttons are misaligned when using HBoxContainer. The left button appears at the right edge.'
    },
    {
        'id': 1004,
        'title': 'Crash when loading large images',
        'body': 'Loading images bigger than 4096x4096 results in crash. Error: std::bad_alloc'
    },
    {
        'id': 1005,
        'title': 'UI button spacing issue',
        'body': 'Buttons in VBoxContainer have incorrect spacing. They overlap each other.'
    },
    {
        'id': 1006,
        'title': 'Editor freezes on texture import',
        'body': 'The editor becomes unresponsive when importing high-resolution textures (8K).'
    },
    {
        'id': 1007,
        'title': 'Text label cut off in forms',
        'body': 'Long text labels are being truncated in the form fields.'
    },
    {
        'id': 1008,
        'title': 'Out of memory during texture loading',
        'body': 'Game crashes due to memory exhaustion when loading large texture files.'
    },
    {
        'id': 1009,
        'title': 'UI elements not responding to resize',
        'body': 'Buttons and labels don\'t resize properly when window is resized.'
    },
    {
        'id': 1010,
        'title': 'Large texture memory leak',
        'body': 'Memory usage keeps increasing when loading multiple large textures.'
    }
]

# Known duplicate relationships (for testing)
# This simulates what human triagers have identified
known_duplicates = [
    {'duplicate_id': 1002, 'original_id': 1001},   # 1002 is duplicate of 1001
    {'duplicate_id': 1004, 'original_id': 1001},   # 1004 is duplicate of 1001
    {'duplicate_id': 1008, 'original_id': 1001},   # 1008 is duplicate of 1001
    {'duplicate_id': 1006, 'original_id': 1001},   # 1006 is duplicate of 1001
    {'duplicate_id': 1010, 'original_id': 1001},   # 1010 is duplicate of 1001
    {'duplicate_id': 1005, 'original_id': 1003},   # 1005 is duplicate of 1003
    {'duplicate_id': 1009, 'original_id': 1003},   # 1009 is duplicate of 1003
]

# Test cases (new bug reports that should be identified as duplicates)
test_cases = [
    {
        'id': 2001,
        'title': 'Memory crash when loading 4K textures',
        'body': 'The game crashes with memory allocation error when loading textures larger than 4096x4096.'
    },
    {
        'id': 2002,
        'title': 'UI buttons overlapping in container',
        'body': 'Buttons in VBoxContainer overlap each other instead of having proper spacing.'
    },
    {
        'id': 2003,
        'title': 'Completely new issue about shader compilation',
        'body': 'Shader compilation fails when using multiple lights in the scene.'
    },
    {
        'id': 2004,
        'title': 'Widget alignment broken in node editor',
        'body': 'when using the horisonal contianer widgets are not snapping to the grid'
    },
    {
        'id': 2005,
        'title': 'crahses when opening pngs that are 4K',
        'body': 'Loading 4k files causes the game to crash, i believe its a ram issue.'
    }
]

def get_dummy_bug_reports():
    """Return dummy bug reports for testing"""
    return dummy_bug_reports

def get_known_duplicates():
    """Return known duplicate relationships"""
    return known_duplicates

def get_test_cases():
    """Return test cases for evaluation"""
    return test_cases