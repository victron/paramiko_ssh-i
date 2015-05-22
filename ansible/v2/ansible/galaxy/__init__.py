########################################################################
#
# (C) 2015, Brian Coca <bcoca@ansible.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#
########################################################################
''' This manages remote shared Ansible objects, mainly roles'''

import os

from ansible.errors import AnsibleError
from ansible.utils.display import Display

#      default_readme_template
#      default_meta_template


class Galaxy(object):
    ''' Keeps global galaxy info '''

    def __init__(self, options, display=None):

        if display is None:
            self.display = Display()
        else:
            self.display = display

        self.options = options
        self.roles_path = getattr(self.options, 'roles_path', None)
        if self.roles_path:
            self.roles_path = os.path.expanduser(self.roles_path)

        self.roles =  {}

        # load data path for resource usage
        this_dir, this_filename = os.path.split(__file__)
        self.DATA_PATH = os.path.join(this_dir, "data")

        #TODO: move to getter for lazy loading
        self.default_readme = self._str_from_data_file('readme')
        self.default_meta = self._str_from_data_file('metadata_template.j2')

    def add_role(self, role):
        self.roles[role.name] = role

    def remove_role(self, role_name):
        del self.roles[role_name]


    def _str_from_data_file(self, filename):
        myfile = os.path.join(self.DATA_PATH, filename)
        try:
            return open(myfile).read()
        except Exception as e:
            raise AnsibleError("Could not open %s: %s" % (filename, str(e)))

