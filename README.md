# Cloud file storage

A file storage that allows you to share a file via a link with other people, customize file permissions, 
and display a list of the most downloaded files.

## Getting started
Fork project's [repository](https://github.com/DaniilDDDDD/b791695f-2051-45c4-bc5a-da485b98270c.git).
Load it to your machine.
You must have python3 installed and create [virtual environment](https://docs.python.org/3/library/venv.html).
To install all required packages open command prompt, activate virtual environment, go to project's directory and write
```pip instal requirements.txt```. When all packages would be installed use commands ```python manage.py collectstatic```
to collect project's static files and ```python manage.py runserver``` to run djnago server on 8000 port of your machine (for example ```localhost:8000```)

## Endpoints
All urls starts with domain name of your machine and port number on which you run the application.
For example ```http://localhost:8000``` or ```http://blablabla.bla:1234```.

### Registration
request:
* url: /api/user/
* method: POST
* data:
 ```
{
    'email': string,
    'username': string,
    'first_name': string,
    'last_name': string,
    'password': string
}
```
response:
```
{
    "email": string,
    "username": string,
    "first_name": string,
    "last_name": string,
    "id": integer
}
```

### Login
request:
* url /api/auth/token/login/
* method: POST
* data:
```
{
"email": string,
"password": string
}
```
response:
```
{
    "auth_token": string
}
```
To be authenticated you need to pass token to headers in your following requests, like here:
```
'Authorization': 'Token <your token>'
```

### Logout
request:
* requires authorization
* url /api/auth/token/login/
* method: GET

### Upload file
request:
* requires authorization
* url /api/files/
* method: POST
* data (in form-data format):
```
'file': file,
'access': string
```
response:
```
{
    "access": string,
    "file": string
}
```

### List files
Unauthorized users can read only public files.
Authorized users can read only public and their own files.

* url /api/files/
* method: GET
* query parameters:
```
limit: int - maximum items on one page
page: int - page number
```
response:
without query parameters:
```
[
    {
        "id": int, - file's id in database
        "access": string, - file's access type
        "file": string, - file name in database
        "download_count": int, - number of downloads
        "author": int - file authod's id
    }
]
```
with query parameters:
```
{
    "count": int, - number of elements on one page
    "next": string, - next page address
    "previous": string, - previous page address
    "results": [
        {
            "id": int,
            "access": string,
            "file": string,
            "download_count": int,
            "author": int
        }
    ]
}
```

### Update access to file
If file is ```public``` all users can view and download it.
If file is ```only_author``` only author of file can view and download it.
if file is ```by_link``` users can open it if they have link.
request:
* requires authorization
* url /api/files/<file_id_in_database>/
* method: PATCH
* data:
```
{
    'access': string
}
```
response:
```
{
    'id': int,
    'access': string
}
```

### Delete file
You can delete only your files.
request:
* requires authorization
* url: /api/files/<file_id_in_database>/
* method: DELETE

### Get link on your file
Get link on one of your file which you can share to other users.
request:
* requires authorization
* url: /api/files/<file_id_in_database>/link
* method: GET
response:
```
{
    "id": 16,
    "view_link": string, - link to view fiel
    "download_link": string - link to download file
}
```

### View file
To view your files you need to be authorized, unlike public files.
request:
* url: /api/files/view/<file_name_in_database>/
* method: GET

### Download file
To download your files you need to be authorized, unlike public files.
* url: /api/files/download/<file_name_in_database>/
* method: GET
