#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for VB/C# Transpiler
Tests all endpoints with various scenarios
"""

import requests
import sys
import json
from datetime import datetime

class VBCSharpTranspilerTester:
    def __init__(self, base_url="https://vb-csharp-bridge.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            self.failed_tests.append({"name": name, "details": details})
            print(f"❌ {name} - FAILED: {details}")

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if endpoint else self.api_url
        if headers is None:
            headers = {'Content-Type': 'application/json'}

        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        if data:
            print(f"   Data: {json.dumps(data, indent=2)}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")

            print(f"   Response Status: {response.status_code}")
            
            success = response.status_code == expected_status
            
            if success:
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                    self.log_test(name, True)
                    return True, response_data
                except json.JSONDecodeError:
                    print(f"   Response Text: {response.text[:200]}...")
                    self.log_test(name, True)
                    return True, response.text
            else:
                error_details = f"Expected {expected_status}, got {response.status_code}"
                try:
                    error_data = response.json()
                    error_details += f" - {error_data}"
                except:
                    error_details += f" - {response.text[:100]}"
                
                self.log_test(name, False, error_details)
                return False, {}

        except Exception as e:
            error_details = f"Exception: {str(e)}"
            self.log_test(name, False, error_details)
            return False, {}

    def test_health_check(self):
        """Test GET /api/ - Health check"""
        return self.run_test(
            "Health Check",
            "GET",
            "",
            200
        )

    def test_parse_vbnet_code(self):
        """Test POST /api/parse with VB.NET code"""
        vbnet_code = """Public Class Calculator
    Public Function Add(a As Integer, b As Integer) As Integer
        Return a + b
    End Function
