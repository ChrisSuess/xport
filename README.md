# xport
The web portal for xbow/xflow

Instructions:

xport is not in pip yet. To install on a freshly-launched xbow cluster,
log in to the head node and then run:

```
sudo pip install git+git://github.com/CharlieLaughton/xport.git#egg=xport
```

Then activate the web interface:
```
sudo xport-config
```

Log out of the cluster, then find its URL using xbow-hostname:
```
xbow-hostname
```

Put the returned address into your web browser and you should be connected to the cluster.
