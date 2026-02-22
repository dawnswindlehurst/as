#!/usr/bin/env python3
"""Test script for Dashboard and Notifications."""
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database.db import init_db, get_db_session
from notifications.manager import NotificationManager
from dashboard.app import app
from fastapi.testclient import TestClient


def test_database():
    """Test database initialization."""
    print("🔍 Testing database initialization...")
    try:
        init_db()
        db = get_db_session()
        db.close()
        print("✅ Database working")
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False


def test_dashboard():
    """Test dashboard endpoints."""
    print("\n🔍 Testing dashboard endpoints...")
    try:
        client = TestClient(app)
        
        # Test home page
        response = client.get("/")
        print(f"  GET / - Status: {response.status_code}")
        assert response.status_code == 200, "Home page should return 200"
        
        # Test opportunities page
        response = client.get("/opportunities")
        print(f"  GET /opportunities - Status: {response.status_code}")
        assert response.status_code == 200, "Opportunities page should return 200"
        
        # Test sports page
        response = client.get("/sports")
        print(f"  GET /sports - Status: {response.status_code}")
        assert response.status_code == 200, "Sports page should return 200"
        
        # Test bets page
        response = client.get("/bets")
        print(f"  GET /bets - Status: {response.status_code}")
        assert response.status_code == 200, "Bets page should return 200"
        
        # Test API stats
        response = client.get("/api/stats")
        print(f"  GET /api/stats - Status: {response.status_code}")
        assert response.status_code == 200, "API stats should return 200"
        data = response.json()
        assert "total_profit" in data, "API should return total_profit"
        print(f"    API Response: {data}")
        
        # Test API opportunities
        response = client.get("/api/opportunities")
        print(f"  GET /api/opportunities - Status: {response.status_code}")
        assert response.status_code == 200, "API opportunities should return 200"
        data = response.json()
        assert "count" in data, "API should return count"
        print(f"    API Response: count={data.get('count', 0)}")
        
        print("✅ All dashboard endpoints working")
        return True
    except Exception as e:
        print(f"❌ Dashboard error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_notifications():
    """Test notification system."""
    print("\n🔍 Testing notification system...")
    try:
        manager = NotificationManager()
        
        # Check if providers are loaded
        print(f"  Providers loaded: {len(manager.providers)}")
        
        if len(manager.providers) == 0:
            print("  ⚠️  No notification providers configured (this is OK for testing)")
        
        # Test opportunity notification structure
        test_opp = {
            'match_name': 'Test Team A vs Test Team B',
            'bet_on': 'team1',
            'odds': 2.5,
            'edge': 0.08,
            'our_probability': 0.5,
            'implied_probability': 0.4
        }
        
        # This should not fail even without providers
        await manager.notify_opportunity(test_opp, min_edge=0.05)
        
        print("✅ Notification system structure working")
        return True
    except Exception as e:
        print(f"❌ Notification error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Dashboard + Notifications Implementation")
    print("=" * 60)
    
    results = []
    
    # Test database
    results.append(test_database())
    
    # Test dashboard
    results.append(test_dashboard())
    
    # Test notifications
    results.append(asyncio.run(test_notifications()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
