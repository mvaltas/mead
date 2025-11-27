import contextvars

# Context variable to hold the currently active Model instance.
# Elements will check this variable upon initialization to auto-register.
current_model = contextvars.ContextVar("current_model", default=None)
