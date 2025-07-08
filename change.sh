DIR=.venv
flag=0
#!/bin/bash
os=$(grep '^ID=' /etc/os-release)
ver=$(grep '^VERSION_ID=' /etc/os-release)
os=${os:3}
ver=${ver:11}
cmd='apt-get'
if [ $os = '"redos"' ]; then
  cmd='dnf'
fi

if [ ! -d "$DIR" ]; then
  echo -e "\n\E[033;32mInstalling python""\033[1m\033[0m"
  sudo $cmd install python3 -y
  echo -e "\n\E[033;32mInstalling pip""\033[1m\033[0m"
  sudo $cmd install python3-pip -y
  echo -e "\n\E[033;32mInstalling python3-venv""\033[1m\033[0m"
  sudo $cmd install python3-venv -y
  echo -e "\n\E[033;32mInstalling the virtual environment and libraries""\033[1m\033[0m"
  python3 -m venv $DIR
  source $DIR/bin/activate
  pip install -r requirements.txt
  flag=1
fi
echo -e "\n\E[033;32mRun upload_calendar.py script""\033[1m\033[0m"
if [ $flag = 0 ]; then
  source $DIR/bin/activate
fi
python3 pass_change.py
