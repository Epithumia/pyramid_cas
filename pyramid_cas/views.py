import logging
logger = logging.getLogger(__name__)

from pyramid.httpexceptions import HTTPFound, HTTPForbidden
from pyramid.security import remember, forget, unauthenticated_userid
from pyramid.view import view_config

from .cas import CASProvider


def _get_next_url(request, default):
    """
    Returns the next URL (the page to redirect to after a successful CAS auth.)
    @param request:  Pyramid request object
    @param default:  name of the configuration directive to inspect in order to
                     get the route name to redirect to.
                     Example: you have "pyramid_cas.route_on_login" in
                     your .ini file, you would use default="route_on_login"
    """
    next_url = request.GET.get("next")
    if next_url is None:
        config = request.registry.settings
        next_url = request.route_url(config["pyramid_cas.%s" % default])
    return next_url


@view_config(route_name="cas-login", renderer="string")
def cas_login(request):
    "CAS login and user challenger view"
    username = unauthenticated_userid(request)
    # Already authenticated
    if username is not None:
        logger.info("Already authenticated: username=%s", username)
        raise HTTPForbidden

    next_url = _get_next_url(request, "route_on_login")
    cas = CASProvider(request, next_url)

    ticket = request.GET.get("ticket", None)
    if ticket is None:
        logger.info("No ticket, redirecting to CAS login page")
        return HTTPFound(location=cas.get_login_url())
    else: # We have a ticket
        logger.info("Verifying ticket")
        username, userdata = cas.verify_cas_20(ticket)
        if username is None:
            msg = "Authentication failure: CAS returned no user"
            logger.error(msg)
            return msg

        # We have a username
        logger.info("Successful authentication for username: %s", username)
        headers = remember(request, username, max_age="86400")
        request.session['userdata'] = userdata  # Store the user's data in the session
        return HTTPFound(location=next_url, headers=headers)


@view_config(route_name="cas-logout", renderer="string")
def cas_logout(request):
    "CAS logout page (clears the session and AND does a real CAS logout)"
    headers = forget(request)
    request.session.clear()

    next_url = _get_next_url(request, "route_on_logout")
    cas = CASProvider(request, next_url)
    logger.info("Session cleared, redirecting to CAS logout page")
    return HTTPFound(location=cas.get_logout_url(), headers=headers)
