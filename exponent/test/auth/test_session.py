"""
Tests for session-based authentication.
"""
from axiom import store
from exponent.auth import errors, session, user
from twisted.trial import unittest
from txampext import commandtests


class RequestSesssionTests(unittest.TestCase, commandtests.CommandTestMixin):
    """
    Tests for the AMP command to request a session identifier.
    """
    command = session.RequestSession
    argumentObjects = argumentStrings = {}
    responseObjects = responseStrings = {"sessionIdentifier": "sid"}



class LoginSessionTests(unittest.TestCase, commandtests.CommandTestMixin):
    """
    Tests for the session-based login AMP command.
    """
    command = session.LoginWithSession
    argumentObjects = argumentStrings = {
        "userIdentifier": "uid",
        "sessionIdentifier": "sid"
    }
    responseObjects = responseStrings = {
        "sessionIdentifier": "newsid"
    }



class LoginTests(unittest.TestCase):
    def setUp(self):
        self.store = store.Store()
        self.user = user.User(store=store.Store(), uid="uid")
        session._Session(store=self.user.store, identifier="sid")
        self._locator = session.Locator(self.store)


    def _login(self, userIdentifier=None, sessionIdentifier=None):
        if userIdentifier is None:
            userIdentifier = self.user.uid
        if sessionIdentifier is None:
            sessionIdentifier = self._getCurrentIdentifier()

        return self._locator.login(userIdentifier, sessionIdentifier)


    def _getCurrentIdentifier(self):
        """
        Returns the current identifier, as a string.
        """
        return self.user.store.findUnique(session._Session).identifier


    def test_cantLoginWithInvalidSessionIdentifier(self):
        """
        Tests that users can not log in with an invalid session identifier.
        """
        d = self._login(self.user.uid, "BOGUS")
        self.assertFailure(d, errors.BadCredentials)
        return d


    def test_cantLoginWithInvalidUserIdentifier(self):
        """
        Tests that users can not log in with an invalid user identifier.
        """
        d = self._login("BOGUS", self._getCurrentIdentifier())
        self.assertFailure(d, errors.BadCredentials)
        return d


    def test_cantLoginTwiceWithSameSessionIdentfiier(self):
        """
        Tests that session identifiers are invalidated after single use.
        """
        oldIdentifier = self._getCurrentIdentifier()
        d = self._login(self.user.uid, oldIdentifier)
        return d
