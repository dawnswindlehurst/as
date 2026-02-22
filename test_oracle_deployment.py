"""Test Oracle Cloud deployment configuration."""
import os
import sys

# Get project root directory
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


def test_env_example_exists():
    """Test that .env.example exists and contains Oracle settings."""
    env_example_path = os.path.join(PROJECT_ROOT, '.env.example')
    assert os.path.exists(env_example_path), ".env.example not found"
    
    with open(env_example_path, 'r') as f:
        content = f.read()
    
    # Check for key Oracle settings
    required_vars = [
        'ORACLE_DEPLOYMENT',
        'COLLECTION_INTERVAL_HOURS',
        'INITIAL_COLLECTION_DAYS',
        'ENABLE_INITIAL_COLLECTION',
        'TRADITIONAL_SPORTS_RATE_LIMIT',
        'HLTV_RATE_LIMIT',
        'VLR_RATE_LIMIT',
        'SUPERBET_RATE_LIMIT',
        'MAX_WORKERS',
        'BATCH_SIZE',
    ]
    
    for var in required_vars:
        assert var in content, f"Missing {var} in .env.example"
    
    print("✓ .env.example contains all required Oracle settings")


def test_docker_compose_oracle_exists():
    """Test that docker-compose.oracle.yml exists."""
    compose_path = os.path.join(PROJECT_ROOT, 'docker-compose.oracle.yml')
    assert os.path.exists(compose_path), "docker-compose.oracle.yml not found"
    print("✓ docker-compose.oracle.yml exists")


def test_oracle_config_exists():
    """Test that config/oracle.py exists."""
    config_path = os.path.join(PROJECT_ROOT, 'config', 'oracle.py')
    assert os.path.exists(config_path), "config/oracle.py not found"
    print("✓ config/oracle.py exists")


def test_collection_service_exists():
    """Test that jobs/collection_service.py exists."""
    service_path = os.path.join(PROJECT_ROOT, 'jobs', 'collection_service.py')
    assert os.path.exists(service_path), "jobs/collection_service.py not found"
    print("✓ jobs/collection_service.py exists")


def test_deployment_scripts_exist():
    """Test that deployment scripts exist and are executable."""
    scripts_dir = os.path.join(PROJECT_ROOT, 'scripts')
    
    oracle_setup = os.path.join(scripts_dir, 'oracle_setup.sh')
    deploy = os.path.join(scripts_dir, 'deploy.sh')
    
    assert os.path.exists(oracle_setup), "oracle_setup.sh not found"
    assert os.path.exists(deploy), "deploy.sh not found"
    
    # Check if executable (on Unix systems)
    if os.name != 'nt':  # Not Windows
        assert os.access(oracle_setup, os.X_OK), "oracle_setup.sh not executable"
        assert os.access(deploy, os.X_OK), "deploy.sh not executable"
    
    print("✓ Deployment scripts exist and are executable")


def test_documentation_exists():
    """Test that documentation files exist."""
    docs_dir = os.path.join(PROJECT_ROOT, 'docs')
    
    oracle_doc = os.path.join(docs_dir, 'ORACLE_DEPLOYMENT.md')
    migration_doc = os.path.join(docs_dir, 'MIGRATION_GUIDE.md')
    
    assert os.path.exists(oracle_doc), "ORACLE_DEPLOYMENT.md not found"
    assert os.path.exists(migration_doc), "MIGRATION_GUIDE.md not found"
    
    print("✓ Documentation files exist")


def test_dockerfile_dashboard_exists():
    """Test that Dockerfile.dashboard exists."""
    dockerfile_path = os.path.join(PROJECT_ROOT, 'Dockerfile.dashboard')
    assert os.path.exists(dockerfile_path), "Dockerfile.dashboard not found"
    print("✓ Dockerfile.dashboard exists")


def test_dockerignore_exists():
    """Test that .dockerignore exists."""
    dockerignore_path = os.path.join(PROJECT_ROOT, '.dockerignore')
    assert os.path.exists(dockerignore_path), ".dockerignore not found"
    print("✓ .dockerignore exists")


if __name__ == "__main__":
    print("Testing Oracle Cloud deployment configuration...\n")
    
    tests = [
        test_env_example_exists,
        test_docker_compose_oracle_exists,
        test_oracle_config_exists,
        test_collection_service_exists,
        test_deployment_scripts_exist,
        test_documentation_exists,
        test_dockerfile_dashboard_exists,
        test_dockerignore_exists,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__}: Unexpected error: {e}")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"Tests passed: {passed}/{len(tests)}")
    print(f"Tests failed: {failed}/{len(tests)}")
    print(f"{'='*60}")
    
    sys.exit(0 if failed == 0 else 1)
