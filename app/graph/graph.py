import atexit
from configparser import SectionProxy
import json
import os
import re

from azure.identity import InteractiveBrowserCredential
from msal import PublicClientApplication, SerializableTokenCache
import requests


class Graph:
    settings : SectionProxy
    access_token_cache : SerializableTokenCache
    app_client : PublicClientApplication
    interactive_code_credential : InteractiveBrowserCredential

    def __init__(self, config: SectionProxy) -> None:
        self.settings = config

        self.client_id = self.settings['client_id']
        self.authority = self.settings['authority']
        self.scope = str.split(self.settings['scope'])

        self.username = self.settings['username']
        self.password = self.settings['password']
        self.cache_file = self.settings['token_cache_file']
        self.access_token_cache = SerializableTokenCache()
        
        self.app_client = PublicClientApplication(
            client_id=self.client_id,
            authority=self.authority,
            token_cache=self.access_token_cache
        )

        self.token_response = dict()
    
    def generate_access_token(self, acquire_token_by='username_password' or 'interactive'):
        """Microsoft Graph API access token generator.
        Option to acquire token by username and password or interactively.
        MS will eventually remove the option to acquire token by username and password.
        """

        if os.path.exists(self.cache_file):
            self.access_token_cache.deserialize(open(self.cache_file, "r").read())

        atexit.register(lambda:
            open(self.cache_file, "w").write(self.access_token_cache.serialize())
            if self.access_token_cache.has_state_changed else None
            )

        accounts = self.app_client.get_accounts()

        if accounts:
            self.token_response  = self.app_client.acquire_token_silent(
                scopes=self.scope,
                account=accounts[0]
                )

        else:
            if acquire_token_by == 'username_password':
                self.token_response = self.app_client.acquire_token_by_username_password(
                    self.username,
                    self.password,
                    self.scope
                    )

            elif acquire_token_by == 'interactive':
                self.token_response = self.app_client.acquire_token_interactive(scopes=self.scope)

            else:
                raise ValueError('acquire_token_by must be either username_password or interactive')
        
        with open(self.cache_file, 'w') as _f:
            _f.write(self.access_token_cache.serialize())
        return self.token_response
    
    @staticmethod
    def create_headers(access_token: str):
        return {
            'Authorization': f"Bearer {access_token['access_token']}",
            'Content-Type': 'application/json'
            }
    
    
class EGL(Graph):
    def __init__(self, config: SectionProxy, headers: dict) -> None:
        super().__init__(config)

        self.headers = headers
        self.endpoint = self.settings['endpoint']
        self.egl_folder_id = self.settings['egl_folder_id']

        # Not currently used
        self.db_folder_id = self.settings['db_folder_id']
        self.cancel_folder_id = self.settings['cancel_folder_id']
        self.no_change_folder_id = self.settings['no_change_folder_id']
        self.no_voyage_folder_id = self.settings['no_voyage_folder_id']
        self.no_terminal_folder_id = self.settings['no_terminal_folder_id']
        self.not_for_us_folder_id = self.settings['not_for_us_folder_id']

        self.url = f'{self.endpoint}/me/mailFolders/{self.egl_folder_id}/messages'

        self.file_with_folder_ids = self.settings['file_with_folder_ids']

    
    def download_pdf_from_email(self) -> str:
        response = requests.get(
            self.url,
            headers=self.headers
            )
        
        dir_path = os.path.abspath(os.path.dirname(__file__))

        if response.ok:
            emails = response.json()['value']

            if not emails:
                print(f"No e-mails in folder.")
                exit()         
            else:
                last_email = emails.pop()

            email_id = last_email['id']
            
            email_url = f"{self.url}/{email_id}?$expand=attachments"
            email_response = requests.get(
                email_url,
                headers=self.headers
                )

            if email_response.ok:
                email_data = email_response.json()

                """ Check if e-mail has attachments. If not, exit.
                Then get the first attachment only and download it."""

                if not email_data['attachments']:
                    print(f"No attachments in e-mail.")
                    exit()
                
                attachment = email_data['attachments'][0]
                attachment_id = attachment['id']
                attachment_filename = attachment['name']

                # Check if attachment is a PDF
                if attachment['contentType'] == "application/pdf":

                    attachment_url = f"{self.url}/{email_id}/attachments/{attachment_id}/$value"

                    attachment_response = requests.get(
                        attachment_url, 
                        headers=self.headers
                        )

                    filename = os.path.join(dir_path,'pdfs', attachment_filename)
                    
                    if attachment_response.ok:
                        with open(filename, 'wb') as file:
                            file.write(attachment_response.content)

                            print(f"Attachment downloaded: {attachment_filename}" )

                    else:
                        print(f"Error downloading attachment: {attachment_filename}")
                                
            else:
                print(f"Error retrieving e-mail: {attachment_response.status_code, attachment_response.text}")

        return email_id
    

    def get_mail_subjects(self) -> list:
        response = requests.get(
            self.url,
            headers=self.headers
            )

        if response.ok:
            response = response.json()

            if "value" in response:
                pattern = r"^\d+"
                booking_numbers_in_folder = []

                for item in response['value']:
                    match = re.match(pattern, item['subject'])

                    if match is not None:
                        booking = match.group()

                        if len(booking) == 12:
                            booking_numbers_in_folder.append(booking)

        else:
            print(f"Error: {response.status_code, response.text}")

        return booking_numbers_in_folder
    

    def move_email_to_folder(self, email_id:str, folder:str) -> None:

        folder_dict = {
            'egl_folder_id': self.egl_folder_id,
            'db_folder_id': self.db_folder_id,
            'cancel_folder_id': self.cancel_folder_id,
            'no_change_folder_id': self.no_change_folder_id,
            'no_voyage_folder_id': self.no_voyage_folder_id,
            'no_terminal_folder_id': self.no_terminal_folder_id,
            'not_for_us_folder_id': self.not_for_us_folder_id
        }

        move_url = f"{self.url}/{email_id}/move"
        payload = {
            'destinationId': folder_dict[folder]
            }
        
        response = requests.post(
            move_url,
            headers=self.headers,
            json=payload
            )

        if response.status_code == 201:
            print(f"Email moved to folder")
        else:
            print(f"Error moving email: {response.status_code, response.text}")


    def get_folder_ids(self) -> None:
        response = requests.get(
            f"{self.endpoint}/me/mailfolders/{self.egl_folder_id}/childFolders",
            headers=self.headers
            ).json()
            
        json_str = json.dumps(response, indent=4)

        with open(self.file_with_folder_ids, 'w') as _f:
            _f.write(json_str)

        
