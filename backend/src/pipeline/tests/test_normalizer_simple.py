"""Simple test script for normalizer (no dependencies)."""

import sys
import os

# Add pipeline directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import directly to avoid __init__ importing parser
from normalizer import normalize_extracted_data


def run_tests():
    """Run all normalizer tests."""
    print("Running normalizer tests...\n")
    passed = 0
    failed = 0
    
    # Test 1: Empty data
    try:
        result = normalize_extracted_data({})
        assert result["name"] is None
        assert result["skills"] == []
        assert result["degree"] == []
        print("✓ test_empty_data passed")
        passed += 1
    except Exception as e:
        print(f"✗ test_empty_data failed: {e}")
        failed += 1
    
    # Test 2: String to list conversion
    try:
        data = {"degree": "Bachelor", "college_name": "MIT"}
        result = normalize_extracted_data(data)
        assert result["degree"] == ["Bachelor"]
        assert result["college_name"] == ["MIT"]
        print("✓ test_string_to_list passed")
        passed += 1
    except Exception as e:
        print(f"✗ test_string_to_list failed: {e}")
        failed += 1
    
    # Test 3: Skills deduplication
    try:
        data = {"skills": ["Python", "python", "JavaScript"]}
        result = normalize_extracted_data(data)
        assert len(result["skills"]) == 2
        assert "Python" in result["skills"]
        assert "JavaScript" in result["skills"]
        print("✓ test_skills_deduplication passed")
        passed += 1
    except Exception as e:
        print(f"✗ test_skills_deduplication failed: {e}")
        failed += 1
    
    # Test 4: Type conversions
    try:
        data = {"total_experience": "5.5", "no_of_pages": "2"}
        result = normalize_extracted_data(data)
        assert isinstance(result["total_experience"], float)
        assert isinstance(result["no_of_pages"], int)
        assert result["total_experience"] == 5.5
        assert result["no_of_pages"] == 2
        print("✓ test_type_conversions passed")
        passed += 1
    except Exception as e:
        print(f"✗ test_type_conversions failed: {e}")
        failed += 1
    
    # Test 5: All keys present
    try:
        data = {"name": "Test"}
        result = normalize_extracted_data(data)
        required_keys = ['name', 'email', 'mobile_number', 'skills', 'total_experience',
                        'degree', 'college_name', 'designation', 'company_names', 'no_of_pages']
        assert all(key in result for key in required_keys)
        print("✓ test_all_keys_present passed")
        passed += 1
    except Exception as e:
        print(f"✗ test_all_keys_present failed: {e}")
        failed += 1
    
    print(f"\n{'='*50}")
    print(f"Tests passed: {passed}")
    print(f"Tests failed: {failed}")
    if failed == 0:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())

