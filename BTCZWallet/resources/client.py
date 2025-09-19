
import asyncio
import subprocess
import json
import binascii
import aiohttp

from toga import App
from ..framework import Os


class RPC():
    def __init__(self, app:App, utils):
        super().__init__()

        self.app = app
        self.utils = utils

    async def _rpc_call(self, method, params):
        try:
            rpcuser, rpcpassword, rpcport = self.utils.get_rpc_config()
            url = f"http://localhost:{rpcport}/"
            auth = aiohttp.BasicAuth(rpcuser, rpcpassword)
            payload = {
                "jsonrpc": "1.0",
                "id": "curltest",
                "method": method,
                "params": params,
            }
            async with aiohttp.ClientSession(auth=auth) as session:
                async with session.post(url, json=payload) as response:
                    text = await response.text()
                    try:
                        data = json.loads(text)
                    except json.JSONDecodeError:
                        return None, text.strip()

                    error = data.get("error")
                    if error:
                        code = error.get("code")
                        message = error.get("message", "").strip()
                        if code == -28:
                            return None, message
                        return None, message

                    return data.get("result"), None

        except Exception as e:
            return None, str(e).strip()
        
    
    async def getInfo(self):
        return await self._rpc_call(
            "getinfo",
            []
        )
    
    async def getBlockchainInfo(self):
        return await self._rpc_call(
            "getblockchaininfo",
            []
        )
    
    async def getNetworkSolps(self):
        return await self._rpc_call(
            "getnetworksolps",
            []
        )
    
    async def getPeerInfo(self):
        return await self._rpc_call(
            "getpeerinfo",
            []
        )
    
    async def getConnectionCount(self):
        return await self._rpc_call(
            "getconnectioncount",
            []
        )
    
    async def getPeerinfo(self):
        return await self._rpc_call(
            "getpeerinfo",
            []
        )
    
    async def getDeprecationInfo(self):
        return await self._rpc_call(
            "getdeprecationinfo",
            []
        )
    
    async def z_getTotalBalance(self):
        return await self._rpc_call(
            "z_gettotalbalance",
            []
        )
    
    async def z_getBalance(self, address):
        return await self._rpc_call(
            "z_getbalance",
            [f"{address}"]
        )
    
    async def getUnconfirmedBalance(self):
        return await self._rpc_call(
            "getunconfirmedbalance",
            []
        )
    
    async def listAddressgroupPings(self):
        return await self._rpc_call(
            "listaddressgroupings",
            []
        )
    
    async def ListAddresses(self):
        return await self._rpc_call(
            "listaddresses",
            []
        )
    
    async def z_listAddresses(self):
        return await self._rpc_call(
            "z_listaddresses",
            []
        )
    
    async def getTransaction(self, txid):
        return await self._rpc_call(
            "gettransaction",
            [f"{txid}"]
        )
    
    async def getBlock(self, block):
        return await self._rpc_call(
            "getblock",
            [f"{block}", 2]
        )
    
    async def listTransactions(self, count, tx_from):
        return await self._rpc_call(
            "listtransactions",
            ["*", count, tx_from]
        )
    
    async def z_listUnspent(self, address:str, minconf:int, maxconf:int = 9999999):
        return await self._rpc_call(
            "z_listunspent",
            [minconf, maxconf, True, [address]]
        )



