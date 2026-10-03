import json
import os
import sys


def validate_traceability(json_path: str, repo_root: str) -> bool:
    print(f"Validating traceability artifact at {json_path}")

    if not os.path.exists(json_path):
        print(f"ERROR: Traceability JSON not found at {json_path}")
        return False

    with open(json_path) as f:
        try:
            records = json.load(f)
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON format: {e}")
            return False

    valid = True
    seen_ids = set()

    for record in records:
        req_id = record.get("id")
        if not req_id:
            print("ERROR: Record missing 'id'")
            valid = False
            continue

        if req_id in seen_ids:
            print(f"ERROR: Duplicate requirement ID: {req_id}")
            valid = False

        seen_ids.add(req_id)

        # Check required fields
        required_fields = ["type", "title", "description", "acceptance_criteria", "components", "implementation_refs", "test_refs", "status"]
        for field in required_fields:
            if field not in record:
                print(f"ERROR: Requirement {req_id} missing required field '{field}'")
                valid = False

        # Check that file references actually exist in the file system
        for ref_field in ["implementation_refs", "evidence_refs"]:
            for file_path in record.get(ref_field, []):
                full_path = os.path.join(repo_root, file_path)
                if not os.path.exists(full_path):
                    print(f"ERROR: File reference '{file_path}' in {req_id} does not exist.")
                    valid = False

        # Check test_refs (can be files or file.py::Function style)
        for test_ref in record.get("test_refs", []):
            test_file = test_ref.split("::")[0]
            full_path = os.path.join(repo_root, test_file)
            if not os.path.exists(full_path):
                print(f"ERROR: Test reference '{test_file}' in {req_id} does not exist.")
                valid = False

    if valid:
        print(f"SUCCESS: All {len(records)} traceability records validated.")
        return True
    else:
        print("FAILURE: Traceability validation errors detected.")
        return False

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(current_dir, ".."))
    json_path = os.path.join(repo_root, "docs", "traceability", "traceability.json")

    success = validate_traceability(json_path, repo_root)
    if not success:
        sys.exit(1)
    sys.exit(0)
