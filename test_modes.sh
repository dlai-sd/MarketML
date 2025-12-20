#!/bin/bash
# Test script for different persona generation modes

API_URL="http://localhost:8000/v1/personas/generate"
echo "🧪 Testing MarketML Persona Generation Modes"
echo "=============================================="
echo ""

# Function to test a mode combination
test_mode() {
    local name="$1"
    local gen_mode="$2"
    local data_source="$3"
    local linkedin="$4"
    
    echo "📋 Testing: $name"
    echo "   Generation: $gen_mode | Data: $data_source | LinkedIn: $linkedin"
    
    response=$(curl -s -X POST "$API_URL" \
        -H 'Content-Type: application/json' \
        -d "{
            \"name\": \"Test User - $name\",
            \"location\": \"Mumbai, Maharashtra\",
            \"description\": \"Testing $name combination\",
            \"generation_mode\": \"$gen_mode\",
            \"data_source\": \"$data_source\",
            \"linkedin_mode\": \"$linkedin\"
        }")
    
    job_id=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin)['job_id'])" 2>/dev/null)
    
    if [ -z "$job_id" ]; then
        echo "   ❌ Failed to submit job"
        echo "   Response: $response"
        echo ""
        return 1
    fi
    
    echo "   ⏳ Job ID: $job_id"
    
    # Wait for completion
    for i in {1..20}; do
        sleep 1
        status=$(curl -s "http://localhost:8000/v1/jobs/$job_id" | python3 -c "import sys, json; print(json.load(sys.stdin)['status'])" 2>/dev/null)
        
        if [ "$status" = "completed" ]; then
            persona_id=$(curl -s "http://localhost:8000/v1/jobs/$job_id" | python3 -c "import sys, json; print(json.load(sys.stdin)['persona_id'])" 2>/dev/null)
            
            # Get persona details
            persona=$(curl -s "http://localhost:8000/v1/personas/$persona_id")
            gen_mode_used=$(echo "$persona" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('generation_mode_used', 'N/A'))" 2>/dev/null || echo "N/A")
            confidence=$(echo "$persona" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('confidence_score', 'N/A'))" 2>/dev/null || echo "N/A")
            
            echo "   ✅ Success! Persona: $persona_id"
            echo "   📊 Mode Used: $gen_mode_used | Confidence: $confidence"
            echo ""
            return 0
        elif [ "$status" = "failed" ]; then
            error=$(curl -s "http://localhost:8000/v1/jobs/$job_id" | python3 -c "import sys, json; print(json.load(sys.stdin).get('error_message', 'Unknown error'))" 2>/dev/null)
            echo "   ❌ Failed: $error"
            echo ""
            return 1
        fi
    done
    
    echo "   ⏱️  Timeout waiting for completion"
    echo ""
    return 1
}

# Test Case 1: Template + Mock (Default, should always work)
test_mode "Template+Mock" "template" "mock" "skip"

# Test Case 2: GPT-3.5 + Mock (Will fallback to template if no API key)
test_mode "GPT-3.5+Mock" "gpt-3.5" "mock" "skip"

# Test Case 3: GPT-4 + Mock (Will fallback to template if no API key)
test_mode "GPT-4+Mock" "gpt-4" "mock" "skip"

# Test Case 4: Template + Google Search (Requires googlesearch-python)
test_mode "Template+Google" "template" "google" "skip"

# Test Case 5: Template + Playwright (Requires playwright)
# test_mode "Template+Playwright" "template" "playwright" "skip"

echo "=============================================="
echo "✅ Testing complete!"
echo ""
echo "💡 Notes:"
echo "   - Template+Mock should always work"
echo "   - GPT modes fallback to template without OpenAI API key"
echo "   - Google mode requires googlesearch-python"
echo "   - Playwright mode requires: pip install playwright && playwright install"
echo "   - LinkedIn basic mode requires Playwright setup"
echo ""
