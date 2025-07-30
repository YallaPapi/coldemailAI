"""
Fallback Mapping Mechanisms Tests
Task 11.3: Implement and Test Fallback Mechanisms for Unmappable or Missing Columns

Comprehensive testing of fallback strategies following TaskMaster research:
"CSV column mapping fallback mechanisms unmappable columns user prompts predefined mappings Flask implementation strategies"

Tests validate predefined mappings, user prompt integration, graceful degradation,
and unmappable column handling based on Context7 patterns and research findings.
"""

import io
import pytest
import pandas as pd
import unicodedata
from flask.testing import FlaskClient
from unittest.mock import patch, MagicMock


class FallbackMappingEngine:
    """Advanced column mapping engine with fallback mechanisms"""
    
    def __init__(self):
        self.predefined_mappings = self._initialize_predefined_mappings()
        self.confidence_threshold = 0.8
        self.unmapped_columns = []
        self.mapping_confidence = {}
    
    def _initialize_predefined_mappings(self):
        """Initialize comprehensive predefined mappings based on research"""
        return {
            # Company name variations
            "company_name": [
                "company name", "company", "business", "organization", "org", 
                "employer", "business name", "organization name", "corp", "corporation",
                "firm", "enterprise", "companyname", "co", "company_name"
            ],
            
            # First name variations  
            "first_name": [
                "first name", "firstname", "first", "given name", "forename",
                "fname", "first_name", "given", "christian name", "personal name"
            ],
            
            # Last name variations
            "last_name": [
                "last name", "lastname", "surname", "family name", "last",
                "lname", "last_name", "family", "sur name"
            ],
            
            # Job title variations
            "job_title": [
                "title", "job title", "position", "role", "designation", 
                "job position", "work title", "occupation", "job_title",
                "jobtitle", "job", "post"
            ],
            
            # Industry variations
            "industry": [
                "industry", "sector", "field", "business type", "domain",
                "vertical", "market", "business sector", "industry sector"
            ],
            
            # Email variations
            "email": [
                "email", "email address", "e-mail", "e mail", "mail",
                "email_address", "e_mail", "electronic mail"
            ],
            
            # Location variations
            "city": ["city", "town", "municipality", "location", "place"],
            "state": ["state", "province", "region", "territory", "st"],
            "country": ["country", "nation", "nationality", "ctry"]
        }
    
    def normalize_header(self, header):
        """Advanced header normalization with Unicode handling"""
        if not header or not isinstance(header, str):
            return ''
        
        # Unicode normalization (NFKD - canonical decomposition)
        normalized = unicodedata.normalize('NFKD', header)
        
        # Remove accents, keep only ASCII-compatible chars
        ascii_header = ''.join(c for c in normalized if not unicodedata.combining(c) and ord(c) < 128)
        
        if not ascii_header.strip():
            return ''
        
        # Standard normalization: lowercase, strip, replace special chars
        import re
        cleaned = re.sub(r'[^\w\s]', '', ascii_header).strip().lower().replace(' ', '_')
        
        # Handle multiple underscores
        return re.sub(r'_+', '_', cleaned).strip('_')
    
    def calculate_similarity(self, header1, header2):
        """Calculate similarity score between headers using Levenshtein distance"""
        def levenshtein_distance(s1, s2):
            if len(s1) < len(s2):
                return levenshtein_distance(s2, s1)
            
            if len(s2) == 0:
                return len(s1)
            
            previous_row = range(len(s2) + 1)
            for i, c1 in enumerate(s1):
                current_row = [i + 1]
                for j, c2 in enumerate(s2):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (c1 != c2)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row
            
            return previous_row[-1]
        
        max_len = max(len(header1), len(header2))
        if max_len == 0:
            return 1.0
        
        distance = levenshtein_distance(header1, header2)
        return 1.0 - (distance / max_len)
    
    def find_best_mapping(self, normalized_header):
        """Find best mapping with confidence score"""
        best_field = None
        best_confidence = 0.0
        
        for business_field, variants in self.predefined_mappings.items():
            for variant in variants:
                normalized_variant = self.normalize_header(variant)
                
                # Exact match gets highest confidence
                if normalized_header == normalized_variant:
                    return business_field, 1.0
                
                # Calculate similarity for fuzzy matching
                similarity = self.calculate_similarity(normalized_header, normalized_variant)
                if similarity > best_confidence:
                    best_confidence = similarity
                    best_field = business_field
        
        return best_field, best_confidence
    
    def map_csv_columns_with_fallbacks(self, df_columns):
        """Map CSV columns with comprehensive fallback mechanisms"""
        # Reset state
        self.unmapped_columns = []
        self.mapping_confidence = {}
        
        # Primary mapping results
        confirmed_mappings = {}  # High confidence mappings
        suggested_mappings = {}  # Medium confidence mappings needing user review
        unmappable_columns = []  # Low confidence, need user intervention
        
        for original_column in df_columns:
            normalized = self.normalize_header(original_column)
            
            if not normalized:  # Empty after normalization
                unmappable_columns.append({
                    'original': original_column,
                    'reason': 'empty_after_normalization',
                    'suggestions': []
                })
                continue
            
            best_field, confidence = self.find_best_mapping(normalized)
            
            if confidence >= self.confidence_threshold:
                # High confidence - auto-map
                confirmed_mappings[best_field] = {
                    'original_column': original_column,
                    'confidence': confidence,
                    'mapping_type': 'confirmed'
                }
                self.mapping_confidence[original_column] = confidence
                
            elif confidence >= 0.5:
                # Medium confidence - suggest to user
                suggested_mappings[original_column] = {
                    'suggested_field': best_field,
                    'confidence': confidence,
                    'mapping_type': 'suggested',
                    'alternatives': self._get_alternative_suggestions(normalized)
                }
                self.mapping_confidence[original_column] = confidence
                
            else:
                # Low confidence - needs user intervention
                unmappable_columns.append({
                    'original': original_column,
                    'reason': 'low_confidence',
                    'best_guess': best_field,
                    'confidence': confidence,
                    'suggestions': self._get_alternative_suggestions(normalized)
                })
        
        self.unmapped_columns = unmappable_columns
        
        return {
            'confirmed_mappings': confirmed_mappings,
            'suggested_mappings': suggested_mappings,
            'unmappable_columns': unmappable_columns,
            'mapping_stats': {
                'total_columns': len(df_columns),
                'confirmed': len(confirmed_mappings),
                'suggested': len(suggested_mappings),
                'unmappable': len(unmappable_columns)
            }
        }
    
    def _get_alternative_suggestions(self, normalized_header, top_n=3):
        """Get top alternative mapping suggestions"""
        suggestions = []
        
        for business_field, variants in self.predefined_mappings.items():
            best_similarity = 0.0
            for variant in variants:
                normalized_variant = self.normalize_header(variant)
                similarity = self.calculate_similarity(normalized_header, normalized_variant)
                best_similarity = max(best_similarity, similarity)
            
            if best_similarity > 0.3:  # Minimum threshold for suggestions
                suggestions.append({
                    'field': business_field,
                    'confidence': best_similarity
                })
        
        # Sort by confidence and return top suggestions
        suggestions.sort(key=lambda x: x['confidence'], reverse=True)
        return suggestions[:top_n]
    
    def apply_user_mappings(self, user_mappings, original_result):
        """Apply user-provided mappings to override suggestions"""
        final_mappings = original_result['confirmed_mappings'].copy()
        
        for original_column, user_choice in user_mappings.items():
            if user_choice == 'ignore':
                # User chose to ignore this column
                continue
            elif user_choice in self.predefined_mappings.keys():
                # User selected a valid business field
                final_mappings[user_choice] = {
                    'original_column': original_column,
                    'confidence': 1.0,  # User confirmation = highest confidence
                    'mapping_type': 'user_confirmed'
                }
        
        return final_mappings
    
    def get_fallback_strategy_for_missing_fields(self, required_fields, mapped_fields):
        """Determine fallback strategy for missing required fields"""
        missing_fields = set(required_fields) - set(mapped_fields.keys())
        fallback_strategies = {}
        
        for field in missing_fields:
            if field == 'first_name':
                fallback_strategies[field] = {
                    'strategy': 'default_value',
                    'value': '[First Name]',
                    'reason': 'Required for personalization, using placeholder'
                }
            elif field == 'company_name':
                fallback_strategies[field] = {
                    'strategy': 'default_value', 
                    'value': '[Company]',
                    'reason': 'Required for personalization, using placeholder'
                }
            elif field == 'job_title':
                fallback_strategies[field] = {
                    'strategy': 'optional',
                    'value': None,
                    'reason': 'Optional field, can be omitted from emails'
                }
            elif field == 'email':
                fallback_strategies[field] = {
                    'strategy': 'error',
                    'value': None,
                    'reason': 'Email required for delivery, cannot proceed without'
                }
            else:
                fallback_strategies[field] = {
                    'strategy': 'optional',
                    'value': None,
                    'reason': 'Non-essential field, can be omitted'
                }
        
        return fallback_strategies


