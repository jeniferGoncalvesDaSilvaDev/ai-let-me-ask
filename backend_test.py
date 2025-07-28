#!/usr/bin/env python3
"""
Backend API Test Suite for NLW Agents API
Tests all endpoints using the public URL from frontend/.env
"""

import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional

class NLWAgentsAPITester:
    def __init__(self, base_url: str = "https://3eed6482-8f1a-47b8-b2e5-42b54c81d8c2.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.created_room_id = None
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})

    def log_test(self, name: str, success: bool, details: str = ""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED {details}")
        else:
            print(f"❌ {name} - FAILED {details}")

    def run_test(self, name: str, method: str, endpoint: str, expected_status: int, 
                 data: Optional[Dict[Any, Any]] = None, files: Optional[Dict] = None) -> tuple[bool, Dict]:
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            if method == 'GET':
                response = self.session.get(url, timeout=30)
            elif method == 'POST':
                if files:
                    # Remove Content-Type header for file uploads
                    headers = {k: v for k, v in self.session.headers.items() if k.lower() != 'content-type'}
                    response = requests.post(url, files=files, headers=headers, timeout=30)
                else:
                    response = self.session.post(url, json=data, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")

            success = response.status_code == expected_status
            response_data = {}
            
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text}

            details = f"(Status: {response.status_code})"
            if not success:
                details += f" Expected: {expected_status}, Response: {response.text[:200]}"
                
            self.log_test(name, success, details)
            return success, response_data

        except Exception as e:
            self.log_test(name, False, f"Exception: {str(e)}")
            return False, {}

    def test_health_check(self) -> bool:
        """Test API health check endpoint"""
        print("\n🔍 Testing Health Check...")
        success, response = self.run_test(
            "Health Check",
            "GET", 
            "api/",
            200
        )
        
        if success and response.get("status") == "online":
            print(f"   API Message: {response.get('message', 'N/A')}")
            return True
        return False

    def test_get_rooms_empty(self) -> bool:
        """Test getting rooms (initially empty)"""
        print("\n🔍 Testing Get Rooms (Initial)...")
        success, response = self.run_test(
            "Get Rooms (Empty)",
            "GET",
            "api/rooms", 
            200
        )
        
        if success:
            rooms_count = len(response) if isinstance(response, list) else 0
            print(f"   Found {rooms_count} existing rooms")
            return True
        return False

    def test_create_room(self) -> bool:
        """Test creating a new room"""
        print("\n🔍 Testing Create Room...")
        
        test_room_data = {
            "name": "Teste Automático",
            "description": "Sala criada por teste automatizado"
        }
        
        success, response = self.run_test(
            "Create Room",
            "POST",
            "api/rooms",
            200,
            data=test_room_data
        )
        
        if success and response.get("id"):
            self.created_room_id = response["id"]
            print(f"   Created room ID: {self.created_room_id}")
            print(f"   Room name: {response.get('name')}")
            print(f"   Room description: {response.get('description')}")
            return True
        return False

    def test_get_rooms_with_data(self) -> bool:
        """Test getting rooms after creating one"""
        print("\n🔍 Testing Get Rooms (With Data)...")
        success, response = self.run_test(
            "Get Rooms (With Data)",
            "GET",
            "api/rooms",
            200
        )
        
        if success and isinstance(response, list):
            rooms_count = len(response)
            print(f"   Found {rooms_count} rooms")
            
            # Check if our created room exists
            if self.created_room_id:
                room_found = any(room.get("id") == self.created_room_id for room in response)
                if room_found:
                    print(f"   ✓ Created room found in list")
                else:
                    print(f"   ⚠ Created room not found in list")
            return True
        return False

    def test_create_question(self) -> bool:
        """Test creating a question in the room"""
        if not self.created_room_id:
            print("\n❌ Cannot test create question - no room created")
            return False
            
        print("\n🔍 Testing Create Question...")
        
        test_questions = [
            "Olá, como você está?",
            "O que é programação?", 
            "Como funciona IA?"
        ]
        
        success_count = 0
        for i, question_text in enumerate(test_questions):
            question_data = {"content": question_text}
            
            success, response = self.run_test(
                f"Create Question {i+1}",
                "POST",
                f"api/rooms/{self.created_room_id}/questions",
                200,
                data=question_data
            )
            
            if success:
                success_count += 1
                print(f"   Question: {question_text}")
                print(f"   Answer: {response.get('answer', 'No answer')[:100]}...")
                
        return success_count > 0

    def test_get_room_questions(self) -> bool:
        """Test getting questions from a room"""
        if not self.created_room_id:
            print("\n❌ Cannot test get questions - no room created")
            return False
            
        print("\n🔍 Testing Get Room Questions...")
        success, response = self.run_test(
            "Get Room Questions",
            "GET",
            f"api/rooms/{self.created_room_id}/questions",
            200
        )
        
        if success and isinstance(response, list):
            questions_count = len(response)
            print(f"   Found {questions_count} questions in room")
            
            for i, question in enumerate(response[:3]):  # Show first 3
                print(f"   Q{i+1}: {question.get('content', 'N/A')[:50]}...")
                if question.get('answer'):
                    print(f"   A{i+1}: {question.get('answer', 'N/A')[:50]}...")
            return True
        return False

    def test_invalid_room_operations(self) -> bool:
        """Test operations with invalid room ID"""
        print("\n🔍 Testing Invalid Room Operations...")
        
        fake_room_id = "non-existent-room-id"
        
        # Test getting questions from non-existent room
        success1, _ = self.run_test(
            "Get Questions (Invalid Room)",
            "GET",
            f"api/rooms/{fake_room_id}/questions",
            404
        )
        
        # Test creating question in non-existent room
        success2, _ = self.run_test(
            "Create Question (Invalid Room)",
            "POST", 
            f"api/rooms/{fake_room_id}/questions",
            404,
            data={"content": "Test question"}
        )
        
        return success1 and success2

    def test_ai_contextual_responses(self) -> bool:
        """Test AI contextual response system"""
        if not self.created_room_id:
            print("\n❌ Cannot test AI responses - no room created")
            return False
            
        print("\n🔍 Testing AI Contextual Responses...")
        
        test_cases = [
            ("Greeting", "Olá!"),
            ("Technology", "O que é programação?"),
            ("AI Question", "Como funciona inteligência artificial?"),
            ("Help Request", "Preciso de ajuda"),
            ("Generic", "Qual é o sentido da vida?")
        ]
        
        success_count = 0
        for category, question in test_cases:
            success, response = self.run_test(
                f"AI Response ({category})",
                "POST",
                f"api/rooms/{self.created_room_id}/questions",
                200,
                data={"content": question}
            )
            
            if success and response.get('answer'):
                success_count += 1
                answer = response.get('answer', '')
                print(f"   {category}: {answer[:80]}...")
                
        return success_count >= len(test_cases) // 2  # At least half should work

    def run_all_tests(self) -> bool:
        """Run all API tests"""
        print("🚀 Starting NLW Agents API Test Suite")
        print(f"📡 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Run tests in logical order
        tests = [
            self.test_health_check,
            self.test_get_rooms_empty,
            self.test_create_room,
            self.test_get_rooms_with_data,
            self.test_create_question,
            self.test_get_room_questions,
            self.test_ai_contextual_responses,
            self.test_invalid_room_operations,
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                print(f"❌ Test {test.__name__} failed with exception: {e}")
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        
        if self.created_room_id:
            print(f"\n🏠 Test Room Created: {self.created_room_id}")
            print("   (This room can be used for frontend testing)")
        
        return self.tests_passed == self.tests_run

def main():
    """Main test execution"""
    tester = NLWAgentsAPITester()
    
    try:
        success = tester.run_all_tests()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Test suite failed with error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())