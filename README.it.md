# Documentazione dell'Orchestratore Tsunami Security Scanner

To read the Italian version of this documentation, click [here](./README.md)

## Introduzione

L'**Orchestratore Tsunami Security Scanner** è uno strumento progettato per automatizzare la scansione di reti e indirizzi IP utilizzando il **Tsunami Security Scanner** di Google. Lo strumento permette di:

* Scansionare singoli indirizzi IP, subnet o liste di indirizzi/subnet.
* Avviare container Docker per eseguire le scansioni.
* Analizzare i risultati delle scansioni tramite un modulo di parsing dei log.

Il programma è suddiviso in due componenti principali:

1. **Orchestratore**: Coordina le scansioni e gestisce l'esecuzione dei container Docker.
2. **Log Parser**: Analizza i risultati delle scansioni e genera report dettagliati.

**Nota**: Il corretto funzionamento di questo programma si basa sull'esecuzione dello strumento **Tsunami Security Scanner**. Maggiori informazioni sono disponibili nel [repository ufficiale del progetto](https://github.com/google/tsunami-security-scanner). Durante l'analisi di alcuni tipi di host o servizi, il tempo di esecuzione del container può essere prolungato (alcuni test hanno registrato fino a 10 minuti). In questi casi, non interrompere il programma, poiché potrebbe trattarsi di una normale fase di elaborazione estesa. Tutti i potenziali errori generati dallo scanner sono gestiti dal programma.

---

## Componenti Principali

### 1. **Orchestratore**

L'orchestratore è il cuore del sistema e si occupa di:

* Validare gli indirizzi IP forniti.
* Identificare gli host attivi tramite `nmap`.
* Avviare container Docker per eseguire le scansioni.
* Coordinare l'intero processo di scansione e parsing.

#### File Principali:

* `orchestrator.py`: Funzione principale che gestisce le scansioni.
* `orch_library.py`: Libreria che contiene tutte le funzioni utilizzate dall'orchestratore.

#### Funzioni Principali:

* `parse_arguments`: Analizza gli argomenti da linea di comando.
* `validate_ip` e `validate_subnet`: Validano la correttezza di indirizzi IP o subnet in formato CIDR.
* `is_ip_active`: Verifica se un IP è attivo tramite `nmap`.
* `remove_duplicates_from_file`: Rimuove le righe duplicate da un file, preservando l'ordine originale.
* `get_positive_integer_input`: Richiede un input numerico positivo all'utente.
* `clear_directories`: Pulisce le directory di output precedentemente utilizzate.
* `scan_single_ip`, `scan_ip_list_manager`, `scan_subnet_and_save_results`, `scan_multiple_subnets_manager`: Gestiscono l'avvio delle scansioni nei vari scenari supportati.
* `start_docker_containers`: Avvia container Docker per una lista di indirizzi IP, con un massimo di \[max\_containers] in esecuzione contemporaneamente.

---

### 2. **Log Parser**

Il log parser analizza i risultati delle scansioni e genera report dettagliati in formato Excel.

#### File Principali:

* `log_parser.py`: Contiene le funzioni di analisi dei log.
* `classes.py`: Contiene le classi utilizzate dal log parser per memorizzare i dati ottenuti da Tsunami Security Scanner.

#### Funzioni Principali:

* `process_all_json_in_directory(input_directory, output_folder)`
* `process_json_based_on_vulnerability(json_path, output_folder)`
* `no_vuln_process`
* `found_vuln_process`
* `process_network_endpoint`, `process_network_services`, `process_no_network_services`
* `append_to_excel`, `append_vuln`
* `adjust_excel_column_width`

---

### 3. **Tsunami Security Scanner**

Lo strumento Tsunami Security Scanner è integrato nel progetto per eseguire scansioni di sicurezza. È configurato tramite Docker e utilizza plugin per rilevare vulnerabilità.

---

## Funzionalità Principali

### 1. **Scansione di Reti e Indirizzi IP**

L'orchestratore supporta vari tipi di scansioni:

* Singolo indirizzo IP
* Lista di indirizzi IP
* Singola subnet (formato CIDR, es. `192.168.1.0/24`)
* Lista di subnet

Le scansioni utilizzano `nmap` per identificare gli host attivi e avviare container Docker per la scansione.

### 2. **Gestione dei Container Docker**

Per ogni host attivo identificato, viene avviato un container Docker per eseguire il **Tsunami Security Scanner**. I risultati vengono salvati in formato JSON nella directory `/Tsunami_Outputs`.

---

## Istruzioni d'Uso

### 1. **Preparazione**

#### Installazione delle Dipendenze

