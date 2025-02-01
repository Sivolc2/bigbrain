{pkgs, ...}: {
  packages = with pkgs; [
    virtualenv
  ];

  languages.python.enable = true;
}
