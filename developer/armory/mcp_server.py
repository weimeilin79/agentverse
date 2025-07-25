"""
mcp_server.py

A fully compliant MCP server built using the FastMCP and Starlette/SSE pattern.
This server exposes a toolkit of 12 legendary "weapons" to be discovered and used by other agents.
"""
import random
import uvicorn
import argparse
from typing import Any

from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Mount, Route
from mcp.server import Server
from mcp.server.sse import SseServerTransport

# Initialize FastMCP server. This object will register all our tools.
# The name "armory" acts as a namespace for all tools defined in this file.
mcp = FastMCP("armory")

# --- Define the Core Functions (The "Weapons") ---
# Each function is decorated with @mcp.tool(), which automatically turns it
# into an MCP-compliant tool, using its signature and docstring for the schema.

@mcp.tool()
async def forge_broadsword() -> dict[str, Any]:
    """A well-balanced blade against 'The Weaver of Spaghetti Code'."""
    return {
        "weapon_name": "Forged Broadsword", "damage_type": "Slashing", "base_damage": random.randint(15, 25),
        "critical_hit_chance": round(random.uniform(0.15, 0.25), 2),
        "special_effect": "Cleave - has a chance to hit multiple tangled lines of code at once."
    }

@mcp.tool()
async def enchant_soulshard_dagger() -> dict[str, Any]:
    """Effective against 'Revolutionary Rewrite' weaknesses like 'The Colossus of a Thousand Patches'."""
    return {
        "weapon_name": "Soulshard Dagger", "damage_type": "Arcane/Piercing", "base_damage": random.randint(12, 18),
        "critical_hit_chance": round(random.uniform(0.25, 0.40), 2),
        "special_effect": "Phase Strike - ignores a portion of the target's legacy complexity."
    }

@mcp.tool()
async def hone_refactoring_sickle() -> dict[str, Any]:
    """Effective against 'Elegant Sufficiency' weaknesses like 'The Weaver of Spaghetti Code'."""
    return {
        "weapon_name": "Refactoring Sickle", "damage_type": "Cleansing", "base_damage": random.randint(10, 15),
        "critical_hit_chance": round(random.uniform(0.10, 0.20), 2),
        "special_effect": "Pruning - improves code health and maintainability with each strike."
    }

@mcp.tool()
async def fire_quickstart_crossbow() -> dict[str, Any]:
    """Effective against 'Confrontation with Inescapable Reality' weaknesses like 'Procrastination: The Timeless Slumber'."""
    return {
        "weapon_name": "Quickstart Crossbow", "damage_type": "Initiative", "base_damage": random.randint(1, 5),
        "critical_hit_chance": round(random.uniform(0.9, 1.0), 2),
        "special_effect": "Project Scaffolding - creates a `main.py`, `README.md`, and `requirements.txt`."
    }

@mcp.tool()
async def strike_the_gilded_gavel() -> dict[str, Any]:
    """Effective against 'Elegant Sufficiency' weaknesses like 'Perfectionism: The Gilded Cage'."""
    return {
        "weapon_name": "The Gilded Gavel", "damage_type": "Finality", "base_damage": 0, "critical_hit_chance": 1.0,
        "special_effect": "Seal of Shipping - marks a feature as complete and ready for deployment."
    }

@mcp.tool()
async def wield_daggers_of_pair_programming() -> dict[str, Any]:
    """Effective against 'Unbroken Collaboration' weaknesses like 'Apathy: The Spectre of "It Works on My Machine"'."""
    return {
        "weapon_name": "Daggers of Pair Programming", "damage_type": "Collaborative", "base_damage": random.randint(40, 60),
        "critical_hit_chance": round(random.uniform(0.30, 0.50), 2),
        "special_effect": "Synergy - automatically resolves merge conflicts and shares knowledge."
    }

