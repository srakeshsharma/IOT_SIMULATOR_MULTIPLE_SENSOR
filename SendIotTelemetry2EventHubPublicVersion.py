## Author- Rakesh Sharma ##

import os
import json
import random
import time
from typing import Dict, Any
from datetime import datetime, timezone

from azure.identity import ClientSecretCredential
from azure.eventhub import EventHubProducerClient, EventData
from azure.eventhub.exceptions import EventHubError



# ---------------------------- Configuration ----------------------------
# Fill these values from your App Registration (Service Principal)
TENANT_ID = "xxxxxxxxxxxxxxxxxxxxx"         
CLIENT_ID = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"          
CLIENT_SECRET = "xxxxxxxxxxxxxxxxxxxxxxxxxxx"  


FULLY_QUALIFIED_NAMESPACE = "rsioteh.servicebus.windows.net"
EVENT_HUB_NAME = "iotehubns"

# Use a stable partition key if you want strict per-device ordering
#PARTITION_KEY = "sensor-01"
PARTITION_KEY = "deviceId"
# Send forever; change to a number for finite sends
SEND_FOREVER = True
TOTAL_EVENTS = 60   # used if SEND_FOREVER = False

# ---------------------------- Helpers ----------------------------
def make_event(i: int) -> EventData:
    """Create one JSON event with dummy telemetry."""
    payload: Dict[str, Any] = {
        "deviceId": f"sensor-{i % 5:02d}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "temperatureC": round(random.uniform(18.0, 38.0), 1),
        "humidityPct": round(random.uniform(25.0, 85.0), 1),
        "location": "BLR-Lab",
        "schema": "iot.temp.v1"
    }
    ed = EventData(json.dumps(payload))
    ed.properties = {
        "contentType": "application/json",
        "source": "python-client",
        "deviceType": "temp-sensor"
    }
    return ed, payload  # return payload so we can log confirmation details

def build_credential() -> ClientSecretCredential:
    """Explicit Entra ID (AAD) credentials."""
    return ClientSecretCredential(
        tenant_id=TENANT_ID,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    )

def create_producer() -> EventHubProducerClient:
    """Create the Event Hubs producer client (no SAS)."""
    return EventHubProducerClient(
        fully_qualified_namespace=FULLY_QUALIFIED_NAMESPACE,
        eventhub_name=EVENT_HUB_NAME,
        credential=build_credential()
    )

# ---------------------------- Main ----------------------------
if __name__ == "__main__":
    # Optional override via environment, while keeping explicit defaults:
    TENANT_ID = os.getenv("AZURE_TENANT_ID", TENANT_ID)
    CLIENT_ID = os.getenv("AZURE_CLIENT_ID", CLIENT_ID)
    CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET", CLIENT_SECRET)

    for (name, value) in [("TENANT_ID", TENANT_ID), ("CLIENT_ID", CLIENT_ID), ("CLIENT_SECRET", CLIENT_SECRET)]:
        if not value or "<YOUR_" in value:
            raise ValueError(
                f"{name} is not set. Populate the constants at the top or provide "
                f"AZURE_TENANT_ID / AZURE_CLIENT_ID / AZURE_CLIENT_SECRET env vars."
            )

    producer = create_producer()

    try:
        with producer:
            i = 0
            while True:
                i += 1
                event, payload = make_event(i)

                # send one event using a small batch to support partition_key
                batch = producer.create_batch(partition_key=PARTITION_KEY)
                try:
                    batch.add(event)
                except ValueError:
                    # Extremely rare for a small event; would indicate the single
                    # event exceeds max batch size
                    raise RuntimeError("Event too large to add even to an empty batch.")

                producer.send_batch(batch)

                # ----- Confirmation message after successful send -----
                print(
                    "✅ Message sent to Event Hub 'iot' "
                    f"(namespace: {FULLY_QUALIFIED_NAMESPACE}) | "
                    f"deviceId={payload['deviceId']}, "
                    f"tempC={payload['temperatureC']}, "
                    f"humidityPct={payload['humidityPct']}, "
                    f"ts={payload['timestamp']}, "
                    f"partitionKey={PARTITION_KEY}"
                )

                # wait 1 second before next message
                time.sleep(1)

                if not SEND_FOREVER and i >= TOTAL_EVENTS:
                    print(f"Completed sending {TOTAL_EVENTS} events.")
                    break

    except EventHubError as eh_err:
        print(f"[EventHubError] {eh_err}")
        print("Troubleshoot: RBAC role (Data Sender), correct namespace/hub, network/firewall, and system clock.")
        raise
    except Exception as ex:
        print(f"[Error] {ex}")