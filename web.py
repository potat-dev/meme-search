from jinja2 import Environment, FileSystemLoader, select_autoescape

env = Environment(
    loader=FileSystemLoader('templates'),
    autoescape=select_autoescape(['html'])
)
template = env.get_template('template.html')

rendered_page = template.render(
    search_q="Cat",
    posts=[
        {
            "text": f"test text {i}",
            "id": i,
            "match": 100 - i,
        } for i in range(30)
    ]
)

with open('index.html', 'w', encoding="utf8") as file:
    file.write(rendered_page)
