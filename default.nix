
{ pkgs ? import <nixpkgs> {} }:

with pkgs;



let



in mkShell {

  packages = [
    (pkgs.python311.withPackages (ps: [
      ps.numpy
      ps.pandas
      ps.requests
      ps.plotly
      ps.pygame
      ps.seaborn
      ps.matplotlib
    ]))
    imagemagick
  ];
}
