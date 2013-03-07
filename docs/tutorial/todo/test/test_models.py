from axiom import store
from datetime import timedelta
from epsilon import extime
from todo import models
from twisted.trial import unittest


ONE_DAY = timedelta(days=1)


class TodoItemTests(unittest.TestCase):
    def test_descriptionIsMandatory(self):
        """
        Tests that you can not make a todo item without a description.
        """
        self.assertRaises(TypeError, models.TodoItem)


    def test_notCompletedByDefault(self):
        """
        Tests that a new todo item is not completed by default.
        """
        item = models.TodoItem(description=u"Test")
        self.assertFalse(item.completed)


    def test_overdue(self):
        """
        Tests that items with their due date in the past are overdue.
        """
        yesterday = extime.Time() - ONE_DAY
        item = models.TodoItem(description=u"Test", dueDate=yesterday)
        self.assertTrue(item.overdue)


    def test_notOverdue(self):
        """
        Tests that items with their due date in the future are not overdue.
        """
        tomorrow = extime.Time() + ONE_DAY
        item = models.TodoItem(description=u"Test", dueDate=tomorrow)
        self.assertFalse(item.overdue)


    def test_notOverdueIfNoDueDate(self):
        """
        Tests that items with no due date are not overdue.
        """
        item = models.TodoItem(description=u"Test")
        self.assertFalse(item.overdue)
