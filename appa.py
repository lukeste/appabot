import discord
import googlemaps
import json
from datetime import datetime

gmaps = googlemaps.Client(key='')
client = discord.Client()

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_message(message):

    # open user list
    with open('users.json', 'r') as f:
        users = json.load(f)

    if message.content.lower().startswith('!home'): #or message.content.lower().startswith('home')
        check_new_user(message.author.id, users)
        home_coords = message.content[6:]
        if '37' not in home_coords and '-122' not in home_coords:
            geocode = gmaps.geocode(address=home_coords)
            home_coords = str(geocode[0]['geometry']['location']['lat']) + ', ' + \
                          str(geocode[0]['geometry']['location']['lng'])
        users[message.author.id]['home'] = home_coords
        await update_users(users, message.channel, 'Successfully added home location.')

    if message.content.lower().startswith('!filter'): #or message.content.lower().startswith('filter')
        if message.author.id in users:
            with open('pokemonnames.json', 'r') as f:
                mon_names = json.load(f)
            new_filter = message.content[8:].split(':')
            user = message.author.id
            mon = new_filter[0]
            if mon in mon_names['pokemon'] or mon == 'default':
                if check_int(new_filter[1]):
                    iv = int(new_filter[1]) - 1
                    if mon == 'default':
                        users[user]['default_iv'] = iv
                        await update_users(users, message.channel, 'Successfully added default.')
                    else:
                        users[user]['iv_filters'][mon] = iv
                        await update_users(users, message.channel, 'Successfully added filter.')
                else:
                    await client.send_message(message.channel, 'Please enter an integer.')
            else:
                await client.send_message(message.channel, '\'{}\' is not a Pokemon. You probably misspelled '
                                                           'something.'.format(mon))
        else:
            await client.send_message(message.channel, 'You have not entered a home location. Please do that first.')

    if message.content.lower().startswith('!radius'): # or message.content.lower().startswith('radius')
        if message.author.id in users:
            radius = message.content[8:]
            if check_int(radius):
                users[message.author.id]['radius'] = radius
                await update_users(users, message.channel, 'Successfully updated radius.')
            else:
                await client.send_message(message.channel, 'Radius not updated. Please enter an integer.')
        else:
            await client.send_message(message.channel, 'You have not entered a home location. Please do that first.')

    if message.embeds and not message.author.id == '389565039625109509' and '?%' not in message.embeds[0]['title']:
        # break down the message
        embed_content = message.embeds[0]
        title = embed_content['title']
        # remove redundant information from the description
        desc = embed_content['description'].split('\n')
        coords = desc[3]  # get coords of spawn

        with open('previous_spawn.txt') as txt:
            previous_spawn = txt.read()
        if coords != previous_spawn:
            with open('previous_spawn.txt', 'w') as txt:
                txt.write(coords)
            mon = title.split(': ')[1].split()[0].lower()
            iv = int(title.split(': ')[1].split()[1].split('.')[0])
            # print('{}: {} {}'.format(datetime.now(), mon, iv))
            title_url = better_gmaps_url(embed_content['url'], mon, desc[2])
            thumbnail_url = embed_content['thumbnail']['url']
            image_url = embed_content['image']['url']
            for user in users:
                user_iv = users[user]['default_iv']
                if mon in users[user]['iv_filters']:
                    user_iv = users[user]['iv_filters'][mon]
                if user_iv <= iv:
                    distance_result = gmaps.distance_matrix(users[user]['home'], coords, mode='driving',
                                                            units='imperial', departure_time=datetime.now(),
                                                            traffic_model='best_guess')
                    # duration_in_traffic = distance_result['rows'][0]['elements'][0]['duration_in_traffic']['text']
                    # print('Duration in traffic: {}    Radius: {} mins'.format(duration_in_traffic,
                    #                                                          users[user]['radius']))
                    try:
                        duration_in_traffic = distance_result['rows'][0]['elements'][0]['duration_in_traffic']['value']\
                                              / 60
                    except KeyError:
                        duration_in_traffic = -1
                    if duration_in_traffic <= int(users[user]['radius']):
                        await build_embed(user, distance_result, title, title_url, desc, thumbnail_url, image_url)

    # if message.content.startswith('!message'):
    #     for user in users:
    #         await client.send_message(await client.get_user_info(user), '')


async def build_embed(user, distance_result, title, title_url, desc, thumbnail_url, image_url):
    # print(distance_result)
    distance = distance_result['rows'][0]['elements'][0]['distance']['text']
    try:
        duration_in_traffic = distance_result['rows'][0]['elements'][0]['duration_in_traffic']['text']
    except KeyError:
        duration_in_traffic = '<error>'
    formatted_desc = '{}\n{}\n{} ({}) from home'.format(desc[0], desc[2], duration_in_traffic, distance)
    em = discord.Embed(title=title, url=title_url, description=formatted_desc)
    em.set_thumbnail(url=thumbnail_url)
    em.set_image(url=image_url)
    try:
        await client.send_message(await client.get_user_info(user), embed=em)
    except discord.Forbidden:
        print('blocked by {}'.format(user))


# checks to see if the user is already in the list of users
# takes user_id and the user list
# if the user is not in the user list, adds them to the user list
def check_new_user(user_id, users):
    if user_id not in users:
        users[user_id] = {"home": "", "default_iv": 80, "iv_filters": {}, "radius": "100"}
        with open('users.json', 'w') as fp:
            json.dump(users, fp, indent=2)


# adds the name of the pokemon and the timer to the google maps link
# takes url, the previous url scraped from the discord embed, mon, the name of the pokemon, and time, the despawn timer
# returns the new url in the correct format
def better_gmaps_url(url, mon, time):
    time = time.split()
    new_url = url[:30] + mon.capitalize() + '%20' + time[0] + '%20' + time[1] + '%20' + time[2] + '%20' + time[3] + \
              '%40' + url[30:]
    return new_url


async def update_users(users, channel, message):
    try:
        with open('users.json', 'w') as fp:
            json.dump(users, fp, indent=2)
        await client.send_message(channel, message)
    except json.JSONDecodeError:
        await client.send_message(channel, 'Something went wrong.')


def check_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


client.run('')