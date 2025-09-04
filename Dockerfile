FROM tsunami:latest

RUN apt-get update \
 && apt-get install -y nmap python3 python3-pip python3-tk\
 #aggiungi il ping per debug
 && apt-get install -y iputils-ping \
 #
 && rm -rf /var/lib/apt/lists/* \
 && rm -rf /usr/share/doc && rm -rf /usr/share/man \
 && apt-get clean

RUN useradd --home /usr/Orchestrator --uid 1000 orchestrator

RUN mkdir /usr/Orchestrator

RUN chown -R 1000:1000 /usr/Orchestrator

USER orchestrator

COPY requirements.txt /usr/Orchestrator/

RUN python3 -m pip install --upgrade pip \
    && python3 -m pip install --no-cache-dir -r /usr/Orchestrator/requirements.txt 

#USER 1000:1000 

WORKDIR /usr/Orchestrator

COPY . .

ENTRYPOINT ["python3", "src/orchestrator.py"]