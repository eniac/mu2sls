## Evaluation Plan

For each benchmark suite, we find a good enough worker/node number based on the number of services (so that we don't overload the cloudlab machine).

Research Questions:
- What are the overheads of our logging runtime?
- What are the overheads of our transaction implementation?
- What is the improvement using our optimized dictionary implementation?

Microbenchmarks (Backends are dict counters):
- Single backend stateful
- Chain of 3 (backend stateful)
- Tree (frontend transaction, 2 stateful backends)

Applications:
- Media
- Hotel 
- Social (if we have time)

For all benchmarks we measure:
- Latency Distribution under minimal load
- Latency Distribution under OK load (50 or 80% of maximum Throughput)
  + These are actually non-comparable, so we need to have throughput/latency plots.
- Maximum Throughput

Configs (TODO):
  + Logging
  + Transactions

For the microbenchmarks we have the following configurations:
- NOP measurements
  - No logging, no DB accesses
  - This shows the optimal performance that we can get (limits of the infrastructure)
- No logging, no transactions
- No logging, Yes transactions
- Yes logging, No transactions (?)
- Yes logging, Yes Transactions
- Yes logging, Yes transactions, Optimized dictionary

For the applications, we just do:
- (There is no way to have NOP measurements and no transactions that make sense -- the application would simply return broken results)
- No logging
- Yes logging
- Yes logging Optimized dictionary

## Results

### Microbenchmarks

#### Single Stateful

##### Nop:

Executing: -t4 -c16 -d30s -s single-stateless.lua
Rate: 1
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     3.31ms  457.60us   4.69ms   78.95%
Requests/sec:      1.03
Rate: 60
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    21.37ms   21.45ms  83.52ms   62.25%
Requests/sec:     60.22
Rate: 100
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    21.18ms   21.18ms  70.14ms   58.35%
Requests/sec:    100.19
Rate: 140
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    23.18ms   21.57ms  93.12ms   69.90%
Requests/sec:    140.18
Rate: 180
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    29.10ms   21.07ms  87.10ms   61.53%
Requests/sec:    180.06
Rate: 220
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    38.03ms   16.45ms  79.87ms   82.87%
Requests/sec:    219.91
Rate: 260
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    39.72ms   14.40ms  86.02ms   87.37%
Requests/sec:    259.80
Rate: 300
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    39.74ms   14.44ms  51.90ms   87.50%
Requests/sec:    299.78
Rate: 340
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    41.91ms   12.21ms  79.10ms   91.26%
Requests/sec:    339.53
Rate: 380
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency   439.70ms  347.78ms   1.92s    81.72%
Requests/sec:    372.28

##### NO Log, NO Txn, NO CustomDict:

Executing: -t4 -c16 -d30s -s single-stateful.lua
Rate: 1
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     7.75ms    0.99ms  11.43ms   85.00%
Requests/sec:      1.03
Rate: 60
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    26.48ms   21.52ms 106.18ms   64.75%
Requests/sec:     60.22
Rate: 100
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    27.74ms   21.63ms  91.20ms   64.10%
Requests/sec:    100.19
Rate: 140
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    28.63ms   21.11ms  82.43ms   63.90%
Requests/sec:    140.08
Rate: 180
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    31.58ms   21.40ms  87.55ms   49.08%
Requests/sec:    180.00
Rate: 220
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    42.25ms   19.17ms 113.60ms   71.99%
Requests/sec:    219.87
Rate: 260
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    39.27ms   21.05ms  96.26ms   60.73%
Requests/sec:    259.73
Rate: 300
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    97.67ms   35.10ms 220.54ms   68.95%
Requests/sec:    299.07
Rate: 340
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     2.39s   678.30ms   3.62s    57.26%
Requests/sec:    299.81

## YES Logging, NO Txn, NO CustomDict

Executing: -t4 -c16 -d30s -s single-stateful.lua
Rate: 1
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    10.23ms    1.87ms  17.68ms   95.00%
Requests/sec:      1.00
Rate: 60
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    48.68ms   33.37ms 199.94ms   68.25%
Requests/sec:     60.22
Rate: 100
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    65.81ms   42.57ms 296.45ms   66.57%
Requests/sec:    100.03
Rate: 140
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency   199.19ms  219.33ms   1.50s    87.98%
Requests/sec:    139.46
Rate: 180
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     4.61s     2.36s   14.48s    74.92%
Requests/sec:    136.43
Rate: 220

## NO Logging, Yes Txn, NO CustomDict

Executing: -t4 -c16 -d30s -s single-stateful.lua
Rate: 1
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    18.71ms    2.03ms  24.54ms   80.00%
Requests/sec:      1.00
Rate: 60
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    27.42ms   21.88ms 105.79ms   62.50%
Requests/sec:     60.22
Rate: 100
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    27.42ms   21.98ms 107.52ms   61.40%
Requests/sec:    100.19
Rate: 140
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    27.69ms   22.55ms 118.72ms   67.87%
Requests/sec:    140.19
Rate: 180
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    34.25ms   22.83ms 109.31ms   56.18%
Requests/sec:    179.97
Rate: 220
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    44.09ms   21.32ms 118.91ms   70.72%
Requests/sec:    219.83
Rate: 260
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    55.03ms   11.49ms 184.83ms   89.40%
Requests/sec:    259.66
Rate: 300
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency   199.65ms  111.42ms 499.46ms   63.37%
Requests/sec:    297.82
Rate: 340
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     2.54s   736.98ms   4.08s    59.54%
Requests/sec:    297.21
Rate: 380

## Yes Logging, Yes Txn, NO CustomDict

Executing: -t4 -c16 -d30s -s single-stateful.lua
Rate: 1
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    14.97ms    2.50ms  25.41ms   90.00%
Requests/sec:      1.00
Rate: 60
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    32.80ms   25.35ms 164.35ms   71.33%
Requests/sec:     60.22
Rate: 100
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    32.28ms   24.16ms 145.54ms   66.02%
Requests/sec:    100.20
Rate: 140
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    33.99ms   24.34ms 140.29ms   56.18%
Requests/sec:    140.11
Rate: 180
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    42.83ms   27.66ms 168.32ms   64.55%
Requests/sec:    179.98
Rate: 220
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    54.11ms   18.52ms 140.80ms   79.21%
Requests/sec:    219.76
Rate: 260
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    71.43ms   23.58ms 227.97ms   81.33%
Requests/sec:    259.52
Rate: 300
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     1.14s   323.27ms   1.89s    59.80%
Requests/sec:    283.22
Rate: 340


## Conclusions

We should always have double connections than the frontend workers otherwise we don't get good results.

Q: Why does throughput increase in Chain when we add 4 nodes for backend, even though backend with single node can handle 89?
A: It seems to have to do wit hthe fact that I called with less threads (only t2/c4)

Our transactions are not stable: Higher throughput leads to much lower throughput.

There are 3 phases:
- Minimal load, measuring minimum latency
- OK Load, measuring normal behavior latency (should be relatively stable, in the ms range but maybe even 10x from the minimum latency)
- High Load, checking maximum throughput (reqs/sec if we overload)

Stateless (1 worker/1 node):
- Minimum: 3ms
- OK: 40ms
  - throughput: 80req/s
- Max Throughput: 89req/s

Stateful (set) (1 worker/1 node):
- Minimum: 7ms -- 27ms
- OK: 58ms -- 100ms
  - throughput: 80req/s
- Max Throughput: 84req/s

Chain (Stateless, Stateless) (1 worker/1 node per service):
- Minimum: 15ms -- 17ms
- OK: 45ms -- 100ms
  - throughput: 30req/s
- Max Throughput: 39req/s

Chain (Stateless, Stateful (set)) (1 worker/1 node per service):
- Minimum: 18ms -- 20ms
- OK: 50ms -- 102ms
  - throughput: 30req/s
- Max Throughput: 36req/s

Chain (Stateless, Stateless) (1 worker/4 node for backend):
- Minimum: 
- OK: 
  - throughput: 
- Max Throughput: 45req/s

Chain (Stateless, Stateless) (1 worker/2 node for frontend):
- Minimum: 
- OK: 
  - throughput: 
- Max Throughput: 45req/s

Chain (Stateless, Stateless) (1 worker/2 node for frontend/2 node for backend):
- Minimum: 
- OK: 
  - throughput: 
- Max Throughput: 52req/s

Chain (Stateless, Stateless) (1 worker/2 node for frontend/4 node for backend):
- Minimum: 
- OK: 
  - throughput: 
- Max Throughput: 63req/s

Chain (Stateless, Stateless) (1 worker/4 node for frontend):
- Minimum: 
- OK: 
  - throughput: 
- Max Throughput: 54req/s

Chain (Stateless, Stateless) (1 worker/4 node for both):
- Minimum: 
- OK: 
  - throughput: 
- Max Throughput: 72req/s

> Correct

Chain (Stateless, Stateless) (1 worker/4 node for frontend):
- Minimum: 
- OK: 130 -- 630
  - throughput: 90req/s
- Max Throughput: 96req/s

Chain (Stateless, Stateless) (8 worker/1 node per service):
- Minimum: 
- OK: 100 -- 300
  - throughput: 200req/s
- Max Throughput: 220req/s

Chain (Stateless, Stateless) (8 worker/2 node for frontend):
- Minimum: 
- OK: 150 -- 470
  - throughput: 400req/s
- Max Throughput: 425req/s

Chain (Stateless, Stateless) (8 worker/4 node for frontend):
- Minimum: 
- OK: 
  - throughput: 
- Max Throughput: 361req/s


TODO: Find if the bottlenect is the frontend or the backend in chain, and then add stateful backend and see how things differ.

TODO: Did we reach the machine limits with 4 nodes and 8 workers for frontend? Why is it slower than the 8/2?

## Results

All of those are taken on the amd204.utah.cloudlab.us machine that has 16 cores.

Standard minikube cluster 8 CPUs, 18GB ram

## Stateless



### Build with 1 hypercorn worker

- Machine: amd204.utah.cloudlab.us
- Physical Cores: 16
- Minikube:
  - Cores: 8
  - Ram: 18GB
- Container:
  - Hypercorn:
    - Workers: 1
- Knative:
  - min: 1
  - max: 1
- Application: "echo"


> ./wrk2/wrk -t1 -c1 -d30s -R10 http://${LOAD_BALANCER_IP}/set -s service1.lua

Running 30s test @ http://10.107.1.26/set
  1 threads and 1 connections
  Thread calibration: mean lat.: 2.498ms, rate sampling interval: 10ms
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     2.77ms    1.96ms  29.78ms   99.50%
    Req/Sec    10.45     31.34   111.00     89.96%
  301 requests in 30.00s, 49.05KB read
Requests/sec:     10.03
Transfer/sec:      1.64KB

> ./wrk2/wrk -t1 -c1 -d30s -R30 http://${LOAD_BALANCER_IP}/set -s service1.lua

Running 30s test @ http://10.107.1.26/set
  1 threads and 1 connections
  Thread calibration: mean lat.: 1245.224ms, rate sampling interval: 4427ms
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     4.90s     1.41s    7.34s    57.62%
    Req/Sec    22.00      0.00    22.00    100.00%
  680 requests in 30.01s, 111.49KB read
Requests/sec:     22.66
Transfer/sec:      3.72KB

> ./wrk2/wrk -t1 -c1 -d30s -R20 http://${LOAD_BALANCER_IP}/set -s service1.lua

Running 30s test @ http://10.107.1.26/set
  1 threads and 1 connections
  Thread calibration: mean lat.: 13.490ms, rate sampling interval: 88ms
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    44.65ms    1.60ms  50.46ms   80.25%
    Req/Sec    19.33      4.71    22.00     75.77%
  600 requests in 30.01s, 98.21KB read
Requests/sec:     20.00
Transfer/sec:      3.27KB

> ./wrk2/wrk -t1 -c2 -d30s -R30 http://${LOAD_BALANCER_IP}/set -s service1.lua
Running 30s test @ http://10.107.1.26/set
  1 threads and 2 connections
  Thread calibration: mean lat.: 23.440ms, rate sampling interval: 91ms
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    23.46ms   21.18ms  51.17ms   54.59%
    Req/Sec    29.41      4.92    33.00     73.06%
  901 requests in 30.01s, 147.28KB read
Requests/sec:     30.03
Transfer/sec:      4.91KB

> ./wrk2/wrk -t2 -c4 -d30s -R30 http://${LOAD_BALANCER_IP}/set -s service1.lua

Running 30s test @ http://10.107.1.26/set
  2 threads and 4 connections
  Thread calibration: mean lat.: 18.189ms, rate sampling interval: 90ms
  Thread calibration: mean lat.: 24.660ms, rate sampling interval: 92ms
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    23.19ms   21.28ms  67.65ms   66.22%
    Req/Sec    14.52      5.65    22.00     79.45%
  902 requests in 30.00s, 147.43KB read
Requests/sec:     30.06
Transfer/sec:      4.91KB

> ./wrk2/wrk -t2 -c4 -d30s -R30 http://${LOAD_BALANCER_IP}/set -s service1.lua
Running 30s test @ http://10.107.1.26/set
  2 threads and 4 connections
  Thread calibration: mean lat.: 18.189ms, rate sampling interval: 90ms
  Thread calibration: mean lat.: 24.660ms, rate sampling interval: 92ms
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    23.19ms   21.28ms  67.65ms   66.22%
    Req/Sec    14.52      5.65    22.00     79.45%
  902 requests in 30.00s, 147.43KB read
Requests/sec:     30.06
Transfer/sec:      4.91KB

> ./wrk2/wrk -t2 -c4 -d30s -R50 http://${LOAD_BALANCER_IP}/set -s service1.lua

Running 30s test @ http://10.107.1.26/set
  2 threads and 4 connections
  Thread calibration: mean lat.: 24.803ms, rate sampling interval: 93ms
  Thread calibration: mean lat.: 26.253ms, rate sampling interval: 91ms
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    26.08ms   21.54ms  50.94ms   52.10%
    Req/Sec    24.50      6.08    44.00     65.13%
  1502 requests in 30.01s, 245.58KB read
Requests/sec:     50.05
Transfer/sec:      8.18KB

> ./wrk2/wrk -t2 -c4 -d30s -R100 http://${LOAD_BALANCER_IP}/set -s service1.lua

Running 30s test @ http://10.107.1.26/set
  2 threads and 4 connections
  Thread calibration: mean lat.: 519.563ms, rate sampling interval: 1827ms
  Thread calibration: mean lat.: 531.141ms, rate sampling interval: 1855ms
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     2.02s   587.06ms   3.06s    57.68%
    Req/Sec    44.35      0.57    45.00    100.00%
  2699 requests in 30.01s, 442.51KB read
Requests/sec:     89.94
Transfer/sec:     14.75KB

> ./wrk2/wrk -t2 -c4 -d30s -R80 http://${LOAD_BALANCER_IP}/set -s service1.lua

Running 30s test @ http://10.107.1.26/set
  2 threads and 4 connections
  Thread calibration: mean lat.: 44.715ms, rate sampling interval: 94ms
  Thread calibration: mean lat.: 31.588ms, rate sampling interval: 93ms
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    44.92ms    1.64ms  50.85ms   68.94%
    Req/Sec    39.91      5.74    43.00     78.17%
  2400 requests in 30.01s, 393.37KB read
Requests/sec:     79.97
Transfer/sec:     13.11KB


- Machine: amd204.utah.cloudlab.us
- Physical Cores: 16
- Minikube:
  - Cores: 8
  - Ram: 18GB
- Container:
  - Hypercorn:
    - Workers: 1
- Knative:
  - min: 2
- Application: "echo"

> ./wrk2/wrk -t1 -c1 -d60s -R10 http://${LOAD_BALANCER_IP}/set -s service1.lua

Running 1m test @ http://10.107.1.26/set
  1 threads and 1 connections
  Thread calibration: mean lat.: 2.932ms, rate sampling interval: 10ms
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     2.73ms    2.23ms  36.86ms   99.40%
    Req/Sec    10.57     31.66   111.00     89.95%
  601 requests in 1.00m, 97.96KB read
Requests/sec:     10.02
Transfer/sec:      1.63KB

./wrk2/wrk -t1 -c1 -d30s -R30 http://${LOAD_BALANCER_IP}/set -s service1.lua
Running 30s test @ http://10.107.1.26/set
  1 threads and 1 connections
  Thread calibration: mean lat.: 2.438ms, rate sampling interval: 10ms
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     2.54ms    1.00ms  20.46ms   98.50%
    Req/Sec    31.86     48.58   111.00     69.84%
  901 requests in 30.00s, 146.85KB read
Requests/sec:     30.03
Transfer/sec:      4.89KB

> ./wrk2/wrk -t1 -c1 -d30s -R40 http://${LOAD_BALANCER_IP}/set -s service1.lua

Running 30s test @ http://10.107.1.26/set
  1 threads and 1 connections
  Thread calibration: mean lat.: 32.336ms, rate sampling interval: 92ms
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    33.47ms   11.71ms  50.11ms   50.12%
    Req/Sec    39.55      7.19    43.00     89.40%
  1199 requests in 30.01s, 196.01KB read
Requests/sec:     39.96
Transfer/sec:      6.53KB

> ./wrk2/wrk -t1 -c1 -d30s -R50 http://${LOAD_BALANCER_IP}/set -s service1.lua

Running 30s test @ http://10.107.1.26/set
  1 threads and 1 connections
  Thread calibration: mean lat.: 31.642ms, rate sampling interval: 291ms
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     1.22s   549.17ms   2.17s    58.08%
    Req/Sec    44.99      3.36    48.00    100.00%
  1393 requests in 30.01s, 227.53KB read
Requests/sec:     46.43
Transfer/sec:      7.58KB

### Build with 2 hypercorn workers

- Machine: amd204.utah.cloudlab.us
- Physical Cores: 16
- Minikube:
  - Cores: 8
  - Ram: 18GB
- Container:
  - Hypercorn:
    - Workers: 2
- Application: "echo"

> ./wrk2/wrk -t1 -c1 -d20s -R1 --latency http://${LOAD_BALANCER_IP}/set -s service1.lua

 50.000%    3.27ms
 75.000%    3.60ms
 90.000%    4.06ms
 99.000%    4.08ms
 99.900%    4.08ms
 99.990%    4.08ms
 99.999%    4.08ms
100.000%    4.08ms

----------------------------------------------------------
  21 requests in 20.00s, 3.42KB read
Requests/sec:      1.05
Transfer/sec:     175.18B

> ./wrk2/wrk -t1 -c1 -d20s -R10 --latency http://${LOAD_BALANCER_IP}/set -s service1.lua

  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     2.81ms  559.96us   4.24ms   62.63%
    Req/Sec    10.45     31.42   111.00     90.02%
  201 requests in 20.00s, 32.76KB read
Requests/sec:     10.05
Transfer/sec:      1.64KB

> ./wrk2/wrk -t1 -c1 -d20s -R100 http://${LOAD_BALANCER_IP}/set -s service1.lua
Running 20s test @ http://10.107.1.26/set
  1 threads and 1 connections
  Thread calibration: mean lat.: 2771.370ms, rate sampling interval: 9945ms
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     8.28s     1.59s   11.01s    57.78%
    Req/Sec    44.00      0.00    44.00    100.00%
  900 requests in 20.01s, 147.12KB read
Requests/sec:     44.98
Transfer/sec:      7.35KB

> ./wrk2/wrk -t4 -c10 -d20s -R100 http://${LOAD_BALANCER_IP}/set -s service1.lua
Running 20s test @ http://10.107.1.26/set
  4 threads and 10 connections
  Thread calibration: mean lat.: 34.615ms, rate sampling interval: 93ms
  Thread calibration: mean lat.: 30.996ms, rate sampling interval: 91ms
  Thread calibration: mean lat.: 28.256ms, rate sampling interval: 89ms
  Thread calibration: mean lat.: 27.616ms, rate sampling interval: 93ms
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    30.69ms   20.29ms  76.35ms   66.30%
    Req/Sec    24.57      9.21    45.00     78.85%
  2003 requests in 20.01s, 327.75KB read
Requests/sec:    100.10
Transfer/sec:     16.38KB


## Stateful (set)

> ./wrk2/wrk -t1 -c2 -d30s -R1 http://${LOAD_BALANCER_IP}/set -s service1.lua

Running 30s test @ http://10.107.1.26/set
  1 threads and 2 connections
  Thread calibration: mean lat.: 6.581ms, rate sampling interval: 15ms
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    16.93ms   18.41ms  46.62ms   72.22%
    Req/Sec     0.95      9.32   142.00     98.87%
  31 requests in 30.01s, 5.05KB read
Requests/sec:      1.03
Transfer/sec:     172.47B

> ./wrk2/wrk -t1 -c1 -d30s -R1 http://${LOAD_BALANCER_IP}/set -s service1.lua

Running 30s test @ http://10.107.1.26/set
  1 threads and 1 connections
  Thread calibration: mean lat.: 6.248ms, rate sampling interval: 13ms
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     7.07ms    4.83ms  27.98ms   95.00%
    Req/Sec     1.03      8.92    83.00     98.69%
  31 requests in 30.01s, 5.06KB read
Requests/sec:      1.03
Transfer/sec:     172.53B




./wrk2/wrk -t2 -c4 -d30s -R30 http://${LOAD_BALANCER_IP}/set -s service1.lua
Running 30s test @ http://10.107.1.26/set
  2 threads and 4 connections
  Thread calibration: mean lat.: 22.353ms, rate sampling interval: 121ms
  Thread calibration: mean lat.: 26.665ms, rate sampling interval: 135ms
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    23.71ms   21.35ms  71.62ms   78.80%
    Req/Sec    14.43      3.88    25.00     74.12%
  902 requests in 30.01s, 147.58KB read
Requests/sec:     30.06
Transfer/sec:      4.92KB
kallas@node0:~/knproto$ ./wrk2/wrk -t2 -c4 -d30s -R50 http://${LOAD_BALANCER_IP}/set -s service1.lua
Running 30s test @ http://10.107.1.26/set
  2 threads and 4 connections
  Thread calibration: mean lat.: 28.148ms, rate sampling interval: 98ms
  Thread calibration: mean lat.: 27.473ms, rate sampling interval: 104ms
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    28.21ms   20.48ms  80.26ms   54.50%
    Req/Sec    24.60      4.78    30.00    100.00%
  1500 requests in 30.01s, 245.23KB read
Requests/sec:     49.98
Transfer/sec:      8.17KB
kallas@node0:~/knproto$ ./wrk2/wrk -t2 -c4 -d30s -R80 http://${LOAD_BALANCER_IP}/set -s service1.lua
Running 30s test @ http://10.107.1.26/set
  2 threads and 4 connections
  Thread calibration: mean lat.: 49.128ms, rate sampling interval: 117ms
  Thread calibration: mean lat.: 52.445ms, rate sampling interval: 131ms
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    58.77ms   11.11ms  98.94ms   63.85%
    Req/Sec    39.71      5.14    51.00     84.16%
  2398 requests in 30.01s, 393.16KB read
Requests/sec:     79.90
Transfer/sec:     13.10KB
kallas@node0:~/knproto$ ./wrk2/wrk -t2 -c4 -d30s -R100 http://${LOAD_BALANCER_IP}/set -s service1.lua
Running 30s test @ http://10.107.1.26/set
  2 threads and 4 connections
  Thread calibration: mean lat.: 749.812ms, rate sampling interval: 2592ms
  Thread calibration: mean lat.: 736.756ms, rate sampling interval: 2568ms
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     3.00s   992.41ms   4.73s    55.72%
    Req/Sec    41.29      1.03    44.00     92.86%
  2532 requests in 30.01s, 415.13KB read
Requests/sec:     84.37
Transfer/sec:     13.83KB



## Chain (Stateless, Stateless)





## Chain (Stateless, Stateful (set))

./wrk2/wrk -t1 -c1 -d30s -R1 http://${LOAD_BALANCER_IP}/compose -s service1.lua
Running 30s test @ http://10.107.1.26/compose
  1 threads and 1 connections
  Thread calibration: mean lat.: 21.486ms, rate sampling interval: 53ms
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    18.26ms  823.67us  20.34ms   80.00%
    Req/Sec     0.98      4.14    19.00     94.68%
  30 requests in 30.01s, 4.98KB read
Requests/sec:      1.00
Transfer/sec:     169.93B
kallas@node0:~/knproto$ kubectl get pods
NAME                                         READY   STATUS    RESTARTS   AGE
caller-00006-deployment-6cd84d74c4-xq8qc     2/2     Running   0          107s
service1-00008-deployment-65bf64fcf9-rc88g   2/2     Running   0          117s
kallas@node0:~/knproto$ ./wrk2/wrk -t1 -c2 -d30s -R1 http://${LOAD_BALANCER_IP}/compose -s service1.lua
Running 30s test @ http://10.107.1.26/compose
  1 threads and 2 connections
  Thread calibration: mean lat.: 32.574ms, rate sampling interval: 66ms
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    29.71ms    9.50ms  59.10ms   90.00%
    Req/Sec     0.99      5.23    30.00     96.36%
  30 requests in 30.01s, 4.98KB read
Requests/sec:      1.00
Transfer/sec:     169.91B
kallas@node0:~/knproto$ ./wrk2/wrk -t2 -c4 -d30s -R100 http://${LOAD_BALANCER_IP}/compose -s service1.lua
Running 30s test @ http://10.107.1.26/compose
  2 threads and 4 connections
  Thread calibration: mean lat.: 2985.077ms, rate sampling interval: 10936ms
  Thread calibration: mean lat.: 2888.270ms, rate sampling interval: 10608ms
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    12.63s     3.88s   19.12s    54.15%
    Req/Sec    17.50      0.50    18.00    100.00%
  1088 requests in 30.01s, 181.24KB read
Requests/sec:     36.25
Transfer/sec:      6.04KB
kallas@node0:~/knproto$ ./wrk2/wrk -t2 -c4 -d30s -R50 http://${LOAD_BALANCER_IP}/compose -s service1.lua
Running 30s test @ http://10.107.1.26/compose
  2 threads and 4 connections
  Thread calibration: mean lat.: 1014.363ms, rate sampling interval: 3762ms
  Thread calibration: mean lat.: 1029.510ms, rate sampling interval: 4194ms
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     4.83s     1.66s    8.21s    62.22%
    Req/Sec    17.22      1.03    19.00     88.89%
  1097 requests in 30.01s, 182.74KB read
Requests/sec:     36.55
Transfer/sec:      6.09KB

./wrk2/wrk -t2 -c4 -d30s -R30 http://${LOAD_BALANCER_IP}/compose -s service1.lua
Running 30s test @ http://10.107.1.26/compose
  2 threads and 4 connections
  Thread calibration: mean lat.: 48.877ms, rate sampling interval: 111ms
  Thread calibration: mean lat.: 49.822ms, rate sampling interval: 112ms
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    50.54ms    9.52ms 102.78ms   86.17%
    Req/Sec    14.85      6.16    27.00     86.87%
  900 requests in 30.01s, 149.33KB read
Requests/sec:     29.99
Transfer/sec:      4.98KB


## Chain Stateless, Stateless

./wrk2/wrk -t8 -c32 -d30s -R200 http://${LOAD_BALANCER_IP}/compose -s service1.lua
Running 30s test @ http://10.107.1.26/compose
  8 threads and 32 connections
  Thread calibration: mean lat.: 102.533ms, rate sampling interval: 339ms
  Thread calibration: mean lat.: 112.274ms, rate sampling interval: 369ms
  Thread calibration: mean lat.: 93.581ms, rate sampling interval: 328ms                                                                                                                                          Thread calibration: mean lat.: 89.723ms, rate sampling interval: 317ms
  Thread calibration: mean lat.: 85.995ms, rate sampling interval: 316ms
  Thread calibration: mean lat.: 91.281ms, rate sampling interval: 338ms
  Thread calibration: mean lat.: 80.408ms, rate sampling interval: 273ms
  Thread calibration: mean lat.: 66.461ms, rate sampling interval: 218ms
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    92.04ms   51.21ms 297.98ms   64.41%
    Req/Sec    24.55      3.65    36.00     83.88%
  6000 requests in 30.02s, 0.97MB read
Requests/sec:    199.88
Transfer/sec:     33.23KB
kallas@node0:~/knproto$ ./wrk2/wrk -t8 -c32 -d30s -R300 http://${LOAD_BALANCER_IP}/compose -s service1.lua
Running 30s test @ http://10.107.1.26/compose
  8 threads and 32 connections
  Thread calibration: mean lat.: 676.873ms, rate sampling interval: 2381ms
  Thread calibration: mean lat.: 905.355ms, rate sampling interval: 3330ms
  Thread calibration: mean lat.: 771.642ms, rate sampling interval: 2881ms
  Thread calibration: mean lat.: 889.798ms, rate sampling interval: 3018ms
  Thread calibration: mean lat.: 886.384ms, rate sampling interval: 3332ms
  Thread calibration: mean lat.: 683.658ms, rate sampling interval: 2494ms
  Thread calibration: mean lat.: 780.488ms, rate sampling interval: 2822ms
  Thread calibration: mean lat.: 819.797ms, rate sampling interval: 2770ms
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     4.34s     2.06s    9.51s    56.95%
    Req/Sec    24.94      3.19    33.00     83.02%
  6629 requests in 30.02s, 1.08MB read
Requests/sec:    220.80
Transfer/sec:     36.82KB