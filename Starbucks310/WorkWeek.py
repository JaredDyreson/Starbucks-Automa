#!/usr/bin/env python3.10

import EventPacket


class WorkWeek:
    def __init__(self, container: list[EventPacket]):
        if not(isinstance(container, list) and
               all([isinstance(_, EventPacket) for _ in container])):
            raise ValueError(f'expected list[EventPacket]')
        self.container = container

    def add(self):
        """
        Add all the events to the calendar
        """

        for event in self.container:
            event.add()
