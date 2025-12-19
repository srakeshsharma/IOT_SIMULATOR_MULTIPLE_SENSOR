# IOT_SIMULATOR_MULTIPLE_SENSOR

This project is a Python-based simulator designed to generate random IoT telemetry data from multiple virtual devices and send it to an Azure Event Hub instance. It enables developers and testers to emulate the data flow of IoT devices, such as temperature and humidity sensors, into the Azure cloud for integration, testing, and demonstration purposes.

## Features

- Simulates multiple IoT device sensors, each sending randomized temperature and humidity readings.
- Sends telemetry data to Azure Event Hub using secure Azure Active Directory authentication (ClientSecretCredential).
- Supports both continuous and finite event transmission modes.
- Easy configuration via environment variables or direct code constants for Azure credentials and Event Hub targets.
- Useful for testing data ingestion, analytics pipelines, and Event Hub integrations in cloud applications.

## Usage

1. Configure your Azure credentials (`TENANT_ID`, `CLIENT_ID`, `CLIENT_SECRET`) and Event Hub details in the script or via environment variables.
2. Install required Python dependencies, including `azure-eventhub` and `azure-identity`.
3. Run the script to start simulating and sending IoT telemetry data to your Azure Event Hub.

---
*For more details, refer to the source code in [`SendIotTelemetry2EventHubPublicVersion.py`](SendIotTelemetry2EventHubPublicVersion.py).*
