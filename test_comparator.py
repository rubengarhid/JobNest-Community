"""
Unit Tests for CV-LinkedIn Comparator
Tests parsing, comparison, and scoring functionality.
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.cv_parser import CVParser, parse_linkedin_text
from backend.comparator import CVLinkedInComparator


class TestCVParser(unittest.TestCase):
    """Test cases for CV Parser."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = CVParser()
    
    def test_split_into_sections_basic(self):
        """Test basic section splitting."""
        text = """
        EXPERIENCE
        Senior Developer at Tech Corp
        
        SKILLS
        Python, JavaScript
        
        EDUCATION
        BS Computer Science
        """
        
        sections = self.parser._split_into_sections(text)
        
        self.assertIn('experience', sections)
        self.assertIn('skills', sections)
        self.assertIn('education', sections)
        self.assertIn('Senior Developer', sections['experience'])
        self.assertIn('Python', sections['skills'])
        self.assertIn('Computer Science', sections['education'])
    
    def test_extract_skills(self):
        """Test skills extraction."""
        text = "I have experience with Python, JavaScript, React, and AWS."
        
        skills = self.parser.extract_skills(text)
        
        self.assertIsInstance(skills, list)
        # Check that at least some skills are extracted
        # Note: Skills are title-cased
        self.assertTrue(any('Python' in skill for skill in skills))
    
    def test_extract_skills_empty(self):
        """Test skills extraction with no skills."""
        text = "This is just regular text with no technical skills."
        
        skills = self.parser.extract_skills(text)
        
        self.assertIsInstance(skills, list)
        # May be empty or have few items
        self.assertLessEqual(len(skills), 2)
    
    def test_experience_section_patterns(self):
        """Test various experience section headers."""
        test_cases = [
            "WORK EXPERIENCE\nSenior Dev",
            "Professional Experience\nSenior Dev",
            "Employment History\nSenior Dev",
            "EXPERIENCIA LABORAL\nSenior Dev",  # Spanish
        ]
        
        for text in test_cases:
            sections = self.parser._split_into_sections(text)
            self.assertIn('Senior Dev', sections['experience'],
                         f"Failed to parse: {text[:20]}")
    
    def test_skills_section_patterns(self):
        """Test various skills section headers."""
        test_cases = [
            "SKILLS\nPython",
            "Technical Skills\nPython",
            "Competencies\nPython",
            "HABILIDADES\nPython",  # Spanish
        ]
        
        for text in test_cases:
            sections = self.parser._split_into_sections(text)
            self.assertIn('Python', sections['skills'],
                         f"Failed to parse: {text[:20]}")


