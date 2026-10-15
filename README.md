# SecretSpec Demo: Mars Weather

A demo of [SecretSpec](https://github.com/cachix/secretspec) secret management, built around a tiny Python web server that calls NASA's API with an API key.

The server fetches Mars weather data from NASA's API. SecretSpec injects `NASA_API_KEY` at runtime, keeping the key out of the application code and the browser. The point of the demo: the app never changes, only where the secret comes from does.

## Requirements

- [Git](https://git-scm.com/)
- [Nix](https://nixos.org/download/) with Flakes enabled. If Flakes aren't on by default, add this line to `~/.config/nix/nix.conf`:

*experimental-features = nix-command flakes*

Nix provides Python and SecretSpec, so there is nothing else to install.

## Step 1: Run the demo

```bash
git clone https://github.com/hruboson/secretspec-demo
cd secretspec-demo
nix run
```

Open http://127.0.0.1:8000.

The first run downloads Python and SecretSpec, which can take a few minutes. With no setup, the demo falls back to NASA's rate-limited `DEMO_KEY`, and the server log shows which key is in use.

*To stop the server press*
```bash
CTRL+C
``` 

## Step 2: Use your own API key

Get a free key at https://api.nasa.gov/, then enter the dev shell and store it with SecretSpec:

```bash
nix develop                 # enter the development shell with secretspec installed
secretspec set NASA_API_KEY # prompts for the value
exit
```

> [!TIP]
> While you're in the dev shell, you can also try the other SecretSpec commands:
> ```bash
> secretspec check                # verify all required secrets are available
> secretspec get NASA_API_KEY     # print a stored secret
> secretspec run -- python server.py
> ```

Run the demo again:

```bash
nix run
```

The server log should now say `NASA key: custom key`.

The dev shell is preconfigured to use SecretSpec's `dotenv` provider, so the key is saved to a local `.env` file (gitignored). Your code never reads that file: SecretSpec injects the key into the server as an environment variable at runtime.

## Step 3: Use a real secret manager (example with Bitwarden)

For this part you will need

1. Bitwarden account (you can get one free at [https://bitwarden.com/go/start-free/](https://bitwarden.com/go/start-free/))
1. [bitwarden-cli utility](https://bitwarden.com/help/cli/) (included in development shell when running `nix develop`)

A `.env` file is plaintext on disk. A secret manager keeps the key encrypted and out of your project folder. Password managers also provide a nicer way to share secrets across your development team. SecretSpec supports many different [providers](https://secretspec.dev/concepts/providers/). In this demo I will show how to use Bitwarden, a popular password manager, to declaratively define secrets in our project.

To set Bitwarden up run:

```bash
nix develop                     # enter the development shell with `bw` cli installed
bw login                        # authenticate with your bitwarden login (prompt for email, password)
export BW_SESSION="XY...Z=="    # unlock the bitwarden session
```

> [!NOTE]
> After successfuly logging in with bitwarden you will be shown the export command, e.g.:
> ```bash
> To unlock your vault, set your session key to the `BW_SESSION` environment variable. ex:
> $ export BW_SESSION="XY...Z=="
> ```
> Copy and paste it and run it.

Then set the key the same way like before, but this time set the `--provider "bw"` flag when running secretspec:

```bash
secretspec set --provider "bw" NASA_API_KEY
```

**Next time you will want to run this project on another machine, you do not have to run `secretspec set`, just authenticate with your Bitwarden** (by running `bw login` and `expor BW_SESSION="..."`) **and you are ready to go.**

> [!TIP]
> To check if the secret actually saved, you can go to your Bitwarden account and you should see an entry for `secretspec/mars-weather/default/NASA_API_KEY`.

Once configured run:

```bash
nix run .#bitwarden
```

In the background this basically just runs `secretspec --provider "bw" -- python server.py`. The part after the double dash (`--`) is where SecretSpec will inject the secrets at runtime.

## How it works

SecretSpec separates *what* secrets an app needs from *where* they are stored:

- `secretspec.toml` declares the secrets (here, `NASA_API_KEY`, with `DEMO_KEY` as a default).
- A **provider** decides where the value comes from: a `.env` file, the system keyring, Bitwarden, and so on.
- `secretspec run -- <command>` fetches the secrets from the chosen provider and starts the command with them in its environment.

| Command | Provider | Secret comes from |
|---|---|---|
| `nix run` | `dotenv` | local `.env` file, else `DEMO_KEY` |
| `nix run .#bitwarden` | `bw` | your Bitwarden vault |

## Development

```bash
nix develop
```

This opens a shell with Python, SecretSpec and the Bitwarden CLI, with `SECRETSPEC_PROVIDER=dotenv` set. Run the server directly through SecretSpec:

```bash
secretspec run -- python server.py
```

The server uses only Python's standard library.

## Troubleshooting

**`error: experimental Nix feature 'nix-command' is disabled`**
Enable Flakes (see [Requirements](#requirements)).

**`Keyring error: No default store has been set`**
You ran SecretSpec with its default `keyring` provider on a machine with no keyring service. Use `nix run` / `nix develop` as described above, which select the `dotenv` provider.

## License

[MIT](./LICENSE)
