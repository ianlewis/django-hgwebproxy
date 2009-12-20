import authority
from authority.permissions import BasePermission

from models import Repository

class RepositoryPermission(BasePermission):
    label = 'repository_permission'
    checks = ('push', 'pull', 'browse', 'can_push', 'can_pull')

    def can_pull(self, repo):
        if repo.owner == self.user:
            return True
        return self.pull_repository(repo)

    def can_push(self, repo):
        if repo.owner == self.user:
            return True
        return self.push_repository(repo)

    def browse(self, repo):
        if repo.owner == self.user:
            return True
        return self.browse_repository(repo)

authority.register(Repository, RepositoryPermission)
