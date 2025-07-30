import codecs
import re
import unicodedata

_utf8_encoder = codecs.getencoder("utf-8")
_utf8_decoder = codecs.getdecoder("utf-8")
_unicode_normalize = unicodedata.normalize
_unicode_category = unicodedata.category

MATCH_OPEN_TAG = re.compile(r"\<([^\/]+?)\>")
MATCH_CLOSE_TAG = re.compile(r"\<(\/.+?)\>")


def enc_utf8(s):
    return _utf8_encoder(s)[0]


def dec_utf8(s):
    return _utf8_decoder(s)[0]


def normalize_token(t):
    key = t.replace("\u00a9", "c")

    def is_not_mn(c):
        cat = _unicode_category(c)
        return cat != "Mn"

    return "".join(c for c in _unicode_normalize("NFKD", key) if is_not_mn(c))


def normalize_index_key(key):
    # remove space at the beginning and at the end of the string
    key = key.strip().lower()
    key = key.replace("\u00a9", "c")

    def is_wd(c):
        cat = _unicode_category(c)
        return cat == "Ll" or cat == "Nd"

    return "".join(c for c in _unicode_normalize("NFKD", key) if is_wd(c))


def ellipsis(s, length):
    if len(s) >= length:
        return s[: length - 1] + "\u2026"
    return s
