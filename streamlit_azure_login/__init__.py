import os
import streamlit.components.v1 as components
from dataclasses import dataclass

from time import sleep
from datetime import datetime
from typing import Callable
from functools import wraps

from streamlit import session_state


@dataclass
class Account:
    authenticated: bool
    token: str | None = None
    token_expire_date: datetime | None = None
    user: dict | None = None

    _token_expire_date: str | None = None

    def __post_init__(self):
        if self._token_expire_date:
            self.token_expire_date = datetime.fromisoformat(
                self._token_expire_date.replace("Z", "")
            )


class RequiredLogin(Exception):
    def __init__(self, msg=None):
        self.msg = msg

    def __str__(self):
        if self.msg:
            return self.msg


class ExpiredToken(Exception):
    def __init__(self, msg=None):
        self.msg = msg

    def __str__(self):
        if self.msg:
            return self.msg


def token_required(func: Callable):
    @wraps(func)
    def check_token(*args, **kwargs):
        if not session_state.account.authenticated:
            raise RequiredLogin("Login necessário")

        if session_state.account.token_expire_date < datetime.now():
            raise ExpiredToken("Token Expirado")

        return func(*args, **kwargs)

    return check_token


# Create a _RELEASE constant. We'll set this to False while we're developing
# the component, and True when we're ready to package and distribute it.
# (This is, of course, optional - there are innumerable ways to manage your
# release process.)
_RELEASE = True

# Declare a Streamlit component. `declare_component` returns a function
# that is used to create instances of the component. We're naming this
# function "_component_func", with an underscore prefix, because we don't want
# to expose it directly to users. Instead, we will create a custom wrapper
# function, below, that will serve as our component's public API.

# It's worth noting that this call to `declare_component` is the
# *only thing* you need to do to create the binding between Streamlit and
# your component frontend. Everything else we do in this file is simply a
# best practice.

if not _RELEASE:
    _azure_ad_component = components.declare_component(
        # We give the component a simple, descriptive name ("my_component"
        # does not fit this bill, so please choose something better for your
        # own component :)
        "azure_login",
        # Pass `url` here to tell Streamlit that the component will be served
        # by the local dev server that you run via `npm run start`.
        # (This is useful while your component is in development.)
        url="http://localhost:3000",
    )
else:
    # When we're distributing a production version of the component, we'll
    # replace the `url` param with `path`, and point it to to the component's
    # build directory:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/public")
    _azure_ad_component = components.declare_component("azure_login", path=build_dir)


# Create a wrapper function for the component. This is an optional
# best practice - we could simply expose the component function returned by
# `declare_component` and call it done. The wrapper allows us to customize
# our component's API: we can pre-process its input args, post-process its
# output value, and add a docstring for users.
def azure_login(
    client_id: str,
    authority: str,
    redirect_uri: str,
    custom_labels: dict | None = None,
    key="account",
) -> Account:
    """Create an instance of the azure_login component. Compatible with Azure AD organizations.

    Args:
        client_id (str): the client_id of you Azure AD application
        authority (str): the authority of you Azure AD application
        redirect_uri (str): a redirect_uri registered you Azure AD application
        custom_labels (dict | None, optional): A dictionary containing the custom label to be shown in your component.
        It can have the keys:
        - labelButtonOut: text to be shown in the logout button
        - labelLogout: text to be show below the logout button. It is appended to the username of the autenticated user.
        - labelButtonIn: text to be shown in the login button
        - labelLogin: text to be shown below the login button
        - labelLoading: text to be show while the component is loading
        - errorFatal: text to be show if an error occurs

    Returns:
        create or updates the account key on session_state with Account object containing the token and user info when autenticated.
        When the user is not autenticated the object contains False on the autenticated flags and None in everything else.
    """

    # Call through to our private component function. Arguments we pass here
    # will be sent to the frontend, where they'll be available in an "args"
    # dictionary.
    #
    # "default" is a special argument that specifies the initial return
    # value of the component before the user has interacted with it.

    auth = _azure_ad_component(
        inputClientId=client_id,
        inputAuthority=authority,
        inputRedirectUri=redirect_uri,
        inputCustomLabels=custom_labels,
    )

    while auth is None:
        sleep(0.1)

    if key not in session_state:
        session_state[key] = Account(**auth)
    else:
        session_state[key] = Account(**auth)