End Class"""
        
        return self.run_test(
            "Parse VB.NET Code",
            "POST",
            "parse",
            200,
            data={
                "code": vbnet_code,
                "source_lang": "vbnet"
            }
        )

    def test_parse_csharp_code(self):
        """Test POST /api/parse with C# code"""
        csharp_code = """public class Calculator
{
    public int Add(int a, int b)
    {
        return a + b;
    }
}"""
        
        return self.run_test(
            "Parse C# Code",
            "POST",
            "parse",
            200,
            data={
                "code": csharp_code,
                "source_lang": "csharp"
            }
        )

    def test_parse_vb_code(self):
        """Test POST /api/parse with VB6 code"""
        vb_code = """Public Class Calculator
    Public Function Add(a As Integer) As Integer
        Add = a + 10
    End Function
End Class"""
        
        return self.run_test(
            "Parse VB6 Code",
            "POST",
            "parse",
            200,
            data={
                "code": vb_code,
                "source_lang": "vb"
            }
        )

    def test_transpile_vbnet_to_csharp(self):
        """Test POST /api/transpile - VB.NET to C#"""
        vbnet_code = """Public Class Calculator
    Public Function Add(a As Integer, b As Integer) As Integer
        Return a + b
    End Function
End Class"""
        
        return self.run_test(
            "Transpile VB.NET to C#",
            "POST",
            "transpile",
            200,
            data={
                "code": vbnet_code,
                "source_lang": "vbnet",
                "target_lang": "csharp",
                "use_mcp": False
            }
        )

    def test_transpile_csharp_to_vbnet(self):
        """Test POST /api/transpile - C# to VB.NET"""
        csharp_code = """public class Calculator
{
    public int Add(int a, int b)
    {
        return a + b;
    }
}"""
        
        return self.run_test(
            "Transpile C# to VB.NET",
            "POST",
            "transpile",
            200,
            data={
                "code": csharp_code,
                "source_lang": "csharp",
                "target_lang": "vbnet",
                "use_mcp": False
            }
        )

    def test_transpile_vb_to_vbnet(self):
        """Test POST /api/transpile - VB6 to VB.NET"""
        vb_code = """Public Class Test
    Public Function Add(a As Integer) As Integer
        Add = a + 10
    End Function
End Class"""
        
        return self.run_test(
            "Transpile VB6 to VB.NET",
            "POST",
            "transpile",
            200,
            data={
                "code": vb_code,
                "source_lang": "vb",
                "target_lang": "vbnet",
                "use_mcp": False
            }
        )

    def test_transpile_vb_to_csharp(self):
        """Test POST /api/transpile - VB6 to C# (two-step)"""
        vb_code = """Public Class Test
    Public Function Add(a As Integer) As Integer
        Add = a + 10
    End Function
End Class"""
        
        return self.run_test(
            "Transpile VB6 to C# (two-step)",
            "POST",
            "transpile",
            200,
            data={
                "code": vb_code,
                "source_lang": "vb",
                "target_lang": "csharp",
                "use_mcp": False
            }
        )

    def test_validate_valid_code(self):
        """Test POST /api/validate with valid code"""
        valid_code = """Public Class Calculator
    Public Function Add(a As Integer, b As Integer) As Integer
        Return a + b
    End Function
End Class"""
        
        return self.run_test(
            "Validate Valid Code",
            "POST",
            "validate",
            200,
            data={
                "code": valid_code,
                "language": "vbnet"
            }
        )

    def test_validate_short_code(self):
        """Test POST /api/validate with very short code"""
        return self.run_test(
            "Validate Short Code",
            "POST",
            "validate",
            200,
            data={
                "code": "x = 1",
                "language": "vbnet"
            }
        )

    def test_mcp_connection_test(self):
        """Test POST /api/mcp/test"""
        return self.run_test(
            "MCP Connection Test",
            "POST",
            "mcp/test",
            200,
            data={
                "server_url": "https://test-mcp-server.com/api",
                "api_key": "test-key-123"
            }
        )

    def test_transpile_empty_code(self):
        """Test transpiling empty code"""
        return self.run_test(
            "Transpile Empty Code",
            "POST",
            "transpile",
            200,
            data={
                "code": "",
                "source_lang": "vbnet",
                "target_lang": "csharp",
                "use_mcp": False
            }
        )

    def test_transpile_same_languages(self):
        """Test transpiling with same source and target language"""
        return self.run_test(
            "Transpile Same Languages",
            "POST",
            "transpile",
            200,
            data={
                "code": "Public Class Test\nEnd Class",
                "source_lang": "vbnet",
                "target_lang": "vbnet",
                "use_mcp": False
            }
        )

    def test_transpile_with_mcp(self):
        """Test transpiling with MCP enabled"""
        return self.run_test(
            "Transpile with MCP",
            "POST",
            "transpile",
            200,
            data={
                "code": "Public Class Test\nEnd Class",
                "source_lang": "vbnet",
                "target_lang": "csharp",
                "use_mcp": True,
                "mcp_config": {
                    "server_url": "https://test-mcp-server.com/api",
                    "api_key": "test-key"
                }
            }
        )

    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting VB/C# Transpiler API Tests")
        print(f"📍 Base URL: {self.base_url}")
        print(f"📍 API URL: {self.api_url}")
        print("=" * 60)

        # Basic functionality tests
        self.test_health_check()
        
        # Parse tests
        self.test_parse_vbnet_code()
        self.test_parse_csharp_code()
        self.test_parse_vb_code()
        
        # Transpilation tests
        self.test_transpile_vbnet_to_csharp()
        self.test_transpile_csharp_to_vbnet()
        self.test_transpile_vb_to_vbnet()
        self.test_transpile_vb_to_csharp()
        
        # Validation tests
        self.test_validate_valid_code()
        self.test_validate_short_code()
        
        # MCP tests
        self.test_mcp_connection_test()
        
        # Edge case tests
        self.test_transpile_empty_code()
        self.test_transpile_same_languages()
        self.test_transpile_with_mcp()

        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Tests Passed: {self.tests_passed}/{self.tests_run}")
        print(f"❌ Tests Failed: {len(self.failed_tests)}/{self.tests_run}")
        
        if self.failed_tests:
            print("\n🔍 FAILED TESTS:")
            for i, test in enumerate(self.failed_tests, 1):
                print(f"{i}. {test['name']}: {test['details']}")
        
        success_rate = (self.tests_passed / self.tests_run) * 100 if self.tests_run > 0 else 0
        print(f"\n📈 Success Rate: {success_rate:.1f}%")
        
        return self.tests_passed == self.tests_run

def main():
    """Main test runner"""
    tester = VBCSharpTranspilerTester()
    
    try:
        success = tester.run_all_tests()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())