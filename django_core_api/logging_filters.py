def sentry_logging_filter(event, hint):
    # Filter in wanted logs by returning the event
    # Discard unwanted log events by returning None
    return event
