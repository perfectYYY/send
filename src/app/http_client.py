import socket  
import json  

class HTTPClient:  
    def __init__(self, host='localhost', port=5001):  
        self.host = host  
        self.port = port  
        self.token = None  

    def _build_http_request(self, method, path, body=None, headers=None):  
        if headers is None:  
            headers = {}  

        headers['Host'] = f'{self.host}:{self.port}'  
        headers['Connection'] = 'close'  
        headers['User-Agent'] = 'Python HTTP Client'  

        if body:  
            body_str = json.dumps(body)  
            headers['Content-Type'] = 'application/json'  
            headers['Content-Length'] = str(len(body_str.encode('utf-8')))  

        request_line = f"{method} {path} HTTP/1.1\r\n"  
        headers_str = ''.join([f"{k}: {v}\r\n" for k, v in headers.items()])  
        full_request = request_line + headers_str + "\r\n"  

        if body:  
            full_request += body_str  

        return full_request  

    def _send_request(self, request):  
        try:  
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:  
                sock.connect((self.host, self.port))  
                sock.sendall(request.encode('utf-8'))  

                response = b''  
                while True:  
                    chunk = sock.recv(4096)  
                    if not chunk:  
                        break  
                    response += chunk  

                response_str = response.decode('utf-8')  
                headers, body = response_str.split('\r\n\r\n', 1)  
                status_line = headers.split('\r\n')[0]  
                status_code = int(status_line.split()[1])  

                return status_code, body  

        except Exception as e:  
            print(f"请求发送失败: {e}")  
            return None, None  

    def login(self, username, password):  
        """用户登录"""  
        body = {  
            'username': username,  
            'password': password  
        }  
        request = self._build_http_request('POST', '/login', body=body)  
        status_code, response_body = self._send_request(request)  

        if status_code == 200:  
            response_data = json.loads(response_body)  
            self.token = response_data.get('token')  
            print("登录成功")  
            return self.token  
        else:  
            print("登录失败")  
            return None  

    def invoke_drone_api(self, endpoint, method='GET', data=None):  
        """调用无人机 API 接口"""  
        path = f"/{endpoint}"  
        headers = {}  
        if self.token:  
            headers['Authorization'] = f'Bearer {self.token}'  

        if method == 'POST':  
            return self._send_request(self._build_http_request('POST', path, body=data, headers=headers))  
        else:  
            return self._send_request(self._build_http_request('GET', path, headers=headers))  