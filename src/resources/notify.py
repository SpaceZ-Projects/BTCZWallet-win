
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



class NotifyTx(NotifyIcon):
    def __init__(self):
        super().__init__(
            icon="images/tx.ico",
            text = "New Transaction"
        )


class NotifyRequest(NotifyIcon):
    def __init__(self):
        super().__init__(
            icon="images/new_request.ico",
            text = "New Request"
        )


class NotifyMessage(NotifyIcon):
    def __init__(self):
        super().__init__(
            icon="images/new_message.ico",
            text = "New Message"
        )
