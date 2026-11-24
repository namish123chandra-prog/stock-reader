# ============================================================
#  THE PLUG-IN RULEBOOK
#  Every feature (News, Best Stocks, Alerts...) is a small
#  Python file in the "features" folder that follows this shape.
#  To add a NEW feature: copy features/_template.py, rename it,
#  fill it in. The app finds it automatically. No old code changes.
# ============================================================


class Feature:
    # Short name of your feature
    name = "unnamed"

    # If you set this, a button with this label appears in the app.
    # Leave it as None for a chat-only feature.
    button = None

    # Lower number = gets first chance to answer a chat message.
    priority = 50

    def can_handle(self, text):
        """Return True if this feature knows how to answer `text`
        (text is the user's message, already lowercased)."""
        return False

    def handle(self, text, app):
        """Answer the user's message. Return a plain string.
        `app` gives you helpers: app.notify(title, message), etc."""
        return "This feature has nothing to say yet."

    def on_button(self, app):
        """What happens when the user clicks this feature's button.
        By default it just calls handle() with an empty message."""
        return self.handle("", app)

    def tick(self, app):
        """Called about once a minute in the background.
        Use it for things like watching prices. Optional."""
        pass
