# Supplément - opentelemetry

Pour aller plus loin, voyons un exemple local de télémétrie.

Ajoutons dans notre application flask la dépendance `opentelemetry`, et configurons là pour envoyer les infos à un service dédié, `jaeger`.

La commande `just run-jaeger` permet de lancer un conteneur `jaeger` sur votre machine.

## Mise en place

Installation de `opentelemetry`

```bash
uv add opentelemetry
```

Nous allons avoir besoin de 3 variables pour configurer la télémétrie :

- `OTEL_ENABLED` qui sera un booléen pour activer ou non la télémétrie
- `OTEL_SERVICE_NAME` une string pour définir le nom de notre service dans notre outil de télémétrie
- `OTEL_EXPORTER_OTLP` une string pour définir l'URL sur laquelle envoyer les metrics.

Mettons ces 3 variables dans `.env.example` et aussi dans notre `.env`

Ensuite, pour utiliser ces variables, créons un fichier `telemetry.py` pour la configuration :

```python
import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def is_enabled() -> bool:
    return os.environ.get("OTEL_ENABLED", "false").lower() in ("true", "1", "yes")


def configure_telemetry() -> None:
    if not is_enabled():
        return

    service_name = os.environ.get("OTEL_SERVICE_NAME", "port-scanner")
    endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")

    resource = Resource(attributes={"service.name": service_name})
    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(endpoint=f"{endpoint}/v1/traces")
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
```

Dans les grandes lignes, ce fichier expose 2 fonctions.

Une qui retourne si la télémétrie doit être activée ou non.

Une autre pour configurer la dépendance.

Enfin on termine d'initialiser tout cela en modifiant le `__init.py`.

Nous pouvons désormais lancer l'app :

```bash
just run-dev
```

Puis ouvrir l'interface web de jaeger pour voir le dashboard : <http://localhost:16686>

Dans le menu à gauche, choisir le service `port-scanner` puis cliquer sur `Find Traces`
