"""
Tests for session-based authentication.
"""
from axiom import store
from exponent.auth import errors, session, common
from twisted.trial import unittest
from txampext import commandtests


class RequestSesssionTests(unittest.TestCase, commandtests.CommandTestMixin):
    """Tests for the AMP command to request a session identifier.

    """
    command = session.RequestSession
    argumentObjects = argumentStrings = {}
    responseObjects = responseStrings = {"sessionIdentifier": "sid"}
    errors = fatalErrors = {}



class LoginSessionTests(unittest.TestCase, commandtests.CommandTestMixin):
    """Tests for the session-based login AMP command.

    """
    command = session.LoginWithSession
    argumentObjects = argumentStrings = {
        "userIdentifier": "uid",
        "sessionIdentifier": "sid"
    }
    responseObjects = responseStrings = {
        "sessionIdentifier": "newsid"
    }
    errors = fatalErrors = {}



class LoginTests(unittest.TestCase):
    """Tests for authenticating using sessions.

    """
    def setUp(self):
        self.store = store.Store()
        self.user = common.User(store=store.Store(), identifier="uid")
        session._Session(store=self.user.store, identifier="sid")
        self._locator = session.LoginLocator(self.store)


    def _login(self, userIdentifier=None, sessionIdentifier=None):
        """Attempts to authenticate as the user using a session.

        :param userIdentifier: The user identifier to use. If unspecified or
            or ``None``, uses the test user identifier.
        :param sessionIdentifier: The session identifier to use. If
            unspecified, uses the first valid session identifier for the
            current user.

        """
        if userIdentifier is None:
            userIdentifier = self.user.identifier
        if sessionIdentifier is None:
            sessionIdentifier = self._getCurrentIdentifier()

        return self._locator.login(userIdentifier, sessionIdentifier)


    def _getCurrentIdentifier(self):
        """Returns the current identifier, as a string.

        """
        return self.user.store.findUnique(session._Session).identifier


    def test_cantLoginWithInvalidSessionIdentifier(self):
        """Users can not log in with an invalid session identifier.

        """
        d = self._login(self.user.uid, "BOGUS")
        self.assertFailure(d, errors.BadCredentials)
        return d


    def test_cantLoginWithInvalidUserIdentifier(self):
        """Users can not log in with an invalid user identifier.

        """
        d = self._login("BOGUS", self._getCurrentIdentifier())
        self.assertFailure(d, errors.BadCredentials)
        return d


    def test_cantLoginTwiceWithSameSessionIdentfiier(self):
        """Session identifiers are invalidated after a single use.

        """
        oldIdentifier = self._getCurrentIdentifier()
        d = self._login(self.user.uid, oldIdentifier)
        self.assertFailure(d, errors.BadCredentials)
        return d



class SessionLocatorTests(unittest.TestCase):
    """
    Tests for the locator for session commands for users that have
    already logged in.
    """
