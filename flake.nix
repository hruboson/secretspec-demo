{
  description = "Mars weather demo (NASA InSight API)";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }:
    let
      systems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
      forAllSystems = f: nixpkgs.lib.genAttrs systems (system: f nixpkgs.legacyPackages.${system});

      mkApp = pkgs: name: provider: extraInputs:
        let
          drv = pkgs.writeShellApplication {
            inherit name;
            runtimeInputs = with pkgs; [ python3 secretspec ] ++ extraInputs;
            text = ''
              exec secretspec run --provider ${provider} -- python server.py "$@"
            '';
          };
        in { type = "app"; program = "${drv}/bin/${name}"; };
    in
    {
      apps = forAllSystems (pkgs: {
        default = mkApp pkgs "mars-weather" "dotenv" [ ];
        bitwarden = mkApp pkgs "mars-weather-bitwarden" "bw" [ pkgs.bitwarden-cli ]; # last argument is extraInputs
      });

      devShells = forAllSystems (pkgs: {
        default = pkgs.mkShell {
          packages = with pkgs; [ python3 secretspec bitwarden-cli ];
          SECRETSPEC_PROVIDER = "dotenv";
          shellHook = ''
            echo "SecretSpec provider for this shell: $SECRETSPEC_PROVIDER"
            echo "Try: secretspec set NASA_API_KEY"
          '';
        };
      });
    };
}
