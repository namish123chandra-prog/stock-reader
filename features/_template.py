# ============================================================
#  COPY ME to make a new feature!
#  1. Copy this file, rename it (e.g. my_feature.py - no leading _)
#  2. Fill in the pieces below
#  3. Restart the app. Done - no other file needs to change.
# ============================================================

from core.feature import Feature


class MyFeature(Feature):
    name = "my feature"
    button = None          # e.g. "My Button" to show a button in the app
    priority = 50          # lower = answers chat sooner

    def can_handle(self, text):
        # text is lowercased. Return True when this is your topic.
        return "my keyword" in text

    def handle(self, text, app):
        # Return the answer as a simple string.
        return "Hello from my new feature!"

    def on_button(self, app):
        return self.handle("", app)

    def tick(self, app):
        # Runs ~once a minute in the background. Optional.
        # To alert the user: app.notify("Title", "message")
        pass