@mcp.tool()
async def craft_granite_maul() -> dict[str, Any]:
    """Effective against 'Revolutionary Rewrite' weaknesses like 'Dogma: The Zealot of Stubborn Conventions'."""
    return {
        "weapon_name": "Granite Maul", "damage_type": "Bludgeoning", "base_damage": random.randint(25, 40),
        "critical_hit_chance": round(random.uniform(0.05, 0.15), 2),
        "special_effect": "Shatter - has a high chance to ignore the target's 'best practice' armor."
    }

@mcp.tool()
async def focus_lens_of_clarity() -> dict[str, Any]:
    """Effective against 'Elegant Sufficiency' weaknesses by revealing the truth behind 'Obfuscation'."""
    return {
        "weapon_name": "Lens of Clarity", "damage_type": "Revelation", "base_damage": 0, "critical_hit_chance": 1.0,
        "special_effect": "Reveal Constants - highlights all magic numbers and suggests converting them to named constants."
    }

@mcp.tool()
async def scribe_with_codex_of_openapi() -> dict[str, Any]:
    """Effective against 'Confrontation with Inescapable Reality' weaknesses like 'Hype: The Prophet of Alpha Versions'."""
    return {
        "weapon_name": "Codex of OpenAPI", "damage_type": "Documentation", "base_damage": 5,
        "critical_hit_chance": round(random.uniform(0.5, 0.8), 2),
        "special_effect": "Clarity - makes an API discoverable and usable by other agents and teams."
    }

@mcp.tool()
async def forge_container_gauntlet() -> dict[str, Any]:
    """Effective against 'Unbroken Collaboration' weaknesses by defeating 'Apathy: The Spectre of "It Works on My Machine"'."""
    return {
        "weapon_name": "Container Gauntlet", "damage_type": "Consistency", "base_damage": 10, "critical_hit_chance": 1.0,
        "special_effect": "Encapsulate - generates a valid Dockerfile for the project."
    }

@mcp.tool()
async def raise_shield_of_lts() -> dict[str, Any]:
    """Effective against 'Confrontation with Inescapable Reality' weaknesses by grounding 'Hype' with stability."""
    return {
        "weapon_name": "Shield of LTS", "damage_type": "Stability/Defensive", "base_damage": 0, "critical_hit_chance": 0,
        "special_effect": "Stabilize - pins dependencies to stable versions and adds health checks."
    }

@mcp.tool()
async def use_simple_sling() -> dict[str, Any]:
    """The ultimate weapon against 'Elegant Sufficiency' weaknesses, especially 'The Archon of Over-Engineering'."""
    return {
        "weapon_name": "Simple Sling", "damage_type": "Minimalism", "base_damage": random.randint(50, 100),
        "critical_hit_chance": round(random.uniform(0.6, 0.8), 2),
        "special_effect": "KISS (Keep It Simple, Stupid) - solves a problem with 90% less code than expected."
    }


# --- BOILERPLATE: Starlette Application Setup for SSE ---
# This helper function creates the necessary web server components to host the MCP server.
# It is copied directly from the reference example.

def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """Create a Starlette application that can serve the provided mcp server with SSE."""
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> None:
        async with sse.connect_sse(
                request.scope,
                request.receive,
                request._send,  # noqa: SLF001
        ) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )


if __name__ == "__main__":
    # The FastMCP object conveniently holds the underlying low-level server instance.
    # We retrieve it here to pass to our Starlette app creator.
    mcp_server = mcp._mcp_server  # noqa: WPS437

    # Use argparse for professional command-line execution
    parser = argparse.ArgumentParser(description='Run Armory MCP Server with SSE transport')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8080, help='Port to listen on')
    args = parser.parse_args()

    # Bind the SSE request handling to our MCP server instance
    starlette_app = create_starlette_app(mcp_server, debug=True)

    print(f"Launching Armory MCP Server on http://{args.host}:{args.port}")
    print("This server provides the 'armory' toolset over Server-Sent Events (SSE).")
    
    uvicorn.run(starlette_app, host=args.host, port=args.port)