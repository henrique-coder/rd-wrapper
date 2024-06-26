## RD Wrapper

[![PyPI version](https://badge.fury.io/py/rd-wrapper.svg)](https://badge.fury.io/py/rd-wrapper)

A simple and easy-to-use Python wrapper for [Real-Debrid API](https://api.real-debrid.com).

### Example Usage

```python
from rd_wrapper import RDW


# Initialize the wrapper with your API token or username and password
rdw = RDW(api_token='YOUR_API_TOKEN', username='YOUR_USERNAME', password='YOUR_PASSWORD')

# Getting account info
print(f'Account E-Mail (str): {rdw.account_email}')
print(f'Is Account Premium? (bool): {rdw.is_premium_account}')
print(f'Account Type (str): {rdw.account_type}')
print(f'Account Plan Expiration Timestamp (int): {rdw.premium_plan_expiration_timestamp}')
print(f'Account Fidelity Points (int): {rdw.account_fidelity_points}')
print(f'Account ID (int): {rdw.account_id}')
print(f'Account Username (str): {rdw.account_username}')
print(f'Account Avatar URL (str): {rdw.account_avatar_url}')
print(f'Account Language Name (str): {rdw.account_language_name}')
print(f'Account Language Code (str): {rdw.account_language_code}')

# Unrestricting a single URL (returns a dict with the download url and other info)
print(f'Unlimited URL Data (dict): {rdw.get_unlimited_url_data(url='http(s)://...', password=None, remote_traffic=False)}')

# Unrestricting a folder URL (returns a list of download URLs)
print(f'Original/Unlimited Folder URLs (list): {rdw.get_unlimited_folder_url_list(url='http(s)://...', unrestrict_urls=True)}')

# --> More methods are available, install the package and check the source code for more info
```


### Installation (from PyPI)

```bash
python -m pip install rd-wrapper
```
