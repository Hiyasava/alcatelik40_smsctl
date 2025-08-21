# Руководство пользователя alcatelik40_smsctl

## Содержание
1. [Введение](#введение)
2. [Системные требования](#системные-требования)
3. [Установка и настройка](#установка-и-настройка)
4. [Основные команды](#основные-команды)
5. [Примеры использования](#примеры-использования)
6. [Автоматизация в Windows](#автоматизация-в-windows)
7. [Автоматизация в Linux](#автоматизация-в-linux)
8. [Устранение неполадок](#устранение-неполадок)
9. [Безопасность](#безопасность)
10. [Часто задаваемые вопросы](#часто-задаваемые-вопросы)

## Введение

**alcatelik40_smsctl** — это утилита командной строки для работы с SMS-сообщениями через модем Alcatel Linkkey IK40V/IK41VE1. 
Она позволяет отправлять и получать SMS без использования веб-интерфейса модема, что удобно для автоматизации и интеграции с другими системами.

**Основные возможности:**
- Отправка SMS сообщений
- Просмотр входящих и исходящих сообщений
- Фильтрация сообщений по номерам и статусу
- Сохранение сообщений в текстовом и JSON форматах
- Автоматизация процессов через планировщик задач (Windows) и cron/systemd (Linux)
- Пакетное удаление сообщений

## Системные требования

**Минимальные требования:**
- Windows 7/8/10/11, Linux, macOS
- Python 3.6+
- Модем Alcatel Linkkey IK40V или IK41VE1
- Подключение к интернету через модем

**Необходимые компоненты:**
- Python 3.x
- requests (`pip install requests`)

## Установка и настройка

1. Установите Python 3.x ([python.org](https://python.org/downloads))
2. Установите зависимости:
   ```bash
   pip install requests
   ```
3. Сохраните файл `alcatelik40_smsctl.py`
4. Подключите модем и убедитесь, что доступен адрес (обычно `192.168.1.1`)

## Основные команды

### Отправка SMS
```bash
python alcatelik40_smsctl.py send <номер> "<сообщение>"
```

### Получение сообщений
```bash
# Все сообщения
python alcatelik40_smsctl.py receive --all

# Только непрочитанные
python alcatelik40_smsctl.py receive --unread

# От конкретного номера
python alcatelik40_smsctl.py receive --contact +79081131592
```

### Удаление сообщений
```bash
# Удалить все
python alcatelik40_smsctl.py clear

# Удалить по номеру
python alcatelik40_smsctl.py clear --contact +79081131592
```

### Справка и отладка
```bash
python alcatelik40_smsctl.py help
python alcatelik40_smsctl.py debug
```

## Автоматизация в Windows

- Использование BAT-файлов
- Планировщик заданий
- Интеграция с Zabbix/Nagios
- Автозагрузка и службы

## Автоматизация в Linux

### 1. Cron
Для регулярной проверки сообщений:
```bash
crontab -e
```
Добавьте строку:
```bash
*/15 * * * * /usr/bin/python3 /path/to/alcatelik40_smsctl.py receive --unread --json >> /var/log/sms.log 2>&1
```

### 2. systemd service
Файл `/etc/systemd/system/sms.service`:
```ini
[Unit]
Description=SMS Monitor Service
After=network.target

[Service]
ExecStart=/usr/bin/python3 /path/to/alcatelik40_smsctl.py receive --unread --json
WorkingDirectory=/path/to/
Restart=always

[Install]
WantedBy=multi-user.target
```

Запуск:
```bash
sudo systemctl daemon-reload
sudo systemctl enable sms.service
sudo systemctl start sms.service
```

## Устранение неполадок

- Проверьте подключение модема (`192.168.1.1`)
- Убедитесь, что баланс SIM положительный
- Проверьте версию Python: `python --version`
- Для логирования: 
  ```bash
  python alcatelik40_smsctl.py receive --all > sms_log.txt 2>&1
  ```

## Безопасность

- Храните логи и SMS в защищённых каталогах
- Используйте шифрование при необходимости
- Регулярно удаляйте ненужные сообщения

## Часто задаваемые вопросы

**Q:** Не отправляются SMS  
**A:** Проверьте баланс и правильность номера  

**Q:** Как запускать автоматически?  
**A:** Используйте Windows Task Scheduler или cron/systemd в Linux  

---

# User Guide alcatelik40_smsctl (English)

## Contents
1. [Introduction](#introduction)
2. [System Requirements](#system-requirements)
3. [Installation & Setup](#installation--setup)
4. [Basic Commands](#basic-commands)
5. [Usage Examples](#usage-examples)
6. [Automation on Windows](#automation-on-windows)
7. [Automation on Linux](#automation-on-linux)
8. [Troubleshooting](#troubleshooting)
9. [Security](#security)
10. [FAQ](#faq)

## Introduction

**alcatelik40_smsctl** is a command-line utility for managing SMS via Alcatel Linkkey IK40V/IK41VE1 modem.  
It allows sending/receiving SMS without using the modem's web interface, making it convenient for automation and integration.

**Features:**
- Send SMS messages
- View incoming and outgoing SMS
- Filter messages by number and status
- Save messages in TXT or JSON
- Automation via Windows Task Scheduler or Linux cron/systemd
- Bulk delete messages

## System Requirements

- Windows 7/8/10/11, Linux, macOS
- Python 3.6+
- Alcatel Linkkey IK40V or IK41VE1 modem
- Internet access via modem
- requests library (`pip install requests`)

## Installation & Setup

1. Install Python 3.x ([python.org](https://python.org/downloads))
2. Install dependencies:
   ```bash
   pip install requests
   ```
3. Save `alcatelik40_smsctl.py` in a working directory
4. Connect modem and ensure access (default `192.168.1.1`)

## Basic Commands

### Send SMS
```bash
python alcatelik40_smsctl.py send <number> "<message>"
```

### Receive SMS
```bash
python alcatelik40_smsctl.py receive --all
python alcatelik40_smsctl.py receive --unread
python alcatelik40_smsctl.py receive --contact +1234567890
```

### Delete SMS
```bash
python alcatelik40_smsctl.py clear
python alcatelik40_smsctl.py clear --contact +1234567890
```

### Help & Debug
```bash
python alcatelik40_smsctl.py help
python alcatelik40_smsctl.py debug
```

## Automation on Windows

- BAT scripts  
- Task Scheduler  
- Monitoring integration (Zabbix/Nagios)  
- Autostart & Services  

## Automation on Linux

### 1. Cron
```bash
*/15 * * * * /usr/bin/python3 /path/to/alcatelik40_smsctl.py receive --unread --json >> /var/log/sms.log 2>&1
```

### 2. systemd Service
File: `/etc/systemd/system/sms.service`
```ini
[Unit]
Description=SMS Monitor Service
After=network.target

[Service]
ExecStart=/usr/bin/python3 /path/to/alcatelik40_smsctl.py receive --unread --json
WorkingDirectory=/path/to/
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl daemon-reload
sudo systemctl enable sms.service
sudo systemctl start sms.service
```

## Troubleshooting

- Check modem connection (`192.168.1.1`)  
- Ensure SIM balance is positive  
- Verify Python version: `python --version`  
- Log errors:  
  ```bash
  python alcatelik40_smsctl.py receive --all > sms_log.txt 2>&1
  ```

## Security

- Store SMS data in protected directories  
- Use encryption if needed  
- Regularly clean old messages  

## FAQ

**Q:** SMS not sent?  
**A:** Check SIM balance and number format.  

**Q:** How to automate?  
**A:** Use Task Scheduler (Windows) or cron/systemd (Linux).  

---

*Version 1.0 – Last update: 21.08.2025*
