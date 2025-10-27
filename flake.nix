{
  description = "Python dev environment for signinghubapi";

  inputs = {
    nixpkgs.url = "nixpkgs/nixos-unstable";  # or a specific version
    flake-utils.url = "github:numtide/flake-utils";
  };
  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
        };

        pythonEnv = pkgs.python311.withPackages (ps: with ps; [
          requests
          pytest
        ]);
      in {
        devShells.default = pkgs.mkShell {
          buildInputs = [
            pythonEnv
            pkgs.pre-commit
            pkgs.ruff
            pkgs.uv
          ];

          # Optional: Set environment variables or shell hooks
          shellHook = ''
            echo "Python dev environment ready."
            echo "Available: python, requests, pre-commit, ruff, uv"
          '';
        };
      }
    );
}
