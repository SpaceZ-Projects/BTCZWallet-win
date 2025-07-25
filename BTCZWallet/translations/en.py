
from toga.constants import RIGHT, LEFT

translations = {
    #startup :
    "main_window": {"title": "BitcoinZ Wallet"},
    "check_network": {"text": "Check the network..."},
    "checktor_files": {"text": "Check Tor files..."},
    "checkbinary_files": {"text": "Check binary files..."},
    "checkparams_files": {"text": "Check Zk params files..."},
    "checkconf_file": {"text": "Check bitcoinz.conf file..."},
    "createconf_file": {"text": "Creating bitcoinz.conf file..."},
    "tornetwork_dialog": {"title": "Tor Network", "message": "This is your first time running the app.\nWould you like to enable the Tor network ?"},
    "missingtorrc_dialog": {"title": "Missing Tor Config", "message": "The Tor configuration file (torrc) was not found.\nWould you like to create a torrc file ?"},
    "bootstarp_dialog": {"title": "Download Bootstarp", "message": "Would you like to download the BitcoinZ bootstrap? This will help you sync faster.\nIf you prefer to sync from block 0, Click NO."},
    "tor_enabled": {"text": "Enabled"},
    "tor_disabled": {"text": "Disabled"},
    "download_tor": {"text": "Downloading Tor bundle..."},
    "download_binary": {"text": "Downloading binary..."},
    "download_params": {"text": "Downloading params..."},
    "download_bootstrap": {"text": "Downloading bootstrap..."},
    "extract_bootstarp": {"text": "Extracting bootstrap..."},
    "execute_tor": {"text": "Launching Tor..."},
    "initialize_tor": {"text": "Waiting for Tor to initialize..."},
    "tor_success": {"text": "Tor started successfully."},
    "tor_failed": {"text": "Failed to communicate with Tor."},
    "tor_tiemout": {"text": "Tor startup timed out."},
    "tor_bootstrap": {"text": "Tor Bootstrap Progress..."},
    "start_node": {"text": "Starting Node..."},
    "blocks_txt": {"text": "Blocks :", "size": 8, "align": LEFT},
    "blocks_value": {"size": 7, "align": LEFT},
    "mediantime_text": {"text": "Date :", "size": 8, "align": LEFT},
    "mediantime_value": {"size": 7, "align": LEFT},
    "sync_txt": {"text": "Sync :", "size": 8, "align": RIGHT},
    "sync_value": {"size": 7, "align": RIGHT},
    "index_size_txt": {"text": "Size :", "size": 8, "align": RIGHT},
    "index_size_value": {"size": 7, "align": RIGHT},
    "loading_blocks": {"text": "Loading block index..."},
    "activebest_chain": {"text": "Activating best chain..."},
    "rewind_blocks" : {"text": "Rewinding blocks if needed..."},
    "loading_wallet": {"text": "Loading wallet..."},
    "rescan_wallet": {"text": "Rescanning..."},
    "tor_icon": {"padding": (0,0,0,10)},

    #toolbar :
    "app_menu" : {"text": "App"},
    "about_cmd" : {"text": "About", "tooltip": "Information about this application"},
    "exit_cmd" : {"text": "Exit               |", "tooltip": "Exit the application and keep node running in background"},
    "stop_exit_cmd": {"text": "Stop node   |", "tooltip": "Stop the node and exit the application"},
    "exit_dialog": {"title": "Exit App", "message": "Are you sure you want to exit the application ?"},
    "stopexit_dialog": {"title": "Exit App", "message": "Are you sure you want to stop the node and exit the application ?"},
    "settings_menu": {"text": "Settings"},
    "currency_cmd": {"text": "Currency                             |", "tooltip": "Change your currency display"},
    "languages_cmd": {"text": "Languages                          |", "tooltip": "Change the application language"},
    "opacity_cmd": {"text": "Window opacity"},
    "opacity_50_cmd": {"text": "50% Opacity"},
    "opacity_75_cmd": {"text": "75% Opacity"},
    "opacity_100_cmd": {"text": "100% Opacity"},
    "hide_balances_cmd": {"text": "Hide balances", "tooltip": "Show/Hide balances"},
    "notification_txs_cmd": {"text": "Notifications txs", "tooltip": "Enable/Disable the transactions notifications"},
    "notification_messages_cmd": {"text": "Notifications messages", "tooltip": "Enable/Disable the messages notifications"},
    "minimize_cmd": {"text": "Minimize to tray", "tooltip": "Enable/Disable minimizing the application to the system tray on close"},
    "startup_cmd": {"text": "Run on startup", "tooltip": "Enable/Disable app startup on boot"},
    "network_menu": {"text": "Network"},
    "peer_info_cmd": {"text": "Peer info        |", "tooltip": "Display data about each node connected"},
    "add_node_cmd": {"text": "Add node", "tooltip": "Add a node to the addnode list"},
    "tor_config_cmd": {"text": "Tor network", "tooltip": "Configure Tor network"},
    "wallet_menu": {"text": "Wallet"},
    "generate_address_cmd": {"text": "Generate address"},
    "generate_t_cmd": {"text": "Transparent address (T)", "tooltip": "Generate a new transparent (T) address"},
    "generate_z_cmd": {"text": "Shielded address (Z)", "tooltip": "Generate a new shielded (Z) address"},
    "importkey_cmd": {"text": "Import private key", "tooltip": "Import a private key into your wallet"},
    "export_wallet_cmd": {"text": "Export wallet", "tooltip": "Export your wallet data to a file"},
    "import_wallet_cmd": {"text": "Import wallet", "tooltip": "Import a wallet from a file"},
    "messages_menu": {"text": "Messages"},
    "edit_username_cmd": {"text": "Edit username", "tooltip": "Change your messaging username"},
    "backup_messages_cmd": {"text": "Backup messages", "tooltip": "Backup your messages to a file"},
    "help_menu": {"text": "Help"},
    "check_update_cmd": {"text": "Check update", "tooltip": "Check for application updates"},
    "join_us_cmd": {"text": "Join us", "tooltip": "Join our community on Discord"},

    #menu :
    "home_button": {"text": "  Home", "size": 10},
    "transactions_button": {"text": "  Transactions", "size": 10},
    "receive_button": {"text": "  Receive", "size": 10},
    "send_button": {"text": "  Send", "size": 10},
    "messages_button": {"text" : "  Messages", "size": 10},
    "mining_button": {"text": "  Mining", "size": 10},
    "newaddress_dialog": {"title": "New Address", "message": "Generated address :"},
    "backupmessages_dialog": {"title": "Backup Successful", "message": "Your messages have been successfully backed up to:"},
    "selectfolder_dialog": {"title": "Select folder"},
    "savefile_dialog": {"title": "Save As…"},
    "checkupdates_dialog": {"title": "Check updates", "message": "The app version is up to date."},
    "questionupdates_dialog": {"message": "Would you like to update the app ?"},
    "current_version": {"text": "Current version :"},
    "git_version": {"text": "Git version :"},
    "missingexportdir_dialog": {"title": "Missing Export Dir", "message": "The '-exportdir' option is not configured in your bitcoinz.conf file.\n""Would you like to configure it ?"},
    "exportdirset_dialog": {"title": "Export Directory Set", "message": "Your export folder has been successfully saved. Would you like to restart your node now to apply this change ?"},
    "walletexported_dialog": {"title": "Wallet Exported Successfully", "message": "Your wallet has been exported as"},

    #network :
    "addnode_window": {"title": "Add Node"},
    "missingnode_dialog": {"title": "Missing Address", "message": "Enter a node address."},
    "proxyerror_dialog": {"title": "Tor Proxy Error", "message": "Could not connect to the .onion address"},
    "invalidnode_dialog": {"title": "Invalid Address", "message": "Enter a valid node address in the format IP:PORT"},
    "connectionfailed_dilag": {"title": "Connection Failed", "message": "Could not connect to the node at"},
    "duplicatenode_dialog": {"title": "Duplicate address", "message": "The node address is already exists in config file"},
    "addednode_dialog": {"title": "Node Added", "message": "has been added to addnode list."},
    "torconfig_window": {"title": "Tor Network"},
    "inputs_box" : {"padding": (10,30,0,0)},
    "options_box" : {"padding": (10,5,10,5)},
    "enabled_label": {"text": "Enabled :", "tooltip": "Enable or disable the Tor network", "size": 11},
    "socks_label": {"text": "Socks Port :", "tooltip": "SOCKS5 proxy port used by Tor (default: 9050)", "size": 11},
    "onlyonion_label": {"text": "Only onion :", "tooltip": "Only connect to nodes in network onion", "size": 11},
    "service_label": {"text": "Tor Service :", "tooltip": "Enable or disable Tor hidden service for BitcoinZ daemon", "size": 11},
    "service_port_label": {"text": "Service Port :", "tooltip": "The BitcoinZ daemon port (default: 1989)", "size": 11},
    "hostname_label": {"text": "Hostname :", "size": 11},
    "nodeinfo_window": {"title": "Node Info"},
    "node_info_cmd": {"text": "More info"},
    "copy_node_cmd": {"text": "Copy node address"},
    "remove_node_cmd": {"text": "Remove node"},
    "copynode_dilog": {"title": "Copied", "message": "The node address has copied to clipboard."},
    "removenode_dialog": {"title": "Node Removed", "message": "has been removed form addnode list"},
    "peer_window": {"title": "Peer Info"},
    "address_title": {"text": "Address"},
    "address_local_title": {"text": "Address Local"},
    "sent_title": {"text": "Sent"},
    "received_title": {"text": "Received"},
    "subversion_title": {"text": "Subversion"},
    "conntime_title": {"text": "Conn. Time"},

    #wallet :
    "bitcoinz_logo": {"padding": (10,0,0,10)},
    "bitcoinz_title": {"text": "Full Node Wallet", "align": LEFT, "size": 22, "padding": (25,0,0,0)},
    "bitcoinz_version": {"padding": (0,0,0,13), "align": LEFT},
    "total_balances_label": {"text": "Total Balances", "size": 14},
    "total_value": {"size": 14},
    "transparent_label": {"text": "Transparent", "size": 11},
    "private_label": {"text": "Private", "size": 11},
    "unconfirmed_box": {"padding": (82,0,0,0)},
    "unconfirmed_label": {"text": "Unconfirmed Balance"},
    "importkey_window" : {"title": "Import Key"},
    "missingkey_dialog": {"title": "Missing Private Key", "message": "Enter a private key to proceed."},
    "invalidkey_dialog": {"title": "Invalid Private Key", "message": "The private key you entered is not valid. Please check the format and try again."},
    "importwallet_window": {"title": "Import Wallet"},
    "missingfile_dialog": {"title": "Missing File", "message": "Select a wallet file to proceed."},
    "invalidfile_dialog": {"title": "Invalid File Format", "message": "Unsupported file type, Select a valid wallet file."},
    "info_label": {"text": "(This operation may take up to 10 minutes to complete.)"},
    "file_input": {"text": "+ Select / Drag and Drop File", "size": 11},
    "selectfile_dialog": {"title": "Select file"},
    "key_input": {"size": 11},

    #home :
    "coingecko_icon": {"padding": (5,0,0,10)},
    "coingecko_label": {"padding": (5,0,0,5)},
    "last_updated_label": {"align": LEFT},
    "language_window": {"title": "Change Language"},
    "language_dialog": {"title": "Language Changed", "message": "The language setting has been updated. Changes will take effect after restarting the application."},
    "currency_window": {"title": "Change Currency"},
    "currency_dialog": {"title": "Currency Changed", "message": "The currency setting has been updated, change will take effect in a few minutes."},
    "price_label": {"text" : "Price :", "size": 11, "align": LEFT},
    "price_value": {"size": 9, "align": LEFT},
    "percentage_24_label": {"text": "Change 24h :", "size": 11, "align": LEFT},
    "percentage_24_value": {"size": 9, "align": LEFT},
    "percentage_7_label": {"text": "Change 7d", "size": 11, "align": LEFT},
    "percentage_7_value": {"size": 9, "align": LEFT},
    "cap_label": {"text": "Cap :", "size": 11, "align": LEFT},
    "cap_value": {"size": 9, "align": LEFT},
    "volume_label": {"text": "Volume :", "size": 11, "align": LEFT},
    "volume_value": {"size": 9, "align": LEFT},
    "circulating_label": {"text": "Circulating :", "size": 11, "align": LEFT},
    "circulating_value": {"size": 9, "align": LEFT},
    "halving_label": {"text": "Next Halving in", "size": 13},
    "remaining_label": {"text": "Remaining", "size": 13},
    "blocks_label": {"text": "Blocks"},
    "days_label": {"text": "Days"},
    "circulating_box": {"align": LEFT},
    "max_emissions_value": {"text": "21000000000", "size": 9, "align": LEFT},
    "circulating_divider": {"size": 100},
    "currencies_selection": {"size": 11},
    "languages_selection": {"size": 11},

    #transactions :
    "txinfo_window": {"title": "Transaction Info"},
    "txid_label": {"text": "Transaction ID :", "padding": (0,0,0,20)},
    "confirmations_label": {"text": "Confirmations :"},
    "confirmations_value": {"align": LEFT},
    "category_label": {"text": "Category :"},
    "category_value": {"align": LEFT},
    "time_label": {"text": "Time :"},
    "amount_label": {"text": "Amount :", "size": 11},
    "amount_value": {"align": LEFT},
    "fee_label": {"text": "Fee :", "size": 11},
    "category_send": {"text": "Send"},
    "category_receive": {"text": "Receive"},
    "copy_txid_cmd": {"text": "Copy txid"},
    "copy_address_cmd": {"text": "Copy address"},
    "explorer_cmd": {"text": "View txid in explorer"},
    "copytxid_dialog": {"title": "Copied", "message": "The transaction ID has copied to clipboard."},
    "copyaddress_dialog": {"title": "Copied", "message": "The address has copied to clipboard."},
    "column_category": {"text": "Category"},
    "column_address": {"text": "Address"},
    "column_amount": {"text": "Amount"},
    "column_time": {"text": "Time"},
    "notify_send" : {"text": "Send"},
    "notify_receive" : {"text": "Receive"},
    "notify_mining": {"text": "Mining"},

    #send :
    "from_address_label": {"text" : "From :", "size": 11},
    "address_selection" : {"size": 11},
    "address_balance_value": {"text": "0.00000000"},
    "destination_input_single": {"text": " Address", "size": 11},
    "destination_input_many": {"text": " Addresses list", "size": 11},
    "is_valid": {"padding": (9,0,0,10)},
    "is_valid_box": {"align": LEFT},
    "amount_input":{"size": 11},
    "single_option": {"text": "Single", "tooltip": "Send to single address", "size": 11},
    "many_option": {"text": "Many", "tooltip": "Send to many addresses", "size": 11},
    "destination_label": {"text": "To :", "size": 11},
    "split_option": {"text": "Split", "tooltip": "Split the total amount equally across all addresses.", "size": 11},
    "each_option": {"text": "Each", "tooltip": "Set a specific amount for each address.", "size": 11, "padding": (0,0,0,20)},
    "fee_input": {"size": 11},
    "operation_label": {"text": "Operation Status :", "align": LEFT},
    "operation_status": {"align": LEFT},
    "operation_box": {"padding": (0,0,0,10)},
    "cashout_button": {"text": "Cash Out", "size": 11, "padding": (10,10,0,0)},
    "send_box": {"align": LEFT},
    "messages_address_cmd": {"text": "Send to messages address"},
    "percentage_25_cmd": {"text": "25 amount"},
    "percentage_50_cmd": {"text": "50 amount"},
    "percentage_75_cmd": {"text": "75 amount"},
    "max_amount_cmd": {"text": "Max amount"},
    "slow_fee_cmd": {"text": "Slow"},
    "normal_fee_cmd": {"text": "Normal"},
    "fast_fee_cmd": {"text": "Fast"},
    "main_account": {"text": "Main Account"},
    "sendsuccess_dialog": {"title": "Success", "message": "Transaction success"},
    "sendfailed_dialog": {"title": "Error", "message": "Transaction failed."},
    "insufficientbalance_dialog": {"title": "Insufficient Balance", "message": "You don't have enough balance to complete this transaction."},
    "missingamount_dialog" : {"title": "Missing Amount", "message": "Specify the amount you wish to send."},
    "selectaddress_dialog": {"title": "No address selected", "message": "Select the address you want to send from."},
    "missingdestination_dialog": {"title": "Missing Destination", "message": "Enter a destination address where you want to send the funds."},
    "zaddresseslimit_dialog": {"title": "Error", "message": "The maximum number of zaddr outputs is 54 due to transaction size limits."},
    "invalidaddress_dialog": {"title": "Invaid Address", "message": "The destination address is not valid"},
    "insufficientmany_dialog": {"title": "Insufficient Balance", "message": "Insufficient balance for this transaction.\nTotal amount ="},
    "check_amount_label": {"text": "Insufficient", "align": LEFT},
    "send_failed":{"text": "Failed"},
    "send_executing": {"text": "Executing"},
    "send_success": {"text": "Success"},

    #receive :
    "copy_key_cmd": {"text": "Copy private key"},
    "exploreraddress_cmd": {"text": "View address in explorer"},
    "columnt_addresses": {"text": "Transparent Addresses"},
    "columnz_addresses": {"text": "Private Addresses"},
    "address_balance": {"text": "Balance :", "align": RIGHT},
    "copykey_dialog": {"title": "Copied", "message": "The private key has been copied to the clipboard."},

    #messages :
    "input_box": {"padding": (0,0,0,0)},
    "list_unspent_utxos": {"padding": (0,0,0,5)},
    "message_box": {"padding": (0,0,0,10)},
    "author_value": {"padding": (0,0,8,5)},
    "message_input": {"text": " Write a message", "size": 11, "padding": (3,0,5,8)},
    "character_count": {"text": "Limit :"},
    "sendmessage_button": {"text": "  Send", "size": 9.5},
    "username_label": {"text": "Username :", "padding": (9,0,0,10)},
    "id_label": {"text": "ID :", "padding": (9,0,0,10)},
    "id_value": {"align": LEFT},
    "username_value": {"align": LEFT},
    "category_icon": {"padding": (0,0,0,10)},
    "unread_label": {"text": "--Unread Messages--"},
    "edituser_window": {"title": "Edit Username"},
    "ban_contact_cmd": {"text": "Ban contact"},
    "unread_messages": {"padding": (15,20,0,0)},
    "gift_value": {"text": "Gift :"},
    "newmessenger_label": {"text": "There no messages address for this wallet, click the button to create new messages address"},
    "create_button": {"text": "New user"},
    "newmessenger_window": {"title": "Create a new user"},
    "username_input": {"text": "required"},
    "pendinglist_window": {"title": "Pending contacts"},
    "no_pending_label": {"text": "Empty list"},
    "addcontact_window": {"title": "Add contact"},
    "addressexists_dialog": {"title": "Address exists", "message": "This address is already in your contacts list."},
    "addressinpending_dialog": {"title": "Address exists", "message": "This address is already in your pending list."},
    "addressinrequest_dialog": {"title": "Address exists", "message": "This address is already in your requests list."},
    "addressisbanned_dialog": {"title": "Address banned", "message": "This address has been banned."},

    #mining :
    "miner_label": {"text": "Miner :"},
    "miner_selection": {"text": "Select Miner"},
    "address_label": {"text": "Address :"},
    "pool_label": {"text": "Pool :"},
    "pool_selection": {"text": "Select Pool"},
    "ssl_switch": {"tooltip": "Enable/Disable SSL"},
    "worker_label": {"text": "Worker :"},
    "start_mining_button": {"text": "Start Mining", "size": 11, "padding": (0,10,0,0)},
    "stop_mining_button": {"text": "Stop Mining"},
    "worker_input": {"text": "Worker Name"},
    "totalshares_icon": {"tooltip": "Total shares"},
    "balance_icon": {"tooltip": "Balance"},
    "immature_icon": {"tooltip": "Immature balance"},
    "paid_icon": {"tooltip": "Total paid"},
    "solutions_icon": {"tooltip": "Solutions speed"},
    "estimated_icon": {"tooltip": "Estimated reward"},
    "estimated_value": {"text": "/Day"},
    "notifymining_solutions": {"text": "Solutions :"},
    "notifymining_balance": {"text": "Balance :"},
    "notifymining_immature": {"text": "Immature :"},
    "notifymining_paid": {"text": "Paid :"},
    "miner_stopped": {"text": "Miner Stopped !"},
    "mining_box": {"align": LEFT},
    "miningstats_icon": {"padding": (0,0,0,20)},
    "miningstats_value": {"padding": (0,0,0,6)},
    "progress_bar": {"padding": (0,0,0,20)},
    

    #notify :
    "notifyexit_cmd": {"text": "Exit"},
    "notifystopexit_cmd": {"text": "Stop node"},

    #status :
    "appstatusbar": {"size": 24},
    "status_label": {"text": "Status :"},
    "blocks_status": {"text": "Blocks :"},
    "deprecation_status": {"text": "Deps :"},
    "date_status": {"text": "Date :"},
    "sync_status": {"text": "Sync :"},
    "network_status": {"text": "NetHash :"},
    "connections_status": {"text": "Peer :"},
    "size_status": {"text": "Size :"},

    #other :
    "confirm_button": {"text": "Confirm", "size": 9},
    "cancel_button": {"text":  "Cancel", "size": 9},
    "close_button": {"text": "Close", "size": 9},
    "add_button": {"text": "Add", "size": 9},
    "save_button": {"text": "Save", "size": 9},
    "import_button": {"text": "Import", "size": 9},
}
