# Session <-> Tdata converter rest api

## Installation

1. Clone the repository:

```sh
git clone https://github.com/gaponukz/converter_service.git
cd converter_service
```

2. Install pyhton packages
```sh
pip install -r requirements.txt
```

## Deployment
To run the app on your local machine, simply execute the server.py file:
```sh
python server.py
```

The app should now be accessible at [http://localhost:5000](http://localhost:5000).

### Important
Before is starts you need to create file `proxy.json`:
```json
{
    "ip": "ip.com",
    "port": 8000,
    "username": "username",
    "password": "password"
}
```
Also create some folders:
```bash
mkdir sessions
mkdir tdatas
mkdir results
```

## Testing
In [`test`](test) folder you can find script.js file that demonstrates how to use the converter, and index.html provides the opportunity to test it immediately with a convenient interface.
![image](https://github.com/gaponukz/converter_service/assets/49754258/cb902df8-edbd-4f70-a482-e6b48a48ef25)
