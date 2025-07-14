DIR=.venv
flag=0
#!/bin/bash
os=$(grep '^ID=' /etc/os-release)
ver=$(grep '^VERSION_ID=' /etc/os-release)
os=${os:3}
ver=${ver:11}
path=$(dirname $0)
cmd='apt-get'
choice=""
while [[ "$choice" != "1" && "$choice" != "2" ]]; do
  echo "Выберите способ выполнения скрипта:"
  echo "1 - Запуск скрипта на сервере с доступом к интернету"
  echo "2 - Запуск скрипта на сервере без доступа к интернету (заранее должен быть скачан архив пакетов для python)"
  read -p "Введите 1 или 2: " choice
done

if [ $os = '"redos"' ]; then
  cmd='dnf'
fi

if [ ! -d "$DIR" ]; then
  if [ "$choice" -eq 1 ]; then
    echo -e "\n\E[033;32mInstalling python""\033[1m\033[0m"
    sudo $cmd install python3 -y
    echo -e "\n\E[033;32mInstalling pip""\033[1m\033[0m"
    sudo $cmd install python3-pip -y
    echo -e "\n\E[033;32mInstalling python3-venv""\033[1m\033[0m"
    sudo $cmd install python3-venv -y
  fi
  echo -e "\n\E[033;32mInstalling the virtual environment and libraries""\033[1m\033[0m"
  python3 -m venv $DIR
  source $DIR/bin/activate
  if [ "$choice" -eq 1 ]; then
    pip install -r $path/requirements.txt
  else
    unzip -j -o python_packages.zip -d python_packages
    pip install --no-index --find-links=./python_packages $(ls python_packages/*.whl python_packages/*.tar.gz 2>/dev/null)
    rm -rf python_packages
  fi
  flag=1
fi
echo -e "\n\E[033;32mRun pass_change.py script""\033[1m\033[0m"
if [ $flag = 0 ]; then
  source $DIR/bin/activate
fi
python3 $path/pass_change.py
