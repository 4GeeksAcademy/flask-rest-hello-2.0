import os
from flask_admin import Admin
from models import db, User, People, Planet, Favorite
from flask_admin.contrib.sqla import ModelView


class FavoriteAdmin(ModelView):
    column_list = ('id', 'user_id', 'planet_name', 'people_name')

    def planet_name(self, obj):
        return obj.planet.name if obj.planet else ''

    def people_name(self, obj):
        return obj.people.name if obj.people else ''

    column_formatters = {
        'planet_name': lambda v, c, m, p: m.planet.name if m.planet else '',
        'people_name': lambda v, c, m, p: m.people.name if m.people else ''
    }


def setup_admin(app):
    app.secret_key = os.environ.get('FLASK_APP_KEY', 'sample key')
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'

    admin = Admin(app, name='4Geeks Admin', template_mode='bootstrap3')

    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(People, db.session))
    admin.add_view(ModelView(Planet, db.session))
    admin.add_view(FavoriteAdmin(Favorite, db.session))
