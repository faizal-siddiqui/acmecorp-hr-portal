import asyncio
import time

import httpx

from app.main import app


async def benchmark_endpoint(client, name, url, iterations=50):
    print(f"Benchmarking {name} ({url})...")
    latencies = []

    for _ in range(iterations):
        start_time = time.perf_counter()
        response = await client.get(url)
        end_time = time.perf_counter()

        if response.status_code != 200:
            print(f"  Error: {response.status_code} - {response.text}")
            continue

        latencies.append((end_time - start_time) * 1000)  # ms

    if not latencies:
        return None

    avg = sum(latencies) / len(latencies)
    p95 = sorted(latencies)[int(len(latencies) * 0.95)]
    p99 = sorted(latencies)[int(len(latencies) * 0.99)]
    min_lat = min(latencies)
    max_lat = max(latencies)

    print(f"  Results for {name}:")
    print(f"    Avg: {avg:.2f}ms")
    print(f"    P95: {p95:.2f}ms")
    print(f"    P99: {p99:.2f}ms")
    print(f"    Min: {min_lat:.2f}ms")
    print(f"    Max: {max_lat:.2f}ms")

    return {"name": name, "avg": avg, "p95": p95, "p99": p99, "min": min_lat, "max": max_lat}


async def main():
    # Use AsyncClient with the app directly to avoid needing a running server
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        # 1. Login to get token
        print("Logging in...")
        login_response = await client.post(
            "/auth/login", json={"email": "maya@example.com", "password": "admin123"}
        )

        if login_response.status_code != 200:
            print(f"Login failed: {login_response.text}")
            return

        token = login_response.json()["access_token"]
        client.headers["Authorization"] = f"Bearer {token}"

        # 2. Benchmark /employees/
        employees_res = await benchmark_endpoint(client, "Employees List (Page 1)", "/employees/")

        # 3. Benchmark /analytics/summary
        analytics_res = await benchmark_endpoint(client, "Analytics Summary", "/analytics/summary")

        # 4. Benchmark /employees/ with search
        search_res = await benchmark_endpoint(
            client, "Employees Search (q=John)", "/employees/?q=John"
        )

        # 5. Benchmark /analytics/summary with filter
        analytics_filter_res = await benchmark_endpoint(
            client, "Analytics Summary (country=US)", "/analytics/summary?country=US"
        )

        print("\nSummary Table:")
        print(f"{'Endpoint':<30} | {'Avg (ms)':<10} | {'P95 (ms)':<10}")
        print("-" * 55)
        for res in [employees_res, analytics_res, search_res, analytics_filter_res]:
            if res:
                print(f"{res['name']:<30} | {res['avg']:<10.2f} | {res['p95']:<10.2f}")


if __name__ == "__main__":
    asyncio.run(main())
