from flask import current_app as app, request, session, redirect, url_for, abort, render_template
from CTFd.models import db, Tracking

from CTFd.utils import markdown, get_config
from CTFd.utils.dates import unix_time_millis, unix_time, isoformat

from CTFd.utils import config
from CTFd.utils.config import can_send_mail, ctf_logo, ctf_name, ctf_theme
from CTFd.utils.config.pages import get_pages

from CTFd.utils.plugins import get_registered_stylesheets, get_registered_scripts, get_configurable_plugins

from CTFd.utils.countries import get_countries, lookup_country_code
from CTFd.utils.user import authed, get_ip, get_current_user, get_current_team
from CTFd.utils.modes import generate_account_url
from CTFd.utils.config import is_setup
from CTFd.utils.security.csrf import generate_nonce

from CTFd.utils.config.visibility import (
    accounts_visible,
    challenges_visible,
    registration_visible,
    scores_visible
)

from sqlalchemy.exc import InvalidRequestError, IntegrityError

import datetime


def init_template_filters(app):
    app.jinja_env.filters['markdown'] = markdown
    app.jinja_env.filters['unix_time'] = unix_time
    app.jinja_env.filters['unix_time_millis'] = unix_time_millis
    app.jinja_env.filters['isoformat'] = isoformat


def init_template_globals(app):
    app.jinja_env.globals.update(config=config)
    app.jinja_env.globals.update(get_pages=get_pages)
    app.jinja_env.globals.update(can_send_mail=can_send_mail)
    app.jinja_env.globals.update(get_ctf_name=ctf_name)
    app.jinja_env.globals.update(get_ctf_logo=ctf_logo)
    app.jinja_env.globals.update(get_ctf_theme=ctf_theme)
    app.jinja_env.globals.update(get_configurable_plugins=get_configurable_plugins)
    app.jinja_env.globals.update(get_registered_scripts=get_registered_scripts)
    app.jinja_env.globals.update(get_registered_stylesheets=get_registered_stylesheets)
    app.jinja_env.globals.update(get_config=get_config)
    app.jinja_env.globals.update(generate_account_url=generate_account_url)
    app.jinja_env.globals.update(get_countries=get_countries)
    app.jinja_env.globals.update(lookup_country_code=lookup_country_code)
    app.jinja_env.globals.update(accounts_visible=accounts_visible)
    app.jinja_env.globals.update(challenges_visible=challenges_visible)
    app.jinja_env.globals.update(registration_visible=registration_visible)
    app.jinja_env.globals.update(scores_visible=scores_visible)


def init_request_processors(app):
    @app.context_processor
    def inject_user():
        if session:
            return dict(session)
        return dict()

    @app.before_request
    def needs_setup():
        if request.path == '/setup' or request.path.startswith('/themes'):
            return
        if not is_setup():
            return redirect(url_for('views.setup'))

    @app.before_request
    def tracker():
        # TODO: This function shouldn't cause a DB hit for lookups if possible
        if authed():
            track = Tracking.query.filter_by(ip=get_ip(), user_id=session['id']).first()
            if not track:
                visit = Tracking(ip=get_ip(), user_id=session['id'])
                db.session.add(visit)
            else:
                track.date = datetime.datetime.utcnow()

            try:
                db.session.commit()
            except (InvalidRequestError, IntegrityError) as e:
                print(e.message)
                db.session.rollback()
                session.clear()

            if authed():
                user = get_current_user()
                team = get_current_team()

                if request.path.startswith('/themes') is False:
                    if user and user.banned:
                        return render_template('errors/403.html', error='You have been banned from this CTF'), 403

                    if team and team.banned:
                        return render_template('errors/403.html', error='Your team has been banned from this CTF'), 403

            db.session.close()

    @app.before_request
    def csrf():
        try:
            func = app.view_functions[request.endpoint]
        except KeyError:
            abort(404)
        if hasattr(func, '_bypass_csrf'):
            return
        if not session.get('nonce'):
            session['nonce'] = generate_nonce()
        if request.method == "POST":
            if request.content_type != 'application/json':
                if session['nonce'] != request.form.get('nonce'):
                    abort(403)
