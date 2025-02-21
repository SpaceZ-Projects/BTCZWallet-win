
import asyncio
import subprocess
import json
import binascii

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
    
    async def getUnconfirmedBalance(self):
        command = f'{self.bitcoinz_cli_file} getunconfirmedbalance'
        return await self._run_command(command)
    
    async def getTransaction(self, txid):
        command = f'{self.bitcoinz_cli_file} gettransaction {txid}'
        return await self._run_command(command)
    
    async def validateAddress(self, address):
        command = f'{self.bitcoinz_cli_file} validateaddress {address}'
        return await self._run_command(command)
    
    async def z_validateAddress(self, address):
        command = f'{self.bitcoinz_cli_file} z_validateaddress {address}'
        return await self._run_command(command)
    
    async def sendToAddress(self, address, amount):
        command = f'{self.bitcoinz_cli_file} sendtoaddress "{address}" {amount}'
        return await self._run_command(command)
    
    async def z_sendMany(self, uaddress, toaddress, amount, txfee):
        command = f'{self.bitcoinz_cli_file} z_sendmany "{uaddress}" "[{{\\"address\\": \\"{toaddress}\\", \\"amount\\": {amount}}}]" 1 {txfee}'
        return await self._run_command(command)
    
    async def z_sendToManyAddresses(self, uaddress, addresses):
        transactions_json = json.dumps(addresses)
        addresses_array = transactions_json.replace('"', '\\"')
        command = f'{self.bitcoinz_cli_file} z_sendmany "{uaddress}" "{addresses_array}" 1 0.0001'
        return await self._run_command(command)
    
    async def SendMemo(self, uaddress, toaddress, amount, txfee, memo):
        hex_memo = binascii.hexlify(memo.encode()).decode()
        command = f'{self.bitcoinz_cli_file} z_sendmany "{uaddress}" "[{{\\"address\\": \\"{toaddress}\\", \\"amount\\": {amount}, \\"memo\\": \\"{hex_memo}\\"}}]" 1 {txfee}'
        return await self._run_command(command)
    
    async def z_getOperationStatus(self, operation_ids):
        command = f'{self.bitcoinz_cli_file} z_getoperationstatus "[\\"{operation_ids}\\"]"'
        return await self._run_command(command)
    
    async def z_getOperationResult(self, operation_ids):
        command = f'{self.bitcoinz_cli_file} z_getoperationresult "[\\"{operation_ids}\\"]"'
        return await self._run_command(command)
    
    async def ImportPrivKey(self, key):
        command = f'{self.bitcoinz_cli_file} importprivkey "{key}" true'
        return await self._run_command(command)
    
    async def z_ImportKey(self, key):
        command = f'{self.bitcoinz_cli_file} z_importkey "{key}" yes'
        return await self._run_command(command)
    
    async def DumpPrivKey(self, address):
        command = f'{self.bitcoinz_cli_file} dumpprivkey "{address}"'
        return await self._run_command(command)
    
    async def z_ExportKey(self, address):
        command = f'{self.bitcoinz_cli_file} z_exportkey "{address}"'
        return await self._run_command(command)
    
    async def z_listUnspent(self, address):
        command = f'{self.bitcoinz_cli_file} z_listunspent 0 9999999 true "[\\"{address}\\"]"'
        return await self._run_command(command)