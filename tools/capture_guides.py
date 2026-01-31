from pathlib import Path
from playwright.sync_api import sync_playwright

OUT_DIR = Path(__file__).resolve().parent.parent / 'assets' / 'help'
OUT_DIR.mkdir(parents=True, exist_ok=True)
ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / 'index.html'

with sync_playwright() as p:
    browser = p.chromium.launch()
    context = browser.new_context(viewport={'width':1400, 'height':900})
    page = context.new_page()
    page.goto(INDEX.as_uri())
    page.wait_for_load_state('networkidle')
    try:
        page.wait_for_selector('#main-stage', timeout=10000)
    except Exception:
        pass
    # small pause to let in-page scripts initialize
    page.wait_for_timeout(500)

    # Ensure overlays closed
    page.evaluate("() => { document.getElementById('help-screen').style.display = 'none'; document.getElementById('overlay').style.display = 'none'; document.getElementById('deck-overlay').style.display = 'none'; }")

    # 1) Combos (belt track)
    try:
        el = page.query_selector('#belt-track')
        target = el if el else page
        el.screenshot(path=str(OUT_DIR / 'combos.png')) if el else page.screenshot(path=str(OUT_DIR / 'combos.png'))
        print('combos.png created')
    except Exception as e:
        print('combos capture failed', e)

    # 2) Deck build (deck stack)
    try:
        el = page.query_selector('#deck-stack')
        el.screenshot(path=str(OUT_DIR / 'deck_build.png'))
        print('deck_build.png created')
    except Exception as e:
        print('deck capture failed', e)

    # 3) Relics (open shop overlay)
    try:
        page.evaluate("() => { if (window.game && game.openShop) game.openShop(); }")
        # Allow the overlay animation to run slightly then force-ensure it's visible
        page.wait_for_timeout(600)
        page.evaluate("() => { const w = document.getElementById('shop-content-wrapper'); if (w) { w.style.transform='none'; w.style.opacity='1'; w.style.visibility='visible'; } const o = document.getElementById('overlay'); if (o) o.style.display='flex'; }")
        el = page.query_selector('#shop-content-wrapper')
        if el:
            try:
                el.screenshot(path=str(OUT_DIR / 'relics.png'))
                print('relics.png created')
            except Exception:
                # fallback to full-page crop around expected center area
                page.screenshot(path=str(OUT_DIR / 'relics.png'))
                print('relics.png (fallback full page) created')
        else:
            page.screenshot(path=str(OUT_DIR / 'relics.png'))
            print('relics.png (fallback full page) created')
        # close shop
        page.evaluate("() => { document.getElementById('overlay').style.display = 'none'; }")
    except Exception as e:
        print('shop capture failed', e)

    # 4) Daily overview (full stage)
    try:
        height = page.evaluate('() => Math.max(document.documentElement.scrollHeight, document.body.scrollHeight)')
        page.set_viewport_size({'width':1400, 'height': min(2000, height)})
        page.screenshot(path=str(OUT_DIR / 'daily.png'), full_page=True)
        print('daily.png created')
    except Exception as e:
        print('daily capture failed', e)

    # 5) Accessibility / Controls (ticket column)
    try:
        el = page.query_selector('#ticket-column')
        el.screenshot(path=str(OUT_DIR / 'accessibility.png'))
        print('accessibility.png created')
    except Exception as e:
        print('ticket capture failed', e)

    # Quick smoke test: open Help, expand first guide, click image, verify overlay
    try:
        # Use game.showHelp so event handlers are attached
        page.evaluate("() => { if (window.game && game.showHelp) game.showHelp('guides'); }")
        page.wait_for_timeout(120)
        # click the first guide header directly via element handle
        headers = page.query_selector_all('#help-guides .guide-section .guide-header')
        if headers and len(headers) > 0:
            try:
                headers[0].click(timeout=600)
            except Exception:
                pass
        page.wait_for_timeout(120)
        img_sel = '#help-guides .guide-section .guide-image img'
        imgs = page.query_selector_all(img_sel)
        clicked = False
        for im in imgs:
            try:
                im.click(timeout=600)
                clicked = True
                break
            except Exception:
                continue
        page.wait_for_timeout(180)
        overlay_display = page.evaluate("() => document.getElementById('image-overlay').style.display")
        print('overlay_display=' + str(overlay_display) + ' clicked=' + str(clicked))
        # close overlay
        page.evaluate("() => { document.getElementById('image-overlay').style.display = 'none'; if (document.getElementById('help-screen')) document.getElementById('help-screen').style.display = 'none'; }")
    except Exception as e:
        print('smoke test failed', e)

    browser.close()
    print('done')
