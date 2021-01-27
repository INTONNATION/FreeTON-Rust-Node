#!/bin/bash

if  python -mplatform|grep "centos"
     then
      echo "OS is Centos"
      if ! which ansible > /dev/null; then
         read -p "Ansible not found! Install? [y/N] " -n 1 -r choice
         if [[ $choice = y ]]; then
           sudo yum -y install epel-release
           sudo yum-config-manager --enable epel
           sudo yum -y install ansible
         else
           echo -e "\nFor run this playbook you need Ansible"
           exit 1
         fi
      fi  
elif python -mplatform|grep "Ubuntu"
      then
       echo "OS is Ubuntu"
       if ! which ansible > /dev/null; then
          read -p "Ansible not found! Install? [y/N] " -r choice
          if [ $choice = y ]; then
            sudo apt-get install software-properties-common
            sudo apt-add-repository ppa:ansible/ansible
            sudo apt-get update
            sudo apt-get install ansible
          else
            echo "\nFor run this playbook you need Ansible"
            exit 1
         fi
      fi  
else
       echo "OS is not supported"
fi

export ANSIBLE_HOST_KEY_CHECKING=False


PS3='Please enter install method: '
options=("SSH" "Local" "Quit")
select opt in "${options[@]}"
do
    case $opt in
        "SSH")
            echo "Installation on remote server..."
	    read -p "IP address or hostname of remote server: " -r host
            read -p "SSH username: " -r username
	    printf '%s\n%s\n' '[monitoring-server]' ${host} '[rustnode]' ${host} > hosts
            ansible-playbook -i hosts -u $username --become --become-method=sudo -k  run.yml
	    break
            ;;
        "Local")
            echo "Installation on local server..."
	    printf '%s\n%s\n' '[monitoring-server]' 'localhost ansible_connection=local' '[rustnode]' 'localhost ansible_connection=local' > hosts
	    ansible-playbook -i hosts run.yml
	    break
            ;;
        "Quit")
            break
            ;;
        *) echo "invalid option $REPLY";;
    esac
done
