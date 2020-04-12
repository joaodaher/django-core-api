from django.conf import settings


class ReaderDatabaseRouter:
    def _has_read_replica(self):
        return bool(settings.READ_DATABASE_URL)

    def db_for_read(self, model, **hints):
        if self._has_read_replica():
            return 'replica'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        return True


class DefaultDatabaseRouter:
    def db_for_read(self, model, **hints):
        return 'default'

    def db_for_write(self, model, **hints):
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        All non-auth models end up in this pool.
        """
        return db == 'default'
