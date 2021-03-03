#!/bin/bash

if [ -z $4 ]; then

    echo 'USAGE: ./start.sh --remote-user root --action install'
    echo 'Supported actions: install, reinstall, upgrade'

else

  username=$2
  action=$4

  if python -mplatform|grep "Ubuntu"
    then
     echo "OS is Ubuntu"
     if ! which ansible > /dev/null; then
        read -p "Ansible not found! Install? [y/N] " -r choice
        if [ $choice = y ]; then
          sudo apt-get install software-properties-common
          sudo apt-add-repository ppa:ansible/ansible
          sudo apt-get update
          sudo apt-get install ansible
          sudo apt-get install python-jmespath
        else
          echo "\nFor run this playbook you need Ansible"
          exit 1
       fi
    fi
  else
    echo "OS is not supported"
  fi

  echo "Please enter what do you want to $4: "
  options=("Rust Node" "Monitoring Server")
  select opt in "${options[@]}"
  do
      case $opt in
          "Rust Node")
  	    yml="rustnode"
            break
  	    ;;
          "Monitoring Server")
            yml="monitoring-server"
  	    break
  	    ;;
          *) echo "invalid option $REPLY";;
      esac
  done

  export ANSIBLE_HOST_KEY_CHECKING=False
  echo 'Please enter connection method: '
  options=("SSH key" "SSH password")
  if [ $username = "root" ]
  then
    select opt in "${options[@]}"
    do
      case $opt in
        "SSH key")
            read -p "Enter path to your SSH key: " keypath
            echo "Start installation..."
            ansible-playbook -i hosts -u $username --private-key $keypath --tags $action ansible/$yml.yml
            break
            ;;
        "SSH password")
            echo "Start installation..."
            ansible-playbook -i hosts -u $username -k --tags $action ansible/$yml.yml
            break
            ;;
        *) echo "invalid option $REPLY";;
      esac
    done
  else
    select opt in "${options[@]}"
    do
      case $opt in
        "SSH key")
            read -p "Enter path to your SSH key: " keypath
            echo "Start installation..."
            ansible-playbook -i hosts -u $username --become --become-method=sudo --ask-become-pass --private-key $keypath --tags $action ansible/$yml.yml
            break
            ;;
        "SSH password")
            echo "Start installation..."
            ansible-playbook -i hosts -u $username --become --become-method=sudo --ask-become-pass -k --tags $action ansible/$yml.yml
            break
            ;;
        *) echo "invalid option $REPLY";;
      esac
    done
  fi
fi
