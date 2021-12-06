from functools import wraps

def log(logger):
    """Sends `action` while processing func command."""

    def decorator(func):
        @wraps(func)
        def command_func(update, context, *args, **kwargs):
            if context.user_data["daten"]:
                logger.info(update)
            return func(update, context,  *args, **kwargs)
        return command_func
    
    return decorator