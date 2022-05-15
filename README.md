# BMW My Garage scraper

The script fetches the production status of your BMW vehicle from My Garage.

## Setup

### Prerequisites
- Python3
- pip3
- Chrome
- Python packages inside requirements.txt

### Install
Install using pip: ```pip3 install -r requirements.txt```

### Configuration
Change the _USERNAME_ and _PASSWORD_ inside _bmw.py_ to that of your own. If you installed Chrome in a different location that's specified in the script, adjust that too.

## Usage
```python3 bmw.py```

## Troubleshooting
If you are getting timeout exceptions, try increasing the _TIMEOUT_ value.
