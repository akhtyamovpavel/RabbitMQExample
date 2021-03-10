### собрать проект
```docker-compose build```

### запустить всё
```docker-compose up -d```

### запустить конкретный сервис
```docker-compose up api```

### посмотреть логи
```docker-compose logs -f```

### посмотреть логи конкретного сервиса
```docker-compose logs api```


### остановить это всё
```docker-compose stop -t 1```

### удалить созданные образы
```docker-compose rm -f```


### Сервис доступен по адресу 
http://0.0.0.0:8080/

### RabbitMq доступен по адресу
http://0.0.0.0:15672/
