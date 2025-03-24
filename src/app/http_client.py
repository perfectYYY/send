import socket
import ssl  # 新增 SSL 支持
import json

class HTTPClient:
    def __init__(self, host='1.94.23.202', port=443):  # 默认端口改为 HTTPS 的 443
        self.host = host
        self.port = port
        self.token = None

    def _build_http_request(self, method, path, body=None, headers=None):
        if headers is None:
            headers = {}

        # 关键修改：Host 头不包含端口（HTTPS 默认 443）
        headers['Host'] = self.host  # 原为 f'{self.host}:{self.port}'
        headers['Connection'] = 'close'
        headers['User-Agent'] = 'Python HTTP Client'

        if body:
            body_str = json.dumps(body)
            headers['Content-Type'] = 'application/json'
            headers['Content-Length'] = str(len(body_str.encode('utf-8')))

        # 确保路径以 '/' 开头
        if not path.startswith('/'):
            path = '/' + path
        request_line = f"{method} {path} HTTP/1.1\r\n"
        headers_str = ''.join([f"{k}: {v}\r\n" for k, v in headers.items()])
        full_request = request_line + headers_str + "\r\n"

        if body:
            full_request += body_str

        return full_request

    def _send_request(self, request):
        try:
            # 创建 SSL 上下文（验证服务器证书）
            context = ssl.create_default_context()
            # 如果是自签名证书，可临时禁用验证（生产环境不推荐！）
            # context.check_hostname = False
            # context.verify_mode = ssl.CERT_NONE

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                # 使用 SSL 包装 Socket
                with context.wrap_socket(sock, server_hostname=self.host) as ssock:
                    ssock.connect((self.host, self.port))
                    ssock.sendall(request.encode('utf-8'))

                    response = b''
                    while True:
                        chunk = ssock.recv(4096)
                        if not chunk:
                            break
                        response += chunk

                    # 处理可能的解码错误（如二进制内容）
                    response_str = response.decode('utf-8', errors='ignore')
                    if '\r\n\r\n' in response_str:
                        headers, body = response_str.split('\r\n\r\n', 1)
                    else:
                        headers, body = response_str, ''
                    status_line = headers.split('\r\n')[0]
                    status_code = int(status_line.split()[1])
                    return status_code, body
        except ssl.SSLError as e:
            print(f"SSL 错误: {e}")
            return None, None
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