# PyHttp
```
usage: pyhttp [-h] [-o OUTPUT] [-t TIMEOUT] [--method METHOD] [--headers HEADERS [HEADERS ...]] [--cookies COOKIES [COOKIES ...]] [--body BODY] [-r]
              [--aheaders] [--nbody] [--srq] [-u USERNAME] [-p PASSWORD]
              url

positional arguments:
  url

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
  -t TIMEOUT, --timeout TIMEOUT
                        timeout in seconds
  --method METHOD
  --headers HEADERS [HEADERS ...]
  --cookies COOKIES [COOKIES ...]
  --body BODY
  -r, --redirect
  --aheaders
  --nbody
  --srq                 show sent request
  -u USERNAME, --username USERNAME
  -p PASSWORD, --password PASSWORD
```

Features
---
1. Контент не считывается без необходимости
(например, при автоматическом перенаправлении считывается только заголовок)
