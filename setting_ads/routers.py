class AppRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'setting_ads':
            return 'settings_ads_database'
        return 'default'

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'setting_ads':
            return 'settings_ads_database'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        if (
            obj1._meta.app_label == 'setting_ads' and
            obj2._meta.app_label == 'setting_ads'
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'setting_ads':
            return db == 'settings_ads_database'
        return db == 'default'
