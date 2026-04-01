import importlib
import inspect
import logging
import pkgutil
from pathlib import Path
from typing import Dict, Optional

from src.core.base_parser import BaseParser

logger = logging.getLogger(__name__)

PARSERS_PKG = "src.parsers"


class ServiceRegistry:
    def __init__(self):
        self.services: Dict[str, object] = {}
        self.intent_to_service: Dict[str, str] = {}

    def _register_service(self, svc: dict, source: str):
        service_name = svc.get("name")
        intents = svc.get("intents", [])
        if not service_name or not intents:
            logger.warning("Skipping invalid plugin from %s", source)
            return

        self.services[service_name] = svc
        for intent in intents:
            self.intent_to_service[intent] = service_name
        logger.info("Registered service plugin: %s (%s)", service_name, source)

    def _load_class_based_service(self, mod, parser_module: str) -> bool:
        for _, cls in inspect.getmembers(mod, inspect.isclass):
            if cls is BaseParser or not issubclass(cls, BaseParser):
                continue
            parser = cls()
            self._register_service(parser.to_service_dict(), parser_module)
            return True
        return False

    def autodiscover(self, package_name: str = PARSERS_PKG):
        """Dynamically discover and load service plugins from parsers directory."""
        logger.info("Discovering service plugins in %s", package_name)
        try:
            pkg = importlib.import_module(package_name)
        except Exception as e:
            logger.exception("Failed to import %s: %s", package_name, e)
            return

        package_path = Path(pkg.__file__).parent
        for _, name, ispkg in pkgutil.iter_modules([str(package_path)]):
            if name.startswith("_") or not ispkg:
                continue

            parser_module = f"{package_name}.{name}.parser"
            try:
                mod = importlib.import_module(parser_module)

                # Preferred: class-based parser that inherits BaseParser.
                if self._load_class_based_service(mod, parser_module):
                    continue

                # Backward compatibility: legacy module contract.
                if hasattr(mod, "SERVICE_NAME") and hasattr(mod, "get_service"):
                    self._register_service(mod.get_service(), f"{parser_module} [legacy]")
                else:
                    logger.debug(
                        "Module %s missing class-based parser and legacy SERVICE_NAME/get_service",
                        parser_module,
                    )
            except Exception:
                logger.exception("Failed to load plugin %s", parser_module)

        logger.info("Total services registered: %d", len(self.services))

    def get(self, service_name: str):
        return self.services.get(service_name)

    def get_service_for_intent(self, intent: str) -> Optional[dict]:
        """Get service that handles the given intent."""
        service_name = self.intent_to_service.get(intent)
        if service_name:
            return self.services.get(service_name)
        return None

    def list_services(self):
        return list(self.services.keys())


registry = ServiceRegistry()
