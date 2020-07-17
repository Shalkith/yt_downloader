def processfile(filename):
    import requests
    import re, os
    import json
    from urllib.parse import parse_qs, unquote
    import csv
    import pytube
    import moviepy.editor as mp
    import string, random

    def get_random_string(length):
        letters = string.ascii_lowercase
        result_str = ''.join(random.choice(letters) for i in range(length))
        print("Random string of length", length, "is:", result_str)
        return result_str


    def zippem(filename,dir):
        import shutil
        shutil.make_archive(filename, 'zip', dir)

    def apply_descrambler(stream_data, key):
        """Apply various in-place transforms to YouTube's media stream data.
        Creates a ``list`` of dictionaries by string splitting on commas, then
        taking each list item, parsing it as a query string, converting it to a
        ``dict`` and unquoting the value.
        :param dict stream_data:
            Dictionary containing query string encoded values.
        :param str key:
            Name of the key in dictionary.
        **Example**:
        >>> d = {'foo': 'bar=1&var=test,em=5&t=url%20encoded'}
        >>> apply_descrambler(d, 'foo')
        >>> print(d)
        {'foo': [{'bar': '1', 'var': 'test'}, {'em': '5', 't': 'url encoded'}]}
        """
        otf_type = "FORMAT_STREAM_TYPE_OTF"

        if key == "url_encoded_fmt_stream_map" and not stream_data.get(
            "url_encoded_fmt_stream_map"
        ):
            formats = json.loads(stream_data["player_response"])["streamingData"]["formats"]
            formats.extend(
                json.loads(stream_data["player_response"])["streamingData"][
                    "adaptiveFormats"
                ]
            )
            try:
                stream_data[key] = [
                    {
                        "url": format_item["url"],
                        "type": format_item["mimeType"],
                        "quality": format_item["quality"],
                        "itag": format_item["itag"],
                        "bitrate": format_item.get("bitrate"),
                        "is_otf": (format_item.get("type") == otf_type),
                    }
                    for format_item in formats
                ]
            except KeyError:
                cipher_url = []
                for data in formats:
                    cipher = data.get("cipher") or data["signatureCipher"]
                    cipher_url.append(parse_qs(cipher))
                stream_data[key] = [
                    {
                        "url": cipher_url[i]["url"][0],
                        "s": cipher_url[i]["s"][0],
                        "type": format_item["mimeType"],
                        "quality": format_item["quality"],
                        "itag": format_item["itag"],
                        "bitrate": format_item.get("bitrate"),
                        "is_otf": (format_item.get("type") == otf_type),
                    }
                    for i, format_item in enumerate(formats)
                ]
        else:
            stream_data[key] = [
                {k: unquote(v) for k, v in parse_qsl(i)}
                for i in stream_data[key].split(",")
            ]




    try:
        pytube.__main__.apply_descrambler = apply_descrambler
        #filename = 'video_list.csv'

        with open(filename,'r',encoding="latin1") as f:
            reader = csv.reader(f)
            #print(len(reader))
            videos = list(reader)

        for video in videos:
            y = pytube.YouTube(video[0])
            t = y.streams
            outfolder = r"output"
            randomfoldername = get_random_string(8)
            t[0].download(output_path=outfolder+'/'+randomfoldername)

        for file in [n for n in os.listdir(outfolder+'/'+randomfoldername) if re.search('mp4',n)]:
            full_path = os.path.join(outfolder+'/'+randomfoldername, file)
            output_path = os.path.join(outfolder+'/'+randomfoldername, os.path.splitext(file)[0] + '.mp3')
            clip = mp.AudioFileClip(full_path).subclip(10,) # disable if do not want any clipping
            clip.write_audiofile(output_path)
            os.remove(full_path)

        zippem(r'static/output/'+randomfoldername,outfolder+'/'+randomfoldername)

        for file in [n for n in os.listdir(outfolder+'/'+randomfoldername) if re.search('mp3',n)]:
            full_path = os.path.join(outfolder+'/'+randomfoldername, file)
            os.remove(full_path)

        return r'static/output/'+randomfoldername
    except Exception as e:
        input(e)
