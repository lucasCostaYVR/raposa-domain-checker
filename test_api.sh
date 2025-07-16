#!/bin/bash

# Test script for the Raposa Domain Checker API

BASE_URL="http://localhost:8000"

echo "🧪 Testing Raposa Domain Checker API"
echo "=================================="
echo ""

# Test 1: Health check
echo "📋 Test 1: Health Check"
echo "GET $BASE_URL/healthz/"
curl -s "$BASE_URL/healthz/" | python3 -m json.tool
echo -e "\n"

# Test 2: Root endpoint
echo "📋 Test 2: Root Endpoint"
echo "GET $BASE_URL/"
curl -s "$BASE_URL/" | python3 -m json.tool
echo -e "\n"

# Test 3: Domain check (POST request)
echo "📋 Test 3: Domain Check"
echo "POST $BASE_URL/check-domain"
curl -s -X POST "$BASE_URL/check-domain" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "domain": "google.com",
    "opt_in_marketing": false
  }' | python3 -m json.tool
echo -e "\n"

# Test 4: Domain usage check
echo "📋 Test 4: Domain Usage Check"
echo "GET $BASE_URL/domain-usage/google.com"
curl -s "$BASE_URL/domain-usage/google.com" | python3 -m json.tool
echo -e "\n"

# Test 5: API documentation
echo "📋 Test 5: API Documentation Available"
echo "You can view the interactive API docs at:"
echo "🌐 $BASE_URL/docs"
echo "🌐 $BASE_URL/redoc"
echo ""

echo "✅ All tests completed!"
