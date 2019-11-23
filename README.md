# UAD Plugin Price Scraper
Grab plugin pricing information from the UAD website and store it in a database.

## Setup
```bash
git clone git@github.com/cartfisk/uad-plugin-price-api.git
cd uad-plugin-price-api
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```

### Configure Mongo
If you don't have MongoDB installed, install it.

> Something like:
```bash
sudo apt-get install mongodb # linux
brew install mongodb # mac
```

The `server/constants.py` file will attempt to read/write from/to a Mongo instance at the default port (27017) on `localhost`, to override this, set the following environment variables:
  - `UAD_SCRAPER_MONGO_ADDRESS`
  - `UAD_SCRAPER_MONGO_PORT`
  - `UAD_SCRAPER_MONGO_USER`
  - `UAD_SCRAPER_MONGO_PASS`

## Usage
```bash
source env/bin/activate
python app.py
```

If everything goes according to plan, you should have some price data in whatever mongo database you've set up.
