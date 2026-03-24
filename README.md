# receipt-printing-management
A suit of apps, APIs, and webapps designed to print receipts for various reasons (including sending messages, printing tasks, tracking Pull Requests, and more!)  


### auth key settings:
Auth key settins are stored in a json object in key value pairs. If a setting is not found the api assumes the setting is false or 0.
- auto-renew (bool): Allows the user to fetch a new key when their current one expires. Default: False.
- urgent-messages (int): The ammount of urgent messages the user has remaining. Defualt: 0 (3, if user has uMessage permission)
- monthly-uMessages (int): The ammount of monthly urgent messages the user gets monthly. Default: 0.