import re

class QueueHandler:
    def __init__(self, owner):
        self.owner = owner

    def parse_input(self, input_str):
        """
        Parses action input. 
        !action -> Priority push.
        action -> Append to queue.
        """
        if input_str.startswith('!'):
            action = input_str[1:]
            self.push_priority(action)
            return f"Prioritized {action}."
        
        # Standard queue append
        queue = list(self.owner.db.manual_queue)
        if len(queue) < 3:
            queue.append(input_str)
            self.owner.db.manual_queue = queue
            return f"Queued {input_str}."
        return "Queue full."

    def push_priority(self, action):
        """Clears index 0, inserts new action."""
        queue = list(self.owner.db.manual_queue)
        if queue:
            queue.pop(0)
        queue.insert(0, action)
        self.owner.db.manual_queue = queue

    def get_next_action(self):
        """Pops index 0, or parses preferred_moves."""
        queue = list(self.owner.db.manual_queue)
        if queue:
            return queue.pop(0)
        # Parse preferred_moves logic here
        return "Attack"
