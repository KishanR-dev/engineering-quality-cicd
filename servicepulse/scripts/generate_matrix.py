import json
import os
import sys


def generate_matrix():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(current_dir, ".."))
    json_path = os.path.join(repo_root, "docs", "traceability", "traceability.json")
    matrix_path = os.path.join(repo_root, "docs", "traceability-matrix.md")

    if not os.path.exists(json_path):
        print(f"Error: Could not find {json_path}")
        sys.exit(1)

    with open(json_path) as f:
        records = json.load(f)

    fr_records = [r for r in records if r.get("type") == "functional"]
    nfr_records = [r for r in records if r.get("type") == "non-functional"]

    with open(matrix_path, "w") as f:
        f.write("# ServicePulse — Traceability Matrix\n")
        f.write("**Projects 1–4 — Engineering Traceability & CI/CD Verification**\n\n")
        f.write(
            "> Automatically generated from canonical `traceability.json` to prevent drift.\n\n"
        )
        f.write("---\n\n")

        f.write("## 1. Functional Requirements (FR)\n\n")
        f.write("| ID | Title | Components | Implementation Refs | Tests | CI/CD |\n")
        f.write("|---|---|---|---|---|---|\n")
        for r in fr_records:
            comps = ", ".join(r.get("components", []))
            impls = "<br>".join([f"`{x}`" for x in r.get("implementation_refs", [])])
            tests = "<br>".join([f"`{x}`" for x in r.get("test_refs", [])])
            cis = ", ".join(r.get("ci_checks", []))
            f.write(f"| **{r['id']}** | {r['title']} | {comps} | {impls} | {tests} | {cis} |\n")

        f.write("\n---\n\n")
        f.write("## 2. Non-Functional Requirements (NFR)\n\n")
        f.write("| ID | Title | Components | Implementation Refs | Tests | CI/CD |\n")
        f.write("|---|---|---|---|---|---|\n")
        for r in nfr_records:
            comps = ", ".join(r.get("components", []))
            impls = "<br>".join([f"`{x}`" for x in r.get("implementation_refs", [])])
            tests = "<br>".join([f"`{x}`" for x in r.get("test_refs", [])])
            cis = ", ".join(r.get("ci_checks", []))
            f.write(f"| **{r['id']}** | {r['title']} | {comps} | {impls} | {tests} | {cis} |\n")

    print(f"Successfully generated {matrix_path}")


if __name__ == "__main__":
    generate_matrix()
