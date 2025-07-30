"""
Large File Processing Tests for ColdEmailAI

Comprehensive testing of chunked processing capabilities following TaskMaster research:
"CSV chunked processing performance testing memory monitoring pandas chunksize benchmarking 2025 large file processing"

Tests validate memory management, processing speed, data integrity, and performance benchmarking.
Based on Context7 patterns and ZAD requirements for enterprise-scale CSV processing.
"""

import io
import time
import pytest
import psutil
import pandas as pd
from flask.testing import FlaskClient


class TestLargeFileProcessing:
    """Test large file processing with chunked processing validation"""
    
    @pytest.mark.performance
    @pytest.mark.real_data
    def test_enterprise_csv_processing_performance(self, client: FlaskClient, memory_monitor, performance_thresholds):
        """Test processing of 2000+ row CSV file with performance monitoring"""
        # Load the enterprise dataset
        enterprise_file_path = "test_data/enterprise_leads.csv"
        
        # Start comprehensive monitoring
        memory_monitor.start_monitoring()
        start_time = time.time()
        
        # Process the large file
        with open(enterprise_file_path, 'rb') as f:
            file_content = f.read()
            
        csv_file = io.BytesIO(file_content)
        
        response = client.post('/upload',
                             data={'file': (csv_file, 'enterprise_leads.csv')},
                             content_type='multipart/form-data')
        
        processing_time = time.time() - start_time
        
        # Verify successful processing
        assert response.status_code == 200
        
        # Performance assertions based on ZAD requirements
        assert processing_time < performance_thresholds['processing_timeout'], \
            f"Processing took {processing_time:.2f}s, max allowed: {performance_thresholds['processing_timeout']}s"
        
        # Memory usage assertions
        memory_monitor.assert_memory_increase_under(performance_thresholds['large_file_max_increase'])
        
        # Calculate processing speed (records per second)
        file_size_bytes = len(file_content)
        df = pd.read_csv(io.BytesIO(file_content))
        record_count = len(df)
        processing_speed = record_count / processing_time
        
        # Assert processing speed meets target (>1000 leads/second)
        assert processing_speed > 1000, f"Processing speed: {processing_speed:.0f} records/second, target: >1000"
        
        # Log detailed performance metrics
        stats = memory_monitor.get_stats()
        print(f"\nEnterprise CSV Processing Performance:")
        print(f"  - File size: {file_size_bytes:,} bytes ({file_size_bytes/1024/1024:.2f} MB)")
        print(f"  - Record count: {record_count:,} records")
        print(f"  - Processing time: {processing_time:.2f}s")
        print(f"  - Processing speed: {processing_speed:.0f} records/second")
        print(f"  - Memory baseline: {stats['baseline']:,} bytes")
        print(f"  - Memory peak: {stats['peak']:,} bytes")
        print(f"  - Memory increase: {stats['increase']:,} bytes ({stats['increase']/1024/1024:.2f} MB)")
        
    @pytest.mark.performance
    def test_chunked_processing_simulation(self, large_csv_content, memory_monitor):
        """Test chunked processing approach for memory efficiency"""
        # Simulate chunked processing as per research recommendations
        memory_monitor.start_monitoring()
        
        # Test different chunk sizes
        chunk_sizes = [500, 1000, 2000]
        results = {}
        
        for chunk_size in chunk_sizes:
            chunk_start = time.time()
            chunk_baseline = memory_monitor.process.memory_info().rss
            
            # Simulate chunked processing
            csv_io = io.BytesIO(large_csv_content)
            chunks_processed = 0
            total_records = 0
            memory_peak = chunk_baseline
            
            try:
                for chunk in pd.read_csv(csv_io, chunksize=chunk_size):
                    chunks_processed += 1
                    total_records += len(chunk)
                    
                    # Monitor memory during each chunk
                    current_memory = memory_monitor.process.memory_info().rss
                    memory_peak = max(memory_peak, current_memory)
                    
                    # Simulate processing work (lightweight)
                    _ = chunk.to_dict('records')
                    
            except Exception as e:
                pytest.fail(f"Chunked processing failed with chunk_size={chunk_size}: {e}")
                
            chunk_time = time.time() - chunk_start
            memory_increase = memory_peak - chunk_baseline
            
            results[chunk_size] = {
                'chunks_processed': chunks_processed,
                'total_records': total_records,
                'processing_time': chunk_time,
                'memory_increase': memory_increase,
                'records_per_second': total_records / chunk_time if chunk_time > 0 else 0
            }
            
        # Verify chunked processing efficiency
        for chunk_size, metrics in results.items():
            # Memory should remain bounded regardless of chunk size
            assert metrics['memory_increase'] < 100 * 1024 * 1024, \
                f"Chunk size {chunk_size}: Memory increase {metrics['memory_increase']/1024/1024:.2f}MB exceeds 100MB limit"
            
            # All records should be processed
            assert metrics['total_records'] > 2000, \
                f"Chunk size {chunk_size}: Only {metrics['total_records']} records processed, expected >2000"
            
            # Performance should be reasonable
            assert metrics['records_per_second'] > 500, \
                f"Chunk size {chunk_size}: {metrics['records_per_second']:.0f} records/second too slow"
                
        # Log chunked processing results
        print(f"\nChunked Processing Performance Analysis:")
        for chunk_size, metrics in results.items():
            print(f"  Chunk Size {chunk_size}:")
            print(f"    - Chunks processed: {metrics['chunks_processed']}")
            print(f"    - Total records: {metrics['total_records']:,}")
            print(f"    - Processing time: {metrics['processing_time']:.2f}s")
            print(f"    - Memory increase: {metrics['memory_increase']/1024/1024:.2f} MB")
            print(f"    - Records/second: {metrics['records_per_second']:.0f}")
            
    @pytest.mark.integration
    def test_data_integrity_across_chunks(self, large_csv_content):
        """Test that chunked processing maintains data integrity"""
        # Process entire file at once (baseline)
        csv_io_full = io.BytesIO(large_csv_content)
        df_full = pd.read_csv(csv_io_full)
        full_record_count = len(df_full)
        full_hash = hash(str(df_full.values.tolist()))
        
        # Process in chunks and reassemble
        csv_io_chunks = io.BytesIO(large_csv_content)
        chunks = []
        chunk_count = 0
        
        for chunk in pd.read_csv(csv_io_chunks, chunksize=1000):
            chunks.append(chunk)
            chunk_count += 1
            
        # Reassemble chunks
        df_reassembled = pd.concat(chunks, ignore_index=True)
        reassembled_record_count = len(df_reassembled)
        reassembled_hash = hash(str(df_reassembled.values.tolist()))
        
        # Verify data integrity
        assert chunk_count > 1, f"Expected multiple chunks, got {chunk_count}"
        assert reassembled_record_count == full_record_count, \
            f"Record count mismatch: full={full_record_count}, reassembled={reassembled_record_count}"
        assert reassembled_hash == full_hash, "Data integrity check failed: chunk reassembly doesn't match original"
        
        print(f"\nData Integrity Verification:")
        print(f"  - Chunks processed: {chunk_count}")  
        print(f"  - Original records: {full_record_count:,}")
        print(f"  - Reassembled records: {reassembled_record_count:,}")
        print(f"  - Data integrity: ✅ PASSED")
        
    @pytest.mark.performance
    def test_memory_scalability(self, memory_monitor):
        """Test that memory usage doesn't scale with file size"""
        # Test with progressively larger datasets
        test_sizes = [100, 500, 1000, 2000]  # Row counts
        memory_results = {}
        
        for size in test_sizes:
            memory_monitor.start_monitoring()
            
            # Generate dataset of specific size
            test_data = {
                'first_name': ['Test'] * size,
                'last_name': ['User'] * size,
                'company_name': [f'Company_{i}' for i in range(size)],
                'title': ['Manager'] * size
            }
            
            df = pd.DataFrame(test_data)
            csv_content = df.to_csv(index=False).encode('utf-8')
            
            # Process in chunks
            csv_io = io.BytesIO(csv_content)
            chunks_processed = 0
            
            for chunk in pd.read_csv(csv_io, chunksize=500):
                chunks_processed += 1
                # Simulate processing
                _ = chunk.to_dict('records')
                
            memory_increase = memory_monitor.get_memory_increase()
            memory_results[size] = {
                'memory_increase': memory_increase,
                'chunks_processed': chunks_processed
            }
            
        # Verify memory doesn't scale linearly with data size
        memory_increases = [result['memory_increase'] for result in memory_results.values()]
        
        # Memory increase should be bounded (not growing linearly with data size)
        max_memory_increase = max(memory_increases)
        min_memory_increase = min(memory_increases)
        memory_variation = max_memory_increase - min_memory_increase
        
        # Memory variation should be reasonable (not scaling with data size)
        assert memory_variation < 20 * 1024 * 1024, \
            f"Memory usage varies too much: {memory_variation/1024/1024:.2f}MB variation across different file sizes"
            
        print(f"\nMemory Scalability Analysis:")
        for size, result in memory_results.items():
            print(f"  {size:,} records: {result['memory_increase']/1024/1024:.2f} MB, {result['chunks_processed']} chunks")
        print(f"  Memory variation: {memory_variation/1024/1024:.2f} MB (should be <20MB)")
        
    @pytest.mark.performance  
    def test_chunk_size_optimization(self, large_csv_content, memory_monitor):
        """Test different chunk sizes to find optimal performance"""
        chunk_sizes = [100, 500, 1000, 2000, 5000]
        optimization_results = {}
        
        for chunk_size in chunk_sizes:
            memory_monitor.start_monitoring()
            start_time = time.time()
            
            csv_io = io.BytesIO(large_csv_content)
            total_records = 0
            chunks_processed = 0
            
            try:
                for chunk in pd.read_csv(csv_io, chunksize=chunk_size):
                    total_records += len(chunk)
                    chunks_processed += 1
                    # Simulate processing work
                    _ = chunk.to_dict('records')
            except Exception as e:
                pytest.fail(f"Processing failed with chunk_size={chunk_size}: {e}")
                
            processing_time = time.time() - start_time
            memory_increase = memory_monitor.get_memory_increase()
            
            optimization_results[chunk_size] = {
                'processing_time': processing_time,
                'memory_increase': memory_increase,
                'records_per_second': total_records / processing_time,
                'chunks_processed': chunks_processed,
                'total_records': total_records
            }
            
        # Find optimal chunk size (best balance of speed and memory)
        best_chunk_size = None
        best_score = 0
        
        for chunk_size, metrics in optimization_results.items():
            # Score based on speed (higher is better) and memory efficiency (lower is better)  
            speed_score = metrics['records_per_second'] / 1000  # Normalize to ~1
            memory_score = 50 / (metrics['memory_increase'] / 1024 / 1024)  # Inverse of MB used
            combined_score = speed_score * memory_score
            
            if combined_score > best_score:
                best_score = combined_score
                best_chunk_size = chunk_size
                
        print(f"\nChunk Size Optimization Results:")
        for chunk_size, metrics in optimization_results.items():
            marker = " ⭐ OPTIMAL" if chunk_size == best_chunk_size else ""
            print(f"  Chunk size {chunk_size:,}:")
            print(f"    - Processing time: {metrics['processing_time']:.2f}s")
            print(f"    - Memory increase: {metrics['memory_increase']/1024/1024:.2f} MB")
            print(f"    - Records/second: {metrics['records_per_second']:.0f}")
            print(f"    - Chunks processed: {metrics['chunks_processed']}{marker}")
            
        # Assert optimal chunk size meets performance requirements
        optimal_metrics = optimization_results[best_chunk_size]
        assert optimal_metrics['records_per_second'] > 1000, \
            f"Optimal chunk size {best_chunk_size} only achieves {optimal_metrics['records_per_second']:.0f} records/second"
        assert optimal_metrics['memory_increase'] < 100 * 1024 * 1024, \
            f"Optimal chunk size {best_chunk_size} uses {optimal_metrics['memory_increase']/1024/1024:.2f}MB memory"


