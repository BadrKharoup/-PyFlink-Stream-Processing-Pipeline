import os
from pyflink.table import EnvironmentSettings, StreamTableEnvironment
from pyflink.common import Types
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import FlinkKafkaConsumer
from pyflink.datastream.formats.json import JsonRowDeserializationSchema

# Function to configure JARs for Flink environment
def configure_jars(tbl_env, jar_files):
    current_dir = os.getcwd()
    jar_urls = [f"file://{current_dir}/{jar}" for jar in jar_files]
    tbl_env.get_config().get_configuration().set_string(
        "pipeline.jars",
        ";".join(jar_urls)
    )

# Function to configure Flink environment settings
def configure_flink_env(tbl_env):
    tbl_env.get_config().get_configuration().set_string(
        "execution.checkpointing.interval",
        "5000"
    )
    
    tbl_env.get_config().get_configuration().set_string(
        "parallelism.default",
        "4"
    )

    # Configure checkpointing
    tbl_env.get_config().get_configuration().set_string(
        "execution.checkpointing.mode",
        "EXACTLY_ONCE"
    )

    # Set the checkpointing directory
    checkpoints_directory = "/opt/flink/jobs/checkpoints"
    os.makedirs(checkpoints_directory, exist_ok=True)
    tbl_env.get_config().get_configuration().set_string(
        "execution.checkpointing.checkpoints-directory",
        checkpoints_directory
    )

# Function to consume Kafka messages
def consume_kafka(tbl_env, kafka_topic, kafka_properties):
    kafka_consumer = FlinkKafkaConsumer(
        kafka_topic,
        deserialization_schema=JsonRowDeserializationSchema.builder()
            .type_info(Types.ROW_NAMED(
                ["event_id", "event_timestamp", "camera_id"],
                [Types.STRING(), Types.SQL_TIMESTAMP(), Types.INT()]
            ))
            .build(),
        properties=kafka_properties
    )

    tbl_env.execute_sql(f"""
        CREATE TABLE KafkaTable (
          event_id STRING,
          event_timestamp TIMESTAMP(3) METADATA FROM 'timestamp',
          camera_id INT
        ) WITH (
          'connector' = 'kafka',
          'topic' = '{kafka_topic}',
          'properties.bootstrap.servers' = '{kafka_properties["bootstrap.servers"]}',
          'properties.group.id' = '{kafka_properties["group.id"]}',
          'format' = 'json'
        )
    """)

    return kafka_consumer

# Function to process and insert into PostgreSQL
def process_and_insert(tbl_env, kafka_table, postgres_properties):
    tbl_env.execute_sql(f"""
        CREATE TABLE ProcessedEvents (
          event_id STRING,
          event_timestamp TIMESTAMP(3),
          camera_id INT,
          event_type STRING
        ) WITH (
          'connector' = 'jdbc',
          'url' = 'jdbc:postgresql://{postgres_properties["url"]}:{postgres_properties["port"]}/{postgres_properties["database"]}',
          'table-name' = '{postgres_properties["table-name"]}',
          'username' = '{postgres_properties["username"]}',
          'password' = '{postgres_properties["password"]}',
          'driver' = '{postgres_properties["driver"]}'
        )
    """)
    
    tbl_env.create_temporary_view("KafkaTableView", tbl_env.from_path("KafkaTable"))

    tbl_env.execute_sql("""
        INSERT INTO ProcessedEvents (event_id, event_timestamp, camera_id, event_type)
        SELECT
          event_id,
          event_timestamp,
          camera_id,
          CASE WHEN camera_id = 1000 THEN 'crossingline' ELSE 'linecount' END as event_type
        FROM KafkaTableView
    """)

if __name__ == '__main__':
    # Configuration parameters...
    bootstrap_servers = 'broker:29092'
    group_id = 'Fazora'
    kafka_topic = 'events'

    kafka_properties = {
        'bootstrap.servers': bootstrap_servers,
        'group.id': group_id,
        'auto.offset.reset': 'latest',
        'enable.auto.commit': 'true'
    }

    postgres_properties = {
        'url': '172.18.0.6',
        'port': '5432',
        'database': 'kafka',
        'table-name': 'event_types',
        'username': 'postgres',
        'password': 'changeme',
        'driver': 'org.postgresql.Driver'
    }

    env_settings = EnvironmentSettings.new_instance().in_streaming_mode().build()
    env = StreamExecutionEnvironment.get_execution_environment()
    tbl_env = StreamTableEnvironment.create(env, environment_settings=env_settings)

    jar_files = [
        "flink-sql-connector-postgres-cdc-2.4.2.jar",
        "postgresql-42.7.1.jar",
        "flink-connector-jdbc-1.16.1.jar",
        "flink-sql-connector-kafka-3.0.2-1.18.jar"
    ]

    # Configure JARs and Flink environment
    configure_jars(tbl_env, jar_files)
    configure_flink_env(tbl_env)

    # Consume Kafka messages
    kafka_consumer = consume_kafka(tbl_env, kafka_topic, kafka_properties)

    # Process and insert into PostgreSQL
    process_and_insert(tbl_env, kafka_consumer, postgres_properties)
