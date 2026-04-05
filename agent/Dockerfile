FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    stress \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /agent

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY agent.py .

CMD ["python3", "agent.py"]
