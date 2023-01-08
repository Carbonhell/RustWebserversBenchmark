# Constant data

The amount of total requests for all tests is fixed at 20.000 with keepalive always on.

Every result is taken as the best of 3 attempts.

For each table record, the web server process has been killed and started again to prevent possible memory leaks from falsifying the data.

# Results

The benchmark type "Single" refers to requesting a single HTML document without any linked resource.

| Web server | Compression | Single threaded | Concurrency level | Benchmark type | Requests per second | Time per request (mean) | Time per request (mean, across all concurrent requests) | Transfer rate |
|------------|-------------|-----------------|-------------------|----------------|---------------------|-------------------------|---------------------------------------------------------|---------------|
| Actix Web  | ❌           | ❌               | 1                 | Single         |                     |                         |                                                         |               |

