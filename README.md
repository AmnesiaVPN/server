# Vobla VPN Server


## Setup WireGuard Easy Server

GitHub Source: https://github.com/WeeJeWel/wg-easy

```docker
docker run -d \
  --name=wg-easy \
  -e WG_HOST=🚨YOUR_SERVER_IP \
  -e PASSWORD=🚨YOUR_ADMIN_PASSWORD \
  -v ~/.wg-easy:/etc/wireguard \
  -p 51820:51820/udp \
  -p 51821:51821/tcp \
  --cap-add=NET_ADMIN \
  --cap-add=SYS_MODULE \
  --sysctl="net.ipv4.conf.all.src_valid_mark=1" \
  --sysctl="net.ipv4.ip_forward=1" \
  --restart unless-stopped \
  weejewel/wg-easy
```

> Replace YOUR_SERVER_IP with your WAN IP, or a Dynamic DNS hostname.
>
> Replace YOUR_ADMIN_PASSWORD with a password to log in on the Web UI.
