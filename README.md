# SecretSpec Demo: Mars Weather
Demo showcascing SecretSpec abilities shown on a simple python server calling some API with an API key. A tiny Python web server demonstrating [SecretSpec](https://github.com/onetwopunch/SecretSpec) secret management in a Nix development environment.

The server fetches Mars weather data from NASA's API. SecretSpec injects `NASA_API_KEY` at runtime, keeping the API key out of the application code and browser.

## Run

Requires [Nix](https://nixos.org/download/) with Flakes enabled.

```bash
# Clone the repository
git clone https://github.com/hruboson/secretspec-demo
cd secretspec-demo

# Run the demo
nix run
```

Open http://127.0.0.1:8000.

## Configure your API key

The demo defaults to NASA's rate-limited `DEMO_KEY`. To use your own key, obtain one at https://api.nasa.gov/ and configure SecretSpec:

```bash
secretspec set NASA_API_KEY
```

Then run `nix run` again.

## Development

Enter the development shell with:

```bash
nix develop
```

Or run the server directly through SecretSpec:

```bash
secretspec run -- python server.py
```

The server uses only Python's standard library; Nix provides Python and SecretSpec.

## License

[MIT](./LICENSE)
