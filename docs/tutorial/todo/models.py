from axiom import attributes, item
from epsilon import extime


class TodoItem(item.Item):
    """
    A to-do item.
    """
    description = attributes.text(allowNone=False)
    completed = attributes.boolean(default=False)
    dueDate = attributes.timestamp()

    @property
    def overdue(self):
        """
        Returns ``True`` if the todo item is overdue, ``False`` otherwise.

        An item is overdue if it has a due date and that date is in the past.
        """
        return self.dueDate is not None and extime.Time() > self.dueDate
