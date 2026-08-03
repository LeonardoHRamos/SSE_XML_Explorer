# SSE XML Explorer

> Industrial XML extraction and inspection tool for manufacturing environments.

Desktop application developed in **Python** to locate, read and extract information from XML files stored on remote workstations.

The project provides a contingency workflow for environments where centralized traceability services may be temporarily unavailable. Instead of depending exclusively on a central server, the application searches XML files directly on authorized network workstations, processes their contents and presents the relevant information through a desktop interface.

> The public version uses fictional stations, reserved IP addresses and synthetic XML data for demonstration purposes.

---

## Overview

SSE XML Explorer allows support analysts and engineers to retrieve XML data by selecting a workstation and entering a KNR identifier.

The application connects to the configured network share, locates the corresponding file, parses the XML and displays the extracted information. Successful queries can also be stored in a local history for quick reference.

---

## Interface

### Main Application

![Main application](images/app.jpg)

---

### Search

![Search form](images/search.jpg)

---

### Search Result

![Search result and history](images/search-result-demo.jpg)

---

### XML Inspection

![XML viewer](images/xml-viewer.jpg)

---

## Features

- XML search by KNR
- Workstation selection and filtering
- Automatic IP lookup
- Access to authorized Windows network shares
- Recursive XML file search
- XML parsing with namespace support
- Extraction of station, operator, sequence and timestamp
- Local query history
- Integration with the system XML viewer
- Background processing to keep the interface responsive
- Environment-based configuration
- Structured logging without sensitive information
- Custom error handling

---

## Architecture

```text
User
  │
  ▼
Desktop Interface
  │
  ├── Workstation selection
  ├── KNR validation
  └── Query history
  │
  ▼
Network Reader
  │
  ├── Network authentication
  ├── Remote share access
  └── Recursive file search
  │
  ▼
XML Parser
  │
  ├── Namespace handling
  ├── Data extraction
  └── Result normalization
  │
  ▼
Application Result
  │
  ├── Station
  ├── Operator
  ├── Sequence
  ├── Timestamp
  └── XML file
```

The graphical interface, network access and XML parsing responsibilities are separated into independent modules, reducing coupling and making the application easier to maintain.

---

## Technology Stack

- Python
- Tkinter
- ElementTree
- XML
- JSON
- python-dotenv
- Threading
- Windows Network Shares
- Structured logging

---

## Project Structure

```text
SSE_XML_Explorer/
├── config/
│   └── stations.example.json
├── images/
│   ├── app.jpg
│   ├── search.jpg
│   ├── search-result-demo.jpg
│   └── xml-viewer.jpg
├── utils/
│   ├── __init__.py
│   └── errors.py
├── .env.example
├── .gitignore
├── app.py
├── logger.py
├── network_reader.py
├── requirements.txt
├── xml_parser.py
└── README.md
```

---

## How It Works

1. The user selects a configured workstation.
2. The application retrieves the corresponding IP address.
3. The user enters an eight-digit KNR.
4. A background thread starts the query.
5. The application authenticates to the authorized network share.
6. The configured directories are searched recursively.
7. The matching XML file is located.
8. Relevant information is extracted and normalized.
9. The result is displayed in the interface.
10. The successful query is added to the local history.

---

## Installation

Clone the repository:

```bash
git clone https://github.com/LeonardoHRamos/SSE_XML_Explorer.git
```

Enter the project directory:

```bash
cd SSE_XML_Explorer
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

---

## Configuration

Create a local `.env` file from the example:

```powershell
Copy-Item .env.example .env
```

Configure the network variables using only credentials and paths from an environment you are authorized to access.

Example:

```env
NETWORK_USERNAME=example-user
NETWORK_PASSWORD=replace-me
NETWORK_SHARE=d
XML_BASE_PATHS=example/path/xml-data,alternative/path/xml-data
LOG_LEVEL=INFO
```

Never commit the local `.env`.

### Workstations

The repository includes a fictional example:

```text
config/stations.example.json
```

Create a local workstation configuration:

```powershell
Copy-Item config/stations.example.json config/stations.local.json
```

Example:

```json
{
  "STATION_A01": "192.0.2.10",
  "STATION_A02": "192.0.2.11",
  "STATION_B01": "198.51.100.10"
}
```

Files named `*.local.json` are excluded from version control.

---

## Running the Application

Start the interface:

```bash
python app.py
```

Then:

1. Select a workstation.
2. Enter the KNR.
3. Click **Consultar**.
4. Review the extracted information.
5. Use **Abrir XML** to inspect the located file.

---

## Demonstration Data

The screenshots use the following fictional values:

```text
Station: STATION_A01
IP: 192.0.2.10
KNR: 12345678
Sequence: 4321
Operator: DEMO USER 000001
```

The XML shown in the interface was generated specifically for demonstration and does not represent a real vehicle, workstation, operator or manufacturing environment.

---

## Security

The public repository does not contain:

- Production credentials
- Internal IP addresses
- Real workstation names
- Company or plant identifiers
- Real operator information
- Original production XML files
- Network paths from an operational environment
- Logs or query histories containing operational data
- Executables, installers or compiled builds

Sensitive configuration is loaded locally through environment variables and ignored configuration files.

---

## Limitations

- Requires access to an authorized Windows network share.
- Remote paths can differ between environments.
- XML structures may vary between systems and versions.
- Network authentication was designed for Windows environments.
- The public repository cannot reproduce a real remote query without a compatible test environment.
- The project is a contingency and diagnostic tool, not a replacement for a centralized traceability platform.

---

## Roadmap

- [ ] Add automated tests for the complete search workflow
- [ ] Add a dedicated XML preview inside the application
- [ ] Support multiple workstation queries
- [ ] Add optional CSV export
- [ ] Add indexed XML search
- [ ] Improve query performance for large directories
- [ ] Package the application for simplified installation
- [ ] Add a fully isolated demonstration mode

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