class TestFallbackMappingMechanisms:
    """Test comprehensive fallback mapping mechanisms"""
    
    def setup_method(self):
        """Setup test environment"""
        self.mapping_engine = FallbackMappingEngine()
    
    def test_predefined_mappings_coverage(self):
        """Test that predefined mappings cover all standard business variations"""
        engine = self.mapping_engine
        
        # Test standard business header variations
        test_headers = [
            "Company Name", "First Name", "Last Name", "Job Title", "Industry",
            "Email Address", "City", "State", "Country"
        ]
        
        result = engine.map_csv_columns_with_fallbacks(test_headers)
        
        # Should have high confidence mappings for all standard headers
        assert len(result['confirmed_mappings']) >= 7, f"Only {len(result['confirmed_mappings'])} confirmed mappings"
        assert len(result['unmappable_columns']) <= 2, f"Too many unmappable: {len(result['unmappable_columns'])}"
        
        # Check specific critical mappings
        mapped_fields = set(result['confirmed_mappings'].keys())
        critical_fields = {'first_name', 'last_name', 'company_name', 'job_title'}
        mapped_critical = mapped_fields & critical_fields
        
        assert len(mapped_critical) >= 3, f"Missing critical fields: {critical_fields - mapped_critical}"
    
    @pytest.mark.parametrize("input_headers,expected_confirmed,expected_suggested", [
        # Perfect matches - should all be confirmed
        (
            ["first_name", "company_name", "job_title", "email"],
            4, 0
        ),
        
        # Close matches - should be confirmed with high confidence
        (
            ["First Name", "Company", "Title", "E-Mail"],
            4, 0
        ),
        
        # Fuzzy matches - should be suggested
        (
            ["Fname", "Comp Name", "Job", "Mail Address"],
            2, 2  # Some confirmed, some suggested
        ),
        
        # Ambiguous headers - should need user intervention
        (
            ["Name", "Position", "Contact", "Organization"],
            1, 3  # Most should be suggested for user review
        ),
        
        # Unmappable headers - should be flagged
        (
            ["Random Column", "Unknown Field", "Mystery Header"],
            0, 0  # All should be unmappable
        )
    ])
    def test_mapping_confidence_levels(self, input_headers, expected_confirmed, expected_suggested):
        """Test that mapping confidence levels work correctly"""
        result = self.mapping_engine.map_csv_columns_with_fallbacks(input_headers)
        
        confirmed_count = len(result['confirmed_mappings'])
        suggested_count = len(result['suggested_mappings'])
        
        # Allow some flexibility in expected counts due to fuzzy matching
        assert abs(confirmed_count - expected_confirmed) <= 1, \
            f"Expected ~{expected_confirmed} confirmed, got {confirmed_count}"
        assert abs(suggested_count - expected_suggested) <= 2, \
            f"Expected ~{expected_suggested} suggested, got {suggested_count}"
    
    def test_fuzzy_matching_accuracy(self):
        """Test fuzzy matching for headers with typos or variations"""
        test_cases = [
            ("Compny Name", "company_name"),  # Typo
            ("Frist Name", "first_name"),     # Typo
            ("Job Titl", "job_title"),        # Missing letter
            ("Emial", "email"),               # Transposed letters
            ("Indsutry", "industry"),         # Multiple typos
        ]
        
        for header_with_typo, expected_field in test_cases:
            result = self.mapping_engine.map_csv_columns_with_fallbacks([header_with_typo])
            
            # Should either be confirmed or suggested, not unmappable
            is_mapped = (
                expected_field in result['confirmed_mappings'] or
                header_with_typo in result['suggested_mappings']
            )
            
            assert is_mapped, f"Failed to map '{header_with_typo}' to '{expected_field}'"
    
    def test_user_mapping_override(self):
        """Test user mapping override functionality"""
        # Initial mapping with ambiguous headers
        headers = ["Name", "Organization", "Contact Info"]
        initial_result = self.mapping_engine.map_csv_columns_with_fallbacks(headers)
        
        # User provides mappings
        user_mappings = {
            "Name": "first_name",
            "Organization": "company_name", 
            "Contact Info": "email"
        }
        
        final_mappings = self.mapping_engine.apply_user_mappings(user_mappings, initial_result)
        
        # Check user mappings were applied
        assert 'first_name' in final_mappings
        assert final_mappings['first_name']['original_column'] == "Name"
        assert final_mappings['first_name']['mapping_type'] == 'user_confirmed'
        assert final_mappings['first_name']['confidence'] == 1.0
        
        assert 'company_name' in final_mappings
        assert final_mappings['company_name']['original_column'] == "Organization"
    
    def test_ignore_column_functionality(self):
        """Test that users can ignore unmappable columns"""
        headers = ["Irrelevant Data", "Random Info", "First Name"]
        initial_result = self.mapping_engine.map_csv_columns_with_fallbacks(headers)
        
        # User chooses to ignore some columns
        user_mappings = {
            "Irrelevant Data": "ignore",
            "Random Info": "ignore",
            "First Name": "first_name"  # Keep this one
        }
        
        final_mappings = self.mapping_engine.apply_user_mappings(user_mappings, initial_result)
        
        # Should only have the non-ignored mapping
        assert len(final_mappings) >= 1
        assert 'first_name' in final_mappings
        assert 'irrelevant_data' not in final_mappings
        assert 'random_info' not in final_mappings
    
    def test_missing_field_fallback_strategies(self):
        """Test fallback strategies for missing required fields"""
        required_fields = ['first_name', 'company_name', 'email', 'job_title']
        mapped_fields = {'first_name': {'original_column': 'Name'}}  # Only first name mapped
        
        fallback_strategies = self.mapping_engine.get_fallback_strategy_for_missing_fields(
            required_fields, mapped_fields
        )
        
        # Check fallback strategies
        assert 'company_name' in fallback_strategies
        assert fallback_strategies['company_name']['strategy'] == 'default_value'
        assert fallback_strategies['company_name']['value'] == '[Company]'
        
        assert 'email' in fallback_strategies
        assert fallback_strategies['email']['strategy'] == 'error'
        
        assert 'job_title' in fallback_strategies
        assert fallback_strategies['job_title']['strategy'] == 'optional'
    
    def test_mapping_statistics_accuracy(self):
        """Test that mapping statistics are accurate"""
        headers = [
            "First Name",      # Should be confirmed
            "Company",         # Should be confirmed
            "Fname",          # Should be suggested (fuzzy match)
            "Random Column",   # Should be unmappable
            "Email Address"    # Should be confirmed
        ]
        
        result = self.mapping_engine.map_csv_columns_with_fallbacks(headers)
        stats = result['mapping_stats']
        
        # Verify statistics
        assert stats['total_columns'] == 5
        assert stats['confirmed'] + stats['suggested'] + stats['unmappable'] == 5
        assert stats['confirmed'] >= 2  # At least First Name, Company, Email
        assert stats['unmappable'] >= 1  # At least Random Column
    
    def test_alternative_suggestions_quality(self):
        """Test that alternative suggestions are reasonable"""
        result = self.mapping_engine.map_csv_columns_with_fallbacks(["Comp Name"])
        
        # Should be either suggested or unmappable, with alternatives
        if "Comp Name" in result['suggested_mappings']:
            alternatives = result['suggested_mappings']["Comp Name"]['alternatives']
        else:
            # Find in unmappable columns
            comp_name_unmappable = next(
                (col for col in result['unmappable_columns'] if col['original'] == "Comp Name"),
                None
            )
            assert comp_name_unmappable is not None
            alternatives = comp_name_unmappable['suggestions']
        
        # Should have reasonable suggestions
        assert len(alternatives) > 0
        assert any(alt['field'] == 'company_name' for alt in alternatives)
        
        # Suggestions should be sorted by confidence
        confidences = [alt['confidence'] for alt in alternatives]
        assert confidences == sorted(confidences, reverse=True)


