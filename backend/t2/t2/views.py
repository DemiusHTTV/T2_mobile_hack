from django.http import HttpRequest, HttpResponse


def index(_request: HttpRequest) -> HttpResponse:
    return HttpResponse(
        """
<!doctype html>
<html lang="ru">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <title>t2 backend</title>
  </head>
  <body>
    <h1>t2 backend</h1>
    <ul>
      <li><a href="/admin/">Админка</a></li>
      <li><a href="/api/shifts/">API смен</a> (нужна авторизация)</li>
    </ul>
  </body>
</html>
""".strip(),
        content_type="text/html; charset=utf-8",
    )
