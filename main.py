import requests
import json
import argparse
import os
import subprocess

def load_config(config_file):
    with open(config_file, 'r') as file:
        return json.load(file)

def get_oauth_token(client_id, client_secret=None):
    url = 'https://id.twitch.tv/oauth2/token'
    data = {
        'client_id': client_id,
        'grant_type': 'client_credentials'
    }
    if client_secret:
        data['client_secret'] = client_secret
    response = requests.post(url, data=data)
    response_data = response.json()
    if 'access_token' in response_data:
        return response_data['access_token']
    else:
        raise Exception(f"Error obtaining access token: {response_data}")

def get_user_id(channel_name, client_id, access_token):
    url = f"https://api.twitch.tv/helix/users?login={channel_name}"
    headers = {
        'Client-ID': client_id,
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url, headers=headers)
    response_data = response.json()
    if 'data' in response_data and len(response_data['data']) > 0:
        return response_data['data'][0]['id']
    else:
        raise Exception(f"Error obtaining user ID: {response_data}")

def get_highlights(user_id, client_id, access_token):
    url = f"https://api.twitch.tv/helix/videos?user_id={user_id}&type=highlight"
    headers = {
        'Client-ID': client_id,
        'Authorization': f'Bearer {access_token}'
    }
    highlights = []
    while url:
        response = requests.get(url, headers=headers)
        response_data = response.json()
        if 'data' in response_data:
            highlights.extend(response_data['data'])
            url = response_data.get('pagination', {}).get('cursor')
            if url:
                url = f"https://api.twitch.tv/helix/videos?user_id={user_id}&type=highlight&after={url}"
        else:
            raise Exception(f"Error obtaining highlights: {response_data}")
    return highlights

def calculate_total_duration(highlights):
    total_duration = 0
    for highlight in highlights:
        duration = highlight['duration']
        hours, minutes, seconds = 0, 0, 0
        if 'h' in duration:
            hours, duration = duration.split('h')
            hours = float(hours)
        if 'm' in duration:
            minutes, duration = duration.split('m')
            minutes = float(minutes)
        if 's' in duration:
            seconds = float(duration[:-1])
        total_duration += hours * 3600 + minutes * 60 + seconds
    return total_duration / 3600  # Convert to hours

def get_at_risk_highlights(highlights):
    highlights.sort(key=lambda x: x['created_at'])  # Sort by oldest first
    highlights.sort(key=lambda x: x['view_count'])  # Then sort by view count
    at_risk = []
    total_duration = calculate_total_duration(highlights)
    print(f"Total duration: {total_duration} hours")  # Debug statement
    while total_duration > 100:
        at_risk.append(highlights.pop(0))
        total_duration = calculate_total_duration(highlights)
    
    # Check from most recent but least viewed
    highlights.sort(key=lambda x: x['created_at'], reverse=True)  # Sort by newest first
    highlights.sort(key=lambda x: x['view_count'])  # Then sort by view count
    while total_duration > 100:
        highlight = highlights.pop(0)
        if highlight not in at_risk:
            at_risk.append(highlight)
            total_duration = calculate_total_duration(highlights)
    
    return at_risk

def export_at_risk_highlights(at_risk_highlights, channel_name):
    filename_txt = f'at_risk_highlights_{channel_name}.txt'
    filename_json = f'at_risk_highlights_{channel_name}.json'
    
    with open(filename_txt, 'w') as file:
        for highlight in at_risk_highlights:
            file.write(f"{highlight['url']}\n")
    print(f"Exported {len(at_risk_highlights)} at-risk highlights to {filename_txt}")  # Debug statement
    
    with open(filename_json, 'w') as file:
        json.dump(at_risk_highlights, file, indent=4)
    print(f"Exported {len(at_risk_highlights)} at-risk highlights to {filename_json}")  # Debug statement

def backup_at_risk_highlights(at_risk_highlights, channel_name):
    os.makedirs(channel_name, exist_ok=True)
    for highlight in at_risk_highlights:
        url = highlight['url']
        subprocess.run(['youtube-dl', '-o', f'{channel_name}/%(title)s.%(ext)s', url])
    print(f"Downloaded {len(at_risk_highlights)} at-risk highlights to folder {channel_name}")

if __name__ == "__main__":
    config = load_config('config.json')
    client_id = config['client_id']
    client_secret = config.get('client_secret')
    access_token = get_oauth_token(client_id, client_secret)
    
    parser = argparse.ArgumentParser(description='Twitch Highlight Saver')
    parser.add_argument('mode', type=str, choices=['check', 'backup'], help='Mode of operation: check or backup')
    parser.add_argument('channel_name', type=str, help='The name of the Twitch channel')
    args = parser.parse_args()

    user_id = get_user_id(args.channel_name, client_id, access_token)
    highlights = get_highlights(user_id, client_id, access_token)
    print(f"Retrieved {len(highlights)} highlights")  # Debug statement
    at_risk_highlights = get_at_risk_highlights(highlights)
    
    if args.mode == 'check':
        export_at_risk_highlights(at_risk_highlights, args.channel_name)
    elif args.mode == 'backup':
        backup_at_risk_highlights(at_risk_highlights, args.channel_name)