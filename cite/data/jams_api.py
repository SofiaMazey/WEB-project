import flask
from flask import jsonify
from cite.data import db_session
from cite.data.jams import Jams

blueprint = flask.Blueprint(
    'jams_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/jams')
def get_jams():
    db_sess = db_session.create_session()
    jams = db_sess.query(Jams).all()
    return jsonify(
        {
            'jams':
                [item.to_dict(only=('title', 'picture', 'about', 'sugar'))
                 for item in jams]
        }
    )