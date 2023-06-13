import atexit
import json
import os
import re
from configparser import SectionProxy

import requests
from msal import PublicClientApplication, SerializableTokenCache
from tqdm import tqdm

from eglhandler.src.parser.parser_functions import cfg_to_dict


class Graph:
    """Microsoft Graph API handler.
    
    Attributes:
        settings (SectionProxy): Config settings.
        access_token_cache (SerializableTokenCache): Token cache.
        app_client (PublicClientApplication): MSAL client.
        token_response (dict): Token response.

    :param config: Config settings.
    """

    settings : SectionProxy
    access_token_cache : SerializableTokenCache
    app_client : PublicClientApplication
    token_response : dict

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

        self.token_response = None
    
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
    

    def create_headers(self, access_token: str):
        return {
            'Authorization': f"Bearer {access_token['access_token']}",
            'Content-Type': 'application/json'
            }
    
    
class EGL(Graph):
    """EGL Graph API handler.

    :param config: ConfigParser object with settings.
    :param headers: Dictionary with headers for requests.
    :param folder: Name of folder to download e-mails from. Optional.
    """

    def __init__(self, config: SectionProxy, headers: dict, folder: str=None) -> None:
        super().__init__(config)

        self.headers = headers
        self.endpoint = self.settings['endpoint']
        if folder is None:
            folder = 'main_folder_id'
        self.main_folder_id = self.settings[folder]

        self.db_folder_id = self.settings['db_folder_id']
        self.cancel_folder_id = self.settings['cancel_folder_id']
        self.no_change_folder_id = self.settings['no_change_folder_id']
        self.no_voyage_folder_id = self.settings['no_voyage_folder_id']
        self.no_terminal_folder_id = self.settings['no_terminal_folder_id']
        self.not_for_us_folder_id = self.settings['not_for_us_folder_id']

        self.url = f'{self.endpoint}/me/mailFolders/{self.main_folder_id}/messages'

        self.file_with_folder_ids = self.settings['file_with_folder_ids']
        self.dir_path = os.path.abspath(os.path.dirname(__file__))

    
    def download_pdf_from_email(self, config: SectionProxy, dir_path: str=None) -> str:
        """Download PDF attachment from e-mail.
        Will download the attachment from last e-mail in folder.

        :param config: ConfigParser object with settings.
        """

        if dir_path is not None:
            self.dir_path = dir_path

        response = requests.get(
            self.url,
            headers=self.headers
            )

        if not response.ok:
            print(f"Error retrieving e-mails: {response.status_code, response.text}")
            return None

        emails = response.json()['value']

        if not emails:
            print(f"No e-mails in folder.")
            return None         
        else:
            last_email = emails.pop()
        
        self.email_body_preview = last_email['bodyPreview']
        email_id = last_email['id']

        terminal_found_in_email = self._check_bodypreview_for_terminal(config)
        
        email_url = f"{self.url}/{email_id}?$expand=attachments"
        email_response = requests.get(
            email_url,
            headers=self.headers
            )

        if not email_response.ok:
            print(f"Error retrieving e-mail: {attachment_response.status_code, attachment_response.text}")
            return None
        
        email_data = email_response.json()

        """ Check if e-mail has attachments. If not, exit.
        Then get the first attachment only and download it."""
        if not email_data['hasAttachments']:
            print(f"No attachments in e-mail.")
            return None
        
        attachment = email_data['attachments'][0]
        attachment_id = attachment['id']
        attachment_filename = attachment['name']

        # Check if attachment is a PDF
        if attachment['contentType'] != "application/pdf":
            print(f"Attachment is not a PDF: {attachment_filename}")
            return None

        attachment_url = f"{self.url}/{email_id}/attachments/{attachment_id}/$value"

        attachment_response = requests.get(
            attachment_url, 
            headers=self.headers
            )

        filename = os.path.join(self.dir_path, attachment_filename)
        
        if not attachment_response.ok:
            print(f"Error retrieving attachment: {attachment_response.status_code, attachment_response.text}")
            
        with open(filename, 'wb') as file:
            file.write(attachment_response.content)

        print(f"Attachment downloaded: {attachment_filename}")
                            
        return email_id, terminal_found_in_email, attachment_filename
    

    def _check_bodypreview_for_terminal(self, config: SectionProxy) -> str:
        """
        """
        dict_with_terminal_names = cfg_to_dict(config, section_num=3)
        terminal_names = list(dict_with_terminal_names.keys())

        body_preview = self.email_body_preview.upper()

        for terminal in terminal_names:
            # self.
            if terminal in body_preview: 
                found_terminal = dict_with_terminal_names[terminal]
                return found_terminal
        return None


    def download_pdfs_from_all_emails(self, url: str=None) -> str:
        """Download all PDFs from all e-mails in folder.
        Requires a bit more set up to work and should not be used very often."""

        if url is not None:
            response = requests.get(
                f"{url}",
                headers=self.headers
            )
        else:
            response = requests.get(
                f"{self.url}?$top=100",
                headers=self.headers
                )
        
        if not response.ok:
            print(f"Error retrieving e-mails: {response.status_code, response.text}")
            return None

        response_data = response.json()
        emails = response_data['value']

        """This is the return value of the function.
        Used to get the next page of e-mails."""
        next_link = '@odata.nextLink'
        if next_link in response_data:
            next_url_page = response_data[next_link]
        else:
            next_url_page = None

        # Loop through all e-mails in page
        for email in tqdm(emails):
            email_id = email['id']

            
            if not email['hasAttachments']:
                print(f"No attachments in e-mail.")
                continue

            email_url = f"{self.url}/{email_id}?$expand=attachments"
            email_response = requests.get(
                email_url,
                headers=self.headers
                )

            if not email_response.ok:
                print(f"Error retrieving email: {email_response.status_code}, {email_response.text}")
                continue

            email_data = email_response.json()
            
            # Only get the first attachment
            attachment = email_data['attachments'][0]
            attachment_id = attachment['id']
            attachment_filename = attachment['name']

            # Check if attachment is a PDF
            if attachment['contentType'] != "application/pdf":
                continue

            attachment_url = f"{self.url}/{email_id}/attachments/{attachment_id}/$value"

            attachment_response = requests.get(
                attachment_url, 
                headers=self.headers
                )

            # Full filepath to save PDF
            filename = os.path.join(self.dir_path,'pdfs', attachment_filename)
            
            if not attachment_response.ok:
                print(f"Error downloading attachment: {attachment_filename}")
                continue
            try:
                with open(filename, 'wb') as file:
                    file.write(attachment_response.content)
            except:
                print(f"Error saving file: {attachment_filename}")

        return next_url_page, len(emails)
    

    def count_emails_in_folder(self):
        """Count the number of e-mails in folder and return it"""

        url = f"{self.endpoint}/me/mailFolders/{self.main_folder_id}?$select=totalItemCount"
        response = requests.get(
            url,
            headers=self.headers
        )

        if not response.ok:
            print(f"Error: {response.status_code, response.text}")
            return None
        
        return response.json()['totalItemCount']
    

    def get_booking_numbers_in_subjects(self) -> list:
        """Get all booking numbers from subjects in folder."""

        response = requests.get(
            self.url,
            headers=self.headers
            )

        if not response.ok:
            print(f"Error: {response.status_code, response.text}")
            return None
        
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
           

        return booking_numbers_in_folder
    

    def move_email_to_folder(self, email_id:str, folder:str) -> None:
        """Move e-mail to folder. Used in conjunction with get_email_id_from_folder.

        Folder can be one of the following:
        main_folder_id,
        db_folder_id,
        cancel_folder_id,
        no_change_folder_id,
        no_voyage_folder_id,
        no_terminal_folder_id,
        not_for_us_folder_id
        
        Example:
        move_email_to_folder(email_id, 'main_folder_id')
        """

        folder_dict = {
            'main_folder_id': self.main_folder_id,
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


    def get_folder_ids(self, folder: str=None) -> None:
        """Get all folder ids and save to file.
        
        :param folder: Folder to get ids from. Default is main_folder_id."""

        if folder is None:
            folder = self.main_folder_id

        response = requests.get(
            f"{self.endpoint}/me/mailfolders/{folder}/childFolders",
            headers=self.headers
            ).json()
            
        json_str = json.dumps(response, indent=4)

        with open(self.file_with_folder_ids, 'w') as _f:
            _f.write(json_str)

        
