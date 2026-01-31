from playwright.sync_api import sync_playwright
from pathlib import Path
p=Path(__file__).resolve().parent.parent / 'index.html'
with sync_playwright() as pw:
    b=pw.chromium.launch()
    ctx=b.new_context(viewport={'width':1200,'height':900})
    page=ctx.new_page()
    # log console messages (helps detect JS errors)
    page.on('console', lambda msg: print('PAGE LOG ->', msg.type, msg.text))
    page.on('pageerror', lambda exc: print('PAGE ERROR ->', exc))
    page.goto(p.as_uri())
    page.wait_for_load_state('networkidle')
    page.evaluate("() => { document.getElementById('options-overlay').style.display='flex'; }")
    page.select_option('#lang-select','es')
    page.wait_for_timeout(600)
    page.evaluate("() => { if (window.game && game.showHelp) game.showHelp('guides'); }")
    page.wait_for_timeout(200)
    # Force set language directly to ensure listeners/fire timing
    page.evaluate("() => { if (window.game) game.setLanguage('es'); }")
    page.wait_for_timeout(300)

    # Try to detect script parse errors by validating script blocks
    check = page.evaluate("() => { const scripts = Array.from(document.scripts).map(s => s.textContent || ''); for (let i=0;i<scripts.length;i++){ try{ new Function(scripts[i]); } catch(e){ return {index:i,msg:e.toString(), snippet: scripts[i].slice(0,200)} } } return {ok:true} }")
    print('script check ->', check)

    val = page.locator('[data-i18n="guide.basics.caption"]').inner_text()
    print('basics caption ->', val)
    shop = page.locator('[data-i18n="guide.header.shop"]').inner_text()
    print('shop header ->', shop)
    conveyor = page.locator('[data-i18n="guide.caption.conveyor"]').inner_text()
    print('conveyor caption ->', conveyor)
    tip1 = page.locator('[data-i18n="tip.1"]').inner_text()
    print('tip1 ->', tip1)
    hasSet = page.evaluate('() => !!(window.game && window.game.setLanguage)')
    print('game.has setLanguage ->', hasSet)
    try:
        translations = page.evaluate('() => JSON.stringify(window.game._translations)')
    except Exception as e:
        translations = f'error: {e}'
    print('game._translations ->', translations)
    b.close()