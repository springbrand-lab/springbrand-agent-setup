# SpringBrand Agent Plugin Distribution

This context defines how one SpringBrand integration is packaged and verified across native agent hosts without duplicating its behavior.

## Language

**Canonical Skill**:
The single authoritative `springbrand-resource-discovery` Skill whose instructions all supported hosts package unchanged.
_Avoid_: Host Skill, Skill fork, copied Skill

**Host Adapter**:
The smallest host-native package that connects the Canonical Skill, SpringBrand MCP endpoint, routing policy, and lifecycle metadata to one plugin engine and configuration contract.
_Avoid_: Host implementation, generic plugin wrapper

**Surface**:
A user-facing runtime or UI that requires its own installation and behavior evidence but may share a Host Adapter with another Surface.
_Avoid_: Adapter, when only the UI or launch path differs

**Distribution Mirror**:
A generated, verified copy of canonical assets required only when a host marketplace demands a self-contained package directory.
_Avoid_: Source of truth, maintained copy

**Native Evidence**:
A recorded test performed through the host's own install, authentication, trust, update, and removal lifecycle.
_Avoid_: Schema validation, inferred support
