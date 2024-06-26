## RD Wrapper

![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/Henrique-Coder/rd-wrapper/.github%2Fworkflows%2Fpython-package.yml?branch=main&style=for-the-badge&logo=github&labelColor=gray&cacheSeconds=60&link=https%3A%2F%2Fgithub.com%2FHenrique-Coder%2Frd-wrapper)
![PyPI - Version](https://img.shields.io/pypi/v/rd-wrapper?style=for-the-badge&logo=pypi&labelColor=gray&color=white&cacheSeconds=60&link=https%3A%2F%2Fpypi.org%2Fproject%2Frd-wrapper)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/rd-wrapper?style=for-the-badge&logo=pypi&labelColor=gray&color=white&cacheSeconds=60&link=https%3A%2F%2Fpypi.org%2Fproject%2Frd-wrapper)

A simple and easy-to-use Python wrapper for [Real-Debrid API](https://api.real-debrid.com).

### Installation (from PyPI)

```bash
python -m pip install rd-wrapper
```

### Example Usage

```python
from rd_wrapper import RDW


# Initialize the wrapper with your API token or username and password
rdw = RDW(api_token='YOUR_API_TOKEN', username='YOUR_USERNAME', password='YOUR_PASSWORD',  anonymous_access=False)

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

# Retrieve server time and server iso time
print(f'Server Time (str|int): {rdw.get_server_time(unix_timestamp=False)}')
print(f'Server ISO Time (str|int): {rdw.get_server_iso_time(unix_timestamp=True)}')

# Check if the url is supported
print(f'Is URL Supported? (bool): {rdw.is_url_supported(url='http(s)://...', password=None)}')

# Unrestricting a single URL (returns a dict with the download url and other info)
print(f'Unlimited URL Data (dict): {rdw.get_unlimited_url_data(url='http(s)://...', password=None, remote_traffic=False)}')

# Unrestricting a folder URL (returns a list of download URLs)
print(f'Original/Unlimited Folder URLs (list): {rdw.get_unlimited_folder_url_list(url='http(s)://...', unrestrict_urls=True)}')

# --> More methods are available to use, check the source code for more info
```
