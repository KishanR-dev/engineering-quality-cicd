import asyncio
import time

import httpx


async def create_request(client, idx):
    payload = {
        "customer_id": f"CUST-0{idx:03d}",
        "request_type": "SERVICE",
        "description": "Benchmark after transformation",
    }
    try:
        response = await client.post("http://localhost:8000/api/v1/requests", json=payload)
        return response.status_code, response.text
    except Exception as e:
        return 999, str(e)


async def main():
    async with httpx.AsyncClient(timeout=30.0) as client:
        start = time.perf_counter()
        tasks = [create_request(client, i) for i in range(50)]
        results = await asyncio.gather(*tasks)
        duration = time.perf_counter() - start

        success = [r for r in results if r[0] == 201]
        errors = [r for r in results if r[0] != 201]

        print(f"Total time: {duration:.4f}s")
        print(f"Successes: {len(success)}")
        print(f"Failures: {len(errors)}")
        if errors:
            print(f"First 5 errors: {errors[:5]}")

        with open("benchmarks/transformed_results.json", "w") as f:
            import json

            json.dump({"duration": duration, "successes": len(success), "failures": len(errors)}, f)


if __name__ == "__main__":
    asyncio.run(main())
