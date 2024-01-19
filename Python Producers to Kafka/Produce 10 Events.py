
from confluent_kafka import Producer
import json
from datetime import datetime, timezone
import time
import random

# Kafka broker address
bootstrap_servers = 'broker:29092'
# Kafka topic to produce messages to
topic = 'events'

# Camera IDs
camera_ids = [1000, 1001, 1002]

# Create Producer configuration
conf = {
    'bootstrap.servers': bootstrap_servers,
    'client.id': 'python-producer'
}

# Create a Kafka Producer instance
producer = Producer(conf)

# Function to generate a sample event message
def generate_event():
    event_id = str(int(time.time() * 10))  # Unique event ID based on timestamp in microseconds
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')  # Current UTC time in "YYYY-MM-DD HH:MM:SS" format
    camera_id = random.choice(camera_ids)  # Randomly select a camera ID

    event = {
        'event_id': event_id,
        'timestamp': timestamp,
        'camera_id': camera_id
    }

    return json.dumps(event)

# Function to produce messages to Kafka
def produce_messages():
    try:
        # Produce 10 events
        for _ in range(10):
            event_message = generate_event()
            producer.produce(topic, value=event_message)
            producer.poll(0)  # Handle delivery reports
            time.sleep(random.uniform(0.1, 1))  # Introduce some delay

        producer.flush()  # Wait for any outstanding messages to be delivered

    except Exception as e:
        print(f"Error producing messages: {e}")

if __name__ == '__main__':
    produce_messages()
