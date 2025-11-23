"""
Populate comprehensive demo data for all clients to make dashboards look presentable
"""
import pandas as pd
import random
from datetime import datetime, timedelta
import os

# Ensure data directory exists
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

def generate_dates(days_back=90, count=30):
    """Generate realistic posting dates"""
    end_date = datetime.now()
    dates = []
    for i in range(count):
        days_ago = random.randint(0, days_back)
        hours = random.randint(8, 22)
        minutes = random.randint(0, 59)
        date = end_date - timedelta(days=days_ago, hours=24-hours, minutes=minutes)
        dates.append(date.strftime('%Y-%m-%d %H:%M:%S'))
    return sorted(dates, reverse=True)

# Brand-specific content templates
BRAND_CONTENT = {
    'nike': {
        'captions': [
            "Just Do It. New season, new goals 💪 #Nike #JustDoIt",
            "Unleash your potential. The all-new Air Max is here 🔥",
            "Victory is in the details. Train like a champion 🏆",
            "Run the world. New running collection drops today 👟",
            "Athletes inspire athletes. What's your story? #NikeAthletes",
            "Breaking barriers, setting records. Who's ready? 💯",
            "Comfort meets performance. The future is now ⚡",
            "Push your limits. Greatness awaits 🌟",
            "From the court to the streets. Style never stops 🏀",
            "Chase your dreams. We've got your back 💪 #NikeFamily",
            "Innovation at every step. Check out our latest tech 🔬",
            "Sweat, smile, repeat. Workout essentials now available 💦",
            "Game day ready. Are you? 🏈 #NikeFootball",
            "Rise and grind. Morning motivation starts here ☀️",
            "Champions are made in training. Let's work 🎯",
            "Your journey, our mission. Together we rise 🚀",
            "Performance redefined. New collection alert 🔔",
            "Born to move. Made to win 🥇",
            "Style that performs. Function that inspires ✨",
            "Every champion was once a beginner. Start today 💫",
            "Unstoppable energy. Unmatched style 🌊",
            "Elevate your game. The future starts now 🎮",
            "From practice to podium. We're with you 🏅",
            "Run faster. Jump higher. Play harder. 🔥",
            "Your best is yet to come. Keep pushing 💪",
            "Icons in the making. Join the movement 👑",
            "Train insane or remain the same 💯 #NoExcuses",
            "Winning mindset. Champion attitude 🧠",
            "Gear up for greatness. New drops every week 📦",
            "The only workout you'll regret is the one you skip ⏰"
        ],
        'hashtags': ['#Nike', '#JustDoIt', '#NikeAthletes', '#NikeRunning', '#NikeTraining']
    },
    'adidas': {
        'captions': [
            "Impossible is Nothing. The new Predator boots are here ⚽",
            "Three stripes, endless possibilities 💫 #adidas",
            "Create your own game. New collection drops now 🔥",
            "Champions train here. Are you ready? 🏆 #TeamAdidas",
            "Innovation meets style. The future of sportswear ⚡",
            "From the pitch to the streets. Iconic design 👟",
            "Here to create. The new Ultraboost is revolutionary 🚀",
            "Sustainability meets performance. Better for you, better for planet 🌍",
            "Game changers welcome. Join the movement 💪",
            "Engineered for athletes. Designed for everyone ✨",
            "Speed. Power. Precision. The triple threat 🎯",
            "Legends in the making. Write your story 📝",
            "Performance that speaks for itself 🗣️",
            "Push boundaries. Break records. Repeat 🔄",
            "Your potential is limitless. Let's go 🚀 #ImpossibleIsNothing",
            "Innovation in motion. The future is now 🌟",
            "Built for the boldest athletes 💯",
            "Where comfort meets performance 🎭",
            "Creating the new. Join the revolution 🔥",
            "Icons never fade. New classics just dropped 👑",
            "From grassroots to greatness 🌱➡️🏆",
            "Athlete-tested. Champion-approved ✅",
            "Rise up. Stand out. Be legendary 💫",
            "The world is your playground. Go explore 🌎",
            "Engineered excellence. Designed passion ❤️",
            "Train like tomorrow doesn't exist ⏰",
            "Winning is a habit. Let's build it 🏗️",
            "One team, one dream. Together we rise 🤝",
            "Performance you can feel. Style you can see 👀",
            "Born on the field. Built for the street 🏟️➡️🌃"
        ],
        'hashtags': ['#adidas', '#ImpossibleIsNothing', '#adidasFootball', '#TeamAdidas', '#CreatorsUnite']
    },
    'redbull': {
        'captions': [
            "Wings when you need them 🪽 New energy, new heights",
            "MAX VERSTAPPEN WINS! 🏎️🏆 What a race! #F1 #RedBullRacing",
            "Defying gravity, one stunt at a time 🎪 #ExtremeRacing",
            "From the Alps to your adrenaline 🏔️⛷️ #RedBullSnow",
            "Energy that never quits. Just like you 💪 #GivesYouWings",
            "The most insane freeride line ever! 🏂 Watch till the end",
            "Breaking records. Breaking limits 🚀 #RedBullAthletes",
            "Your adventure starts here. Are you ready? 🎯",
            "Checo delivers! P2 in an epic battle 🏎️💨 #MexicoStrong",
            "When ordinary just won't do. Go extreme 🔥",
            "Wingsuit flying through the city! 😱 Must watch",
            "Fuel your passion. Feed your drive ⚡ #RedBull",
            "This cliff jump is absolutely mental! 🧗‍♂️💦",
            "World champion mindset. Red Bull athlete spirit 🏆",
            "The ultimate adrenaline rush awaits 🎢 #ExtremeLife",
            "From zero to hero in 3.2 seconds 🏎️💨 #F1Power",
            "Skateboarding's new golden era 🛹✨ #RedBullSkate",
            "Energy for every moment, every challenge 💯",
            "This BMX trick defies physics! 🚴‍♂️🔄",
            "Champions choose Red Bull. What's your fuel? ⛽",
            "The most epic fail compilation... that turned into wins! 😂➡️🏆",
            "Sunset session with the crew 🌅🏄‍♂️ #RedBullSurf",
            "When the stakes are high, we rise higher 📈",
            "Breakdancing battle royale! 💃🕺 #RedBullBCOne",
            "Your daily dose of inspiration served 💉✨",
            "This is what 200mph looks like 🏎️👀 #F1Vision",
            "Cliff diving into paradise 🏝️💦 #RedBullCliffDiving",
            "Unleash your inner champion 👊 #NoLimits",
            "The crowd goes wild! What a finish! 🙌🏟️",
            "This is not just a drink. It's a lifestyle 🌟 #WingsForLife"
        ],
        'hashtags': ['#RedBull', '#GivesYouWings', '#RedBullRacing', '#F1', '#ExtremeRacing']
    },
    'gopro': {
        'captions': [
            "Life's an adventure. Capture it 📷 #GoPro #HERO12",
            "POV: You're diving with great whites 🦈😱",
            "The most epic mountain bike run ever filmed 🚵‍♂️⛰️",
            "Sunrise from 15,000 feet ☀️🪂 #Skydiving",
            "Your moments, our mission. New HERO12 Black 🔥",
            "This surfing footage is absolutely insane 🏄‍♂️🌊",
            "Motorcycle through the Himalayas. Pure magic 🏍️🏔️",
            "Behind the scenes of extreme filmmaking 🎬 #GoProFamily",
            "Underwater world like you've never seen 🐠🐙 #OceanLife",
            "The climb that changed everything 🧗‍♀️💪",
            "Hypersmooth 6.0 in action. Buttery smooth 😮",
            "This BASE jump will make your heart race 🪂❤️",
            "Family adventures, perfectly captured 👨‍👩‍👧‍👦❤️ #GoProFamily",
            "When ordinary cameras can't keep up 🏃‍♂️💨",
            "Skiing the gnarliest run in the Alps ⛷️😈",
            "Your life is worth sharing. Make it epic 🌟",
            "Wingsuit flying in 4K 120fps. Mind = blown 🤯",
            "This is what adventure looks like 🗺️✨ #TravelGoPro",
            "Capturing the moments that matter ❤️📸",
            "Downhill mountain biking POV 🚵‍♂️💥 #Adrenaline",
            "The world is your playground. Document it 🌍",
            "Shark cage diving gone wrong (but so right!) 🦈😅",
            "Small camera. Big adventures 📷🚀 #HERO12",
            "Your next adventure awaits. Are you filming it? 🎥",
            "This snorkeling footage is therapeutic 🐚🌊 #Relax",
            "Behind every great shot is a GoPro 📸💯",
            "Motocross madness in slow-mo 🏍️💨 #SlowMoGuys",
            "The sunset nobody believed was real 🌅✨ (No filter!)",
            "This parkour run is absolutely nuts 🏃‍♂️🔥",
            "Life unfiltered. Adventures unlimited 🎬🌟 #LiveIt"
        ],
        'hashtags': ['#GoPro', '#HERO12', '#GoProFamily', '#Adventure', '#POV']
    },
    'mrbeast': {
        'captions': [
            "$100,000 Challenge! Last person to leave wins 💰🎯",
            "I Gave Away A Private Island! 🏝️😱 Link in bio",
            "Recreating Squid Game in real life! 456 contestants 🔴🔺⭕",
            "I Opened A Free Restaurant For 24 Hours 🍔🍟",
            "$1 vs $100,000 Vacation! Which would you choose? ✈️",
            "Surprising strangers with life-changing gifts 🎁❤️",
            "I Bought Everything In A Store! 🛒💰",
            "Last To Stop Running Wins $100,000! 🏃‍♂️💵",
            "Building 100 Wells In Africa 🌍💧 #TeamTrees",
            "I Spent 7 Days Buried Alive ⚰️😰",
            "Giving Away 10 Cars To Random People! 🚗🎁",
            "World's Largest Pizza! 🍕 40,000 slices served",
            "$1 vs $250,000 Hotel Room! 🏨✨",
            "I Survived 24 Hours Straight In Ice ❄️🥶",
            "Giving Away A House To A Random Subscriber! 🏠🔑",
            "100 People vs 1 Million Zombies! 🧟‍♂️💥",
            "I Opened The World's Largest Grocery Store 🛒🌟",
            "Last To Leave Circle Wins $500,000! ⭕💰",
            "Surprising Waitress With $10,000 Tip! 💵😊",
            "I Bought A Private Island For $1! 🏝️🤑",
            "Going Through The Same Drive Thru 1,000 Times 🚗🍔",
            "I Adopted Every Dog In A Shelter! 🐕❤️",
            "Building The World's Biggest Lego Tower 🧱🏗️",
            "$10,000 Every Day You Survive In The Wilderness 🏕️💵",
            "I Gave My 100 Millionth Subscriber A Private Island 🎉🏝️",
            "Anything You Can Fit In The Circle, I'll Pay For ⭕💰",
            "I Sold My House For $1! 🏠💵",
            "Extreme Hide And Seek For $100,000! 🙈💰",
            "I Ran A Marathon In The World's Largest Shoes! 👟😂",
            "New video dropping in 2 hours! You won't believe this one 🚀🔥"
        ],
        'hashtags': ['#MrBeast', '#Challenge', '#Giveaway', '#BeastPhilanthropy', '#TeamTrees']
    },
    'nasa': {
        'captions': [
            "Earth from the ISS. Never gets old 🌍✨ #SpaceStation",
            "James Webb captures the deepest view of the universe yet 🔭🌌",
            "Artemis Mission Update: We're going back to the Moon! 🌙🚀",
            "This nebula is 7,500 light years away 🌟😍 #JWST",
            "Mars Perseverance found evidence of ancient water! 💧🔴 #MarsRover",
            "The Sun in ultra-HD. Absolutely mesmerizing ☀️🔥",
            "ISS astronauts conducting groundbreaking experiments 🧪🔬",
            "This galaxy is 13 billion years old 🌀⏰ #DeepSpace",
            "Launch countdown begins! T-minus 24 hours 🚀⏰",
            "Earth's atmosphere from 250 miles up 🌏💙 #NASAEarth",
            "The Pillars of Creation in stunning detail ✨🔭 #HubbleSpace",
            "Spacewalk completed successfully! 👨‍🚀🌌 #EVA",
            "This exoplanet might support life 🪐🧬 #Astrobiology",
            "Solar eclipse from space. Unreal view 🌑☀️",
            "International cooperation in action 🤝🌍 #ISS",
            "The beauty of our planet. Let's protect it 🌱💚 #ClimateChange",
            "Black hole discovered 10 billion times mass of Sun 🕳️😱",
            "Astronaut training: It's not for the faint of heart! 💪👨‍🚀",
            "This meteor shower will be visible tonight! 🌠✨ #StarGazing",
            "The Aurora Borealis from orbit 🌌💚💜 #NorthernLights",
            "Mars helicopter Ingenuity completes 50th flight! 🚁🔴",
            "Earth science missions saving lives 🌍❤️ #EarthObservation",
            "The Orion Nebula in infrared. Mind-blowing 🔥🌌",
            "Preparing for humanity's next giant leap 🦶🌙",
            "This supernova explosion is spectacular! 💥⭐",
            "Life aboard the ISS: A day in orbit 👨‍🚀🏠 #SpaceLife",
            "Discovering water ice on the Moon! 💧🌙 #Artemis",
            "Saturn's rings in unprecedented detail 🪐💍",
            "The future of space exploration starts now 🚀🔮",
            "Happy Earth Day from space! 🌍💚 #EarthDay"
        ],
        'hashtags': ['#NASA', '#Space', '#ISS', '#Mars', '#Artemis']
    }
}

