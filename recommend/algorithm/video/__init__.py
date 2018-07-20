# -*- coding: utf8 -*-
from youtube_dl import (
    DateRange,
    YoutubeDL,
)
from recommend.const import (
    video_index,
    video_type,
)
from recommend.models import es_client


ydl_opts = {
    'usenetrc': False,
    'username': None,
    'password': None,
    'twofactor': None,
    'videopassword': None,
    'ap_mso': None,
    'ap_username': None,
    'ap_password': None,
    'quiet': True,
    'no_warnings': False,
    'forceurl': False,
    'forcetitle': False,
    'forceid': False,
    'forcethumbnail': False,
    'forcedescription': False,
    'forceduration': False,
    'forcefilename': False,
    'forceformat': False,
    'forcejson': False,
    'dump_single_json': False,
    'simulate': False,
    'skip_download': True,
    'format': None,
    'listformats': None,
    'outtmpl': '%(title)s-%(id)s.%(ext)s',
    'autonumber_size': None,
    'autonumber_start': 1,
    'restrictfilenames': False,
    'ignoreerrors': False,
    'force_generic_extractor': False,
    'ratelimit': None,
    'nooverwrites': False,
    'retries': 10,
    'fragment_retries': 10,
    'skip_unavailable_fragments': True,
    'keep_fragments': False,
    'buffersize': 1024,
    'noresizebuffer': False,
    'http_chunk_size': None,
    'continuedl': True,
    'noprogress': False,
    'progress_with_newline': False,
    'playliststart': 1,
    'playlistend': None,
    'playlistreverse': None,
    'playlistrandom': None,
    'noplaylist': False,
    'logtostderr': False,
    'consoletitle': False,
    'nopart': False,
    'updatetime': True,
    'writedescription': False,
    'writeannotations': False,
    'writeinfojson': False,
    'writethumbnail': False,
    'write_all_thumbnails': False,
    'writesubtitles': False,
    'writeautomaticsub': False,
    'allsubtitles': False,
    'listsubtitles': False,
    'subtitlesformat': 'best',
    'subtitleslangs': [],
    'matchtitle': None,
    'rejecttitle': None,
    'max_downloads': None,
    'prefer_free_formats': False,
    'verbose': False,
    'dump_intermediate_pages': False,
    'write_pages': False,
    'test': False,
    'keepvideo': False,
    'min_filesize': None,
    'max_filesize': None,
    'min_views': None,
    'max_views': None,
    'daterange': DateRange(),
    'cachedir': None,
    'youtube_print_sig_code': False,
    'age_limit': None,
    'download_archive': None,
    'cookiefile': None,
    'nocheckcertificate': False,
    'prefer_insecure': None,
    'proxy': None,
    'socket_timeout': None,
    'bidi_workaround': None,
    'debug_printtraffic': False,
    'prefer_ffmpeg': None,
    'include_ads': None,
    'default_search': None,
    'youtube_include_dash_manifest': True,
    'encoding': None,
    'extract_flat': False,
    'mark_watched': False,
    'merge_output_format': None,
    'postprocessors': [],
    'fixup': 'detect_or_warn',
    'source_address': None,
    'call_home': False,
    'sleep_interval': None,
    'max_sleep_interval': None,
    'external_downloader': None,
    'list_thumbnails': False,
    'playlist_items': None,
    'xattr_set_filesize': None,
    'match_filter': None,
    'no_color': False,
    'ffmpeg_location': None,
    'hls_prefer_native': None,
    'hls_use_mpegts': None,
    'external_downloader_args': None,
    'postprocessor_args': None,
    'cn_verification_proxy': None,
    'geo_verification_proxy': None,
    'config_location': None,
    'geo_bypass': True,
    'geo_bypass_country': None,
    'autonumber': None,
    'usetitle': None
}

