#!/bin/bash

# Air Quality Ingestion Observability Test Script
# This script provides quick commands to test the observability setup

set -e

echo "🔍 Air Quality Ingestion Observability Test Script"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    print_error "docker-compose not found. Please install Docker Compose."
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    print_error "docker-compose.yml not found. Please run this script from the project root."
    exit 1
fi

echo ""
print_info "Starting observability tests..."

# Test 1: Check if services are running
echo ""
echo "📋 Test 1: Checking service status"
echo "----------------------------------"
if docker-compose ps | grep -q "Up"; then
    print_status "Services are running"
    docker-compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
else
    print_warning "Some services may not be running. Starting services..."
    docker-compose up -d
    sleep 10
fi

# Test 2: Check metrics endpoint
echo ""
echo "📊 Test 2: Checking metrics endpoint"
echo "-----------------------------------"
if curl -s http://localhost:8000/metrics > /dev/null; then
    print_status "Metrics endpoint is accessible"
    METRIC_COUNT=$(curl -s http://localhost:8000/metrics | grep -c "^# HELP\|^# TYPE" || echo "0")
    print_info "Found $METRIC_COUNT metric definitions"
else
    print_error "Metrics endpoint not accessible at http://localhost:8000"
fi

# Test 3: Check Prometheus targets
echo ""
echo "🎯 Test 3: Checking Prometheus targets"
echo "-------------------------------------"
if curl -s http://localhost:9090/api/v1/targets > /dev/null; then
    print_status "Prometheus is accessible"
    UP_TARGETS=$(curl -s http://localhost:9090/api/v1/targets | jq -r '.data.activeTargets[] | select(.health == "up") | .labels.job' 2>/dev/null || echo "")
    if [ -n "$UP_TARGETS" ]; then
        print_status "Up targets:"
        echo "$UP_TARGETS" | sed 's/^/  - /'
    else
        print_warning "No targets are UP yet. Waiting for services to start..."
    fi
else
    print_error "Prometheus not accessible at http://localhost:9090"
fi

# Test 4: Check Grafana
echo ""
echo "📈 Test 4: Checking Grafana"
echo "---------------------------"
GRAFANA_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)
if [ "$GRAFANA_CODE" = "200" ] || [ "$GRAFANA_CODE" = "302" ]; then
    print_status "Grafana is accessible at http://localhost:3000"
    print_info "Login: admin/admin"
else
    print_error "Grafana not accessible at http://localhost:3000 (HTTP $GRAFANA_CODE)"
fi

# Test 5: Check Kafka UI
echo ""
echo "☕ Test 5: Checking Kafka UI"
echo "----------------------------"
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8080 | grep -q "200"; then
    print_status "Kafka UI is accessible at http://localhost:8080"
else
    print_error "Kafka UI not accessible at http://localhost:8080"
fi

# Test 6: Check logs
echo ""
echo "📝 Test 6: Checking ingestion service logs"
echo "------------------------------------------"
if docker-compose logs ingestion 2>/dev/null | grep -q "Starting Air Quality Ingestion Service"; then
    print_status "Ingestion service logs are available"
    ERROR_COUNT=$(docker-compose logs ingestion 2>/dev/null | grep -c "ERROR" || echo "0")
    WARNING_COUNT=$(docker-compose logs ingestion 2>/dev/null | grep -c "WARNING" || echo "0")
    print_info "Found $ERROR_COUNT errors and $WARNING_COUNT warnings in logs"
else
    print_warning "Ingestion service logs not found or service not started"
fi

# Test 7: Check specific metrics
echo ""
echo "🔢 Test 7: Checking specific metrics"
echo "-----------------------------------"
if curl -s http://localhost:8000/metrics > /dev/null; then
    API_CALLS=$(curl -s http://localhost:8000/metrics | grep "api_calls_total" | wc -l || echo "0")
    ERRORS=$(curl -s http://localhost:8000/metrics | grep "errors_total" | wc -l || echo "0")
    PROCESSING=$(curl -s http://localhost:8000/metrics | grep "processing_duration_seconds" | wc -l || echo "0")
    
    print_status "Metric counts:"
    echo "  - API calls metrics: $API_CALLS"
    echo "  - Error metrics: $ERRORS"
    echo "  - Processing metrics: $PROCESSING"
else
    print_error "Cannot retrieve metrics"
fi

# Test 8: Check Loki
echo ""
echo "🔍 Test 8: Checking Loki log aggregation"
echo "----------------------------------------"
if curl -s http://localhost:3100/ready > /dev/null; then
    print_status "Loki is accessible"
else
    print_error "Loki not accessible at http://localhost:3100"
fi

# Summary
echo ""
echo "📋 Test Summary"
echo "==============="
echo ""
print_info "Access URLs:"
echo "  - Grafana Dashboard: http://localhost:3000 (admin/admin)"
echo "  - Prometheus: http://localhost:9090"
echo "  - Kafka UI: http://localhost:8080"
echo "  - Metrics Endpoint: http://localhost:8000/metrics"
echo "  - Loki: http://localhost:3100"
echo ""
print_info "Useful commands:"
echo "  - View logs: docker-compose logs -f ingestion"
echo "  - Check status: docker-compose ps"
echo "  - Restart services: docker-compose restart"
echo "  - Stop services: docker-compose down"
echo ""
print_info "For detailed testing, see TESTING_GUIDE.md"

echo ""
print_status "Observability test completed!"
