from logic.auth import Auth
from logic.manager import Manager
from view.app import View


def run(name):
    print(f'{name} has been started!')

    auth = Auth()
    manager = Manager(auth)
    view = View(manager)
    view.display_view()


if __name__ == '__main__':
    run('FaceId')
