# utils/mock_social.py
import random, time
def mock_fetch_social(username):
    time.sleep(0.02)
    if not username:
        return None
    return {
        'username': username,
        'followers': random.randint(100,10000),
        'latest_posts': [f"Latest post {i} from {username}" for i in range(1,4)]
    }

def mock_fetch_news(name):
    time.sleep(0.02)
    hits = random.randint(0,3)
    return [f"News headline {i} about {name}" for i in range(1,hits+1)]

def aggregate_external_info(user):
    time.sleep(0.02)
    base_score = 20
    if user.name:
        base_score += 30
    if user.phone:
        base_score += 10
    if user.hospital:
        base_score += 10
    social = {}
    for s in ['instagram','twitter','facebook','youtube','telegram']:
        val = getattr(user, s, None)
        if val:
            social[s] = mock_fetch_social(val)
            base_score += 5
    news = mock_fetch_news(user.name or user.email or '')
    external = {
        'social': social,
        'news': news,
        'sources_found': len(social) + len(news),
        'confidence': min(100, base_score + random.randint(-5,10))
    }
    return external

def mock_search_by_name_or_dept(name, dept):
    time.sleep(0.02)
    sample = [
        {'id':1,'name':'Dr. Rajesh Kumar','specialization':'Cardiology','city':'New Delhi','phone':'9876543210','image':'/static/sample1.jpg'},
        {'id':2,'name':'Dr. Priya Sharma','specialization':'Dermatology','city':'Mumbai','phone':'9834567890','image':'/static/sample2.jpg'},
        {'id':3,'name':'Dr. Amit Verma','specialization':'Orthopedics','city':'Kolkata','phone':'','image':'/static/sample3.jpg'},
    ]
    res = []
    q = (name or '').lower()
    d = (dept or '').lower()
    for s in sample:
        if q and q in s['name'].lower():
            res.append(s)
        elif d and d in s['specialization'].lower():
            res.append(s)
    return res
