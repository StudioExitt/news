{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
  packages = [
    pkgs.python311
  ];

  shellHook = ''
    if [ ! -d .venv ]; then
      echo "가상 환경 생성 중..."
      python -m venv .venv
      .venv/bin/pip install -r requirements.txt -q
    fi
    source .venv/bin/activate
  '';
}
