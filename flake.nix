{
  description = "Python SMT Dev Environment";
  inputs.nixpkgs.url = "github:nixos/nixpkgs/nixos-25.11";

  outputs = { self, nixpkgs }:
  let
    pkgs = import nixpkgs { 
      system = "x86_64-linux";
      config.allowUnfree = true;
    };
  in
  {
    devShells.x86_64-linux.default = pkgs.mkShell {
      nativeBuildInputs = [ 
        (pkgs.python3.withPackages (python-pkgs: with python-pkgs; [
            z3-solver
        ]))
     ];

      # This tells nix-ld where to find the libraries ONLY for this project
      shellHook = ''
        python --version
      '';
    };
  };
}