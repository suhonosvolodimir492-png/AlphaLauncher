# AlphaLauncher

Лаунчер Minecraft Java Edition для Windows (с поддержкой Linux и macOS по коду, основная цель — Windows).

## Возможности

- Установка версий Minecraft из официального манифеста Mojang (клиент, библиотеки, natives, ассеты) с проверкой SHA-1.
- Запуск игры с выбранными RAM, Java и JVM-аргументами.
- Вход через Microsoft (OAuth → Xbox Live → XSTS → Minecraft) и офлайн-режим.
- Несколько аккаунтов, выбор активного, автоматическое обновление токена Microsoft.
- Настройки: минимум и максимум ОЗУ, путь к Java (автопоиск и обзор), папка игры, дополнительные JVM-аргументы.
- Управление папкой `mods` (добавить, удалить, открыть).
- Все настройки и аккаунты сохраняются в `data/`.

## Структура папки

```
AlphaLauncher/
├─ main.py                  точка входа
├─ alphalauncher/           исходный код (см. ARCHITECTURE.md)
├─ tests/                   тесты ядра (стандартный unittest)
├─ assets/                  ассеты интерфейса (см. assets/README.md)
├─ data/                    создаётся при запуске: настройки, аккаунты, лог
├─ minecraft/               создаётся при запуске: игра (versions, libraries, assets, mods)
├─ requirements.txt         зависимости (только PySide6)
├─ build.bat                сборка AlphaLauncher.exe
├─ README.md / ARCHITECTURE.md / AGENTS.md
```

## Запуск из исходников

Нужен Python 3.10 или новее.

```bat
cd AlphaLauncher
python -m pip install -r requirements.txt
python main.py
```

Тесты ядра (не требуют PySide6 и интернета):

```bat
python -m unittest discover -s tests -t . -v
```

## Сборка AlphaLauncher.exe

Дважды щёлкните `build.bat` или запустите его из командной строки в папке проекта.
Скрипт устанавливает PySide6 и PyInstaller, собирает однофайловый exe и копирует его в `AlphaLauncher\AlphaLauncher.exe`.
Папки `assets`, `data` и `minecraft` должны лежать рядом с exe.

## Вход через Microsoft

1. Откройте «аккаунт» в левом нижнем углу → «Открыть страницу входа Microsoft».
2. Войдите в браузере. После входа браузер покажет пустую страницу — скопируйте её адрес целиком.
3. Вставьте адрес в поле лаунчера и нажмите «Войти».

Для входа нужна лицензия Minecraft Java Edition на аккаунте.

## Известные ограничения

- Для Microsoft-входа по умолчанию используется публичный client_id официального лаунчера (`MS_CLIENT_ID` в `alphalauncher/config.py`). Для публичного распространения зарегистрируйте собственное приложение в Azure и замените значение. Подробности — в ARCHITECTURE.md.
- Java не скачивается автоматически. Установите нужную версию (Java 21 для Minecraft 1.20.5 и новее) и укажите путь или используйте «Найти Java».
- Токены хранятся в `data/accounts.json` в открытом виде. Не передавайте этот файл третьим лицам.
- Виртуальные ассеты (версии до 1.6) не поддерживаются.
- Моды работают только с установленным загрузчиком (Fabric, Forge, NeoForge); сам лаунчер их не устанавливает.
