# Security policy

Please report suspected vulnerabilities privately to the repository owner; do not open a public issue for a credential leak or a vulnerability that can be exploited.

BackportGuard verifies GitHub's SHA-256 webhook signature before processing, limits webhook bodies to 1 MiB, uses parameterized SQLite queries, deduplicates deliveries, and never executes payload data or repository code.
