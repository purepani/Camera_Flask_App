{
  config,
  dream2nix,
  lib,
  ...
}: 
let 
  pyproject = lib.importTOML (config.mkDerivation.src + /pyproject.toml);
in {
  imports = [
    dream2nix.modules.dream2nix.pip
    #dream2nix.modules.dream2nix.WIP-python-pdm
    #dream2nix.modules.dream2nix.nixpkgs-overrides
  ];
  inherit (pyproject.project) name version;
  # select python 3.11
  deps = {nixpkgs, ...}: {
    python = nixpkgs.python311;
    qt = nixpkgs.qt6;
  };
  #pdm.lockfile = ./pdm.lock;
  #pdm.pyproject = ./pyproject.toml;
  #nixpkgs-overrides.from = config.deps.python.pkgs.opencv4;
  mkDerivation = {
    src = ./.;
    buildInputs = with config.deps; [
      python.pkgs.setuptools
    ];
  };

  buildPythonPackage = {
    format = lib.mkForce "pyproject";
    #pythonImportsCheck = [
    #  "my_tool"
    #];
  };

  pip = {
    requirementsList =
      pyproject.build-system.requires
      or []
      ++ pyproject.project.dependencies;
    flattenDependencies = true;

    drvs = {
    	  
    };
  	
  };

}
