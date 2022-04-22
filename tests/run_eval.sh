#!/bin/bash

## Workers 4 always
duration=30s ## For testing
duration=60s ## (OR more) for final experiment

scale=2
python3 test_services.py single-stateless.csv knative --docker_io_username konstantinoskallas
kn service update echobackend --scale-min ${scale} --scale-max ${scale} --annotation "autoscaling.knative.dev/target=500"

## Minimum Latency
./wrk2/wrk -t1 -c1 -d30s -R1 http://${LOAD_BALANCER_IP}/req -s single-stateless.lua

## Max throughput
./wrk2/wrk -t4 -c16 -d30s -R400 http://${LOAD_BALANCER_IP}/req -s single-stateless.lua

## OK Latency:
./wrk2/wrk -t4 -c16 -d30s -R300 http://${LOAD_BALANCER_IP}/req -s single-stateless.lua

## Minimum: 3.5ms
## Max Throughput: 370rps
## OK Latency: 42ms -- 80ms

 
# Running 30s test @ http://10.107.1.26/req
#   1 threads and 1 connections
#   Thread calibration: mean lat.: 4.446ms, rate sampling interval: 10ms
#   Thread Stats   Avg      Stdev     Max   +/- Stdev
#     Latency     3.31ms  457.60us   4.69ms   78.95%
#     Req/Sec     1.00     10.15   111.00     99.04%
#   31 requests in 30.00s, 5.05KB read
# Requests/sec:      1.03
# Transfer/sec:     172.42B

# Running 30s test @ http://10.107.1.26/req
#   4 threads and 16 connections
#   Thread calibration: mean lat.: 361.197ms, rate sampling interval: 1654ms
#   Thread calibration: mean lat.: 350.308ms, rate sampling interval: 1391ms
#   Thread calibration: mean lat.: 485.407ms, rate sampling interval: 1696ms
#   Thread calibration: mean lat.: 368.363ms, rate sampling interval: 1449ms
#   Thread Stats   Avg      Stdev     Max   +/- Stdev
#     Latency     1.37s   648.22ms   2.69s    63.71%
#     Req/Sec    93.12      2.38    99.00     86.00%
#   11199 requests in 30.02s, 1.79MB read
# Requests/sec:    373.02
# Transfer/sec:     61.13KB

# Running 30s test @ http://10.107.1.26/req
#   4 threads and 16 connections
#   Thread calibration: mean lat.: 45.291ms, rate sampling interval: 97ms
#   Thread calibration: mean lat.: 44.927ms, rate sampling interval: 96ms
#   Thread calibration: mean lat.: 34.346ms, rate sampling interval: 96ms
#   Thread calibration: mean lat.: 34.583ms, rate sampling interval: 96ms
#   Thread Stats   Avg      Stdev     Max   +/- Stdev
#     Latency    42.57ms   10.92ms  80.38ms   93.46%
#     Req/Sec    74.97      9.55    93.00     77.08%
#   8994 requests in 30.02s, 1.44MB read
# Requests/sec:    299.59
# Transfer/sec:     49.10KB

scale=2
python3 test_services.py single-stateful.csv knative --docker_io_username konstantinoskallas
kn service update backend --scale-min ${scale} --scale-max ${scale} --annotation "autoscaling.knative.dev/target=500"

## Minimum Latency
./wrk2/wrk -t1 -c1 -d30s -R1 http://${LOAD_BALANCER_IP}/req -s single-stateful.lua

## Max throughput
./wrk2/wrk -t4 -c16 -d30s -R320 http://${LOAD_BALANCER_IP}/req -s single-stateful.lua

## OK Latency:
./wrk2/wrk -t4 -c16 -d30s -R220 http://${LOAD_BALANCER_IP}/req -s single-stateful.lua

## No logging, No transactions, naive dictionary

## Minimum: 8ms
## Max Throughput: 260rps
## OK Latency: 33ms - 75ms

# ./wrk2/wrk -t1 -c1 -d30s -R1 http://${LOAD_BALANCER_IP}/req -s single-stateful.lua
# Running 30s test @ http://10.107.1.26/req
#   1 threads and 1 connections
#   Thread calibration: mean lat.: 8.027ms, rate sampling interval: 18ms
#   Thread Stats   Avg      Stdev     Max   +/- Stdev
#     Latency     7.87ms    1.50ms  13.74ms   85.00%
#     Req/Sec     1.02      7.49    58.00     98.19%
#   31 requests in 30.01s, 5.00KB read
# Requests/sec:      1.03
# Transfer/sec:     170.49B

