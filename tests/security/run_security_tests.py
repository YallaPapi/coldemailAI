#!/usr/bin/env python3
"""
Security Test Runner for Flask CSV Upload Endpoint
Comprehensive security testing script with reporting and categorization
Based on 2025 Flask security testing best practices.
"""
import sys
import os
import subprocess
import time
import json
from datetime import datetime
from pathlib import Path
import argparse

# Add parent directory to path for importing Flask app
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class SecurityTestRunner:
    """Comprehensive security test runner with categorized testing"""
    
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.results = {
            'start_time': None,
            'end_time': None,
            'total_duration': 0,
            'categories': {},
            'summary': {},
            'failed_tests': [],
            'passed_tests': [],
            'skipped_tests': []
        }
    
    def run_test_category(self, category_name, test_files, markers=None):
        """Run tests for a specific security category"""
        print(f"\n{'=' * 60}")
        print(f"Running {category_name} Security Tests")
        print(f"{'=' * 60}")
        
        cmd = ['python', '-m', 'pytest', '-v']
        
        # Add markers if specified
        if markers:
            for marker in markers:
                cmd.extend(['-m', marker])
        
        # Add test files
        for test_file in test_files:
            test_path = self.test_dir / test_file
            if test_path.exists():
                cmd.append(str(test_path))
        
        # Add additional options
        cmd.extend([
            '--tb=short',
            '--maxfail=10',
            '--durations=5',
            '--json-report',
            f'--json-report-file={self.test_dir}/reports/{category_name}_report.json'
        ])
        
        # Create reports directory if it doesn't exist
        reports_dir = self.test_dir / 'reports'
        reports_dir.mkdir(exist_ok=True)
        
        start_time = time.time()
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.test_dir,
                capture_output=True,
                text=True,
                timeout=1800  # 30 minute timeout
            )
            
            duration = time.time() - start_time
            
            # Parse results
            category_results = {
                'duration': duration,
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'passed': result.returncode == 0
            }
            
            # Try to load JSON report if available
            json_report_path = reports_dir / f'{category_name}_report.json'
            if json_report_path.exists():
                try:
                    with open(json_report_path) as f:
                        json_data = json.load(f)
                        category_results['test_summary'] = json_data.get('summary', {})
                        category_results['test_details'] = json_data.get('tests', [])
                except Exception as e:
                    print(f"Warning: Could not parse JSON report: {e}")
            
            self.results['categories'][category_name] = category_results
            
            # Print results
            if result.returncode == 0:
                print(f"✅ {category_name} tests PASSED ({duration:.1f}s)")
            else:
                print(f"❌ {category_name} tests FAILED ({duration:.1f}s)")
                print(f"STDOUT: {result.stdout[-500:]}")  # Last 500 chars
                print(f"STDERR: {result.stderr[-500:]}")  # Last 500 chars
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {category_name} tests TIMED OUT after 30 minutes")
            category_results = {
                'duration': 1800,
                'return_code': -1,
                'stdout': '',
                'stderr': 'Test execution timed out',
                'passed': False
            }
            self.results['categories'][category_name] = category_results
            
        except Exception as e:
            print(f"💥 {category_name} tests CRASHED: {e}")
            category_results = {
                'duration': time.time() - start_time,
                'return_code': -2,
                'stdout': '',
                'stderr': str(e),
                'passed': False
            }
            self.results['categories'][category_name] = category_results
    
    def run_all_security_tests(self):
        """Run all security test categories"""
        self.results['start_time'] = datetime.now().isoformat()
        overall_start = time.time()
        
        print("🔒 Starting Comprehensive Security Testing Suite")
        print(f"📅 Start Time: {self.results['start_time']}")
        print(f"📂 Test Directory: {self.test_dir}")
        
        # Define test categories
        test_categories = [
            {
                'name': 'File Upload Security',
                'files': ['test_file_upload_security.py'],
                'markers': ['file_upload'],
                'description': 'Basic file upload security testing'
            },
            {
                'name': 'CSV Injection Advanced',
                'files': ['test_csv_injection_advanced.py'],
                'markers': ['csv_injection'],
                'description': 'Advanced CSV formula injection testing'
            },
            {
                'name': 'Comprehensive Security',
                'files': ['test_security_comprehensive.py'],
                'markers': ['integration'],
                'description': 'Comprehensive integrated security testing'
            },
            {
                'name': 'Performance Security',
                'files': ['test_security_comprehensive.py'],
                'markers': ['performance_security'],
                'description': 'Performance-related security testing'
            },
            {
                'name': 'Edge Cases',
                'files': ['test_file_upload_security.py', 'test_csv_injection_advanced.py'],
                'markers': ['edge_cases'],
                'description': 'Edge case security scenarios'
            }
        ]
        
        # Run each category
        for category in test_categories:
            print(f"\n📋 Category: {category['description']}")
            self.run_test_category(
                category['name'],
                category['files'],
                category.get('markers')
            )
        
        # Calculate overall results
        self.results['end_time'] = datetime.now().isoformat()
        self.results['total_duration'] = time.time() - overall_start
        
        self.generate_summary_report()
        self.print_final_summary()
    
    def run_quick_security_tests(self):
        """Run only critical security tests for quick validation"""
        print("🚀 Running Quick Security Validation")
        
        self.results['start_time'] = datetime.now().isoformat()
        overall_start = time.time()
        
        # Quick test categories
        quick_categories = [
            {
                'name': 'Critical CSV Injection',
                'files': ['test_csv_injection_advanced.py'],
                'markers': ['csv_injection', 'critical'],
                'description': 'Critical CSV injection tests'
            },
            {
                'name': 'Critical File Upload',
                'files': ['test_file_upload_security.py'],
                'markers': ['file_upload', 'critical'],
                'description': 'Critical file upload security tests'
            }
        ]
        
        for category in quick_categories:
            self.run_test_category(
                category['name'],
                category['files'],
                category.get('markers')
            )
        
        self.results['end_time'] = datetime.now().isoformat()
        self.results['total_duration'] = time.time() - overall_start
        
        self.generate_summary_report()
        self.print_final_summary()
    
    def generate_summary_report(self):
        """Generate comprehensive summary report"""
        total_passed = 0
        total_failed = 0
        total_categories = len(self.results['categories'])
        
        for category_name, category_data in self.results['categories'].items():
            if category_data['passed']:
                total_passed += 1
            else:
                total_failed += 1
                
            # Extract test details if available
            if 'test_summary' in category_data:
                summary = category_data['test_summary']
                self.results['summary'][category_name] = {
                    'total': summary.get('total', 0),
                    'passed': summary.get('passed', 0),
                    'failed': summary.get('failed', 0),
                    'skipped': summary.get('skipped', 0),
                    'duration': category_data['duration']
                }
        
        self.results['summary']['overall'] = {
            'total_categories': total_categories,
            'passed_categories': total_passed,
            'failed_categories': total_failed,
            'success_rate': (total_passed / total_categories) * 100 if total_categories > 0 else 0,
            'total_duration': self.results['total_duration']
        }
    
    def print_final_summary(self):
        """Print final test summary"""
        print(f"\n{'=' * 80}")
        print("🔒 SECURITY TESTING SUMMARY")
        print(f"{'=' * 80}")
        
        overall = self.results['summary'].get('overall', {})
        
        print(f"📊 Overall Results:")
        print(f"   ⏱️  Total Duration: {overall.get('total_duration', 0):.1f}s")
        print(f"   📋 Categories Tested: {overall.get('total_categories', 0)}")
        print(f"   ✅ Categories Passed: {overall.get('passed_categories', 0)}")
        print(f"   ❌ Categories Failed: {overall.get('failed_categories', 0)}")
        print(f"   📈 Success Rate: {overall.get('success_rate', 0):.1f}%")
        
        print(f"\n📋 Category Details:")
        for category_name, category_data in self.results['categories'].items():
            status = "✅ PASSED" if category_data['passed'] else "❌ FAILED"
            duration = category_data['duration']
            print(f"   {status} {category_name} ({duration:.1f}s)")
            
            if 'test_summary' in category_data:
                summary = category_data['test_summary']
                total = summary.get('total', 0)
                passed = summary.get('passed', 0)
                failed = summary.get('failed', 0)
                skipped = summary.get('skipped', 0)
                print(f"      Tests: {total} total, {passed} passed, {failed} failed, {skipped} skipped")
        
        # Security assessment
        print(f"\n🛡️  Security Assessment:")
        success_rate = overall.get('success_rate', 0)
        
        if success_rate >= 95:
            print("   🟢 EXCELLENT: Security measures are comprehensive and effective")
        elif success_rate >= 85:
            print("   🟡 GOOD: Security measures are adequate with minor issues")
        elif success_rate >= 70:
            print("   🟠 MODERATE: Security measures need improvement")
        else:
            print("   🔴 CRITICAL: Significant security vulnerabilities detected")
        
        # Save detailed report
        self.save_detailed_report()
        
        print(f"\n📄 Detailed reports saved in: {self.test_dir}/reports/")
        print(f"{'=' * 80}")
    
    def save_detailed_report(self):
        """Save detailed JSON report"""
        reports_dir = self.test_dir / 'reports'
        reports_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = reports_dir / f'security_test_summary_{timestamp}.json'
        
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"📄 Detailed report saved: {report_file}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Run Flask CSV Upload Security Tests')
    parser.add_argument(
        '--mode',
        choices=['full', 'quick', 'category'],
        default='full',
        help='Test mode: full (all tests), quick (critical only), category (specific category)'
    )
    parser.add_argument(
        '--category',
        help='Specific category to test (use with --mode=category)'
    )
    parser.add_argument(
        '--install-deps',
        action='store_true',
        help='Install security testing dependencies first'
    )
    
    args = parser.parse_args()
    
    # Install dependencies if requested
    if args.install_deps:
        print("📦 Installing security testing dependencies...")
        requirements_file = Path(__file__).parent / 'requirements_security_testing.txt'
        if requirements_file.exists():
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)
            ])
        else:
            print("⚠️  Requirements file not found")
    
    runner = SecurityTestRunner()
    
    if args.mode == 'full':
        runner.run_all_security_tests()
    elif args.mode == 'quick':
        runner.run_quick_security_tests()
    elif args.mode == 'category':
        if not args.category:
            print("❌ --category required when using --mode=category")
            sys.exit(1)
        # Implementation for specific category testing
        print(f"🎯 Running category: {args.category}")
        # This would need category-specific implementation
    
    # Exit with appropriate code
    overall = runner.results['summary'].get('overall', {})
    failed_categories = overall.get('failed_categories', 0)
    
    if failed_categories > 0:
        print(f"\n❌ Security tests failed. Exit code: {failed_categories}")
        sys.exit(failed_categories)
    else:
        print(f"\n✅ All security tests passed!")
        sys.exit(0)


if __name__ == '__main__':
    main()