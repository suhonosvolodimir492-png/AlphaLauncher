# Архитектура AlphaLauncher

## Слои

Зависимости направлены только вниз. Нижние слои ничего не знают о верхних.

```
main.py
  └─ ui/          PySide6: окна, страницы, диалоги, фоновые задачи (QThread)
       └─ services/   фасад бизнес-логики без Qt (GameService)
            ├─ auth/        аккаунты и вход Microsoft
            ├─ settings/    модель и хранилище настроек
            └─ minecraft/   манифест, пути, установка, Java, команда запуска, процесс
                 └─ core/   ошибки, HTTP, файлы, правила Mojang, система
config.py   константы и пути (не зависит от остального кода)
```

Правило: всё в `core/`, `auth/`, `settings/`, `minecraft/`, `services/` работает без Qt и тестируется через `unittest`. Файлы `ui/` только вызывают сервисы и отображают результат.

## Модули

| Модуль | Ответственность |
|---|---|
| `config.py` | Имена, URL, пути (`ROOT`, `DATA_DIR`, `DEFAULT_GAME_DIR`), определение папки при запуске из exe |
| `core/errors.py` | `LauncherError` и наследники. Текст ошибки показывается пользователю |
| `core/http.py` | `get_json`, `post_json`, `post_form`, `download_file` (потоковая запись в `.part`, SHA-1, отмена) |
| `core/files.py` | `read_json`, `write_json_atomic`, `sha1_of`, `extract_natives` (с защитой от path traversal) |
| `core/rules.py` | `is_allowed` — правила `rules` из version JSON (ОС, архитектура, features) |
| `core/system.py` | Объём ОЗУ (WinAPI), открытие папок |
| `auth/accounts.py` | `Account`, `offline_uuid`, `AccountStore` (JSON, активный аккаунт) |
| `auth/microsoft.py` | `MicrosoftAuthenticator`: код → токены Live → Xbox → XSTS → Minecraft → профиль и лицензия |
| `settings/settings.py` | `Settings` (frozen dataclass), `normalize_settings`, `SettingsStore` |
| `minecraft/paths.py` | `GamePaths` (пути структуры игры), `maven_relative_path`, `library_relative_path` |
| `minecraft/manifest.py` | Список версий (с кэшем для офлайн-режима), загрузка version JSON |
| `minecraft/installer.py` | `GameInstaller.install`: параллельные загрузки, ассеты, natives, маркер `.installed` |
| `minecraft/java.py` | Поиск Java, определение major-версии, `pick_java` |
| `minecraft/launch_args.py` | `build_launch_command` — чистая функция: meta + пути + опции → список аргументов |
| `minecraft/process.py` | `start_game` (запуск Popen) |
| `services/game_service.py` | `GameService`: единая точка для UI (версии, установка, запуск, аккаунты, моды, Java) |
| `ui/theme.py` | Палитра, QSS, поиск ассетов `find_asset` |
| `ui/workers.py` | `TaskWorker` (QThread) и `TaskRunner` — одна фоновая задача за раз, результат в главном потоке |
| `ui/context.py` | `PageContext`: сервисы, runner, навигация и уведомления, передаваемые страницам |
| `ui/main_window.py` | Боковая панель, стек страниц с fade-переходом, баннер задачи, отслеживание процесса игры |
| `ui/home_page.py` | Hero, кнопка «Играть», карточки версии, аккаунта и папки |
| `ui/versions_page.py` | Список версий, установка, выбор, открытие папки |
| `ui/mods_page.py` | Файлы `.jar` в `mods` |
| `ui/settings_page.py` | Настройки ОЗУ, Java, папки, JVM-аргументы |
| `ui/accounts_dialog.py` | Офлайн-аккаунт, вход Microsoft, выбор и удаление |
| `ui/widgets.py` | `LogoMark`, `Card`, `InfoCard`, `HeroBackground`, `TaskBanner` |

## Поток данных: «Играть»

1. `HomePage._play` проверяет выбранную версию и аккаунт.
2. `TaskRunner.run` запускает `GameService.launch` в `QThread`. Прогресс приходит сигналами в `TaskBanner`.
3. `launch`: обновляет токен Microsoft при необходимости → читает или загружает version JSON → ставит версию, если не установлена (`GameInstaller.install`) → выбирает Java (`pick_java`) → собирает команду (`build_launch_command`) → запускает процесс (`start_game`).
4. Главное окно получает `Popen` через callback и опрашивает его таймером раз в секунду, чтобы показать код выхода при сбое.

## Установка версии

`GameInstaller.install(meta)` выполняет три этапа:

1. Клиент, библиотеки и индекс ассетов (`_run_tasks`, до 8 потоков). Библиотеки отбираются по `rules`. Для natives выбирается классификатор текущей ОС.
2. Объекты ассетов из индекса. Одинаковые хеши скачиваются один раз.
3. Распаковка natives (только для библиотек старого формата) и запись `.installed`.

Файл, уже скачанный с верной SHA-1, не загружается повторно. Частично скачанные файлы хранятся как `*.part` и не попадают в итоговые пути.

## Авторизация

Вход Microsoft использует OAuth-код, который пользователь получает в браузере и вставляет в лаунчер (`redirect_uri = https://login.live.com/oauth20_desktop.srf`). Локальный сервер не нужен.

Цепочка: `login.live.com` (токен) → `user.auth.xboxlive.com` → `xsts.auth.xboxlive.com` → `api.minecraftservices.com/authentication/login_with_xbox` → `entitlements/mcstore` (проверка лицензии) → `minecraft/profile`.

Ошибки XSTS (`XErr`) переводятся в понятные сообщения (см. `_XSTS_ERRORS` в `auth/microsoft.py`).

**Client ID.** `MS_CLIENT_ID` сейчас совпадает с публичным client_id официального лаунчера, который используют многие открытые проекты. Для собственного распространения создайте приложение в Azure AD с нужными разрешениями, укажите его `client_id` и проверьте условия использования Mojang и Microsoft.

## Расширение без переписывания

- **Новый экран:** создайте `ui/<name>_page.py` с классом, который принимает `PageContext`. Добавьте его в `_NAV_ITEMS` и `self._pages` в `main_window.py`. Если страница должна обновляться при открытии, добавьте метод `on_show()`.
- **Новая фоновая операция:** добавьте метод в `GameService`, который принимает `progress` и `cancel`, и вызывайте его через `ctx.runner.run(...)`.
- **Загрузчики модов (Fabric, Forge):** добавьте модуль `minecraft/loaders/` с функцией, которая сливает version JSON загрузчика с ванильным (через `inheritsFrom`). Затем подайте результат в `GameInstaller` и `build_launch_command` без изменений в них.
- **Новый способ входа:** добавьте класс в `auth/` с методами `login_*` и `refresh` и возвращайте `Account`. Тип `kind` определяет, как собирается `user_type`.
- **Автоматическая загрузка Java:** модуль `minecraft/runtime.py`, который вызывает `pick_java` при отсутствии подходящей версии.

## Ограничения текущей версии

- Виртуальные ассеты (`map_to_resources`, версии до 1.6) не поддерживаются.
- Java не устанавливается автоматически.
- Проверка версии ОС в правилах `rules` не выполняется (см. комментарий в `core/rules.py`).
- Токены хранятся в открытом виде в `data/accounts.json`. Для защиты можно использовать DPAPI через `ctypes`.
