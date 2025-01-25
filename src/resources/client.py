
import asyncio
import subprocess
import json
from toga import App
from ..framework import Os

class Client():
    def __init__(self, app:App):
        super().__init__()

        self.app = app
        self.app_data = self.app.paths.data
        self.bitcoinz_cli_file = Os.Path.Combine(str(self.app_data), "bitcoinz-cli.exe")

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
    
    async def getNetworkSolps(self):
        command = f'{self.bitcoinz_cli_file} getnetworksolps'
        return await self._run_command(command)
    
    async def getDeprecationInfo(self):
        command = f'{self.bitcoinz_cli_file} getdeprecationinfo'
        return await self._run_command(command)
    
    async def z_getTotalBalance(self):
        command = f'{self.bitcoinz_cli_file} z_gettotalbalance'
        return await self._run_command(command)
    
    async def listTransactions(self, count, tx_from):
        command = f'{self.bitcoinz_cli_file} listtransactions "*" {count} {tx_from}'
        return await self._run_command(command)
    
    async def getBlockCount(self):
        command = f'{self.bitcoinz_cli_file} getblockcount'
        return await self._run_command(command)
    
    async def ListAddresses(self):
        command = f'{self.bitcoinz_cli_file} listaddresses'
        return await self._run_command(command)
    
    async def z_listAddresses(self):
        command = f'{self.bitcoinz_cli_file} z_listaddresses'
        return await self._run_command(command)
    
    async def getNewAddress(self):
        command = f'{self.bitcoinz_cli_file} getnewaddress'
        return await self._run_command(command)
    
    async def z_getNewAddress(self):
        command = f'{self.bitcoinz_cli_file} z_getnewaddress'
        return await self._run_command(command)
    
    async def z_getBalance(self, address):
        command = f'{self.bitcoinz_cli_file} z_getbalance "{address}"'
        return await self._run_command(command)