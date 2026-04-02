# src/core/registry.py
import importlib
import logging
import pkgutil
from pathlib import Path
from typing import Dict

from src.core.base_parser import BaseParser

logger = logging.getLogger(__name__)

PARSERS_PKG = "src.parsers"  # new plugin-based parsers package


class ServiceRegistry:
    def __init__(self):
        self.services: Dict[str, object] = {}
        self.intent_to_service: Dict[str, str] = {}

    def _register_service_dict(self, svc: dict):
        self.services[svc["name"]] = svc
        for intent in svc.get("intents", []):
            self.intent_to_service[intent] = svc["name"]
        logger.info("Registered service plugin: %s", svc["name"])

    def _build_service_dict_from_parser(self, parser: BaseParser) -> dict:
        """Normalize class-based parser plugins into existing service dict schema."""
        return {
            "name": parser.get_service_name(),
            "intents": parser.get_intents(),
            # Backwards-compatible callable interface used by command_generator
            "generate_command": parser.generate_command,
            "validate": parser.validate,
            # New class-based metadata
            "examples": parser.get_examples(),
            "parser": parser,
        }

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
        for _finder, name, ispkg in pkgutil.iter_modules([str(package_path)]):
            if name.startswith("_") or not ispkg:
                continue  # Skip private modules and non-packages

            parser_module = f"{package_name}.{name}.parser"
            try:
                mod = importlib.import_module(parser_module)

                # Preferred class-based plugin API
                if hasattr(mod, "get_parser"):
                    parser = mod.get_parser()
                    if isinstance(parser, BaseParser):
                        self._register_service_dict(
                            self._build_service_dict_from_parser(parser)
                        )
                        continue
                    logger.warning(
                        "Module %s get_parser() did not return BaseParser", parser_module
                    )

                # Legacy function-based plugin API
                if hasattr(mod, "SERVICE_NAME") and hasattr(mod, "get_service"):
                    self._register_service_dict(mod.get_service())
                else:
                    logger.debug(
                        "Module %s missing get_parser() and SERVICE_NAME/get_service",
                        parser_module,
                    )
            except Exception:
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
