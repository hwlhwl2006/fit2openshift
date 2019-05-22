import logging
import os

from django.db import models

from ansible_api.models import Project, Playbook
from openshift_api.models.node import Node
from openshift_api.models.role import Role

logger = logging.getLogger(__name__)


class Cluster(Project):
    OPENSHIFT_STATUS_UNKNOWN = 'UNKNOWN'
    OPENSHIFT_STATUS_RUNNING = 'RUNNING'
    OPENSHIFT_STATUS_INSTALLING = 'INSTALLING'
    OPENSHIFT_STATUS_ERROR = 'ERROR'
    OPENSHIFT_STATUS_WARNING = 'WARNING'

    OPENSHIFT_AUTH_DEFAULT = 'Htpasswd'

    OPENSHIFT_STATUS_CHOICES = (
        (OPENSHIFT_STATUS_RUNNING, 'running'),
        (OPENSHIFT_STATUS_INSTALLING, 'installing'),
        (OPENSHIFT_STATUS_UNKNOWN, 'unknown'),
        (OPENSHIFT_STATUS_ERROR, 'error'),
        (OPENSHIFT_STATUS_WARNING, 'warning')
    )

    package = models.ForeignKey("Package", null=True, on_delete=models.SET_NULL)
    template = models.CharField(max_length=64, blank=True, default='')

    def get_template_meta(self):
        for template in self.package.meta.get('templates', []):
            if template['name'] == self.template:
                return template['name']

    def create_playbooks(self):
        for playbook in self.package.meta.get('playbooks', []):
            url = 'file:///{}'.format(os.path.join(self.package.path))
            Playbook.objects.create(
                name=playbook['name'], alias=playbook['alias'],
                type=Playbook.TYPE_LOCAL, url=url, project=self
            )

    def create_roles(self):
        _roles = {}
        for role in self.package.meta.get('roles', []):
            _roles[role['name']] = role
        template = None
        for tmp in self.package.meta.get('templates', []):
            if tmp['name'] == self.template:
                template = tmp
                break

        for role in template.get('roles', []):
            _roles[role['name']] = role
        roles_data = [role for role in _roles.values()]
        children_data = {}
        for data in roles_data:
            children_data[data['name']] = data.pop('children', [])
            Role.objects.update_or_create(defaults=data, name=data['name'])
        for name, children_name in children_data.items():
            try:
                role = Role.objects.get(name=name)
                children = Role.objects.filter(name__in=children_name)
                role.children.set(children)
            except Role.DoesNotExist:
                pass

    def configs(self, tp='list'):
        self.change_to()
        role = Role.objects.get(name='OSEv3')
        configs = role.vars
        if tp == 'list':
            configs = [{'key': k, 'value': v} for k, v in configs.items()]
        return configs

    def set_config(self, k, v):
        self.change_to()
        role = Role.objects.select_for_update().get(name='OSEv3')
        _vars = role.vars
        if isinstance(v, str):
            v = v.strip()
        _vars[k] = v
        role.vars = _vars
        role.save()

    def get_config(self, k):
        v = self.configs(tp='dict').get(k)
        return {'key': k, 'value': v}

    def del_config(self, k):
        self.change_to()
        role = Role.objects.get(name='OSEv3')
        _vars = role.vars
        _vars.pop(k, None)
        role.vars = _vars
        role.save()

    def create_node_localhost(self):
        Node.objects.create(
            name="localhost", vars={"ansible_connection": "local"},
            project=self, meta={"hidden": True}
        )

    def on_cluster_create(self):
        self.change_to()
        self.create_roles()
        self.create_playbooks()
        self.create_node_localhost()