def generate_youtube_data():
    """Generate YouTube data for all clients"""
    data = []
    
    for brand, content in BRAND_CONTENT.items():
        dates = generate_dates(days_back=60, count=40)
        
        for i, date in enumerate(dates):
            caption = random.choice(content['captions'])
            hashtags = ' '.join(random.sample(content['hashtags'], k=min(3, len(content['hashtags']))))
            
            # Realistic engagement metrics based on brand size
            base_views = {
                'nike': (500000, 2000000),
                'adidas': (300000, 1500000),
                'redbull': (400000, 1800000),
                'gopro': (200000, 1000000),
                'mrbeast': (5000000, 50000000),
                'nasa': (300000, 2000000)
            }
            
            views = random.randint(*base_views.get(brand, (100000, 500000)))
            likes = int(views * random.uniform(0.03, 0.08))  # 3-8% like rate
            comments = int(views * random.uniform(0.001, 0.005))  # 0.1-0.5% comment rate
            
            data.append({
                'platform': 'youtube',
                'username': brand,
                'post_url': f'https://www.youtube.com/watch?v={brand}_{i}',
                'caption': f'{caption} {hashtags}',
                'media_url': f'https://i.ytimg.com/vi/{brand}_{i}/maxresdefault.jpg',
                'likes': likes,
                'comments': comments,
                'views': views,
                'upload_date': date
            })
    
    df = pd.DataFrame(data)
    df.to_csv(os.path.join(DATA_DIR, 'youtube_data.csv'), index=False)
    print(f"✅ Generated {len(data)} YouTube posts")