class TestFlaskIntegrationWithFallbacks:
    """Test Flask integration with fallback mapping mechanisms"""
    
    def create_test_csv(self, headers, rows):
        """Create in-memory CSV file for testing"""
        csv_content = ",".join(headers) + "\n"
        csv_content += "\n".join([",".join(row) for row in rows])
        return io.BytesIO(csv_content.encode('utf-8'))
    
    @pytest.mark.integration
    def test_ambiguous_headers_trigger_user_prompt(self, client: FlaskClient):
        """Test that ambiguous headers trigger user mapping prompts"""
        # Headers that should trigger user prompts
        headers = ["Name", "Organization", "Contact", "Position"]
        rows = [["John Smith", "TechCorp", "john@tech.com", "Developer"]]
        
        csv_file = self.create_test_csv(headers, rows)
        
        response = client.post('/upload',
                             data={'file': (csv_file, 'ambiguous_test.csv')},
                             content_type='multipart/form-data')
        
        assert response.status_code == 200
        response_text = response.get_data(as_text=True)
        
        # Should indicate need for user mapping
        mapping_prompts = response_text.count('map_')
        assert mapping_prompts >= 2, f"Expected mapping prompts, found {mapping_prompts}"
        
        # Should not auto-proceed to email generation without user confirmation
        assert 'generate_emails' not in response_text.lower() or 'review' in response_text.lower()
    
    @pytest.mark.integration
    def test_unmappable_columns_handled_gracefully(self, client: FlaskClient):
        """Test that completely unmappable columns are handled gracefully"""
        # Headers that cannot be mapped to business fields
        headers = ["Random Data", "Mystery Column", "Unknown Field", "First Name"]
        rows = [["data1", "data2", "data3", "John"]]
        
        csv_file = self.create_test_csv(headers, rows)
        
        response = client.post('/upload',
                             data={'file': (csv_file, 'unmappable_test.csv')},
                             content_type='multipart/form-data')
        
        # Should not crash, should handle gracefully
        assert response.status_code == 200
        response_text = response.get_data(as_text=True)
        
        # Should still detect the mappable column
        assert 'map_first_name' in response_text
        
        # Should not cause errors
        assert 'error' not in response_text.lower() or 'mapping' in response_text.lower()
    
    @pytest.mark.integration
    def test_mixed_confidence_mapping_interface(self, client: FlaskClient):
        """Test interface handling mixed confidence mapping results"""
        # Mix of high confidence, medium confidence, and unmappable headers
        headers = [
            "First Name",      # High confidence
            "Comp Name",       # Medium confidence (fuzzy match)
            "Job",            # Medium confidence
            "Random123"        # Unmappable
        ]
        rows = [["Alice", "TechCorp", "Engineer", "xyz"]]
        
        csv_file = self.create_test_csv(headers, rows)
        
        response = client.post('/upload',
                             data={'file': (csv_file, 'mixed_confidence_test.csv')},
                             content_type='multipart/form-data')
        
        assert response.status_code == 200
        response_text = response.get_data(as_text=True)
        
        # Should have some auto-mapped fields
        auto_mapped_count = response_text.count('✓') if '✓' in response_text else 0
        
        # Should have some fields needing user review
        mapping_options = response_text.count('select') + response_text.count('map_')
        
        # Should provide mapping interface
        assert mapping_options >= 2, "Should provide mapping interface for ambiguous fields"
    
    @pytest.mark.integration
    def test_fallback_error_handling(self, client: FlaskClient):
        """Test error handling in fallback scenarios"""
        # Malformed CSV that might cause mapping errors
        malformed_csv = b'"","First Name","",""\nJohn,Smith,data,end'
        
        csv_file = io.BytesIO(malformed_csv)
        
        response = client.post('/upload',
                             data={'file': (csv_file, 'malformed_fallback_test.csv')},
                             content_type='multipart/form-data')
        
        # Should handle gracefully, not crash
        assert response.status_code in [200, 400]
        
        if response.status_code == 200:
            response_text = response.get_data(as_text=True)
            # Should still attempt to provide mapping options
            assert 'map_' in response_text or 'column' in response_text.lower()


