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
module: cs_vmsnapshot
short_description: Manages VM snapshots on Apache CloudStack based clouds.
description: Create, remove and revert VM from snapshots.
version_added: '2.0'
author: René Moser
options:
  name:
    description:
      - Unique Name of the snapshot. In CloudStack terms C(displayname).
    required: true
    aliases: ['displayname']
  description:
    description:
      - Description of the snapshot.
    required: false
    default: null
  snapshot_memory:
    description:
      - Snapshot memory if set to true.
    required: false
    default: false
  project:
    description:
      - Name of the project the VM is assigned to.
    required: false
    default: null
  state:
    description:
      - State of the snapshot.
    required: false
    default: 'present'
    choices: [ 'present', 'absent', 'revert' ]
  poll_async:
    description:
      - Poll async jobs until job has finished.
    required: false
    default: true
'''

EXAMPLES = '''
---
# Create a VM snapshot of disk and memory before an upgrade
- local_action:
    module: cs_vmsnapshot
    name: Snapshot before upgrade
    vm: web-01
    snapshot_memory: yes


# Revert a VM to a snapshot after a failed upgrade
- local_action:
    module: cs_vmsnapshot
    name: Snapshot before upgrade
    vm: web-01
    state: revert


# Remove a VM snapshot after successful upgrade
- local_action:
    module: cs_vmsnapshot
    name: Snapshot before upgrade
    vm: web-01
    state: absent
'''

RETURN = '''
---
name:
  description: Name of the snapshot.
  returned: success
  type: string
  sample: snapshot before update
displayname:
  description: displayname of the snapshot.
  returned: success
  type: string
  sample: snapshot before update
created:
  description: date of the snapshot.
  returned: success
  type: string
  sample: 2015-03-29T14:57:06+0200
current:
  description: true if snapshot is current
  returned: success
  type: boolean
  sample: True
state:
  description: state of the vm snapshot
  returned: success
  type: string
  sample: Allocated
type:
  description: type of vm snapshot
  returned: success
  type: string
  sample: DiskAndMemory
description:
  description:
  description: description of vm snapshot
  returned: success
  type: string
  sample: snapshot brought to you by Ansible
'''

try:
    from cs import CloudStack, CloudStackException, read_config
    has_lib_cs = True
except ImportError:
    has_lib_cs = False

# import cloudstack common
from ansible.module_utils.cloudstack import *


class AnsibleCloudStackVmSnapshot(AnsibleCloudStack):

    def __init__(self, module):
        AnsibleCloudStack.__init__(self, module)
        self.result = {
            'changed': False,
        }


    def get_snapshot(self):
        args = {}
        args['virtualmachineid'] = self.get_vm_id()
        args['projectid'] = self.get_project_id()
        args['name'] = self.module.params.get('name')

        snapshots = self.cs.listVMSnapshot(**args)
        if snapshots:
            return snapshots['vmSnapshot'][0]
        return None


    def create_snapshot(self):
        snapshot = self.get_snapshot()
        if not snapshot:
            self.result['changed'] = True

            args = {}
            args['virtualmachineid'] = self.get_vm_id()
            args['name'] = self.module.params.get('name')
            args['description'] = self.module.params.get('description')
            args['snapshotmemory'] = self.module.params.get('snapshot_memory')

            if not self.module.check_mode:
                res = self.cs.createVMSnapshot(**args)

                if 'errortext' in res:
                    self.module.fail_json(msg="Failed: '%s'" % res['errortext'])

                poll_async = self.module.params.get('poll_async')
                if res and poll_async:
                    snapshot = self._poll_job(res, 'vmsnapshot')

        return snapshot


    def remove_snapshot(self):
        snapshot = self.get_snapshot()
        if snapshot:
            self.result['changed'] = True
            if not self.module.check_mode:
                res = self.cs.deleteVMSnapshot(vmsnapshotid=snapshot['id'])

                if 'errortext' in res:
                    self.module.fail_json(msg="Failed: '%s'" % res['errortext'])

                poll_async = self.module.params.get('poll_async')
                if res and poll_async:
                    res = self._poll_job(res, 'vmsnapshot')
        return snapshot


    def revert_vm_to_snapshot(self):
        snapshot = self.get_snapshot()
        if snapshot:
            self.result['changed'] = True

            if snapshot['state'] != "Ready":
                self.module.fail_json(msg="snapshot state is '%s', not ready, could not revert VM" % snapshot['state'])

            if not self.module.check_mode:
                res = self.cs.revertToVMSnapshot(vmsnapshotid=snapshot['id'])

                poll_async = self.module.params.get('poll_async')
                if res and poll_async:
                    res = self._poll_job(res, 'vmsnapshot')
            return snapshot

        self.module.fail_json(msg="snapshot not found, could not revert VM")


    def get_result(self, snapshot):
        if snapshot:
            if 'displayname' in snapshot:
                self.result['displayname'] = snapshot['displayname']
            if 'created' in snapshot:
                self.result['created'] = snapshot['created']
            if 'current' in snapshot:
                self.result['current'] = snapshot['current']
            if 'state' in snapshot:
                self.result['state'] = snapshot['state']
            if 'type' in snapshot:
                self.result['type'] = snapshot['type']
            if 'name' in snapshot:
                self.result['name'] = snapshot['name']
            if 'description' in snapshot:
                self.result['description'] = snapshot['description']
        return self.result


def main():
    module = AnsibleModule(
        argument_spec = dict(
            name = dict(required=True, aliases=['displayname']),
            vm = dict(required=True),
            description = dict(default=None),
            project = dict(default=None),
            snapshot_memory = dict(choices=BOOLEANS, default=False),
            state = dict(choices=['present', 'absent', 'revert'], default='present'),
            poll_async = dict(choices=BOOLEANS, default=True),
            api_key = dict(default=None),
            api_secret = dict(default=None),
            api_url = dict(default=None),
            api_http_method = dict(default='get'),
        ),
        supports_check_mode=True
    )

    if not has_lib_cs:
        module.fail_json(msg="python library cs required: pip install cs")

    try:
        acs_vmsnapshot = AnsibleCloudStackVmSnapshot(module)

        state = module.params.get('state')
        if state in ['revert']:
            snapshot = acs_vmsnapshot.revert_vm_to_snapshot()
        elif state in ['absent']:
            snapshot = acs_vmsnapshot.remove_snapshot()
        else:
            snapshot = acs_vmsnapshot.create_snapshot()

        result = acs_vmsnapshot.get_result(snapshot)

    except CloudStackException, e:
        module.fail_json(msg='CloudStackException: %s' % str(e))

    module.exit_json(**result)

# import module snippets
from ansible.module_utils.basic import *
main()
