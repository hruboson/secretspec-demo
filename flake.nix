{
  description = "Mars weather demo (NASA InSight API)";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }:
    let
      systems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
      forAllSystems = f: nixpkgs.lib.genAttrs systems (system: f nixpkgs.legacyPackages.${system});
    in
    {
      packages = forAllSystems (pkgs: {
        default = pkgs.writeShellApplication {
          name = "mars-weather";
          runtimeInputs = [ pkgs.python3 pkgs.secretspec ];
          text = ''
            exec secretspec run --provider "''${SECRETSPEC_PROVIDER:-keyring}" -- python server.py "$@"
          '';
        };
      });

      apps = forAllSystems (pkgs: {
        default = {
          type = "app";
          program = "${self.packages.${pkgs.system}.default}/bin/mars-weather";
        };
      });

      devShells = forAllSystems (pkgs: {
        default = pkgs.mkShell {
          packages = [ pkgs.python3 pkgs.secretspec ];
          shellHook = ''
            echo "Run: nix run (or: secretspec run -- python server.py)"
            echo "Set key once: secretspec set NASA_API_KEY"
          '';
        };
      });
    };
}
