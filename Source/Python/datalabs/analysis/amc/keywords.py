""" Lists of words to help flag addresses """
import pickle as pk

FALSE_POSITIVES = [
    'sebastopol',
    'mail stop',
    'mail code',
    'mailstop',
    'mail center',
    'mail slot',
    'mail box',
    'mailslot',
    'mail ctr',
    'vanderbilt mail'
]

def load_flagwords():
    """
    flagwords.pk is a list of blacklisted words that will automatically flag an address for review

    it contains words and phrases relevant to requests to stop mailing
    it also contains some profanity, slurs, and generally-insensitive or offensive language

    :return: list
    """
    return pk.loads('flagwords.pk')
