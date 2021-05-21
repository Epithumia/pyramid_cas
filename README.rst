CAS authentication support for Pyramid
======================================
`pyramid_cas v0.4`
==================

Introduction
============

    `pyramid_cas` allows your application to authenticate against a Jasig CAS server.
    It takes borrowed concepts from different packages like django.cas, anz.client, and collective.cas.

License
============

    `pyramid_cas` is licensed under the Apache License 2.0.

Installation
============
::

    pip install pyramid_cas

Instructions
============
    Required:

        Include `pyramid_cas` under pyramid.includes directive in your `.ini` file like this::

            pyramid.includes =
                [... other packages ...]
                pyramid_cas

        Or, in your application `__init__.py` file::

            config.include("pyramid_cas")

        Set the cas server that will be used for authentication::

            pyramid_cas.cas_server = your-cas-server

        Set the route names to redirect to, if you fail to specify it manually when calling the `cas-login` or `cas-logout` views::

            pyramid_cas.route_on_login = route name
            pyramid_cas.route_on_logout = route name

    Optional:

        In your web app view, you can get the current authenticated user with::

            from pyramid.security import authenticated_userid
            def my_view(request):
                username = authenticated_userid(request)

        To get a real user object, for example a SQLAlchemy model, put this in `__init__.py`::

            from pyramid.security import authenticated_userid
            from my.app.models import User
            from sqlalchemy.orm.exc import NoResultFound

            def get_user(request):
                username = authenticated_userid(request)
                    if username is not None:
                        try:
                            return session.query(User).filter_by(username=username).one()
                        except NoResultFound:
                            return None

            config.add_request_method(get_user, "user", reify=True)

        Then you can use the `request.user` object


    Example::

        pyramid_cas.route_on_login = profile # redirects to profile page on successful authentication
        pyramid_cas.route_on_logout = homepage # redirects to homepage on successful authentication

    Use the following route names for login and logout in your application::

        cas-login
        cas-logout

        config.add_route("cas-login", "/login")
        config.add_route("cas-logout", "/logout")

    Redirect to login page if the permission is denied (and redirect back to the exact denied page when authentication is successful)::

        @forbidden_view_config(renderer="templates/forbidden.jinja2")
            def forbidden_view(request):
                if request.authenticated_userid:
                    # Already authenticated: just display a normal forbidden page
                    return {}
                else:
                    redirect_url = request.host_url + request.path
                    return HTTPFound(location=request.route_url("cas-login", _query={"next": redirect_url}))


    Logging:

        In your .ini file::

            [loggers]
                keys = [ ... some keys ... ], pyramid_cas

            [logger_pyramid_cas]
                level = DEBUG
                handlers =
                qualname = pyramid_cas

TODO
====
    - Implement CAS 1.0 protocol
    - get a dict of attributes instead of just the username
    - Add tests
    - Add demos
