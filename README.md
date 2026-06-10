# ✈️ Oliver's Travel Planning

Personal travel planning workspace powered by the [flights-mcp](https://github.com/ravinahp/flights-mcp) server and Claude. Search real flights via the Duffel API, compare routes, and save beautiful HTML itineraries you can browse from anywhere on your Tailscale network.

## What This Does

- **MCP-powered flight search** — Claude uses Duffel's API to search one-way, round-trip, and multi-city flights in natural language
- **Itinerary viewer** — a local HTTP server at `http://100.126.32.92:3031/` serves your saved itineraries as a slick dark-themed index, readable on phone/laptop while traveling
- **Persistent** — the server runs as a macOS LaunchAgent, auto-starts on login

## Setup

### 1. Prerequisites
- [uv](https://docs.astral.sh/uv/getting-started/installation/) — `brew install uv`
- Python 3.10+
- A Duffel API key ([sign up](https://app.duffel.com/join) — test key works for exploring)

### 2. Clone & configure
```bash
git clone https://github.com/oliverswitzer/olivers-travel-planning
cd olivers-travel-planning
cp .env.sample .env
# Edit .env and set your DUFFEL_API_KEY_LIVE
```

### 3. Run setup (clones flights-mcp, installs deps, starts server)
```bash
bash bin/setup.sh
```

### 4. Open in Claude Code
```bash
claude  # from this directory — .mcp.json auto-loads the flights server
```

## Usage

Open Claude Code in this directory. The `flights-mcp` server is loaded automatically via `.mcp.json`. Try:

- *"Find me the cheapest flight from JFK to Tokyo departing around March 15 for 1 adult"*
- *"Search round-trip SFO → Paris, March 10–20, economy"*
- *"Plan a multi-city: NYC → London Mar 5, London → Rome Mar 10, Rome → NYC Mar 15"*
- *"Save that itinerary as an HTML file in itineraries/"*

Saved itineraries appear at **http://100.126.32.92:3031/** (Tailscale) or **http://localhost:3031/**.

## Structure

```
olivers-travel-planning/
├── .mcp.json              # Auto-loads flights-mcp in Claude Code / ao
├── .env                   # Your Duffel API key (gitignored)
├── .env.sample            # Template — commit this, not .env
├── bin/
│   ├── serve.py           # Itinerary HTTP server (port 3031)
│   ├── setup.sh           # One-time setup script
│   └── com.travel-planning.serve.plist  # macOS LaunchAgent
└── itineraries/           # Saved HTML itineraries go here
```

## Itinerary Server

| | |
|---|---|
| **Local** | http://localhost:3031/ |
| **Tailscale** | http://100.126.32.92:3031/ |
| **Port** | 3031 (avoids conflict with idea-finder on 3030) |

To start manually: `python bin/serve.py`  
To reinstall LaunchAgent: `bash bin/setup.sh`

## API Notes

- **Test key** (`duffel_test_...`): Simulated data, no verification needed
- **Live key** (`duffel_live_...`): Real flights, requires Duffel account verification + payment info (for verification only — this server is **read-only**, no bookings)
- Searches return up to 50 offers (10 for multi-city)
- Supplier timeout: 15–30s depending on search type
