
import json
import binascii
import aiohttp

from toga import App


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
        
        
    async def stopNode(self):
        return await self._rpc_call(
            "stop",
            []
        )
    
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
    
    async def getNewAddress(self):
        return await self._rpc_call(
            "getnewaddress",
            []
        )
    
    async def z_getNewAddress(self):
        return await self._rpc_call(
            "z_getnewaddress",
            []
        )
    
    async def addNode(self, address:str):
        return await self._rpc_call(
            "addnode",
            [f'{address}', "onetry"]
        )
    
    async def removeNode(self, address:str):
        return await self._rpc_call(
            "addnode",
            [f'{address}', "remove"]
        )
    
    async def disconnectNode(self, address:str):
        return await self._rpc_call(
            "disconnectnode",
            [f"{address}"]
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
    
    async def z_ImportWallet(self, path):
        return await self._rpc_call(
            "z_importwallet",
            [f"{path}"]
        )
    
    async def ImportPrivKey(self, key:str):
        return await self._rpc_call(
            "importprivkey",
            [f"{key}"]
        )
    
    async def z_ImportKey(self, key:str):
        return await self._rpc_call(
            "z_importkey",
            [f"{key}"]
        )
    
    async def validateAddress(self, address):
        return await self._rpc_call(
            "validateaddress",
            [address]
        )
        
    async def z_validateAddress(self, address):
        return await self._rpc_call(
            "z_validateaddress",
            [address]
        )
    
    async def z_sendMany(self, uaddress:str, toaddress:str, amount, txfee):
        return await self._rpc_call(
            "z_sendmany",
            [f"{uaddress}", [{"address": f"{toaddress}", "amount": float(amount)}], 1, float(txfee)]
        )
    
    async def z_getOperationStatus(self, operation_ids:str):
        return await self._rpc_call(
            "z_getoperationstatus",
            [[f"{operation_ids}"]]
        )
    
    async def z_getOperationResult(self, operation_ids:str):
        return await self._rpc_call(
            "z_getoperationresult",
            [[f"{operation_ids}"]]
        )
    
    async def z_sendToManyAddresses(self, uaddress:str, addresses):
        return await self._rpc_call(
        "z_sendmany",
            [uaddress, addresses, 1, 0.0001]
        )
    
    async def SendMemo(self, uaddress:str, toaddress:str, amount, txfee, memo):
        hex_memo = binascii.hexlify(memo.encode()).decode()
        return await self._rpc_call(
            "z_sendmany",
            [f"{uaddress}", [{"address": f"{toaddress}", "amount": float(amount), "memo": hex_memo}], 1, float(txfee)]
        )
    
    async def DumpPrivKey(self, address:str):
        return await self._rpc_call(
            "dumpprivkey",
            [f"{address}"]
        )

    async def z_ExportKey(self, address):
        return await self._rpc_call(
            "z_exportkey",
            [f"{address}"]
        )
    
    async def z_ExportWallet(self, file_name):
        return await self._rpc_call(
            "z_exportwallet",
            [f"{file_name}"]
        )