# ./wrk2/wrk -t4 -c16 -d30s -R280 http://${LOAD_BALANCER_IP}/req -s single-stateful.lua
# Running 30s test @ http://10.107.1.26/req
#   4 threads and 16 connections
#   Thread calibration: mean lat.: 51.718ms, rate sampling interval: 117ms
#   Thread calibration: mean lat.: 50.139ms, rate sampling interval: 116ms
#   Thread calibration: mean lat.: 48.275ms, rate sampling interval: 115ms
#   Thread calibration: mean lat.: 43.659ms, rate sampling interval: 115ms
#   Thread Stats   Avg      Stdev     Max   +/- Stdev
#     Latency   834.83ms  974.38ms   2.58s    66.37%
#     Req/Sec    63.35     19.44   104.00     76.31%
#   7888 requests in 30.01s, 1.25MB read
# Requests/sec:    262.88
# Transfer/sec:     42.61KB

# ./wrk2/wrk -t4 -c16 -d30s -R200 http://${LOAD_BALANCER_IP}/req -s single-stateful.lua
# Running 30s test @ http://10.107.1.26/req
#   4 threads and 16 connections
#   Thread calibration: mean lat.: 34.573ms, rate sampling interval: 115ms
#   Thread calibration: mean lat.: 32.660ms, rate sampling interval: 113ms
#   Thread calibration: mean lat.: 32.664ms, rate sampling interval: 112ms
#   Thread calibration: mean lat.: 32.188ms, rate sampling interval: 110ms
#   Thread Stats   Avg      Stdev     Max   +/- Stdev
#     Latency    33.15ms   21.45ms  75.14ms   49.48%
#     Req/Sec    49.83      7.17    70.00     80.65%
#   6002 requests in 30.02s, 0.95MB read
# Requests/sec:    199.94
# Transfer/sec:     32.36KB

## Yes logging, No transactions, naive dictionary

## Minimum: 9.5ms
## Max Throughput: 130rps
## OK Latency: 60 -- 277ms

# ./wrk2/wrk -t1 -c1 -d30s -R1 http://${LOAD_BALANCER_IP}/req -s single-stateful.lua
# Running 30s test @ http://10.107.1.26/req
#   1 threads and 1 connections
#   Thread calibration: mean lat.: 11.235ms, rate sampling interval: 23ms
#   Thread Stats   Avg      Stdev     Max   +/- Stdev
#     Latency     9.55ms  651.71us  11.40ms   75.00%
#     Req/Sec     1.01      6.58    45.00     97.69%
#   30 requests in 30.01s, 4.84KB read
# Requests/sec:      1.00
# Transfer/sec:     165.03B

# ./wrk2/wrk -t4 -c16 -d30s -R180 http://${LOAD_BALANCER_IP}/req -s single-stateful.lua
# Running 30s test @ http://10.107.1.26/req
#   4 threads and 16 connections
#   Thread calibration: mean lat.: 505.445ms, rate sampling interval: 3176ms
#   Thread calibration: mean lat.: 385.541ms, rate sampling interval: 1569ms
#   Thread calibration: mean lat.: 938.021ms, rate sampling interval: 4653ms
#   Thread calibration: mean lat.: 1028.861ms, rate sampling interval: 3205ms
#   Thread Stats   Avg      Stdev     Max   +/- Stdev
#     Latency     2.66s     1.34s   10.04s    71.88%
#     Req/Sec    30.86     12.30    42.00     82.14%
#   3990 requests in 30.02s, 648.67KB read
#   Socket errors: connect 0, read 0, write 0, timeout 2
# Requests/sec:    132.89
# Transfer/sec:     21.60KB

# ./wrk2/wrk -t4 -c16 -d30s -R90 http://${LOAD_BALANCER_IP}/req -s single-stateful.lua
# Running 30s test @ http://10.107.1.26/req
#   4 threads and 16 connections
#   Thread calibration: mean lat.: 64.570ms, rate sampling interval: 237ms
#   Thread calibration: mean lat.: 56.627ms, rate sampling interval: 207ms
#   Thread calibration: mean lat.: 68.307ms, rate sampling interval: 249ms
#   Thread calibration: mean lat.: 61.206ms, rate sampling interval: 218ms
#   Thread Stats   Avg      Stdev     Max   +/- Stdev
#     Latency    62.68ms   38.25ms 277.25ms   64.52%
#     Req/Sec    22.17      4.79    33.00     69.80%
#   2704 requests in 30.02s, 440.50KB read
# Requests/sec:     90.07
# Transfer/sec:     14.67KB

## No logging, Yes transactions, naive dictionary

## Minimum: 12ms
## Max Throughput: 130rps
## OK Latency: 60 -- 277ms


## Custom Dictionary

## TODO: This result looks too good to be true?
##       It is with the custom dictionary
## Minimum: 10ms
## Max Throughput: 290rps
## OK Latency: 57ms - 98ms


