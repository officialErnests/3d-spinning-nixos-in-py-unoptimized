{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {

  nativeBuildInputs = [
  ];

  buildInputs = [
    #pkgs.python3Packages.keyboard
  ];

  shellHook = ''
  '';
}
