#!/usr/bin/env python3
"""Integration test for upload job system."""

import requests
import time
import tempfile
from pathlib import Path

BASE_URL = "http://localhost:8000"

def main():
    print("=== Upload Job Integration Test ===\n")

    # Login
    print("1. Authenticating...")
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    response.raise_for_status()
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"✓ Got token: {token[:30]}...\n")

    # Create test directory with files
    print("2. Creating test directory with sample files...")
    test_dir = tempfile.mkdtemp(prefix="upload_test_")
    Path(test_dir).joinpath("file1.txt").write_text("Test file 1")
    Path(test_dir).joinpath("file2.txt").write_text("Test file 2")
    Path(test_dir).joinpath("subdir").mkdir()
    Path(test_dir).joinpath("subdir/file3.txt").write_text("Test file 3")
    print(f"✓ Created {test_dir} with 3 files\n")

    # Get or create project
    print("3. Creating/getting project...")
    projects = requests.get(f"{BASE_URL}/api/projects/", headers=headers).json()
    if projects:
        project_id = projects[0]["id"]
        print(f"✓ Using existing project ID: {project_id}\n")
    else:
        response = requests.post(f"{BASE_URL}/api/projects/", headers=headers, json={
            "project_name": "Test Project",
            "bucket_name": "test-bucket",
            "aws_region": "us-east-1"
        })
        response.raise_for_status()
        project_id = response.json()["id"]
        print(f"✓ Created project ID: {project_id}\n")

    # Create cycle
    print("4. Creating cycle...")
    response = requests.post(f"{BASE_URL}/api/cycles/", headers=headers, json={
        "project_id": project_id,
        "cycle_name": "Test Cycle",
        "cycle_number": 99,
        "s3_prefix": "test/",
        "status": "pending"
    })
    if response.status_code == 400 and "already exists" in response.text:
        # Get existing cycle
        cycles = requests.get(f"{BASE_URL}/api/cycles/?project_id={project_id}", headers=headers).json()
        cycle_id = cycles[0]["id"] if cycles else None
        print(f"✓ Using existing cycle ID: {cycle_id}\n")
    else:
        response.raise_for_status()
        cycle_id = response.json()["id"]
        print(f"✓ Created cycle ID: {cycle_id}\n")

    # Create session
    print("5. Creating sync session...")
    response = requests.post(f"{BASE_URL}/api/sessions/", headers=headers, json={
        "project_id": project_id,
        "cycle_id": cycle_id,
        "local_directory": test_dir,
        "s3_prefix": "test/batch1/",
        "aws_profile": "default",
        "max_workers": 5,
        "times_to_retry": 2
    })
    response.raise_for_status()
    session_data = response.json()
    session_id = session_data["id"]
    print(f"✓ Created session ID: {session_id}")
    print(f"  Status: {session_data['status']}\n")

    # Start upload job
    print("6. Starting upload job...")
    response = requests.post(f"{BASE_URL}/api/uploads/start", headers=headers, json={
        "session_id": session_id
    })
    response.raise_for_status()
    job_data = response.json()
    job_id = job_data["job_id"]
    print(f"✓ Started job ID: {job_id}")
    print(f"  Status: {job_data['status']}")
    print(f"  Message: {job_data['message']}\n")

    # Monitor job progress
    print("7. Monitoring job progress...")
    for i in range(10):
        time.sleep(1)

        # Check job status
        response = requests.get(f"{BASE_URL}/api/uploads/status/{job_id}", headers=headers)
        job_status = response.json()

        # Check session status
        response = requests.get(f"{BASE_URL}/api/sessions/{session_id}", headers=headers)
        session_status = response.json()

        print(f"  [{i+1}s] Job: {job_status['status']}, Session: {session_status['status']}, "
              f"Files: {session_status['files_uploaded']}/{session_status['total_files']}")

        if job_status['status'] in ['finished', 'failed']:
            break

    print()

    # Final status
    print("8. Final results:")
    response = requests.get(f"{BASE_URL}/api/sessions/{session_id}", headers=headers)
    final_session = response.json()

    print(f"  Session Status: {final_session['status']}")
    print(f"  Total Files: {final_session['total_files']}")
    print(f"  Files Uploaded: {final_session['files_uploaded']}")
    print(f"  Files Failed: {final_session['files_failed']}")
    print(f"  Total Size: {final_session['total_size_bytes']} bytes")

    if job_status['status'] == 'finished':
        print(f"\n✅ Upload job completed successfully!")
        result = job_status.get('result')
        if result:
            print(f"  Result: {result}")
    else:
        print(f"\n❌ Upload job failed")
        print(f"  Error: {job_status.get('error')}")

    # Cleanup
    print(f"\n9. Cleaning up test directory: {test_dir}")
    import shutil
    shutil.rmtree(test_dir)
    print("✓ Cleanup complete\n")

    print("=== Test Complete ===")

if __name__ == "__main__":
    main()
