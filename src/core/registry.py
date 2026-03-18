# src/core/registry.py
import importlib
import logging
import pkgutil
from pathlib import Path
from typing import Dict

logger = logging.getLogger(__name__)

PARSERS_PKG = "src.parsers"  # new plugin-based parsers package


class ServiceRegistry:
    def __init__(self):
        self.services: Dict[str, object] = {}
        self.intent_to_service: Dict[str, str] = {}

    def autodiscover(self, package_name: str = PARSERS_PKG):
        """Dynamically discover and load service plugins from parsers directory."""
        logger.info("Discovering service plugins in %s", package_name)
        try:
            pkg = importlib.import_module(package_name)
        except Exception as e:
            logger.exception("Failed to import %s: %s", package_name, e)
            return

        package_path = Path(pkg.__file__).parent
        # Look for service folders (each containing parser.py)
        for finder, name, ispkg in pkgutil.iter_modules([str(package_path)]):
            if name.startswith("_") or not ispkg:
                continue  # Skip private modules and non-packages

            # Try to import the parser.py module from each service folder
            parser_module = f"{package_name}.{name}.parser"
            try:
                mod = importlib.import_module(parser_module)
                # each parser module must expose SERVICE_NAME and get_service() factory
                if hasattr(mod, "SERVICE_NAME") and hasattr(mod, "get_service"):
                    svc = mod.get_service()
                    self.services[svc["name"]] = svc
                    # Build intent-to-service mapping
                    for intent in svc["intents"]:
                        self.intent_to_service[intent] = svc["name"]
                    logger.info("Registered service plugin: %s", svc["name"])
                else:
                    logger.debug(
                        "Module %s missing SERVICE_NAME/get_service", parser_module
                    )
            except Exception:  # noqa: F841
                logger.exception("Failed to load plugin %s", parser_module)

        logger.info("Total services registered: %d", len(self.services))

    def get(self, service_name: str):
        return self.services.get(service_name)

    def get_service_for_intent(self, intent: str):
        """Get service that handles the given intent."""
        service_name = self.intent_to_service.get(intent)
        if service_name:
            return self.services.get(service_name)
        return None

    def list_services(self):
        return list(self.services.keys())


# global singleton for convenience
registry = ServiceRegistry()