# Running 30s test @ http://10.107.1.26/req
#   1 threads and 1 connections
#   Thread calibration: mean lat.: 11.361ms, rate sampling interval: 26ms
#   Thread Stats   Avg      Stdev     Max   +/- Stdev
#     Latency    10.10ms  728.40us  11.42ms   60.00%
#     Req/Sec     1.02      6.23    40.00     97.39%
#   30 requests in 30.01s, 4.84KB read
# Requests/sec:      1.00
# Transfer/sec:     165.03B

# Running 30s test @ http://10.107.1.26/req
#   4 threads and 16 connections
#   Thread calibration: mean lat.: 484.143ms, rate sampling interval: 1762ms
#   Thread calibration: mean lat.: 451.171ms, rate sampling interval: 1648ms
#   Thread calibration: mean lat.: 413.629ms, rate sampling interval: 1564ms
#   Thread calibration: mean lat.: 479.690ms, rate sampling interval: 1705ms
#   Thread Stats   Avg      Stdev     Max   +/- Stdev
#     Latency     1.88s   550.49ms   2.97s    58.37%
#     Req/Sec    71.89      0.89    74.00     91.30%
#   8703 requests in 30.02s, 1.39MB read
#   Non-2xx or 3xx responses: 12
# Requests/sec:    289.94
# Transfer/sec:     47.34KB

# Running 30s test @ http://10.107.1.26/req
#   4 threads and 16 connections
#   Thread calibration: mean lat.: 57.022ms, rate sampling interval: 149ms
#   Thread calibration: mean lat.: 49.900ms, rate sampling interval: 148ms
#   Thread calibration: mean lat.: 56.793ms, rate sampling interval: 149ms
#   Thread calibration: mean lat.: 46.223ms, rate sampling interval: 143ms
#   Thread Stats   Avg      Stdev     Max   +/- Stdev
#     Latency    57.78ms   15.00ms  98.94ms   81.94%
#     Req/Sec    54.72      4.71    73.00     79.85%
#   6597 requests in 30.02s, 1.05MB read
#   Non-2xx or 3xx responses: 5
# Requests/sec:    219.79
# Transfer/sec:     35.89KB

## Naive Dictionary

## TODO: This result looks too good to be true?
##       It is with the custom dictionary
## Minimum: 18ms
## Max Throughput: 200rps
## OK Latency: 36 - 120ms

#./wrk2/wrk -t1 -c1 -d30s -R1 http://${LOAD_BALANCER_IP}/req -s single-stateful.lua

# Running 30s test @ http://10.107.1.26/req
#   1 threads and 1 connections
#   Thread calibration: mean lat.: 18.100ms, rate sampling interval: 41ms
#   Thread Stats   Avg      Stdev     Max   +/- Stdev
#     Latency    18.50ms    2.06ms  24.78ms   75.00%
#     Req/Sec     1.01      4.87    25.00     95.89%
#   30 requests in 30.01s, 4.86KB read
# Requests/sec:      1.00
# Transfer/sec:     165.96B

# ./wrk2/wrk -t4 -c16 -d30s -R200 http://${LOAD_BALANCER_IP}/req -s single-stateful.lua
# Running 30s test @ http://10.107.1.26/req
#   4 threads and 16 connections
#   Thread calibration: mean lat.: 201.160ms, rate sampling interval: 1711ms
#   Thread calibration: mean lat.: 184.601ms, rate sampling interval: 1257ms
#   Thread calibration: mean lat.: 188.783ms, rate sampling interval: 1207ms
#   Thread calibration: mean lat.: 195.458ms, rate sampling interval: 1378ms
#   Thread Stats   Avg      Stdev     Max   +/- Stdev
#     Latency     3.70s     1.21s    6.70s    61.33%
#     Req/Sec    42.27     23.39    74.00     62.50%
#   5106 requests in 30.00s, 853.66KB read
# Requests/sec:    170.18
# Transfer/sec:     28.45KB

# ./wrk2/wrk -t4 -c16 -d30s -R170 http://${LOAD_BALANCER_IP}/req -s single-stateful.lua
# Running 30s test @ http://10.107.1.26/req
#   4 threads and 16 connections
#   Thread calibration: mean lat.: 41.774ms, rate sampling interval: 128ms
#   Thread calibration: mean lat.: 36.182ms, rate sampling interval: 123ms
#   Thread calibration: mean lat.: 33.793ms, rate sampling interval: 126ms
#   Thread calibration: mean lat.: 31.613ms, rate sampling interval: 120ms
#   Thread Stats   Avg      Stdev     Max   +/- Stdev
#     Latency    36.93ms   23.95ms 115.71ms   57.91%
#     Req/Sec    42.20      7.69    65.00     68.54%
#   5104 requests in 30.02s, 850.98KB read
# Requests/sec:    170.01
# Transfer/sec:     28.34KB