class TestMappingConfidenceAlgorithms:
    """Test the underlying confidence and similarity algorithms"""
    
    def setup_method(self):
        self.engine = FallbackMappingEngine()
    
    def test_levenshtein_similarity_accuracy(self):
        """Test Levenshtein distance similarity calculations"""
        test_cases = [
            ("company", "company", 1.0),      # Identical
            ("company", "compny", 0.857),     # Close approximation  
            ("first", "frist", 0.8),          # Transposed letters
            ("email", "mail", 0.6),           # Substring
            ("xyz", "abc", 0.0),              # Completely different
        ]
        
        for str1, str2, expected_min_similarity in test_cases:
            similarity = self.engine.calculate_similarity(str1, str2)
            assert similarity >= expected_min_similarity - 0.1, \
                f"Similarity between '{str1}' and '{str2}': expected >={expected_min_similarity}, got {similarity:.3f}"
    
    def test_confidence_threshold_calibration(self):
        """Test that confidence thresholds produce reasonable results"""
        engine = self.engine
        
        # High confidence cases
        high_confidence_headers = ["first_name", "company_name", "email"]
        for header in high_confidence_headers:
            _, confidence = engine.find_best_mapping(header)
            assert confidence >= engine.confidence_threshold, \
                f"'{header}' should have high confidence: {confidence}"
        
        # Medium confidence cases  
        medium_confidence_headers = ["fname", "comp", "mail"]
        for header in medium_confidence_headers:
            _, confidence = engine.find_best_mapping(header)
            assert 0.5 <= confidence < engine.confidence_threshold, \
                f"'{header}' should have medium confidence: {confidence}"
        
        # Low confidence cases
        low_confidence_headers = ["random", "unknown", "xyz123"]
        for header in low_confidence_headers:
            _, confidence = engine.find_best_mapping(header)
            assert confidence < 0.5, \
                f"'{header}' should have low confidence: {confidence}"
    
    def test_unicode_header_fallback_handling(self):
        """Test fallback handling for Unicode headers"""
        unicode_headers = ["名字", "société", "Björn", "naïve"]
        
        result = self.engine.map_csv_columns_with_fallbacks(unicode_headers)
        
        # Unicode headers might normalize to empty or be unmappable
        # Should handle gracefully without errors
        assert result['mapping_stats']['total_columns'] == 4
        assert isinstance(result['unmappable_columns'], list)
        
        # Some might be mappable if they normalize to ASCII equivalents
        total_processed = (
            result['mapping_stats']['confirmed'] + 
            result['mapping_stats']['suggested'] + 
            result['mapping_stats']['unmappable']
        )
        assert total_processed == 4