## How to run

Setup a python3 virtual environment:

```sh
python3 -m virtualenv env
source env/bin/activate
```

Install requirements

```sh
pip3 install -r requirements.txt
```

### Generate python files

Run the bash script to generate proto files

```sh
bash run.sh
```

### Start Blockchain

```sh
cd blockchain
python3 flask_server.py --mine "Mining Preference" --stake "Stake Amount" --pem "Pem File"
```

Mining preference - set to 1 to run as miner node, set to 0 otherwise <br/>
Stake Amount - set to 0 by default <br/>
Pem File - Name of the pem file to be used

### Start Provider

```sh
cd provider
python3 provider.py --pem "Pem File"
```

Pem File - Name of the pem file to receive tokens with

### Start Client UI

```sh
cd client
python3 ui.py
```



