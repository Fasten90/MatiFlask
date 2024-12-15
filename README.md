# MatiFlask
Python Flask webserver for my son, Mati


# Test / websites
- menetrend
- menetrend?megallo=valami
- menetrend?megallo=lármákl utca
- menetrend?jarat=3
- menetrend?megallo=l%C3%A1rm%C3%A1kl%20utca&varos=Kiss%20jancsi
- bus?lines=True
- all_lines
- nyomtatas?megallo=lármákl utca
- get_all_nyomtatas


# Testing on server
server side:
```
export DB_PASSWORD=123...  
./start_local_server.sh
```

client side:
```
curl 127.0.0.1:5000/mati_adatbazis
```
