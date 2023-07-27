from pyramid.exceptions import ConfigurationError


def includeme(config):
    settings = config.registry.settings
    if "pyramid_cas.cas_server" not in settings:
        raise ConfigurationError("The CAS server has not been defined")
    if "pyramid_cas.route_on_login" not in settings:
        raise ConfigurationError(
            "The default redirect route for login has not been defined"
        )
    if "pyramid_cas.route_on_logout" not in settings:
        raise ConfigurationError("The redirect route for logout has not been defined")
    config.scan("pyramid_cas.views")
