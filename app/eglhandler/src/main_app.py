import yaml

from eglhandler.src.widget.app import EGLApp
from eglhandler.src.graph.graph import Graph, EGL

def run_application():
    """ Main function"""

    with open(r"app\eglhandler\config.yaml", 'r') as _f:
        config = yaml.safe_load(_f)

    """ Set up graph- and egl objects."""
    graph: Graph = Graph(config)
    access_token = graph.generate_access_token(acquire_token_by="username_password")
    headers = graph.create_headers(access_token)
    egl: EGL = EGL(config, headers)
    email_count= egl.count_emails_in_folder()
    database = r"app\eglhandler\sqlite\egl_sqlite.db"

    app = EGLApp(config, database)
    app.write_out_booking_count(email_count)
    app.run_widget()


if __name__ == "__main__":
    run_application()