from datetime import datetime
from todo import commands
from twisted.protocols import amp
from twisted.trial import unittest


class CommandTestCase(unittest.TestCase):
    """
    Test for a command class.
    """
    def assertWellFormedRequest(self, data):
        """
        Asserts that the request is well-formed.
        """
        self.commandClass.makeArguments(data, None)


    def assertWellFormedResponse(self, data):
        """
        Serializes and parses the data, and verfies the result is
        equal to the original data.
        """
        self.commandClass.makeResponse(data, None)



class AddTodoItemTests(CommandTestCase):
    commandClass = commands.AddTodoItem

    def test_withoutDueDate(self):
        """
        Tests that the adding todo items without a due date works.
        """
        data = {"description": u"Xyzzy"}
        self.assertWellFormedRequest(data)


    def test_withDueDate(self):
        """
        Tests that adding todo items with a due date works.
        """
        data = {"description": u"Xyzzzy", "dueDate": datetime.now(amp.utc)}
        self.assertWellFormedRequest(data)


    def test_emptyResponse(self):
        """
        Tests that an empty response is well-formed.
        """
        self.assertWellFormedResponse({})



class ListTodoItemsTests(CommandTestCase):
    commandClass = commands.ListTodoItems

    def test_withoutListCompleted(self):
        """
        Tests that requesting todo items without passing the ``listCompleted``
        parameter works.
        """
        self.assertWellFormedRequest({})


    def test_withListCompleted(self):
        """
        Tests that requesting todo items while passing the ``listCompleted``
        parameter works.
        """
        self.assertWellFormedRequest({"listCompleted": True})



    def test_emptyResponse(self):
        """
        Tests that a response with no to-do items is valid.
        """
        self.assertWellFormedResponse({"todoItems": []})


    def test_fullResponse(self):
        """
        Tests that a response with some to-do items is valid.
        """
        data = {
            "todoItems": [
                {
                    "description": "Eat cookies",
                    "dueDate":  datetime.now(amp.utc),
                    "completed": True
                },
                {
                    "description": "Be happy",
                    "dueDate":  datetime.now(amp.utc),
                    "completed": False
                }
            ]
        }
        self.assertWellFormedResponse(data)



class CompleteTodoItemTests(CommandTestCase):
    commandClass = commands.CompleteTodoItem

    def test_requestWitDescription(self):
        """
        Tests that a request with a description is valid.
        """
        self.assertWellFormedRequest({"description": "xyzzy"})


    def test_emptyResponse(self):
        """
        Tests that an empty response is valid.
        """
        self.assertWellFormedResponse({})
