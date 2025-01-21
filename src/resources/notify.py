
from toga import App
from ..framework import NotifyIcon, Command


class Notify(NotifyIcon):
    def __init__(self, app:App):

        self.app = app

        self.exit_cmd = Command(
            title="Exit",
            action=self.exit_app
        )
        super().__init__(
            icon="images/BitcoinZ.ico",
            text = "BitcoinZ Wallet",
            commands=[self.exit_cmd]
        )

    def exit_app(self):
        self.hide()
        self.app.exit()