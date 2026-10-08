from playwright.sync_api import sync_playwright

with open('Relatorio_Radar_Editais_PNCP_SIGA_2026.html', 'r', encoding='utf-8') as f:
    html = f.read()

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width': 1440, 'height': 900})
    page.set_content(html, wait_until='networkidle')
    
    page.evaluate("""() => {
        const pages = document.querySelectorAll('.page');
        pages.forEach((p, i) => {
            p.id = 'pg-radar-' + i;
        });
    }""")
    
    for i in range(5):
        el = page.query_selector(f'#pg-radar-{i}')
        if el:
            el.screenshot(path=f'preview_radar_p{i+1}.png')
            print(f'Screenshot pagina {i+1} ok')
    
    browser.close()

print('Todos os screenshots do Radar PNCP gerados!')
