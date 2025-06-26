{ customConfig, pkgs, ... }:
let
  pythonEnv = pkgs.python3.withPackages (
    ps: with ps; [
      requests
      python-dotenv
    ]
  );

  # CHANGE THOSE
  # in my case, those reside in the git repo
  configPath = "/path/to/config";
  mainScript = "/path/to/script/main.py";
in
{
  systemd.services.gameNotifierService = {
    description = "Gaming Notifier instance";
    wantedBy = [ "multi-user.target" ];
    after = [ "network.target" ];

    path = [ pythonEnv ];

    serviceConfig.ExecStart = ''
      ${pythonEnv}/bin/python ${mainScript} \
        --run \
        --config-dir ${configPath}
    '';
  };
}