def generate_instagram_data():
    """Generate Instagram data for all clients"""
    data = []
    
    for brand, content in BRAND_CONTENT.items():
        dates = generate_dates(days_back=45, count=50)
        
        for i, date in enumerate(dates):
            caption = random.choice(content['captions'])
            hashtags = ' '.join(content['hashtags'])
            
            # Instagram engagement metrics
            base_likes = {
                'nike': (100000, 500000),
                'adidas': (80000, 400000),
                'redbull': (90000, 450000),
                'gopro': (50000, 250000),
                'mrbeast': (500000, 2000000),
                'nasa': (200000, 800000)
            }
            
            likes = random.randint(*base_likes.get(brand, (50000, 200000)))
            comments = int(likes * random.uniform(0.01, 0.03))  # 1-3% comment rate
            views = int(likes * random.uniform(2, 4)) if random.random() > 0.5 else None
            
            data.append({
                'platform': 'instagram',
                'username': brand,
                'post_url': f'https://www.instagram.com/p/{brand}_{i}/',
                'caption': f'{caption}\n.\n{hashtags}',
                'media_url': f'https://instagram.com/{brand}/{i}.jpg',
                'likes': likes,
                'comments': comments,
                'views': views if views else '',
                'upload_date': date
            })
    
    df = pd.DataFrame(data)
    df.to_csv(os.path.join(DATA_DIR, 'instagram_data.csv'), index=False)
    print(f"✅ Generated {len(data)} Instagram posts")

