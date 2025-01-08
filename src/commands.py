
import asyncio
import subprocess
import json

from framework import Os, App

class Client():
    def __init__(self):
        super().__init__()

        self.app = App()
        self.app_data = self.app.app_data
        self.bitcoinz_cli_file = Os.Path.Combine(self.app_data, "bitcoinz-cli.exe")

    async def _run_command(self, command):
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                if stdout:
                    try:
                        data = json.loads(stdout.decode())
                        result = json.dumps(data, indent=4)
                        return result, None
                    except json.JSONDecodeError:
                        return stdout.decode().strip(), None
                else:
                    return None, None
            else:
                error_message = stderr.decode()
                if "error message:" in error_message:
                    index = error_message.index("error message:")+len("error message:")
                    return None, error_message[index:].strip()
                else:
                    return None, None
        except Exception as e:
            print(f"An error occurred while running command {command}: {e}")
            return None, None

    async def stopNode(self):
        command = f'{self.bitcoinz_cli_file} stop'
        return await self._run_command(command)
    
    async def getInfo(self):
        command = f'{self.bitcoinz_cli_file} getinfo'
        return await self._run_command(command)
    
    async def getBlockchainInfo(self):
        command = f'{self.bitcoinz_cli_file} getblockchaininfo'
        return await self._run_command(command)