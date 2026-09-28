# auth — сценарии

## Вход через Telegram

```
Mini App → POST /auth/telegram {init_data}
  → LoginWithTelegram
      → TelegramInitDataService.validate   (подпись, auth_date)      → 401 при отказе
      → UserService.get_by_telegram_id
          нет → UserService.create(role=user)
          гонка (UniqueViolation) → повторный get_by_telegram_id
      → TokenService.create_token          (JWT + Redis SET с TTL)
  ← {access_token, token_type, user}
```

## Запрос с токеном

```
Authorization: Bearer <jwt> → get_bearer_token → get_current_user
  → AuthenticateByToken
      → TokenService.verify_token   (подпись, exp, ключ есть в Redis)
      → UserService.get_by_id       (нет → InvalidToken, 401)
  ← User → endpoint
```

## Выход

```
POST /auth/logout → Logout → TokenService.revoke_token → Redis DEL
```

Только текущий токен; токены с других устройств остаются действительными.
