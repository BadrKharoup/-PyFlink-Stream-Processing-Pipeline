# PyFlink Stream Processing Pipeline for Kafka to Postgres with Exactly-Once Semantics
This project implements a real-time data processing pipeline using PyFlink that reads messages from a Kafka topic, performs basic processing, and inserts them into a PostgreSQL database, ensuring exactly-once semantics for data integrity.

## Key Features:

Stream Processing: Leverages PyFlink's streaming capabilities to handle continuous data flow from Kafka.
Exactly-Once Semantics: Configures Flink checkpointing and Kafka transactions to guarantee each message is processed and inserted only once, even in case of failures.
Source and Sink Connectors: Utilizes Flink's Kafka and JDBC connectors to seamlessly read from Kafka and write to PostgreSQL.
Customizable Processing: Includes a basic example of data transformation (adding event type based on camera ID) before insertion. This can be easily modified to implement more complex logic.
Modular Design: Employs functions to separate individual steps (consuming, processing, and inserting) for improved code organization and maintainability.

## Potential Applications:
Real-time analytics on data streams, such as monitoring website traffic or analyzing sensor readings.
Building event pipelines for triggering actions based on incoming data, like sending alerts or activating notifications.
Data warehousing for near real-time updates in operational databases.

## Getting Started:

You can easily clone the repository on Github and explore it further.
Feel free to adapt and modify this project to fit your specific needs and integrate it into your own data processing workflows.
