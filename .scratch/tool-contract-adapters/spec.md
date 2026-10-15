# Unified Tool Contract Skill migration

**Status:** implementation

The setup repository consumes the Gateway's five Meta Tools. Canonical Skills
only describe the generic discovery, contract, confirmation, execution and
status framework. Tool-specific behavior belongs to the Tool description
returned by `get_tool_schemas`.

