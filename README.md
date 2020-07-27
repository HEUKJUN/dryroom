## flask_web

```shell
virtualenv flask_web 
cd flask_web 
Scripts\activate.bat
> (flask_web) c:\apps\flask_web>
```

flask 라이브러리 설치

```shell
pip install flask
```

requirements.txt 로 라이브러리 관리

```powershell
pip freeze > requirements.txt
```

app.py 파일을 생성후 다음과 같은 코드 추가



```python
from flask import Flask ,render_template

app = Flask(__name__)
app.debug=True

@app.route('/data')
def index():
    print("Success")
    # return "TEST"
    return render_template('home.html', hello="GaryKim")

if __name__ =='__main__':
    # app.run(host='0.0.0.0', port='8080')
    app.run()
```





templates폴더 생성

teamplates/home.html

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>
<body>
    
    <h1>Hello {{ hello }} 님!!</h1>
   
</body>
</html>
```



navigation bar => navbar를 만들기 위해서 bootstrap 4 를 이용한다.

layouts.html생성후 다음과 같이 코딩

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css" integrity="sha384-9aIt2nRpC12Uk9gS9baDl411NQApFmC26EwAOH8WgZl5MYYxFfc+NcPb1dKGj7Sk" crossorigin="anonymous">
    
    <title>Flask_Web</title>
</head>
<body>
    
    
    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js" integrity="sha384-DfXdz2htPH0lsSSs5nCTpuj/zy4C+OGpamoFVy38MVBnE+IbbVYUew+OrCXaRkfj" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js" integrity="sha384-Q6E9RHvbIyZFJoft+2mJbHaEWldlvI9IOYy5n3zV9zzTtmI3UksdQRVvoxMfooAo" crossorigin="anonymous"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/js/bootstrap.min.js" integrity="sha384-OgVRvuATP1z7JjHLkuOU7Xw704+h835Lr+6QL9UvYjZE3Ipu6Tp75j7Bh/kR0JKI" crossorigin="anonymous"></script>
</body>
</html>
```