from evernote.edam.notestore.ttypes import NoteFilter, NotesMetadataResultSpec
from evernote.api.client import EvernoteClient

import random
from datetime import datetime

from gmail import send_mail

# DO NOT CHANGE
MAX_NOTES_RETURNABLE = 250  # Max number of notes Evernote API can return in a single filter query
SERVICE = "www.evernote.com"

# CHANGE
PROD_DEVELOPER_TOKEN = ""

SELECTED_TAG = "Daily-Email"  # Randomly choose between notes with this tag
NUM_NOTES_TO_EMAIL = 5
SENDING_EMAIL = ""
RECEIVING_EMAIL = ""


if __name__ == "__main__":
    client = EvernoteClient(token=PROD_DEVELOPER_TOKEN, 
                            sandbox=False)

    userStore = client.get_user_store()
    user = userStore.getUser()
    user_id = user.id
    shard_id = user.shardId

    noteStore = client.get_note_store()

    # Get the unique GUID for the tag that we want
    tag_infos = noteStore.listTags()
    selected_tag_obj = [tag for tag in tag_infos if tag.name == SELECTED_TAG]
    if len(selected_tag_obj) == 0:
        raise Exception("Selected tag not found")
    selected_tag_guid = selected_tag_obj[0].guid

    # Filter by the guid of the tag that we want
    filter = NoteFilter(tagGuids=[selected_tag_guid])
    resultSpec = NotesMetadataResultSpec(includeTitle=True, includeTagGuids=True)

    note_metadata = noteStore.findNotesMetadata(filter, 0, MAX_NOTES_RETURNABLE, resultSpec)
    num_notes_found = note_metadata.totalNotes

    notes_to_select_from = []

    # If num notes with this tag is greater than MAX_NOTES_RETURNABLE need to iterate
    for offset in range(0, num_notes_found, MAX_NOTES_RETURNABLE):
        note_metadata = noteStore.findNotesMetadata(filter, offset, MAX_NOTES_RETURNABLE, resultSpec)
        notes_to_select_from.extend(note_metadata.notes)

    print(f"Total Number of Tagged Notes: {len(notes_to_select_from)}")

    selected_notes_to_email = random.sample(notes_to_select_from, NUM_NOTES_TO_EMAIL)

    note_links = []
    for note in selected_notes_to_email:
        note_link = f"https://{SERVICE}/shard/{shard_id}/nl/{user_id}/{note.guid}/"
        note_links.append(note_link)

        # TODO: in-app hyperlinks
        # in_app_link = f"evernote:///view/{user_id}/{shard_id}/{note.guid}/{note.guid}/"
        # note_links.append(in_app_link)

    note_titles = [note.title for note in selected_notes_to_email]

    email_html_string_lines = []

    for title, link in zip(note_titles, note_links):
        email_html_string_lines.append(f'{title} - {link}')
        # email_html_string_lines.append(f'<a href={link}>{title}</a>')

    now = datetime.now()
    date_str = now.strftime("%m/%d/%Y")

    send_mail(SENDING_EMAIL, 
              RECEIVING_EMAIL,
              f'Daily Evernote Notes To Review - {date_str}',
              '<br><br>'.join(email_html_string_lines)
             )

    print(f"Email sent to {RECEIVING_EMAIL}!")