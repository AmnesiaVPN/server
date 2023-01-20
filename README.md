
# Amnesia VPN server

Backend for Amnesia VPN server.



## API Reference

#### Create user

```http
  POST /api/users/
```

#### Get user by Telegram ID

```http
  GET /api/users/${telegram_id}/
```

| Parameter          | Type     | Description                           |
| :----------------- | :------- | :------------------------------------ |
| `telegram_id`      | `number` | **Required**. Telegram ID of the user |

#### Activate user's promocode

```http
  POST /api/users/${telegram_id}/promocodes/
```

| Parameter          | Type     | Description                           |
| :----------------- | :------- | :------------------------------------ |
| `telegram_id`      | `number` | **Required**. Telegram ID of the user |

#### Get user's config

```http
  GET /api/users/${telegram_id}/config/
```

| Parameter          | Type     | Description                           |
| :----------------- | :------- | :------------------------------------ |
| `telegram_id`      | `number` | **Required**. Telegram ID of the user |

## Installation

Setup WireGuard Easy Server

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

## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

`SECRET_KEY` - any string as your secret key.

`DEBUG` - debug mode (true, false).

`BOT_TOKEN` - token of your Telegram bot which will send notifications.

`DONATION_ALERTS_ACCESS_TOKEN` - token for donationalerts API.

`CELERY_BROKER_URL` - celery broker (redis recommended).

`DATABASE_HOST`
`DATABASE_PORT`
`DATABASE_NAME`
`DATABASE_USER`
`DATABASE_PASSWORD` - database settings.

`ALLOWED_HOSTS` - allowed hosts.

`PAYMENT_PAGE_URL` - page where users can buy subscription.

