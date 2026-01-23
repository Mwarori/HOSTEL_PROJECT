"""
Database router for MongoDB to prevent Django migrations
"""

class MongoDBRouter:
    """
    A router to control all database operations on models in the api application.
    """

    def db_for_read(self, model, **hints):
        """
        Attempts to read api models go to MongoDB.
        """
        if model._meta.app_label == 'api':
            return None  # Return None to use mongoengine instead of Django ORM
        return 'default'

    def db_for_write(self, model, **hints):
        """
        Attempts to write api models go to MongoDB.
        """
        if model._meta.app_label == 'api':
            return None  # Return None to use mongoengine instead of Django ORM
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if both models are part of the api app.
        """
        if obj1._meta.app_label == 'api' and obj2._meta.app_label == 'api':
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the api app only appears in the 'default'
        database.
        """
        if app_label == 'api':
            return False  # Don't migrate api models
        return None
