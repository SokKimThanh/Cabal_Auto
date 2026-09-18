from typing import Dict, List, Optional

class ComponentRegistry:
    """
    A centralized in-memory registry acting as the Source of Truth for mappable UI components.
    This allows UI components to auto-register themselves when they are created,
    and provides a lookup list for settings screens (like Icon Manager) to easily
    map icons to these components by name instead of hardcoded IDs.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ComponentRegistry, cls).__new__(cls)
            cls._instance._registry = {}  # Format: { "Display Name": {"mod": str, "comp": str, "id": str} }
        return cls._instance

    def register_component(self, name: str, mod: str, comp: str, element_id: str):
        """
        Register a component into the registry.

        Args:
            name: The human-readable name of the component (e.g., "Sidebar: Class Manager").
                  This acts as the unique display key in dropdowns.
            mod: The module the component belongs to (e.g., "ui").
            comp: The type of component (e.g., "sidebar_button", "button").
            element_id: The unique ID string representing the element.
        """
        if not name:
            return

        self._registry[name] = {
            "mod": mod,
            "comp": comp,
            "id": element_id
        }

    def get_all_components(self) -> Dict[str, Dict[str, str]]:
        """
        Returns a dictionary of all registered components.
        Format: { "Name": {"mod": "...", "comp": "...", "id": "..."} }
        """
        return dict(self._registry)

    def get_component_names(self) -> List[str]:
        """Returns a sorted list of registered component names."""
        return sorted(list(self._registry.keys()))

    def get_component(self, name: str) -> Optional[Dict[str, str]]:
        """Retrieve component details by its registered name."""
        return self._registry.get(name)

    def clear(self):
        """Clear the registry (mainly for testing purposes)."""
        self._registry.clear()

# Global instance accessor
def get_component_registry() -> ComponentRegistry:
    return ComponentRegistry()
