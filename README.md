# Distributed-Load-Testing-System
## Overview

This repository contains the implementation of a Distributed Load Testing System, designed and built as part of the Big Data Project 2023 at PES University. The system coordinates multiple driver nodes to perform highly concurrent, high-throughput load tests on a web server. The communication between nodes is facilitated using Kafka as the messaging service.

## Application Architecture


- The system comprises Orchestrator and Driver nodes, implemented as separate processes.
- Orchestrator and Driver nodes communicate via Kafka using specified topics and message formats.
- The system supports Avalanche and Tsunami testing, with configurable parameters for each test type.
- Metrics reporting and a scalable architecture for running tests with varying numbers of nodes are integral features.

## Solution Approach

### Orchestrator Node (`load-orchestrator.py`)

- Exposes a REST API for controlling and monitoring tests.
- Implements a Runtime controller to handle heartbeats, coordinate between driver nodes, and store metrics.
- Uses Kafka for communication, publishing to topics such as `register`, `test_config`, `trigger`, `metrics`, and `heartbeat`.
- Achieves scalability by supporting a variable number of driver nodes.

### Driver Node (`load-driver.py`)

- Sends requests to the target web server based on Orchestrator's instructions.
- Records statistics for response times (mean, median, min, max) and sends results back to the Orchestrator.
- Implements a communication layer using Kafka, publishing heartbeats and metrics.

### Target HTTP Server (`target-server.py`)

- Provides endpoints `/ping` for testing and `/metrics` for observing request and response counts.
- Serves as the target web server for load testing.

### Client (`load-client.py`)

- Allows users to initiate load tests by providing test type, message count per driver, and optional parameters.
- Sends a POST request to the Orchestrator to start the load test.

## Usage

### Prerequisites

- Python (3.x)
- Kafka (running on `localhost:9092`)
- Flask (for Orchestrator and Target Server)

### Running the System

1. Start Kafka and ensure it's accessible on `localhost:9092`.
2. Run the Orchestrator node:

   ```bash
   python load-orchestrator.py
   ```

3. Run Driver nodes (for example, two nodes):

   ```bash
   python load-driver.py
   ```

4. Run the Target HTTP Server:

   ```bash
   python target-server.py
   ```

5. Optionally, use the Client to start load tests:

   ```bash
   python load-client.py
   ```

## Conclusion

Distributed Load Testing System with Kafka. Orchestrator and Driver nodes, scalable tests. Code files (`load-orchestrator.py`, `load-driver.py`, `load-client.py`, `target-server.py`) and README for easy use.