class Client():
    def __init__(self, app:App):
        super().__init__()

        self.app = app
        self.app_data = self.app.paths.data
        self.bitcoinz_cli_file = Os.Path.Combine(str(self.app_data), "bitcoinz-cli.exe")
        
        if Os.File.Exists(self.bitcoinz_cli_file):
            Os.FileStream(
                self.bitcoinz_cli_file,
                Os.FileMode.Open,
                Os.FileAccess.Read,
                Os.FileShare.Read
            )


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
                if "error" in error_message:
                    if process.returncode != 28:
                        if process.returncode == 1:
                            self.app.console.warning_log("BitcoinZ node is not running.")
                        elif process.returncode == 4:
                            pass
                        else:
                            self.app.console.error_log(error_message)
                    index = error_message.index("error message:")+len("error message:")
                    return None, error_message[index:].strip()
                else:
                    return None, None
        except Exception as e:
            return None, None

    async def stopNode(self):
        """
        Stop BitcoinZ server.
        """
        command = f'{self.bitcoinz_cli_file} stop'
        return await self._run_command(command)
    
    async def getInfo(self):
        """
        Returns an object containing various state info.
        """
        command = f'{self.bitcoinz_cli_file} getinfo'
        return await self._run_command(command)
    
    async def getBlockchainInfo(self):
        """
        Returns an object containing various state info regarding block chain processing.
        """
        command = f'{self.bitcoinz_cli_file} getblockchaininfo'
        return await self._run_command(command)
    
    async def getBlock(self, blockhash):
        """
        information about the block
        """
        command = f'{self.bitcoinz_cli_file} getblock "{blockhash}"'
        return await self._run_command(command)
    
    async def getNetworkSolps(self):
        """
        Returns the estimated network solutions per second based on the last n blocks.
        """
        command = f'{self.bitcoinz_cli_file} getnetworksolps'
        return await self._run_command(command)
    
    async def getConnectionCount(self):
        """
        Returns the number of connections to other nodes.
        """
        command = f'{self.bitcoinz_cli_file} getconnectioncount'
        return await self._run_command(command)
    
    async def getDeprecationInfo(self):
        """
        Returns an object containing current version and deprecation block height.
        """
        command = f'{self.bitcoinz_cli_file} getdeprecationinfo'
        return await self._run_command(command)
    
    async def getPeerinfo(self):
        """
        Returns data about each connected network node as a json array of objects.
        """
        command = f'{self.bitcoinz_cli_file} getpeerinfo'
        return await self._run_command(command)
    
    async def addNode(self, address:str):
        command = f'{self.bitcoinz_cli_file} addnode "{address}" "onetry"'
        return await self._run_command(command)
    
    async def removeNode(self, address:str):
        command = f'{self.bitcoinz_cli_file} addnode "{address}" "remove"'
        return await self._run_command(command)
    
    async def disconnectNode(self, address:str):
        """
        Immediately disconnects from the specified node.
        """
        command = f'{self.bitcoinz_cli_file} disconnectnode "{address}"'
        return await self._run_command(command)
    
    async def z_getTotalBalance(self):
        """
        Return the total value of funds stored in the node's wallet.
        """
        command = f'{self.bitcoinz_cli_file} z_gettotalbalance'
        return await self._run_command(command)
    
    async def listTransactions(self, count:int, tx_from:int):
        """
        Returns up to 'count' most recent transactions skipping the first 'from' transactions for account '*'.
        """
        command = f'{self.bitcoinz_cli_file} listtransactions "*" {count} {tx_from}'
        return await self._run_command(command)
    
    async def getBlockCount(self):
        """
        Returns the number of blocks in the best valid block chain.
        """
        command = f'{self.bitcoinz_cli_file} getblockcount'
        return await self._run_command(command)
    
    async def listAddressgroupPings(self):
        """
        Lists groups of addresses which have had their common ownership
        made public by common use as inputs or as the resulting change
        in past transactions
        """
        command = f'{self.bitcoinz_cli_file} listaddressgroupings'
        return await self._run_command(command)
    
    async def ListAddresses(self):
        """
        Returns the list of Transparent addresses belonging to the wallet.
        """
        command = f'{self.bitcoinz_cli_file} listaddresses'
        return await self._run_command(command)
    
    async def z_listAddresses(self):
        """
        Returns the list of Sprout and Sapling shielded addresses belonging to the wallet.
        """
        command = f'{self.bitcoinz_cli_file} z_listaddresses'
        return await self._run_command(command)
    
    async def getNewAddress(self):
        """
        Returns a new BitcoinZ address for receiving payments.
        """
        command = f'{self.bitcoinz_cli_file} getnewaddress'
        return await self._run_command(command)
    
    async def z_getNewAddress(self):
        """
        Returns a new BitcoinZ shielded address for receiving payments.
        """
        command = f'{self.bitcoinz_cli_file} z_getnewaddress'
        return await self._run_command(command)
    
    async def z_getBalance(self, address:str):
        """
        Returns the balance of a taddr or zaddr belonging to the node's wallet.
        """
        command = f'{self.bitcoinz_cli_file} z_getbalance "{address}"'
        return await self._run_command(command)
    
    async def getReceivedByAddress(self, address:str, minconf:int = 1):
        """
        Returns the total amount received by the given BitcoinZ address in transactions with at least minconf confirmations.
        """
        command = f'{self.bitcoinz_cli_file} getreceivedbyaddress "{address}" {minconf}'
        return await self._run_command(command) 
    
    async def getUnconfirmedBalance(self):
        """
        Returns the total unconfirmed balance
        """
        command = f'{self.bitcoinz_cli_file} getunconfirmedbalance'
        return await self._run_command(command)
    
    async def getTransaction(self, txid:str):
        """
        Get detailed information about in-wallet transaction
        """
        command = f'{self.bitcoinz_cli_file} gettransaction {txid}'
        return await self._run_command(command)
    
    async def validateAddress(self, address:str):
        """
        Return information about the given BitcoinZ address.
        """
        command = f'{self.bitcoinz_cli_file} validateaddress {address}'
        return await self._run_command(command)
    
    async def z_validateAddress(self, address:str):
        """
        Return information about the given z address.
        """
        command = f'{self.bitcoinz_cli_file} z_validateaddress {address}'
        return await self._run_command(command)
    
    async def sendToAddress(self, address:str, amount):
        """
        Send an amount to a given address.
        """
        command = f'{self.bitcoinz_cli_file} sendtoaddress "{address}" {amount}'
        return await self._run_command(command)
    
    async def z_sendMany(self, uaddress:str, toaddress:str, amount, txfee):
        """
        Send multiple times. Amounts are decimal numbers with at most 8 digits of precision.
        Change generated from a taddr flows to a new taddr address, while change generated from a zaddr returns to itself.
        When sending coinbase UTXOs to a zaddr, change is not allowed. The entire value of the UTXO(s) must be consumed.
        Before Sapling activates, the maximum number of zaddr outputs is 54 due to transaction size limits.
        """
        command = f'{self.bitcoinz_cli_file} z_sendmany "{uaddress}" "[{{\\"address\\": \\"{toaddress}\\", \\"amount\\": {amount}}}]" 1 {txfee}'
        return await self._run_command(command)
    
    async def z_sendToManyAddresses(self, uaddress:str, addresses):
        transactions_json = json.dumps(addresses)
        addresses_array = transactions_json.replace('"', '\\"')
        command = f'{self.bitcoinz_cli_file} z_sendmany "{uaddress}" "{addresses_array}" 1 0.0001'
        return await self._run_command(command)
    
    async def SendMemo(self, uaddress:str, toaddress:str, amount, txfee, memo):
        hex_memo = binascii.hexlify(memo.encode()).decode()
        command = f'{self.bitcoinz_cli_file} z_sendmany "{uaddress}" "[{{\\"address\\": \\"{toaddress}\\", \\"amount\\": {amount}, \\"memo\\": \\"{hex_memo}\\"}}]" 1 {txfee}'
        return await self._run_command(command)
    
    async def z_getOperationStatus(self, operation_ids:str):
        """
        Get operation status and any associated result or error data. The operation will remain in memory.
        """
        command = f'{self.bitcoinz_cli_file} z_getoperationstatus "[\\"{operation_ids}\\"]"'
        return await self._run_command(command)
    
    async def z_getOperationResult(self, operation_ids:str):
        """
        Retrieve the result and status of an operation which has finished, and then remove the operation from memory.
        """
        command = f'{self.bitcoinz_cli_file} z_getoperationresult "[\\"{operation_ids}\\"]"'
        return await self._run_command(command)
    
    async def z_ImportWallet(self, path):
        """
        Imports taddr and zaddr keys from a wallet export file.
        """
        command = f'{self.bitcoinz_cli_file} z_importwallet "{path}"'
        return await self._run_command(command)
    
    async def z_ExportWallet(self, file_name):
        """
        Exports all wallet keys, for taddr and zaddr, in a human-readable format.  Overwriting an existing file is not permitted.
        """
        command = f'{self.bitcoinz_cli_file} z_exportwallet "{file_name}"'
        return await self._run_command(command)
    
    async def ImportPrivKey(self, key:str):
        """
        Adds a private key (as returned by dumpprivkey) to your wallet.
        """
        command = f'{self.bitcoinz_cli_file} importprivkey "{key}" false'
        return await self._run_command(command)
    
    async def z_ImportKey(self, key:str):
        """
        Adds a zkey (as returned by z_exportkey) to your wallet.
        """
        command = f'{self.bitcoinz_cli_file} z_importkey "{key}" no'
        return await self._run_command(command)
    
    async def DumpPrivKey(self, address:str):
        """
        Reveals the private key corresponding to 't-addr'.
        Then the importprivkey can be used with this output
        """
        command = f'{self.bitcoinz_cli_file} dumpprivkey "{address}"'
        return await self._run_command(command)
    
    async def z_ExportKey(self, address):
        """
        Reveals the zkey corresponding to 'zaddr'.
        Then the z_importkey can be used with this output
        """
        command = f'{self.bitcoinz_cli_file} z_exportkey "{address}"'
        return await self._run_command(command)
    
    async def ListUnspent(self, address:str, minconf:int, maxconf:int = 9999999):
        """
        Returns array of unspent transaction outputs
        with between minconf and maxconf (inclusive) confirmations.
        Optionally filter to only include txouts paid to specified addresses.
        """
        command = f'{self.bitcoinz_cli_file} listunspent {minconf} {maxconf} "[\\"{address}\\"]"'
        return await self._run_command(command)
    
    async def z_listUnspent(self, address:str, minconf:int, maxconf:int = 9999999):
        """
        Returns array of unspent shielded notes with between minconf and maxconf (inclusive) confirmations.
        Optionally filter to only include notes sent to specified addresses.
        When minconf is 0, unspent notes with zero confirmations are returned, even though they are not immediately spendable.
        """
        command = f'{self.bitcoinz_cli_file} z_listunspent {minconf} {maxconf} true "[\\"{address}\\"]"'
        return await self._run_command(command)