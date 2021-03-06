from app import db, BaseLayer, Condiment, FullTaco, Mixin, Seasoning, Shell
import requests
from os import path
from urlparse import urlparse
from bs4 import BeautifulSoup
import markdown2 as md

base_url = 'https://raw.github.com/sinker/tacofancy/master'

def get_cookin(model, links):
    saved = []
    for link in links:
        full_url = '%s/%s' % (base_url, link)
        recipe = requests.get(full_url)
        soup = BeautifulSoup(md.markdown(recipe.content))
        name = soup.find('h1')
        if name:
            name = name.text
        else:
            name = ' '.join(path.basename(urlparse(full_url).path).split('_')).title()
        ingredient = db.session.query(model).get(full_url)
        ingredient_data = {
            'url': full_url,
            'name': name,
            'recipe': recipe.content.decode('utf-8'),
        }
        if not ingredient:
            ingredient = model(**ingredient_data)
            db.session.add(ingredient)
            db.session.commit()
        else:
            for k,v in ingredient_data.items():
                setattr(ingredient, k, v)
            db.session.add(ingredient)
            db.session.commit()
        saved.append(ingredient)
    return saved

MAPPER = {
    'base_layers': BaseLayer,
    'condiments': Condiment, 
    'mixins': Mixin,
    'seasonings': Seasoning,
}

def preheat():
    index = requests.get('%s/INDEX.md' % base_url)
    soup = BeautifulSoup(md.markdown(index.content))
    links = [a for a in soup.find_all('a') if a.get('href').endswith('.md')]
    full_tacos = [f.get('href') for f in links if 'full_tacos/' in f.get('href')]
    base_layers = [b.get('href') for b in links if 'base_layers/' in b.get('href')]
    mixins = [m.get('href') for m in links if 'mixins/' in m.get('href')]
    condiments = [c.get('href') for c in links if 'condiments/' in c.get('href')]
    seasonings = [s.get('href') for s in links if 'seasonings/' in s.get('href')]
    bases = get_cookin(BaseLayer, base_layers)
    conds = get_cookin(Condiment, condiments)
    seas = get_cookin(Seasoning, seasonings)
    mix = get_cookin(Mixin, mixins)
    for full_taco in get_cookin(FullTaco, full_tacos):
        soup = BeautifulSoup(md.markdown(full_taco.recipe))
        ingredient_links = [l.get('href') for l in soup.find_all('a') if l.get('href').endswith('.md')]
        for link in ingredient_links:
            parts = urlparse(link).path.split('/')[-2:]
            kind = MAPPER[parts[0]]
            scrubbed_link = '/'.join(parts)
            full_link = '%s/%s' % (base_url, scrubbed_link)
            ingredient = db.session.query(kind).get(full_link)
            setattr(full_taco, ingredient.__tablename__, ingredient)
            db.session.add(full_taco)
            db.session.commit()
    return None

if __name__ == '__main__':
    preheat()
