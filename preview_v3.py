from playwright.sync_api import sync_playwright
import os

with open('Relatorio_DTO_2026_v3.html', 'r', encoding='utf-8') as f:
    html = f.read()

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width': 1440, 'height': 900})
    page.set_content(html, wait_until='networkidle')
    
    page.evaluate("""() => {
        const pages = document.querySelectorAll('.page');
        pages.forEach((p, i) => {
            p.id = 'pg-' + i;
        });
    }""")
    
    for i in range(8):
        el = page.query_selector(f'#pg-{i}')
        if el:
            el.screenshot(path=f'preview_v3_p{i+1}.png')
            print(f'Screenshot pagina {i+1} ok')
    
    browser.close()

print('Todos os screenshots v3 gerados!')
