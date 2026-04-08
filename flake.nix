{
  description = "Python SMT Dev Environment";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-25.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          config.allowUnfree = true;
        };
        
        pythonPackages = pkgs.python3Packages;

        cspuz-core = pythonPackages.buildPythonPackage rec {
          pname = "cspuz-core";
          version = "unstable";
          format = "pyproject";

          src = pkgs.fetchFromGitHub {
            owner = "semiexp";
            repo = "cspuz_core";
            rev = "5f3b2d561f00c2373129d2aef72fa2151129e7ac";
            fetchSubmodules = true;
            hash = "sha256-U+neBMjXuwG5bqCIxb8eyBUZcwfVEwwtJI/AU0kc5z4=";
          };

          cargoDeps = pkgs.rustPlatform.importCargoLock {
            lockFile = ./Cargo.lock;
          };
          
          postPatch = ''
            cp ${./Cargo.lock} Cargo.lock
          '';

          nativeBuildInputs = [
            pkgs.cargo
            pkgs.rustc
            pkgs.rustPlatform.cargoSetupHook
            pythonPackages.setuptools
            pythonPackages.wheel
            pythonPackages.setuptools-rust
          ] ++ pkgs.lib.optionals pkgs.stdenv.isDarwin [
            pkgs.darwin.apple_sdk.frameworks.Security
            pkgs.darwin.apple_sdk.frameworks.CoreFoundation
            pkgs.libiconv
          ];

          doCheck = false;
        };

        cspuz = pythonPackages.buildPythonPackage rec {
          pname = "cspuz";
          version = "unstable";
          format = "pyproject";

          src = pkgs.fetchFromGitHub {
            owner = "semiexp";
            repo = "cspuz";
            rev = "1d074431984148944dde4c7d5d1636ac9cfe29e2";
            hash = "sha256-6YGssL8EimD7MSfgzelOh8YHFaXVVZucWA9wDz5L5cM=";
          };

          propagatedBuildInputs = [
            cspuz-core
            pythonPackages.z3-solver
          ];

          nativeBuildInputs = [
            pythonPackages.setuptools
            pythonPackages.wheel
          ];

          doCheck = false;
        };

      in {
        packages = {
          inherit cspuz-core cspuz;
          default = cspuz;
        };

        devShells.default = pkgs.mkShell {
          nativeBuildInputs = [
            (pkgs.python3.withPackages (python-pkgs: with python-pkgs; [
              z3-solver
              cspuz
            ]))
          ];

          shellHook = ''
            python --version
            export CSPUZ_DEFAULT_BACKEND="cspuz_core"
          '';
        };
      }
    );
}