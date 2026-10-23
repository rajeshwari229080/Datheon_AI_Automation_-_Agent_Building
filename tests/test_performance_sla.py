import time
import pytest
from app.modules.lead_routing.schemas import LeadIntakeRequest
from app.modules.lead_routing.service import lead_routing_service

def test_lead_routing_sla_latency_benchmark(db_session):
    """
    Benchmark lead routing end-to-end processing latency over multiple iterations.
    SLA Target: Strict sub-10 second (< 10,000ms) completion per intake.
    """
    latencies_ms = []
    iterations = 5

    for i in range(iterations):
        payload = LeadIntakeRequest(
            name=f"Benchmark Lead {i}",
            email=f"perf.benchmark_{i}_{int(time.time()*1000)}@enterprise-scale.io",
            phone=f"+1-555-010-{i:04d}",
            company=f"Performance Benchmark Entity {i}",
            company_size="201-1000",
            budget=50000.0 + (i * 5000),
            business_need="Validating high-throughput sub-10 second qualification SLA for enterprise deployment.",
            consent=True
        )

        start = time.perf_counter()
        res = lead_routing_service.process_lead(db=db_session, payload=payload)
        duration_ms = (time.perf_counter() - start) * 1000

        latencies_ms.append(duration_ms)
        assert res.success is True
        assert res.latency_ms < 10000

    avg_latency = sum(latencies_ms) / len(latencies_ms)
    max_latency = max(latencies_ms)

    print(f"\n[PERFORMANCE BENCHMARK] Iterations: {iterations} | Mean: {avg_latency:.2f}ms | Max: {max_latency:.2f}ms | SLA Target: < 10,000ms")
    assert avg_latency < 10000.0, f"Average latency {avg_latency}ms exceeded 10s SLA target!"
