# Use the official Flink image as the base image
FROM flink:latest

# Switch to root user to perform system-level installations
USER root

# Install necessary dependencies
RUN apt-get update -y && \
    apt-get install -y \
        python3 \
        python3-pip \
        python3-dev && \
    rm -rf /var/lib/apt/lists/* && \
    # Symlink python3 to python to ensure compatibility
    ln -s /usr/bin/python3 /usr/bin/python && \
    # Add the 'flink' user to the 'sudo' group and allow sudo without a password
    usermod -aG sudo flink && \
    echo "flink ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# Install PyFlink with the specified version
RUN pip3 install apache-flink\
    # Install additional Python packages
    sqlalchemy psycopg2-binary

# Change ownership of the Flink installation directory to the 'flink' user
RUN chown -R flink:flink /opt/flink

# Switch back to the 'flink' user
USER flink