stop_words_set = {
    "a", "able", "about", "above", "according",
    "accordingly", "across", "actually", "after", "afterwards",
    "again", "against", "ain't", "all", "allow",
    "allows", "almost", "alone", "along", "already",
    "also", "although", "always", "am", "among",
    "amongst", "an", "and", "another", "any",
    "anybody", "anyhow", "anyone", "anything", "anyway",
    "anyways", "anywhere", "apart", "appear", "appreciate",
    "appropriate", "are", "aren't", "around", "as",
    "aside", "ask", "asking", "associated", "at",
    "available", "away", "awfully", "be", "became",
    "because", "become", "becomes", "becoming", "been",
    "before", "beforehand", "behind", "being", "believe",
    "below", "beside", "besides", "best", "better",
    "between", "beyond", "both", "brief", "but",
    "by", "c'mon", "c's", "came", "can",
    "can't", "cannot", "cant", "cause", "causes",
    "certain", "certainly", "changes", "clearly", "co",
    "com", "come", "comes", "concerning", "consequently",
    "consider", "considering", "contain", "containing", "contains",
    "corresponding", "could", "couldn't", "course", "currently",
    "definitely", "described", "despite", "did", "didn't",
    "different", "do", "does", "doesn't", "doing",
    "don't", "done", "down", "downwards", "during",
    "each", "edu", "eg", "eight", "either",
    "else", "elsewhere", "enough", "entirely", "especially",
    "et", "etc", "even", "ever", "every",
    "everybody", "everyone", "everything", "everywhere", "ex",
    "exactly", "example", "except", "far", "few",
    "fifth", "first", "five", "followed", "following",
    "follows", "for", "former", "formerly", "forth",
    "four", "from", "further", "furthermore", "get",
    "gets", "getting", "given", "gives", "go",
    "goes", "going", "gone", "got", "gotten",
    "greetings", "had", "hadn't", "happens", "hardly",
    "has", "hasn't", "have", "haven't", "having",
    "he", "he's", "hello", "help", "hence",
    "her", "here", "here's", "hereafter", "hereby",
    "herein", "hereupon", "hers", "herself", "hi",
    "him", "himself", "his", "hither", "hopefully",
    "how", "howbeit", "however", "i'd", "i'll",
    "i'm", "i've", "ie", "if", "ignored",
    "immediate", "in", "inasmuch", "inc", "indeed",
    "indicate", "indicated", "indicates", "inner", "insofar",
    "instead", "into", "inward", "is", "isn't",
    "it", "it'd", "it'll", "it's", "its",
    "itself", "just", "keep", "keeps", "kept",
    "know", "known", "knows", "last", "lately",
    "later", "latter", "latterly", "least", "less",
    "lest", "let", "let's", "like", "liked",
    "likely", "little", "look", "looking", "looks",
    "ltd", "mainly", "many", "may", "maybe",
    "me", "mean", "meanwhile", "merely", "might",
    "more", "moreover", "most", "mostly", "much",
    "must", "my", "myself", "name", "namely",
    "nd", "near", "nearly", "necessary", "need",
    "needs", "neither", "never", "nevertheless", "new",
    "next", "nine", "no", "nobody", "non",
    "none", "noone", "nor", "normally", "not",
    "nothing", "novel", "now", "nowhere", "obviously",
    "of", "off", "often", "oh", "ok",
    "okay", "old", "on", "once", "one",
    "ones", "only", "onto", "or", "other",
    "others", "otherwise", "ought", "our", "ours",
    "ourselves", "out", "outside", "over", "overall",
    "own", "particular", "particularly", "per", "perhaps",
    "placed", "please", "plus", "possible", "presumably",
    "probably", "provides", "que", "quite", "qv",
    "rather", "rd", "re", "really", "reasonably",
    "regarding", "regardless", "regards", "relatively", "respectively",
    "right", "said", "same", "saw", "say",
    "saying", "says", "second", "secondly", "see",
    "seeing", "seem", "seemed", "seeming", "seems",
    "seen", "self", "selves", "sensible", "sent",
    "serious", "seriously", "seven", "several", "shall",
    "she", "should", "shouldn't", "since", "six",
    "so", "some", "somebody", "somehow", "someone",
    "something", "sometime", "sometimes", "somewhat", "somewhere",
    "soon", "sorry", "specified", "specify", "specifying",
    "still", "sub", "such", "sup", "sure",
    "t's", "take", "taken", "tell", "tends",
    "th", "than", "thank", "thanks", "thanx",
    "that", "that's", "thats", "the", "their",
    "theirs", "them", "themselves", "then", "thence",
    "there", "there's", "thereafter", "thereby", "therefore",
    "therein", "theres", "thereupon", "these", "they",
    "they'd", "they'll", "they're", "they've", "think",
    "third", "this", "thorough", "thoroughly", "those",
    "though", "three", "through", "throughout", "thru",
    "thus", "to", "together", "too", "took",
    "toward", "towards", "tried", "tries", "truly",
    "try", "trying", "twice", "two", "un",
    "under", "unfortunately", "unless", "unlikely", "until",
    "unto", "up", "upon", "us", "use",
    "used", "useful", "uses", "using", "usually",
    "value", "various", "very", "via", "viz",
    "vs", "want", "wants", "was", "wasn't",
    "way", "we", "we'd", "we'll", "we're",
    "we've", "welcome", "well", "went", "were",
    "weren't", "what", "what's", "whatever", "when",
    "whence", "whenever", "where", "where's", "whereafter",
    "whereas", "whereby", "wherein", "whereupon", "wherever",
    "whether", "which", "while", "whither", "who",
    "who's", "whoever", "whole", "whom", "whose",
    "why", "will", "willing", "wish", "with",
    "within", "without", "won't", "wonder", "would",
    "wouldn't", "yes", "yet", "you", "you'd",
    "you'll", "you're", "you've", "your", "yours",
    "yourself", "yourselves", "zero",

    "video", "videos", "title", "latest", "download", "ki",
    "full", "year", "week", "film", "tape", "tapes",
    "hq", "hd", "epic", "part", "singer", "top", "lyrics"
    "records", "trailer", "audio", "lyric"
}


def get_videos(video_ids):
    """批量查询视频id

    Args:
        video_ids (list): 视频id列表
    """
    if not video_ids:
        return

    query = {'docs': [{'_index': video_index, '_type': video_type, '_id': x} for x in video_ids]}
    query_result = es_client.mget(query)
    docs = query_result['docs']

    result = []
    for item in docs:
        source = item.get('_source', {})
        if not source:
            continue
        source.pop('tag', None)
        source.pop('genre')
        source['poster'] = source['poster'].replace('maxresdefalut', 'hqdefault')
        result.append(source)
    return result


def extract_youtube_info(url):
    """解析youtube详情页

    Args:
        url (str): 视频播放页
    """
    with YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url)


def get_video(video_id):
    """查询youtube视频详情
    如果视频不存在es中,需要爬一次

    Args:
        video_id (str): 视频id
    """
    if es_client.exists(video_index, video_type, video_id):
        video = es_client.get(video_index, video_type, id=video_id)
        return video['_source']

    play_url = 'https://youtube.com/watch?v={}'.format(video_id)
    data = extract_youtube_info(play_url)
    body = {
        'id': video_id,
        'type': 'mv',
        'p_type': 'video',
        'slate': play_url,
        'poster': data['thumbnail'],
        'runtime': data['duration'],
        'hot': data['view_count'],
        'genre': ['youtube'],
        'title': data['title'],
        'tag': data['tags']
    }
    es_client.index(video_index, video_type, body, id=video_id)
    return body
