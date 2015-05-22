# Ansible paramiko connection plugin with support interactive session

---
Some devices, such routers (cisco) need interactive session, in reason sub-menu hierarchy.
It's just modification of standard paramiko pluging, to keep session active and allow walk trough menu.

#### below example how play-book could look
```
---
  # simple playbook for testing
  #- debug: var=result
  #- debug: var=result.stdout_lines
  #- debug: var=result.stdout.find("#")
  
- hosts: cisco
  gather_facts: False

  tasks:
  - name: check "enable" mode (super user mode)
    raw: ;empty command                                      # it's just empty comment in console
    register: check_mode

  - name: 'enable'
    raw: enable
    when: check_mode.stdout.find("#") == -1
    register: result                                          # not used

  - name: 'configure terminal'
    raw: conf t
    when: check_mode.stdout.find("#") != -1
    register: result
    failed_when: result.stdout.find("(config)") == -1
    

  - name: 'interface configuration fa0/1'
    raw: int fa0/1
    register: check_mode
    failed_when: check_mode.stdout.find("(config-if)") == -1

  - name: no shutdown
    raw:  shutdown
    register: result

  - name: close connection
    raw: exit
    register: result
```

## Test environment
Project directory includes ready for test environment based on GNS3 simulator inside vagrant.
### Topology
![alt topology](GNS3/GNS3_ans-v/topology.png)
Everything should be ready after 
```
vagrant up
```
After connecting to virtual machine
```
vagrant ssh
```
[tmux](http://tmux.sourceforge.net/) loaded automatically with 3 tabs.
#### In first two tabs - simulation of console connection to two routers (R1, R2)
```
telnet 127.0.0.1 2501 # or telnet 127.0.0.1 2502 call from console
```
In those tabs it's easy to control what commands successfully executed on routers
Output example:
```
*Mar  1 00:19:47.679: %HA_EM-6-LOG: CLIaccounting: interface FastEthernet0/1
*Mar  1 00:19:48.719: %HA_EM-6-LOG: CLIaccounting: description connection to R
*Mar  1 00:19:49.631: %HA_EM-6-LOG: CLIaccounting: interface FastEthernet0/0
*Mar  1 00:19:50.651: %HA_EM-6-LOG: CLIaccounting: description not use
*Mar  1 00:19:51.563: %HA_EM-6-LOG: CLIaccounting: shutdown
```
If command is unsuccessful or wrong syntax, it missing inside output.
To capture such errors ```failed_when:``` need inside playbook.

#### In third tab working directory with ansible environment
```
 # direct call
cd /vagrant/play && source ansible/hacking/env-setup
```
#### There are two working playbooks for configure R1 and R2 for test
```
ansible-playbook R1_configure.yml
```
and
```
ansible-playbook R2_configure.yml
```
