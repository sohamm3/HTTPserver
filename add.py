status_codes = {200 : 'OK',
                201 : 'Created',
                204 : 'No Content',
                301 : 'Moved Permanently',
                304 : 'Not Modified',
                400 : 'Bad Request',
                401 : 'Unauthorized',
                403 : 'Forbidden',
                404 : 'Not Found',
                405 : 'Method Not Allowed',
                408 : 'Request Timeout',
				411 : 'Length Required',
                413 : 'Payload Too Large',
                414 : 'URI Too Long',
				415 : 'Unsupported Media Type',
                500 : 'Internal Server Error',
                501 : 'Not Implemented',
                502 : 'Bad Gateway',
				503 : 'Service Unavailable',
                505 : 'HTTP Version not Supported'
                }

http_versions = ['HTTP/1.0', 'HTTP/1.1']

mime_types = ['text/html', 'text/css', 'text/plain', 'text/csv',
                'application/pdf', 'application/json', 'audio/mpeg',
                'image/jpeg', 'image/png', 'image/gif', 'video/mp4']

binary_extensions = ['png', 'jpg', 'jpeg', 'mp3', 'mp4', 'pdf', 'gif']

Allow = ['GET', 'HEAD', 'DELETE', 'PUT', 'POST']