Per visualizzare tutte le dipendenze richieste da questo programma, consulta la sezione dedicata alla fine del file, oppure [clicca qui](#dipendenze).

* Clona il repository:

```bash
git clone --recurse-submodules https://github.com/Amplifon-Organization/Tsunami-Orchestrator.git
```

* Installa Docker:

  * Docker Desktop: [https://docs.docker.com/desktop/](https://docs.docker.com/desktop/)
  * Docker Engine: [https://docs.docker.com/engine/](https://docs.docker.com/engine/)

* Costruisci le immagini Docker:

```bash
docker build -t tsunami:latest ./tsunami-security-scanner
docker build -t orch:latest .
```

**Nota**: In alcune situazioni, durante la fase di build delle immagini Docker, potrebbero comparire errori come:
```bash
E: Unable to locate package nmap
E: Unable to locate package ncrack
```
In tal caso, è consigliato ripetere il comando di build aggiungendo l’opzione `--network=host` come segue:
```bash
docker build --network=host -t tsunami:latest ./tsunami-security-scanner
docker build --network=host -t orch:latest .
```

### 2. **Esecuzione del Programma**

**Nota**: Esegui i comandi dalla directory principale del repository (Tsunami-Orchestrator/).

* **Modalità Interattiva**:

```bash
sudo docker run -it --network="network_name" \
 --rm \
 -v $(pwd)/Parsed_report:/usr/Orchestrator/Parsed_report \
 -v $(pwd)/Tsunami_outputs:/usr/Orchestrator/logs \
 -v $(pwd)/input_files:/usr/Orchestrator/input_files \
 orch:latest
```

* **Con Argomenti Specifici**:

```bash
sudo docker run -it --network="network_name" \
 --rm \
 -v $(pwd)/Parsed_report:/usr/Orchestrator/Parsed_report \
 -v $(pwd)/Tsunami_outputs:/usr/Orchestrator/logs \
 -v $(pwd)/input_files:/usr/Orchestrator/input_files \
 orch:latest [args] [val]
```

* **Opzioni di Aiuto**:

```bash
sudo docker run -it --network="network_name" \
 --rm \
 -v $(pwd)/Parsed_report:/usr/Orchestrator/Parsed_report \
 -v $(pwd)/Tsunami_outputs:/usr/Orchestrator/logs \
 -v $(pwd)/input_files:/usr/Orchestrator/input_files \
 orch:latest -h
```

* **Avvio della GUI**:
  Per utilizzare la GUI, attiva un ambiente virtuale Python (`python3 -m venv`) e installa le dipendenze richieste elencate in `requirements.txt`. Per dettagli, consulta la [documentazione ufficiale di venv](https://docs.python.org/3/library/venv.html).

Poi esegui:

```bash
sudo /percorso/del/venv/bin/python src/GUI/orchestrator_GUI.py
```

### Precisazione Volumes

Quando si esegue il programma tramite Docker, è possibile (e consigliato) montare alcune directory del sistema locale come volumi all’interno del container. Ogni volume ha una funzione specifica:

   * Parsed_Report: directory in cui verranno salvati i risultati finali dell’esecuzione, ovvero il file Excel contenente tutte le informazioni rilevanti raccolte durante la scansione.
   * Tsunami_Outputs (opzionale): directory che conterrà i file JSON grezzi generati dal Tsunami Security Scanner. È utile per conservare i risultati originali delle scansioni, ma il programma funziona correttamente anche senza montare questo volume.
   * Input_Files: directory dove l’utente può inserire i file di input necessari per alcune modalità di esecuzione (ad esempio, scansioni su liste di IP o subnet). Non è sempre obbligatorio montare questo volume, ma è richiesto nei casi in cui siano necessari file di input per la corretta esecuzione del programma.


### 3. **Testing**

#### Test degli Ambienti Vulnerabili

La directory `Vulnerable_env/` contiene ambienti di test configurati con `docker compose`.
Alcune immagini sono prese dal repository [VulHub](https://github.com/vulhub/vulhub); queste devono essere costruite localmente, ma per farlo basta eseguire `./build_images.sh` in `Vuln_env/` per scaricare i dati necessari. Successivamente, esegui il comando `docker compose up` per avviare l'intero ambiente.

**N.B.**: Per comodità, ho creato una rete esterna chiamata **Vuln_net** all'interno del file compose, con indirizzo **192.168.147.0**; questo perché è un indirizzo raramente utilizzato e quindi non dovrebbe interferire con le reti locali esistenti. In caso di problemi, modifica semplicemente l'indirizzo nel file `docker-compose.yaml`.
**Alcuni docker compose sono buildati localmente e non funzionano su architetture Linux Arm64**

Per scansionare la rete vulnerabile:

```bash
sudo docker run -it --network="vuln_net" \
 --rm \
 -v $(pwd)/Parsed_report:/usr/Orchestrator/Parsed_report \
 -v $(pwd)/Tsunami_outputs:/usr/Orchestrator/logs \
 -v $(pwd)/input_files:/usr/Orchestrator/input_files \
 orch:latest -sub 192.168.147.0/24
```

Per forzare l'arresto di tutti i container:

```bash
docker stop $(docker ps -q)
```

#### Test del Log Parser

Esegui `log_parser.py` su una directory contenente file di scansione JSON.

---

## Flusso di Esecuzione

1. **Preparazione**:

   * Le directory di output vengono pulite.
   * Gli input vengono raccolti da CLI o in modo interattivo.

2. **Scansione**:

   * Le scansioni vengono eseguite in base all'input dell'utente.
   * I container Docker vengono avviati per gli host attivi.

3. **Parsing dei Log**:

   * Il modulo `log_parser` analizza i file JSON generati.

4. **Output**:

   * I risultati vengono salvati come file JSON ed Excel.

---

## Requisiti

### Dipendenze

#### Strumenti di Sistema

* **Python 3.x**
  * `python3-pip`
  * `python3-venv`
  * `python3-tk`
* **nmap**
* **ncrack**
* **Docker**

#### Moduli Python

Installa usando:

```bash
pip install -r requirements.txt
```

* numpy
* openpyxl
* rich
* customtkinter

---

## Struttura del Repository

### Directory Principali

* `Tsunami-Orchestrator/`
* `src/`
* `input_files/`
* `Parsed_report/`
* `Tsunami_outputs/`
* `Vulnerable_env/`
* `tsunami-security-scanner/`

---

## Licenza

Questo progetto è rilasciato sotto licenza Apache 2.0. Per dettagli, consulta il file LICENSE.md.