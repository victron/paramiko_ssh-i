#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# (c) 2015, René Moser <mail@renemoser.net>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible. If not, see <http://www.gnu.org/licenses/>.

DOCUMENTATION = '''
---
module: cs_sshkeypair
short_description: Manages SSH keys on Apache CloudStack based clouds.
description:
  - If no key was found and no public key was provided and a new SSH
    private/public key pair will be created and the private key will be returned.
version_added: '2.0'
author: René Moser
options:
  name:
    description:
      - Name of public key.
    required: true
  project:
    description:
      - Name of the project the public key to be registered in.
    required: false
    default: null
  state:
    description:
      - State of the public key.
    required: false
    default: 'present'
    choices: [ 'present', 'absent' ]
  public_key:
    description:
      - String of the public key.
    required: false
    default: null
'''

EXAMPLES = '''
---
# create a new private / public key pair:
- local_action: cs_sshkeypair name=linus@example.com
  register: key
- debug: msg='private key is {{ key.private_key }}'

# remove a public key by its name:
- local_action: cs_sshkeypair name=linus@example.com state=absent

# register your existing local public key:
- local_action: cs_sshkeypair name=linus@example.com public_key='{{ lookup('file', '~/.ssh/id_rsa.pub') }}'
'''

RETURN = '''
---
name:
  description: Name of the SSH public key.
  returned: success
  type: string
  sample: linus@example.com
fingerprint:
  description: Fingerprint of the SSH public key.
  returned: success
  type: string
  sample: "86:5e:a3:e8:bd:95:7b:07:7c:c2:5c:f7:ad:8b:09:28"
private_key:
  description: Private key of generated SSH keypair.
  returned: changed
  type: string
  sample: "-----BEGIN RSA PRIVATE KEY-----\nMIICXQIBAAKBgQCkeFYjI+4k8bWfIRMzp4pCzhlopNydbbwRu824P5ilD4ATWMUG\nvEtuCQ2Mp5k5Bma30CdYHgh2/SbxC5RxXSUKTUJtTKpoJUy8PAhb1nn9dnfkC2oU\naRVi9NRUgypTIZxMpgooHOxvAzWxbZCyh1W+91Ld3FNaGxTLqTgeevY84wIDAQAB\nAoGAcwQwgLyUwsNB1vmjWwE0QEmvHS4FlhZyahhi4hGfZvbzAxSWHIK7YUT1c8KU\n9XsThEIN8aJ3GvcoL3OAqNKRnoNb14neejVHkYRadhxqc0GVN6AUIyCqoEMpvhFI\nQrinM572ORzv5ffRjCTbvZcYlW+sqFKNo5e8pYIB8TigpFECQQDu7bg9vkvg8xPs\nkP1K+EH0vsR6vUfy+m3euXjnbJtiP7RoTkZk0JQMOmexgy1qQhISWT0e451wd62v\nJ7M0trl5AkEAsDivJnMIlCCCypwPN4tdNUYpe9dtidR1zLmb3SA7wXk5xMUgLZI9\ncWPjBCMt0KKShdDhQ+hjXAyKQLF7iAPuOwJABjdHCMwvmy2XwhrPjCjDRoPEBtFv\n0sFzJE08+QBZVogDwIbwy+SlRWArnHGmN9J6N+H8dhZD3U4vxZPJ1MBAOQJBAJxO\nCv1dt1Q76gbwmYa49LnWO+F+2cgRTVODpr5iYt5fOmBQQRRqzFkRMkFvOqn+KVzM\nQ6LKM6dn8BEl295vLhUCQQCVDWzoSk3GjL3sOjfAUTyAj8VAXM69llaptxWWySPM\nE9pA+8rYmHfohYFx7FD5/KWCO+sfmxTNB48X0uwyE8tO\n-----END RSA PRIVATE KEY-----\n"
'''


try:
    from cs import CloudStack, CloudStackException, read_config
    has_lib_cs = True
except ImportError:
    has_lib_cs = False

try:
    import sshpubkeys
    has_lib_sshpubkeys = True