def generate_facebook_data():
    """Generate Facebook data for all clients"""
    data = []
    
    for brand, content in BRAND_CONTENT.items():
        dates = generate_dates(days_back=50, count=35)
        
        for i, date in enumerate(dates):
            caption = random.choice(content['captions'])
            
            # Facebook engagement metrics
            base_likes = {
                'nike': (50000, 150000),
                'adidas': (40000, 120000),
                'redbull': (60000, 180000),
                'gopro': (30000, 100000),
                'mrbeast': (200000, 800000),
                'nasa': (100000, 400000)
            }
            
            likes = random.randint(*base_likes.get(brand, (30000, 100000)))
            comments = int(likes * random.uniform(0.005, 0.02))  # 0.5-2% comment rate
            views = int(likes * random.uniform(3, 6))
            
            data.append({
                'platform': 'facebook',
                'username': brand,
                'post_url': f'https://www.facebook.com/{brand}/posts/{i}',
                'caption': caption,
                'media_url': f'https://facebook.com/{brand}/photos/{i}.jpg',
                'likes': likes,
                'comments': comments,
                'views': views,
                'upload_date': date
            })
    
    df = pd.DataFrame(data)
    df.to_csv(os.path.join(DATA_DIR, 'facebook_data.csv'), index=False)
    print(f"✅ Generated {len(data)} Facebook posts")

