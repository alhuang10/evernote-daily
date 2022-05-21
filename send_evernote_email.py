from evernote.edam.notestore.ttypes import NoteFilter, NotesMetadataResultSpec
from evernote.api.client import EvernoteClient

from redmail import gmail

from datetime import datetime
import random, argparse, os, pickle


MAX_NOTES_RETURNABLE = 250  # Max number of notes Evernote API can return in a single filter query
SERVICE = "www.evernote.com"
LAST_SENT_DICT = 'guid_to_last_sent_date.p'  # Map from note GUID to datetime.date of last send

# CHANGE (See README)
PROD_DEVELOPER_TOKEN = ""
SENDING_EMAIL = ""
APP_PASSWORD_FOR_SENDING_EMAIL = ""
RECEIVING_EMAIL = ""


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get desired tags and other counts")
    parser.add_argument('--tag', type=str, default='Daily Email')
    parser.add_argument('--select-count', type=int, default=5)
    parser.add_argument('--min-days-between', type=int, default=30, 
                        help='Only select from notes after X days since last send')

    args = parser.parse_args()

    selected_tag = args.tag
    num_notes_to_email = args.select_count
    min_days_between = args.min_days_between

    print(f"Selecting from notes with this tag: {selected_tag}")
    print(f"Selecting this num notes: {num_notes_to_email}")

    # Set up auth in redmail using app password
    gmail.username = SENDING_EMAIL
    gmail.password = APP_PASSWORD_FOR_SENDING_EMAIL

    client = EvernoteClient(token=PROD_DEVELOPER_TOKEN, 
                            sandbox=False)

    userStore = client.get_user_store()
    user = userStore.getUser()
    user_id = user.id
    shard_id = user.shardId

    noteStore = client.get_note_store()

    # Get the unique GUID for the tag that we want
    tag_infos = noteStore.listTags()
    selected_tag_obj = [tag for tag in tag_infos if tag.name == selected_tag]
    if len(selected_tag_obj) == 0:
        raise Exception("Selected tag not found")
    selected_tag_guid = selected_tag_obj[0].guid

    # Get all the notes that have the tag we want
    filter = NoteFilter(tagGuids=[selected_tag_guid])
    resultSpec = NotesMetadataResultSpec(includeTitle=True, includeTagGuids=True)

    note_metadata = noteStore.findNotesMetadata(filter, 0, MAX_NOTES_RETURNABLE, resultSpec)
    num_notes_found = note_metadata.totalNotes

    notes_with_tag = []

    # If num notes with this tag is greater than MAX_NOTES_RETURNABLE need to iterate
    for offset in range(0, num_notes_found, MAX_NOTES_RETURNABLE):
        note_metadata = noteStore.findNotesMetadata(filter, offset, MAX_NOTES_RETURNABLE, resultSpec)
        notes_with_tag.extend(note_metadata.notes)

    print(f"Total Number of Tagged Notes: {len(notes_with_tag)}")

    # Only consider notes that we haven't sent recently (args.min-days-between)
    if not os.path.exists(LAST_SENT_DICT):
        guid_to_last_sent_date = {}        
    else:
        guid_to_last_sent_date = pickle.load(open(LAST_SENT_DICT, 'rb'))

    # Only consider notes that haven't been sent before or been long enough time since last send
    notes_to_select_from = []
    current_time = datetime.now()

    for note in notes_with_tag:
        # Never sent before
        if note.guid not in guid_to_last_sent_date:
            notes_to_select_from.append(note)
        else:
            last_send_date = guid_to_last_sent_date[note.guid]
            delta = current_time - last_send_date

            days_since_send = delta.days
            # Only append if the threshold is high enough
            if days_since_send > min_days_between:
                notes_to_select_from.append(note)

    selected_notes_to_email = random.sample(notes_to_select_from, num_notes_to_email)
    for note in selected_notes_to_email:
        guid_to_last_sent_date[note.guid] = current_time
    pickle.dump(guid_to_last_sent_date, open(LAST_SENT_DICT, 'wb'))

    # Construct links to notes and email
    note_links = []
    for note in selected_notes_to_email:
        note_link = f"https://{SERVICE}/shard/{shard_id}/nl/{user_id}/{note.guid}/"
        note_links.append(note_link)

    note_titles = [note.title for note in selected_notes_to_email]

    email_html_string_lines = []

    for title, link in zip(note_titles, note_links):
        email_html_string_lines.append(f'{title} - {link}')

    now = datetime.now()
    date_str = now.strftime("%m/%d/%Y")
    
    gmail.send(
        subject=f'Daily Evernote To Review ({selected_tag}) - {date_str}',
        receivers=[RECEIVING_EMAIL],
        html='<br><br>'.join(email_html_string_lines)
    )

    print(f"Email sent to {RECEIVING_EMAIL}!")