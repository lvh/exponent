from todo.models import TodoItem
from twisted.protocols import amp
from txampext.axiomtypes import typeFor


class AddTodoItem(amp.Command):
    arguments = [
        ("description", typeFor(TodoItem.description)),
        ("dueDate", typeFor(TodoItem.dueDate, optional=True))
    ]


class ListTodoItems(amp.Command):
    arguments = [
        ("listCompleted", amp.Boolean(optional=True))
    ]
    response = [
        ("todoItems", amp.AmpList([
            ("description", typeFor(TodoItem.description)),
            ("dueDate", typeFor(TodoItem.dueDate)),
            ("completed", typeFor(TodoItem.completed))
        ])),
    ]

class CompleteTodoItem(amp.Command):
    arguments = [
        ("description", typeFor(TodoItem.description))
    ]
