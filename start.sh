env=$(basename "$PWD")

sh shell/install_ffmpeg.sh

# 初始化conda环境，不然每次activate切换环境会失败，默认在base环境
source /root/.bashrc
conda env list | awk -v awk_variable="$env" '$1 == awk_variable {found=1; exit} END {exit !found}'
if [ $? != 0 ]; then
  conda create -n $env python=3.10 -y
  conda activate $env
fi
conda activate $env
conda info
pip install -r requirements.txt

if [ "$(cat /proc/1/comm)" = "systemd" ]; then
  current_path=$(pwd)
  env_location=`conda info | grep 'active env location' | awk -F: '{print $2}'`
  python_path=$env_location/bin

  cat > /etc/systemd/system/$env.service<<EOF
  [Unit]
  Description=$env Service
  After=network.target

  [Service]
  Type=simple
  User=root
  WorkingDirectory=$current_path
  Environment=SVC_ENV=prod
  ExecStart=/bin/bash -c '$python_path/python $current_path/main.py >> $current_path/log/output.log 2>&1'
  ExecReload=/bin/kill -HUP \$MAINPID
  ExecStop=/bin/kill -SIGINT \$MAINPID
  Restart=on-failure

  [Install]
  WantedBy=multi-user.target
EOF
  sudo systemctl daemon-reload
  sudo systemctl enable $env
  sudo systemctl restart $env
else
  mkdir -p log
  sudo kill -9 $(cat python_app.pid)
  SVC_ENV=prod nohup python main.py >> log/output.log 2>&1 &
  echo $! > python_app.pid
fi
