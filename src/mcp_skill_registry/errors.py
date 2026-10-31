class MCPRegistryError(Exception):
    pass


class CatalogError(MCPRegistryError):
    pass


class SchemaError(MCPRegistryError):
    pass


class SkillError(MCPRegistryError):
    pass
