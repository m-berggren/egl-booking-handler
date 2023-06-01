import configparser 

from graph import Graph, EGL


def main():

    config = configparser.ConfigParser()
    config.read(['setup.cfg', 'setup.dev.cfg'])
    azure_settings = config['azure']

    graph: Graph = Graph(azure_settings)

    # Option to set acquire_token_by to 'interactive' or 'username_password' as arguments to generate_access_token()
    access_token = graph.generate_access_token(acquire_token_by='username_password')

    # Call create_headers() after generate_access_token() to update the headers with the new access token
    headers = graph.create_headers(access_token)

    egl: EGL = EGL(azure_settings, headers)

    subjects = egl.get_mail_subjects()
    print(subjects)
    
    email_id = egl.download_pdf_from_email()
    egl.move_email_to_folder(email_id, folder='db_folder_id')

main()