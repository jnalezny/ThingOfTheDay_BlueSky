import requests
import json
from datetime import datetime, timezone


#BSKY_HANDLE = "fsodtest.bsky.social"
#BSKY_PASS = "WizardOfOz123!"


def send_post(text, image_name, alt_image_text, handle, password):
    print("send_post " + text + " " +image_name + " " + alt_image_text)
    resp = requests.post("https://bsky.social/xrpc/com.atproto.server.createSession",
    json={"identifier":handle,"password":password},)

    print(resp)
    resp.raise_for_status()
    session = resp.json()
    session_jwt = session["accessJwt"]
    print(session_jwt)

    full_token = "Bearer " + session_jwt
    #print(full_token)

    now = datetime.now(timezone.utc).isoformat().replace("+00:00","Z")

    padded_text = text + " "
    #to make sure when I scan, I can find a blank at the end
    start_link = padded_text.find("http")
    end_link = 0
    link = None
    if start_link > -1:
        end_link = padded_text.find(" ", start_link + 1)
        link = text[start_link:end_link]
    
    my_post = {
        "$type": "app.bsky.feed.post",
        "text": text,
        "createdAt": now,
    }
    if image_name:
        with open(image_name, "rb") as f:
            img_bytes = f.read()
        if len(img_bytes) > 1000000:
            raise Exception(f"image too large {len(img_bytes)}")
        image_mimetype = None
        if image_name.find(".jpg") > -1:
            image_mimetype = "image/jpg"
        if image_name.find(".JPG") > -1:
            image_mimetype = "image/jpg"
        if image_name.find(".gif") > -1:
            image_mimetype = "image/gif"
        if image_name.find(".png") > -1:
            image_mimetype = "image/png"
            
        resp = requests.post(
            "https://bsky.social/xrpc/com.atproto.repo.uploadBlob",
            headers={
            "Content-Type": image_mimetype,
            "Authorization": "Bearer " + session["accessJwt"],
            },data=img_bytes,)
        resp.raise_for_status()
        blob = resp.json()["blob"]
        
        my_post["embed"] = {
            "$type": "app.bsky.embed.images",
            "images": [{
            "alt": alt_image_text,
            "image": blob,
        }],}
    facets = []    
    if end_link:
        """ OLD way to do this.
        my_post["facets"] = [{
        "index":{
            "byteStart":start_link,
            "byteEnd":end_link
            },
        "features":[
        {
            "$type": "app.bsky.richtext.facet#link",
            "uri":link
        }]
        }]
        """
        facets.append(
            {
            "index":{
            "byteStart":start_link,
            "byteEnd":end_link
            },
            "features":[
            {
                "$type": "app.bsky.richtext.facet#link",
                "uri":link
            }]
            }
        )
    start_link = 1
    while start_link > 0:
        start_link = padded_text.find(" #", start_link )
        end_link = 0
        tag = None
        if start_link > -1:
            end_link = padded_text.find(" ", start_link + 1)
            tag = text[start_link+2:end_link]
            #print("found tag " + tag)
            facets.append(
                {
                "index":{
                "byteStart":start_link+1,
                "byteEnd":end_link
                },
                "features":[
                {
                    "$type": "app.bsky.richtext.facet#tag",
                    "tag":tag
                }]
                }
            )
            start_link += 1
        #possible facet for hashtags app.bsky.richtext.facet#tag.
        #OR make it a link like this https://bsky.app/hashtag/P4A
        # https://docs.bsky.app/docs/advanced-guides/post-richtext#rich-text-facets
    if len(facets):
        my_post["facets"] = facets
        #print("facets " + str(facets))
            
    resp = requests.post("https://bsky.social/xrpc/com.atproto.repo.createRecord",
    headers={"Authorization": "Bearer " + session_jwt},
    json={ "repo":session["did"], "collection":"app.bsky.feed.post","record":my_post,},)
    print()
    print("attempted post")
    print(resp)

#send_post("still testing https://en.wikipedia.org/wiki/Pencil ", "./test.JPG",
#          "an image of a squirrel")

            
