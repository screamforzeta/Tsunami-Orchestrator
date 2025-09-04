FROM tsunami:latest

RUN apt-get update \
 && apt-get install -y nmap python3 python3-pip python3-tk \
 #aggiungi il ping per debug
 && apt-get install -y iputils-ping \
 && rm -rf /var/lib/apt/lists/* \
 && rm -rf /usr/share/doc && rm -rf /usr/share/man \
 && apt-get clean

RUN useradd --home /usr/Orchestrator --uid 1001 orchestrator

RUN mkdir /usr/Orchestrator

RUN chown -R 1001:1001 /usr/Orchestrator

#USER orchestrator

RUN python3 -m pip install --break-system-packages uv

COPY requirements.txt /usr/Orchestrator/

RUN uv python install 3.8

WORKDIR /usr/Orchestrator

RUN uv init \
    && uv add -r /usr/Orchestrator/requirements.txt 

#USER 1000:1000 

COPY . .

ENTRYPOINT ["uv", "run", "src/orchestrator.py"]