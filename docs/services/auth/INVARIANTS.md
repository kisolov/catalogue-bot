# auth — инварианты

| Правило | Где обеспечено |
|---|---|
| `initData` принимается, если подпись верна и `auth_date` не старше `TELEGRAM_INIT_DATA_MAX_AGE_SECONDS` (24 ч) и не «из будущего» (> 60 с) | [`TelegramInitDataService.validate`](../../../src/auth/telegram.py) |
| Ключ подписи = `HMAC_SHA256("WebAppData", bot_token)`; сравнение хэшей — `compare_digest` | там же |
| Поля `initData`, кроме `hash`, сортируются по ключу и склеиваются через `\n` — как требует [спецификация Telegram](https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app) | там же |
| Первый вход создаёт пользователя только с ролью `user`; роль существующего не меняется | [`LoginWithTelegram`](../../../src/auth/uc/telegram.py) |
| Одновременный первый вход одного пользователя не даёт двух записей и не падает | там же (перехват `UniqueViolation`) |
| Токен действителен, только пока он есть в Redis: `logout` отзывает его немедленно | [`TokenService.verify_token`](../../../src/auth/services.py) |
| Токен с битым `sub` или без него — `InvalidToken`, а не 500 | там же |
| Валидный токен удалённого пользователя — 401, не 404 | [`AuthenticateByToken`](../../../src/auth/uc/session.py) |
| Заголовок должен быть строго `Bearer <token>`; иначе 401 | [`get_bearer_token`](../../../src/bootstrap/dependencies/auth.py) |
| Один пользователь может иметь несколько активных токенов (по одному на вход) | `create_token` не отзывает прежние |

Тесты: [`test_auth.py`](../../../tests/cases/groups/test_auth.py),
хелпер подписи — [`tests/utils/telegram.py`](../../../tests/utils/telegram.py).