def generate_twitter_data():
    """Generate Twitter/X data for all clients"""
    data = []
    
    for brand, content in BRAND_CONTENT.items():
        dates = generate_dates(days_back=30, count=60)
        
        for i, date in enumerate(dates):
            # Twitter has shorter captions
            caption_base = random.choice(content['captions'])
            # Trim to Twitter length
            caption = caption_base[:200] if len(caption_base) > 200 else caption_base
            hashtags = ' '.join(random.sample(content['hashtags'], k=min(2, len(content['hashtags']))))
            
            # Twitter engagement metrics
            base_likes = {
                'nike': (10000, 50000),
                'adidas': (8000, 40000),
                'redbull': (12000, 60000),
                'gopro': (5000, 30000),
                'mrbeast': (100000, 500000),
                'nasa': (50000, 200000)
            }
            
            likes = random.randint(*base_likes.get(brand, (5000, 25000)))
            comments = int(likes * random.uniform(0.02, 0.05))  # 2-5% reply rate
            views = int(likes * random.uniform(10, 20))
            
            data.append({
                'platform': 'twitter',
                'username': brand,
                'post_url': f'https://twitter.com/{brand}/status/{1000000000 + i}',
                'caption': f'{caption} {hashtags}',
                'media_url': f'https://pbs.twimg.com/media/{brand}_{i}.jpg',
                'likes': likes,
                'comments': comments,
                'views': views,
                'upload_date': date
            })
    
    df = pd.DataFrame(data)
    df.to_csv(os.path.join(DATA_DIR, 'twitter_data.csv'), index=False)
    print(f"✅ Generated {len(data)} Twitter posts")

if __name__ == '__main__':
    print("🚀 Starting data population...")
    print()
    
    generate_youtube_data()
    generate_instagram_data()
    generate_facebook_data()
    generate_twitter_data()
    
    print()
    print("✅ All data populated successfully!")
    print(f"📁 Data files saved to: {DATA_DIR}")
    print()
    print("📊 Summary:")
    for filename in ['youtube_data.csv', 'instagram_data.csv', 'facebook_data.csv', 'twitter_data.csv']:
        filepath = os.path.join(DATA_DIR, filename)
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)
            print(f"   - {filename}: {len(df)} posts across {df['username'].nunique()} clients")
    print()
    print("🎉 Your dashboard should now look much more presentable!")
    print("💡 Tip: Refresh your browser to see the new data")
