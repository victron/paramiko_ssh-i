# -*- coding: utf-8 -*-
# Copyright (c) 2015 René Moser <mail@renemoser.net>
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


class ModuleDocFragment(object):

    # Standard cloudstack documentation fragment
    DOCUMENTATION = '''
options:
  api_key:
    description:
      - API key of the CloudStack API.
    required: false
    default: null
    aliases: []
  api_secret:
    description:
      - Secret key of the CloudStack API.
    required: false
    default: null
    aliases: []
  api_url:
    description:
      - URL of the CloudStack API e.g. https://cloud.example.com/client/api.
    required: false
    default: null
    aliases: []
  api_http_method:
    description:
      - HTTP method used.
    required: false
    default: 'get'
    aliases: []
requirements:
  - cs
notes:
  - Ansible uses the C(cs) library's configuration method if credentials are not
    provided by the options C(api_url), C(api_key), C(api_secret).
    Configuration is read from several locations, in the following order:
    - The C(CLOUDSTACK_ENDPOINT), C(CLOUDSTACK_KEY), C(CLOUDSTACK_SECRET) and
       C(CLOUDSTACK_METHOD) environment variables.
    - A C(CLOUDSTACK_CONFIG) environment variable pointing to an C(.ini) file,
    - A C(cloudstack.ini) file in the current working directory.
    - A C(.cloudstack.ini) file in the users home directory.
    See https://github.com/exoscale/cs for more information.
  - This module supports check mode.
'''