class TestComparator(unittest.TestCase):
    """Test cases for Comparator."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock the sentence transformer model to avoid loading it
        with patch('backend.comparator.SentenceTransformer') as mock_model:
            # Create a mock model that returns dummy embeddings
            mock_instance = MagicMock()
            mock_instance.encode.return_value = [[0.1] * 384, [0.1] * 384]
            mock_model.return_value = mock_instance
            
            self.comparator = CVLinkedInComparator()
    
    def test_compute_similarity_empty(self):
        """Test similarity computation with empty strings."""
        similarity = self.comparator.compute_similarity("", "test")
        self.assertEqual(similarity, 0.0)
        
        similarity = self.comparator.compute_similarity("test", "")
        self.assertEqual(similarity, 0.0)
    
    def test_compute_similarity_valid(self):
        """Test similarity computation with valid texts."""
        # Mock the encode method to return similar vectors
        self.comparator.model.encode.return_value = [
            [1.0] * 384,  # First text embedding
            [0.9] * 384   # Second text embedding (similar)
        ]
        
        similarity = self.comparator.compute_similarity(
            "Python developer with 5 years experience",
            "Senior Python engineer with extensive experience"
        )
        
        # Should return a similarity score between 0 and 1
        self.assertGreaterEqual(similarity, 0.0)
        self.assertLessEqual(similarity, 1.0)
    
    def test_calculate_score_structure(self):
        """Test that calculate_score returns correct structure."""
        cv_data = {
            'experience': 'Senior Developer at Tech Corp',
            'skills': 'Python, JavaScript',
            'education': 'BS Computer Science',
            'extracted_skills': ['Python', 'JavaScript']
        }
        
        linkedin_data = {
            'experience': 'Senior Software Engineer at Tech Corp',
            'skills': 'Python, JavaScript, React',
            'education': 'Bachelor of Science in CS',
            'extracted_skills': ['Python', 'JavaScript', 'React']
        }
        
        result = self.comparator.calculate_score(cv_data, linkedin_data)
        
        # Check structure
        self.assertIn('overall_score', result)
        self.assertIn('section_scores', result)
        self.assertIn('skills_comparison', result)
        self.assertIn('discrepancies', result)
        self.assertIn('weights', result)
        
        # Check types
        self.assertIsInstance(result['overall_score'], float)
        self.assertIsInstance(result['section_scores'], dict)
        self.assertIsInstance(result['skills_comparison'], dict)
        self.assertIsInstance(result['discrepancies'], list)
    
    def test_skills_comparison(self):
        """Test skills comparison logic."""
        cv_data = {
            'experience': 'Dev',
            'skills': 'Skills',
            'education': 'Edu',
            'extracted_skills': ['Python', 'JavaScript', 'React']
        }
        
        linkedin_data = {
            'experience': 'Dev',
            'skills': 'Skills',
            'education': 'Edu',
            'extracted_skills': ['Python', 'JavaScript', 'Docker']
        }
        
        result = self.comparator.calculate_score(cv_data, linkedin_data)
        skills = result['skills_comparison']
        
        # Check common skills
        self.assertIn('Python', skills['common'])
        self.assertIn('JavaScript', skills['common'])
        
        # Check CV-only skills
        self.assertIn('React', skills['cv_only'])
        
        # Check LinkedIn-only skills
        self.assertIn('Docker', skills['linkedin_only'])
    
    def test_get_recommendations(self):
        """Test recommendations generation."""
        comparison_result = {
            'overall_score': 85.0,
            'section_scores': {
                'experience': 90.0,
                'skills': 80.0,
                'education': 85.0
            },
            'skills_comparison': {
                'common': ['Python', 'JavaScript'],
                'cv_only': ['React'],
                'linkedin_only': ['Docker'],
                'match_rate': 66.7
            }
        }
        
        recommendations = self.comparator.get_recommendations(comparison_result)
        
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
        
        # Should include positive feedback for high score
        self.assertTrue(any('Excellent' in rec or '✅' in rec for rec in recommendations))


class TestLinkedInParser(unittest.TestCase):
    """Test cases for LinkedIn text parsing."""
    
    def test_parse_linkedin_basic(self):
        """Test basic LinkedIn profile parsing."""
        linkedin_text = """
        EXPERIENCE
        Senior Developer at Tech Corp (2020-2023)
        Led team of 5 developers
        
        SKILLS
        Python, JavaScript, React, AWS
        
        EDUCATION
        BS Computer Science, University XYZ (2016-2020)
        """
        
        result = parse_linkedin_text(linkedin_text)
        
        self.assertIn('experience', result)
        self.assertIn('skills', result)
        self.assertIn('education', result)
        self.assertIn('extracted_skills', result)
        
        # Check content
        self.assertIn('Senior Developer', result['experience'])
        self.assertIsInstance(result['extracted_skills'], list)


class TestIntegration(unittest.TestCase):
    """Integration tests."""
    
    def test_end_to_end_comparison(self):
        """Test complete comparison flow (without model loading)."""
        # This test would require the actual model, so we skip it in CI
        # It's meant for manual testing
        pass


def run_tests():
    """Run all tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCVParser))
    suite.addTests(loader.loadTestsFromTestCase(TestComparator))
    suite.addTests(loader.loadTestsFromTestCase(TestLinkedInParser))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