except ImportError:
    has_lib_sshpubkeys = False

from ansible.module_utils.cloudstack import *

class AnsibleCloudStackSshKey(AnsibleCloudStack):

    def __init__(self, module):
        AnsibleCloudStack.__init__(self, module)
        self.result = {
            'changed': False,
        }
        self.ssh_key = None


    def register_ssh_key(self, public_key):
        ssh_key = self.get_ssh_key()
  
        args = {}
        args['projectid'] = self.get_project_id()
        args['name'] = self.module.params.get('name')

        res = None
        if not ssh_key:
            self.result['changed'] = True
            args['publickey'] = public_key
            if not self.module.check_mode:
                res = self.cs.registerSSHKeyPair(**args)

        else:
            fingerprint = self._get_ssh_fingerprint(public_key)
            if ssh_key['fingerprint'] != fingerprint:
                self.result['changed'] = True
                if not self.module.check_mode:
                    self.cs.deleteSSHKeyPair(**args)
                    args['publickey'] = public_key
                    res = self.cs.registerSSHKeyPair(**args)

        if res and 'keypair' in res:
            ssh_key = res['keypair']

        return ssh_key


    def create_ssh_key(self):
        ssh_key = self.get_ssh_key()
        if not ssh_key:
            self.result['changed'] = True
            args = {}
            args['projectid'] = self.get_project_id()
            args['name'] = self.module.params.get('name')
            if not self.module.check_mode:
                res = self.cs.createSSHKeyPair(**args)
                ssh_key = res['keypair']
        return ssh_key


    def remove_ssh_key(self):
        ssh_key = self.get_ssh_key()
        if ssh_key:
            self.result['changed'] = True
            args = {}
            args['name'] = self.module.params.get('name')
            args['projectid'] = self.get_project_id()
            if not self.module.check_mode:
                res = self.cs.deleteSSHKeyPair(**args)
        return ssh_key


    def get_ssh_key(self):
        if not self.ssh_key:
            args = {}
            args['projectid'] = self.get_project_id()
            args['name'] = self.module.params.get('name')

            ssh_keys = self.cs.listSSHKeyPairs(**args)
            if ssh_keys and 'sshkeypair' in ssh_keys:
                self.ssh_key = ssh_keys['sshkeypair'][0]
        return self.ssh_key


    def get_result(self, ssh_key):
        if ssh_key:
            if 'fingerprint' in ssh_key:
                self.result['fingerprint'] = ssh_key['fingerprint']

            if 'name' in ssh_key:
                self.result['name'] = ssh_key['name']

            if 'privatekey' in ssh_key:
                self.result['private_key'] = ssh_key['privatekey']
        return self.result


    def _get_ssh_fingerprint(self, public_key):
        key = sshpubkeys.SSHKey(public_key)
        return key.hash()


def main():
    module = AnsibleModule(
        argument_spec = dict(
            name = dict(required=True, default=None),
            public_key = dict(default=None),
            project = dict(default=None),
            state = dict(choices=['present', 'absent'], default='present'),
            api_key = dict(default=None),
            api_secret = dict(default=None),
            api_url = dict(default=None),
            api_http_method = dict(default='get'),
        ),
        supports_check_mode=True
    )

    if not has_lib_cs:
        module.fail_json(msg="python library cs required: pip install cs")

    if not has_lib_sshpubkeys:
        module.fail_json(msg="python library sshpubkeys required: pip install sshpubkeys")

    try:
        acs_sshkey = AnsibleCloudStackSshKey(module)
        state = module.params.get('state')
        if state in ['absent']:
            ssh_key = acs_sshkey.remove_ssh_key()
        else:
            public_key = module.params.get('public_key')
            if public_key:
                ssh_key = acs_sshkey.register_ssh_key(public_key)
            else:
                ssh_key = acs_sshkey.create_ssh_key()

        result = acs_sshkey.get_result(ssh_key)

    except CloudStackException, e:
        module.fail_json(msg='CloudStackException: %s' % str(e))

    module.exit_json(**result)

# import module snippets
from ansible.module_utils.basic import *
main()