class TestLargeFileEdgeCases:
    """Test edge cases in large file processing"""
    
    @pytest.mark.performance
    def test_mixed_data_quality_chunked_processing(self, messy_csv_content, memory_monitor):
        """Test chunked processing with messy real-world data"""
        memory_monitor.start_monitoring()
        
        csv_io = io.BytesIO(messy_csv_content)
        chunks_processed = 0
        errors_encountered = 0
        
        try:
            for chunk in pd.read_csv(csv_io, chunksize=10):  # Small chunks for messy data
                chunks_processed += 1
                try:
                    # Attempt to process chunk
                    _ = chunk.to_dict('records')
                except Exception:
                    errors_encountered += 1
                    
        except Exception as e:
            # Should handle messy data gracefully
            print(f"Messy data processing encountered error: {e}")
            
        # Should process at least some chunks
        assert chunks_processed > 0, "No chunks were processed from messy data"
        
        # Memory should remain bounded
        memory_monitor.assert_memory_increase_under(10 * 1024 * 1024)  # 10MB
        
        print(f"\nMessy Data Processing Results:")
        print(f"  - Chunks processed: {chunks_processed}")
        print(f"  - Errors encountered: {errors_encountered}")
        print(f"  - Memory increase: {memory_monitor.get_memory_increase()/1024/1024:.2f} MB")
        
    @pytest.mark.security
    def test_malformed_csv_chunk_processing(self, malicious_files, memory_monitor):
        """Test chunked processing resilience against malformed CSV"""
        memory_monitor.start_monitoring()
        
        # Test with malformed CSV
        malformed_content = malicious_files.get('invalid_csv.csv', b'invalid,csv,content\nbroken"quote,data')
        
        csv_io = io.BytesIO(malformed_content)
        processing_completed = False
        
        try:
            chunks = list(pd.read_csv(csv_io, chunksize=5, on_bad_lines='skip'))
            processing_completed = True
        except Exception as e:
            print(f"Malformed CSV handled with error: {e}")
            
        # Should either process gracefully or fail safely
        # Memory should not increase significantly regardless
        memory_monitor.assert_memory_increase_under(5 * 1024 * 1024)  # 5MB
        
        print(f"\nMalformed CSV Processing:")
        print(f"  - Processing completed: {processing_completed}")
        print(f"  - Memory increase: {memory_monitor.get_memory_increase()/1024/1024:.2f} MB")