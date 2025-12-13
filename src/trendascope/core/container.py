"""
Dependency injection container.
Manages service lifecycle and dependencies.
"""
from typing import Dict, Any, Optional, Callable
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)


class ServiceContainer:
    """
    Simple service container for dependency injection.
    Supports singleton and factory patterns.
    """
    
    def __init__(self):
        self._singletons: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._instances: Dict[str, Any] = {}
    
    def register_singleton(
        self,
        name: str,
        instance: Any
    ):
        """Register a singleton instance."""
        self._singletons[name] = instance
        logger.debug(f"Registered singleton: {name}")
    
    def register_factory(
        self,
        name: str,
        factory: Callable,
        singleton: bool = False
    ):
        """
        Register a factory function.
        
        Args:
            name: Service name
            factory: Factory function
            singleton: If True, factory result is cached
        """
        self._factories[name] = (factory, singleton)
        logger.debug(f"Registered factory: {name} (singleton={singleton})")
    
    def get(self, name: str) -> Any:
        """
        Get service instance.
        
        Args:
            name: Service name
            
        Returns:
            Service instance
            
        Raises:
            KeyError: If service not found
        """
        # Check singletons first
        if name in self._singletons:
            return self._singletons[name]
        
        # Check factories
        if name in self._factories:
            factory, is_singleton = self._factories[name]
            
            if is_singleton:
                # Cache instance
                if name not in self._instances:
                    self._instances[name] = factory()
                return self._instances[name]
            else:
                # Create new instance each time
                return factory()
        
        raise KeyError(f"Service '{name}' not found")
    
    def has(self, name: str) -> bool:
        """Check if service is registered."""
        return (
            name in self._singletons or
            name in self._factories
        )
    
    def clear(self):
        """Clear all registered services (for testing)."""
        self._singletons.clear()
        self._factories.clear()
        self._instances.clear()


# Global container instance
_container: Optional[ServiceContainer] = None


def get_container() -> ServiceContainer:
    """Get global service container."""
    global _container
    if _container is None:
        _container = ServiceContainer()
    return _container


def reset_container():
    """Reset container (for testing)."""
    global _container
    _container = None

