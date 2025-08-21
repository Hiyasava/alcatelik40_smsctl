# Alcatel LINKKEY IK40/IK41 SMS Tool

**Программа для работы с модемом Alcatel LINKKEY IK41VE1 для приема и отправки SMS сообщений**
**Alcatel LINKKEY IK40/IK41 SMS Tool for sending and receiving SMS messages via modem**

---

## Установка / Installation

```bash
git clone <репозиторий>
cd <папка проекта>
pip install -r requirements.txt
```

---

## Использование / Usage

Скрипт `alcatelik40_smsctl.py` поддерживает следующие команды:
The `alcatelik40_smsctl.py` script supports the following commands:

| Команда / Command                                                  | Русский / Russian                   | Английский / English         | Пример / Example                                            |
| ------------------------------------------------------------------ | ----------------------------------- | ---------------------------- | ----------------------------------------------------------- |
| `send <номер> <текст>`                                             | Отправка SMS                        | Send SMS                     | `python alcatelik40_smsctl.py send +79161234567 "Привет!"`  |
| `receive [--all] [--unread] [--contact <номер>] [--file] [--json]` | Получение SMS                       | Receive SMS                  | `python alcatelik40_smsctl.py receive --unread --file`      |
| `clear [--contact <номер>]`                                        | Удаление SMS                        | Clear SMS                    | `python alcatelik40_smsctl.py clear --contact +79161234567` |
| `monitor [--interval <секунды>]`                                   | Мониторинг новых SMS                | Monitor SMS                  | `python alcatelik40_smsctl.py monitor --interval 5`         |
| `debug`                                                            | Отладка, показать текущие настройки | Debug, show current settings | `python alcatelik40_smsctl.py debug`                        |
| `help`                                                             | Справка по командам                 | Help                         | `python alcatelik40_smsctl.py help`                         |

---

### Параметры команды receive / Receive command options

| Опция / Option      | Русский / Russian          | Английский / English |
| ------------------- | -------------------------- | -------------------- |
| `--all`             | Показать все сообщения     | Show all messages    |
| `--unread`          | Только непрочитанные       | Unread only          |
| `--contact <номер>` | Фильтр по номеру           | Filter by number     |
| `--file`            | Сохранить в текстовый файл | Save to text file    |
| `--json`            | Сохранить в JSON файл      | Save to JSON file    |

---

### Параметры команды monitor / Monitor command options

| Опция / Option         | Русский / Russian                                          | Английский / English                                   |
| ---------------------- | ---------------------------------------------------------- | ------------------------------------------------------ |
| `--interval <секунды>` | Интервал проверки новых сообщений (по умолчанию 10 секунд) | Polling interval for new messages (default 10 seconds) |

Новые сообщения будут записываться в файл `sms_messages/monitor_log.txt`.
New messages will be written to the file `sms_messages/monitor_log.txt`.

---

### Примеры / Examples

**Отправка SMS / Send SMS:**

```bash
python alcatelik40_smsctl.py send +79161234567 "Привет!"
```

**Получение непрочитанных сообщений и сохранение в файл / Receive unread messages and save to file:**

```bash
python alcatelik40_smsctl.py receive --unread --file
```

**Мониторинг новых сообщений каждые 5 секунд / Monitor incoming messages every 5 seconds:**

```bash
python alcatelik40_smsctl.py monitor --interval 5
```

**Очистка сообщений от конкретного контакта / Clear messages from specific contact:**

```bash
python alcatelik40_smsctl.py clear --contact +79161234567
```
