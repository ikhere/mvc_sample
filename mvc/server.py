from mvc.api.router import APIRouter
from paste.httpserver import serve


if __name__ == '__main__':
    serve(APIRouter.factory(), host='0.0.0.0', port='9090')
