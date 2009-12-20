import authority
from authority.permissions import BasePermission

from models import Repository

class RepositoryPermission(BasePermission):
    label = 'repository_permission'

authority.register(Repository, RepositoryPermission)
